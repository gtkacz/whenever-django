# whenever-django

[![PyPI](https://img.shields.io/pypi/v/whenever-django.svg?color=blue)](https://pypi.org/project/whenever-django/)
[![Python](https://img.shields.io/pypi/pyversions/whenever-django.svg)](https://pypi.org/project/whenever-django/)
[![Django](https://img.shields.io/badge/django-%3E%3D4.2-green.svg)](https://www.djangoproject.com/)
[![Documentation](https://img.shields.io/badge/docs-GitHub%20Pages-blue.svg)](https://python-whenever.github.io/whenever-django/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

Type-safe temporal fields and ORM expressions for Django, powered by
[`whenever`](https://github.com/ariebovenberg/whenever).

`whenever-django` keeps distinct concepts distinct: instants, local
datetimes, zoned and offset datetimes, dates, times, and fixed or calendar-aware
durations. It integrates those types with Django models, forms, admin, optional
DRF serializers, and common ORM queries.

Read the complete documentation at
**https://python-whenever.github.io/whenever-django/**.

## Installation

```bash
pip install whenever-django
```

With Django REST Framework support:

```bash
pip install "whenever-django[drf]"
```

Add `"whenever_django"` to `INSTALLED_APPS`.

Requirements: Python 3.10+, Django 4.2+, whenever 0.10.0+, and PostgreSQL or
SQLite.

## Quick start

```python
import whenever
from django.db import models

from whenever_django.fields import (
    InstantField,
    WheneverDateField,
    ZonedDateTimeField,
)


class Event(models.Model):
    name = models.CharField(max_length=200)
    created_at = InstantField(default=whenever.Instant.now)
    starts_at = ZonedDateTimeField()
    event_date = WheneverDateField(null=True)


event = Event.objects.create(
    name="PyCon",
    starts_at=whenever.ZonedDateTime(
        2026, 5, 15, 9, 0, tz="America/Chicago"
    ),
    event_date=whenever.Date(2026, 5, 15),
)

upcoming = Event.objects.filter(
    created_at__gte=whenever.Instant.now(),
)

event.refresh_from_db()
assert event.starts_at.tz == "America/Chicago"
```

Fields reject standard-library values by default. Use `from_stdlib=True`
temporarily when staging a migration from existing Django fields.

## Included fields

| Category | Fields |
|---|---|
| Core | `InstantField`, `PlainDateTimeField`, `WheneverDateField`, `WheneverTimeField` |
| Composite | `ZonedDateTimeField`, `OffsetDateTimeField` |
| Extended calendar | `YearMonthField`, `MonthDayField` |
| Durations | `TimeDeltaField`, `ItemizedDeltaField`, `ItemizedDateDeltaField` |

Every model field has a corresponding Django form field. Installing the `drf`
extra adds corresponding serializer fields and automatic `ModelSerializer`
mapping.

## ORM expressions

```python
from whenever_django.functions import (
    DurationBetween,
    ToInstant,
    ToZoned,
    WheneverNow,
)

rows = Event.objects.annotate(
    database_now=WheneverNow(),
    starts_instant=ToInstant("starts_at"),
    starts_in_tokyo=ToZoned("starts_at", "Asia/Tokyo"),
    elapsed=DurationBetween("finished_at", "created_at"),
)
```

Standard comparison, range, membership, and null lookups work with whenever
values. Timestamp-like fields also provide `date` and `time` transforms.

Automatic temporal `F()` arithmetic and an `__in_tz` lookup are not currently
part of the supported API. Use `DurationBetween` for timestamp subtraction and
`ToZoned` for fixed-zone result projection.

## Documentation

- [Installation and quick start](https://python-whenever.github.io/whenever-django/installation.html)
- [Model, form, and DRF fields](https://python-whenever.github.io/whenever-django/fields.html)
- [Lookups and database expressions](https://python-whenever.github.io/whenever-django/queries.html)
- [`DateTimeField` migration guide](https://python-whenever.github.io/whenever-django/migrations.html)
- [Cookbook](https://python-whenever.github.io/whenever-django/cookbook.html)
- [Comparison matrix](https://python-whenever.github.io/whenever-django/comparison.html)
- [Limitations and backend support](https://python-whenever.github.io/whenever-django/limitations.html)
- [API reference](https://python-whenever.github.io/whenever-django/api_reference.html)

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

MIT — see [LICENSE](LICENSE).
