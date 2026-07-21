(cookbook)=
# Cookbook

## Callable defaults

Pass callables, rather than evaluated values, for per-instance defaults:

```python
import whenever

from whenever_django.fields import InstantField, WheneverDateField


def today_utc() -> whenever.Date:
    return whenever.Instant.now().to_tz("UTC").date()


created_at = InstantField(default=whenever.Instant.now)
business_date = WheneverDateField(default=today_utc)
```

Avoid `default=whenever.Instant.now()`, which evaluates once when the model
module is imported.

## Typed annotations

Expose an instant from a composite timestamp and calculate elapsed time in one
query:

```python
from whenever_django.functions import DurationBetween, ToInstant, ToZoned

events = Event.objects.annotate(
    starts_instant=ToInstant("starts_at"),
    local_created=ToZoned("created_at", "America/Los_Angeles"),
    elapsed=DurationBetween("finished_at", "created_at"),
)

for event in events:
    reveal_type(event.starts_instant)  # runtime: whenever.Instant
    reveal_type(event.local_created)  # runtime: whenever.ZonedDateTime
    reveal_type(event.elapsed)  # runtime: whenever.TimeDelta | None
```

`ToZoned` uses one timezone for the complete expression. It does not accept an
`F()` expression for a per-row timezone name.

## Composite timezone fields

Use a composite field when the zone or offset is domain data rather than only
a display preference:

```python
class Appointment(models.Model):
    scheduled_for = ZonedDateTimeField()
```

The schema contains `scheduled_for` and `scheduled_for_tz`. Normally, work
through the `scheduled_for` attribute:

```python
appointment = Appointment.objects.create(
    scheduled_for=whenever.ZonedDateTime(
        2026, 10, 25, 9, 30, tz="Europe/Paris"
    )
)
appointment.refresh_from_db()
assert appointment.scheduled_for.tz == "Europe/Paris"
```

For reporting that needs only the exact moment, annotate
`ToInstant("scheduled_for")`. Do not manually modify the paired column while a
composite value is cached on the model instance.

## Forms and DRF boundaries

Django forms parse ISO strings into whenever values:

```python
from django import forms
from whenever_django.forms import ZonedDateTimeFormField


class AppointmentForm(forms.Form):
    scheduled_for = ZonedDateTimeFormField()


form = AppointmentForm(
    {"scheduled_for": "2026-10-25T09:30:00+01:00[Europe/Paris]"}
)
assert form.is_valid()
value = form.cleaned_data["scheduled_for"]
```

With the `drf` extra installed, automatic `ModelSerializer` mapping is enough
for most APIs. Use an explicit serializer field when defining a non-model
property or a computed value:

```python
from rest_framework import serializers
from whenever_django.contrib.drf.fields import InstantSerializerField


class ReportSerializer(serializers.Serializer):
    generated_at = InstantSerializerField()
```

## Staged migration to a zoned composite field

Suppose an existing aware timestamp has a trustworthy `timezone_name` source.
Use separate deployments:

1. Add a nullable `ZonedDateTimeField` while retaining the old timestamp.
2. Backfill both the UTC timestamp and IANA name in a data migration.
3. Deploy application code that writes and reads the new field.
4. Verify counts, nulls, sample instants, DST boundaries, and zone names.
5. Make the new field non-null if required.
6. Remove the old field in a later migration.

For large tables, backfill in bounded batches using the project's operational
tooling. The library intentionally does not provide a bulk `from_db_value`
hook or migration runner.

See the full [`DateTimeField` migration guide](migrations.md) before changing
existing production columns.
