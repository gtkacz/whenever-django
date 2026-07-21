from __future__ import annotations

import datetime as _stdlib
from typing import Any, cast

import whenever
from django.db.backends.base.base import BaseDatabaseWrapper
from django.db.models import Expression, Func
from django.db.models.sql.compiler import SQLCompiler

from whenever_django.fields import InstantField, TimeDeltaField
from whenever_django.fields._base import WheneverField

_REFERENCE_INSTANT = whenever.Instant.parse_iso("2000-01-01T00:00:00Z")


class _IdentityTimestamp(Func):
    """Render a timestamp expression without changing its SQL value."""

    arity = 1
    template = "%(expressions)s"


class _ZonedProjectionField(WheneverField):
    """Convert a timestamp result using one fixed IANA timezone."""

    whenever_type = whenever.ZonedDateTime

    def __init__(self, tz_string: str) -> None:
        self.tz_string = tz_string
        super().__init__()

    def get_internal_type(self) -> str:
        return "DateTimeField"

    def _from_db(self, value: Any, connection: Any) -> whenever.ZonedDateTime:
        instant = InstantField()._from_db(value, connection)
        return instant.to_tz(self.tz_string)

    def _to_db(self, value: whenever.ZonedDateTime) -> _stdlib.datetime:
        return value.to_instant().to_stdlib()

    def _parse(self, value: str) -> whenever.ZonedDateTime:
        return whenever.ZonedDateTime.parse_iso(value)


class WheneverNow(Func):
    """Database-level current timestamp that returns an Instant."""

    template = "CURRENT_TIMESTAMP"

    @property
    def output_field(self) -> InstantField:
        return InstantField()


class ToInstant(_IdentityTimestamp):
    """Project a timestamp expression as :class:`whenever.Instant`.

    Composite zoned and offset fields store their instant in the primary
    timestamp column, so the SQL expression is deliberately an identity.
    """

    def __init__(self, expression: Expression | str) -> None:
        super().__init__(expression, output_field=InstantField())


class ToZoned(_IdentityTimestamp):
    """Project an instant into a fixed IANA timezone.

    The timestamp remains unchanged in SQL. The timezone is attached while
    Django converts each result, preserving folds, skipped times, and
    historical timezone changes.
    """

    def __init__(self, expression: Expression | str, tz_string: str) -> None:
        if not isinstance(tz_string, str):
            raise TypeError("tz_string must be a string")
        _REFERENCE_INSTANT.to_tz(tz_string)
        self.tz_string = tz_string
        super().__init__(
            expression,
            output_field=_ZonedProjectionField(tz_string),
        )


class DurationBetween(Func):
    """Return ``lhs - rhs`` as :class:`whenever.TimeDelta`.

    SQL generation delegates to Django's backend temporal-subtraction API,
    which returns integer microseconds on SQLite and an interval on
    PostgreSQL.
    """

    arity = 2

    def __init__(
        self,
        lhs: Expression | str,
        rhs: Expression | str,
    ) -> None:
        super().__init__(lhs, rhs, output_field=TimeDeltaField())

    def as_sql(
        self,
        compiler: SQLCompiler,
        connection: BaseDatabaseWrapper,
        function: str | None = None,
        template: str | None = None,
        arg_joiner: str | None = None,
        **extra_context: Any,
    ) -> tuple[
        str,
        list[str | int] | tuple[str | int, ...] | tuple[()],
    ]:
        connection.ops.check_expression_support(self)
        lhs_expression, rhs_expression = self.source_expressions
        lhs = compiler.compile(lhs_expression)
        rhs = compiler.compile(rhs_expression)
        return cast(
            tuple[
                str,
                list[str | int] | tuple[str | int, ...] | tuple[()],
            ],
            connection.ops.subtract_temporals(
                lhs_expression.output_field.get_internal_type(),
                lhs,
                rhs,
            ),
        )


__all__ = ["DurationBetween", "ToInstant", "ToZoned", "WheneverNow"]
