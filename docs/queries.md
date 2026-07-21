(queries)=
# Lookups and database expressions

## Standard lookups

The fields prepare whenever values for Django's standard lookups:

- `exact`, `gt`, `gte`, `lt`, and `lte`
- `range` and `in`
- `isnull`

```python
import whenever

Event.objects.filter(created_at__gte=whenever.Instant.now())
Event.objects.filter(
    event_date__range=(
        whenever.Date(2026, 1, 1),
        whenever.Date(2026, 12, 31),
    )
)
```

## Date and time transforms

Timestamp-like fields register `date` and `time` transforms:

```python
Event.objects.filter(created_at__date=whenever.Date(2026, 4, 6))
Event.objects.filter(created_at__time__gte=whenever.Time(9, 0))
```

The transforms operate on the stored timestamp. Database/session timezone
behavior therefore follows the selected backend and Django connection
configuration.

## Database expressions

All four expressions support model annotations and `values_list()`.

### `WheneverNow()`

Returns the database current timestamp as `whenever.Instant`:

```python
from whenever_django.functions import WheneverNow

current = Event.objects.annotate(database_now=WheneverNow())
```

### `ToInstant(expression)`

Projects a timestamp expression as `whenever.Instant`. This is especially
useful for the primary timestamp column of a zoned or offset composite field:

```python
from whenever_django.functions import ToInstant

rows = Event.objects.annotate(
    starts_instant=ToInstant("starts_at"),
)
```

The SQL expression is an identity. Conversion changes only the Python result,
so the precise instant survives DST folds and historical timezone changes.

### `ToZoned(expression, tz_string)`

Projects an instant into one fixed IANA timezone:

```python
from whenever_django.functions import ToZoned

rows = Event.objects.annotate(
    starts_in_paris=ToZoned("created_at", "Europe/Paris"),
)
```

The timezone name is validated when `ToZoned` is constructed. An invalid name
raises `whenever.TimeZoneNotFoundError` before the query runs. The timestamp is
unchanged in SQL and converted to `whenever.ZonedDateTime` in Python. A
per-row timezone expression is not supported.

### `DurationBetween(lhs, rhs)`

Computes `lhs - rhs` and returns `whenever.TimeDelta`:

```python
from whenever_django.functions import DurationBetween

rows = Event.objects.annotate(
    elapsed=DurationBetween("finished_at", "created_at"),
)
```

The expression delegates temporal subtraction to Django's database backend.
It supports positive, zero, negative, and null results. SQLite returns integer
microseconds; PostgreSQL returns an interval represented by
`datetime.timedelta`; both are converted to `whenever.TimeDelta`.

## Deliberate limits

Automatic `F()` arithmetic is not yet part of the public contract. Use
`DurationBetween` for timestamp subtraction. The proposed `__in_tz` lookup is
also not implemented; use `ToZoned` to project results into a fixed zone.
