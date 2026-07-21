(datetimefield-migration)=
# Migrating from Django `DateTimeField`

The physical timestamp column is often compatible with `InstantField` or
`PlainDateTimeField`, but a safe migration starts by deciding what each value
means. Back up the database, rehearse against the production backend, and
inspect generated migrations and SQL.

## 1. Audit and classify each field

Run the built-in audit command:

```bash
python manage.py whenever_audit
python manage.py whenever_audit --app-label your_app
```

Choose a replacement by semantics:

| Existing value means | Replacement | Constraint |
|---|---|---|
| A unique moment in time | `InstantField` | Use `USE_TZ=True`; normalize legacy values to aware UTC instants |
| A wall-clock value without a timezone | `PlainDateTimeField` | Keep the value deliberately naive |
| A moment plus its IANA timezone | `ZonedDateTimeField` | Add and backfill the paired `_tz` column |
| A moment plus a fixed offset | `OffsetDateTimeField` | Add and backfill the paired `_offset` column |

A `DateTimeField` does not preserve the original IANA timezone name. If the
application needs `ZonedDateTimeField`, derive the correct zone from trusted
application data; it cannot be recovered from the timestamp alone.

Do not change `USE_TZ` and the model field in the same deployment. Normalize
legacy naive data first, with an explicitly chosen timezone and a policy for
ambiguous or skipped local times.

## 2. Deploy a compatibility release

Temporarily allow legacy stdlib writers:

```python
from whenever_django.fields import InstantField


class Event(models.Model):
    created_at = InstantField(from_stdlib=True)
```

`from_stdlib=True` affects writes. Values loaded after this deployment are
`whenever.Instant`, so update read-side code in the same release. Use the same
staged approach for a deliberately naive `PlainDateTimeField`.

`InstantField` does not implement `auto_now` or `auto_now_add`. Replace a
creation timestamp with a callable whenever default:

```python
import whenever

created_at = InstantField(
    default=whenever.Instant.now,
    from_stdlib=True,
)
```

For modification timestamps, assign `whenever.Instant.now()` explicitly in
the save or update path. `QuerySet.update()` does not call `Model.save()`.

## 3. Generate and inspect the migration

```bash
python manage.py makemigrations
python manage.py sqlmigrate your_app 0002
python manage.py migrate
```

An aware `DateTimeField` to `InstantField` conversion, and a naive
`DateTimeField` to `PlainDateTimeField` conversion, normally retain compatible
timestamp storage on PostgreSQL and SQLite. Constraints, indexes, defaults,
and backend details can still cause an alteration or table rebuild, so inspect
the SQL.

Composite fields need a staged add/backfill/switch/remove migration. A direct
`AlterField` cannot create the missing zone or offset metadata.

## 4. Move application boundaries to whenever

Update writers, fixtures, tests, tasks, forms, and serializers:

```python
import whenever

event = Event.objects.create(created_at=whenever.Instant.now())
event.refresh_from_db()
assert isinstance(event.created_at, whenever.Instant)
```

At a remaining stdlib boundary, convert an aware value explicitly with
`whenever.Instant(value)`. Validate representative data after deployment,
especially values around DST transitions and application min/max dates.

## 5. Restore strict typing

After every writer sends whenever values, remove `from_stdlib=True`:

```python
class Event(models.Model):
    created_at = InstantField()
```

Generate and inspect the final migration. The option changes Python write
behavior, not the column type. Unexpected stdlib writes will now fail
immediately.
