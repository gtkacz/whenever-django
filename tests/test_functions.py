"""Tests for whenever-aware database expressions."""

from __future__ import annotations

import datetime as stdlib_dt

import pytest
import whenever
from django.db import connection, models

from whenever_django.fields import (
    InstantField,
    OffsetDateTimeField,
    ZonedDateTimeField,
)
from whenever_django.functions import DurationBetween, ToInstant, ToZoned

pytestmark = pytest.mark.django_db(transaction=True)


class FunctionTestModel(models.Model):
    start = InstantField(null=True)
    end = InstantField(null=True)
    zoned = ZonedDateTimeField(null=True)
    offset = OffsetDateTimeField(null=True)

    class Meta:
        app_label = "tests"


@pytest.fixture(autouse=True)
def _create_table():
    with connection.schema_editor() as editor:
        editor.create_model(FunctionTestModel)
    yield
    with connection.schema_editor() as editor:
        editor.delete_model(FunctionTestModel)


class TestToInstant:
    def test_annotation_preserves_composite_instants_and_null(self):
        zoned = whenever.ZonedDateTime.parse_iso(
            "2023-11-05T01:30:00-05:00[America/New_York]"
        )
        offset = whenever.OffsetDateTime.parse_iso("2026-04-06T10:00:00+09:00")
        row = FunctionTestModel.objects.create(zoned=zoned, offset=offset)
        null_row = FunctionTestModel.objects.create()

        annotated = FunctionTestModel.objects.annotate(
            zoned_instant=ToInstant("zoned"),
            offset_instant=ToInstant("offset"),
        ).get(pk=row.pk)
        annotated_null = FunctionTestModel.objects.annotate(
            zoned_instant=ToInstant("zoned"),
            offset_instant=ToInstant("offset"),
        ).get(pk=null_row.pk)

        assert annotated.zoned_instant == zoned.to_instant()
        assert annotated.offset_instant == offset.to_instant()
        assert annotated_null.zoned_instant is None
        assert annotated_null.offset_instant is None

    def test_values_list_returns_instants(self):
        zoned = whenever.ZonedDateTime.parse_iso(
            "2011-12-31T00:00:00+14:00[Pacific/Apia]"
        )
        FunctionTestModel.objects.create(zoned=zoned)

        result = FunctionTestModel.objects.values_list(
            ToInstant("zoned"), flat=True
        ).get()

        assert isinstance(result, whenever.Instant)
        assert result == zoned.to_instant()


class TestToZoned:
    def test_invalid_timezone_is_rejected_at_construction(self):
        with pytest.raises(whenever.TimeZoneNotFoundError):
            ToZoned("start", "Not/AZone")

    @pytest.mark.parametrize(
        ("iso", "expected_local"),
        [
            ("2023-11-05T05:30:00Z", "2023-11-05T01:30:00-04:00"),
            ("2023-11-05T06:30:00Z", "2023-11-05T01:30:00-05:00"),
            ("2024-03-10T06:59:59Z", "2024-03-10T01:59:59-05:00"),
            ("2024-03-10T07:00:00Z", "2024-03-10T03:00:00-04:00"),
        ],
    )
    def test_annotation_preserves_dst_transitions(self, iso: str, expected_local: str):
        instant = whenever.Instant.parse_iso(iso)
        row = FunctionTestModel.objects.create(start=instant)

        result = FunctionTestModel.objects.annotate(
            local=ToZoned("start", "America/New_York")
        ).get(pk=row.pk)

        assert isinstance(result.local, whenever.ZonedDateTime)
        assert result.local.to_instant() == instant
        assert str(result.local).startswith(expected_local)

    @pytest.mark.parametrize(
        ("iso", "expected_local"),
        [
            ("2011-12-30T09:59:59Z", "2011-12-29T23:59:59-10:00"),
            ("2011-12-30T10:00:00Z", "2011-12-31T00:00:00+14:00"),
        ],
    )
    def test_values_list_preserves_apia_date_skip(self, iso: str, expected_local: str):
        instant = whenever.Instant.parse_iso(iso)
        FunctionTestModel.objects.create(start=instant)

        result = FunctionTestModel.objects.values_list(
            ToZoned("start", "Pacific/Apia"), flat=True
        ).get()

        assert result.to_instant() == instant
        assert str(result).startswith(expected_local)

    def test_null_is_preserved(self):
        FunctionTestModel.objects.create(start=None)

        result = FunctionTestModel.objects.values_list(
            ToZoned("start", "Europe/Paris"), flat=True
        ).get()

        assert result is None


class TestDurationBetween:
    def test_annotation_handles_positive_zero_negative_and_null(self):
        first = whenever.Instant.parse_iso("2026-04-06T10:00:00Z")
        later = whenever.Instant.parse_iso("2026-04-06T12:30:00Z")
        rows = [
            FunctionTestModel.objects.create(start=first, end=later),
            FunctionTestModel.objects.create(start=first, end=first),
            FunctionTestModel.objects.create(start=later, end=first),
            FunctionTestModel.objects.create(start=first, end=None),
        ]

        results = {
            row.pk: row.duration
            for row in FunctionTestModel.objects.annotate(
                duration=DurationBetween("end", "start")
            )
        }

        assert results[rows[0].pk] == whenever.TimeDelta(hours=2, minutes=30)
        assert results[rows[1].pk] == whenever.TimeDelta()
        assert results[rows[2].pk] == whenever.TimeDelta(hours=-2, minutes=-30)
        assert results[rows[3].pk] is None
        assert all(
            value is None or isinstance(value, whenever.TimeDelta)
            for value in results.values()
        )

    def test_values_list_returns_time_delta(self):
        start = whenever.Instant.parse_iso("2026-04-06T10:00:00Z")
        end = whenever.Instant.parse_iso("2026-04-06T10:00:00.000001Z")
        FunctionTestModel.objects.create(start=start, end=end)

        result = FunctionTestModel.objects.values_list(
            DurationBetween("end", "start"), flat=True
        ).get()

        assert result == whenever.TimeDelta(microseconds=1)


def test_time_delta_field_converts_postgresql_timedelta_result():
    from whenever_django.fields import TimeDeltaField

    result = TimeDeltaField().from_db_value(
        stdlib_dt.timedelta(days=-1, microseconds=1),
        expression=None,
        connection=None,
    )

    assert result == whenever.TimeDelta(stdlib_dt.timedelta(days=-1, microseconds=1))


def test_time_delta_field_converts_integer_microseconds():
    from whenever_django.fields import TimeDeltaField

    result = TimeDeltaField().from_db_value(
        1_500_001,
        expression=None,
        connection=None,
    )

    assert result == whenever.TimeDelta(seconds=1, microseconds=500_001)
