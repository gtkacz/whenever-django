(quickstart)=
# Quick start

Define model fields according to their semantics:

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
```

Create and query instances with whenever values:

```python
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
```

After a database reload, field values are whenever objects. A composite field
also restores its zone:

```python
event.refresh_from_db()
assert isinstance(event.created_at, whenever.Instant)
assert event.starts_at.tz == "America/Chicago"
```

Fields reject corresponding standard-library values by default. During a
staged migration, `from_stdlib=True` can temporarily accept them on writes:

```python
from whenever_django.fields import InstantField

legacy_timestamp = InstantField(from_stdlib=True)
```

This compatibility flag affects ORM write preparation. It does not eagerly
convert an instance attribute at assignment time; values are converted after
they are loaded from the database.

Continue with the [field guide](fields.md), [query guide](queries.md), or
[`DateTimeField` migration guide](migrations.md).
