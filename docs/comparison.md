(comparison)=
# Comparison with complementary Django tools

Last verified: **2026-07-21**.

These projects solve different layers of temporal modeling and can be used
together. This matrix is a selection guide, not a winner ranking.

| Capability | whenever-django | Django built-ins | django-timezone-field | django-model-utils 5.0 |
|---|---|---|---|---|
| Primary focus | Typed temporal model/form/serializer values | General-purpose date, time, datetime, and duration fields | Store and validate a timezone identifier | Reusable model mixins and managers |
| Temporal type coverage | 11 whenever-backed fields: instants, local/zoned/offset datetimes, date/time, extended dates, and fixed/itemized deltas | Stdlib `date`, `time`, `datetime`, and `timedelta` through separate fields | `zoneinfo.ZoneInfo` timezone values, not timestamps | Uses Django `DateTimeField`; adds no replacement temporal value types |
| IANA-zone preservation | Yes, paired with each `ZonedDateTimeField` value | `DateTimeField` does not pair the original zone name with the timestamp | Yes, as a dedicated zone field; combine it with a separate timestamp when needed | No additional zone storage beyond the fields chosen by the application |
| Durations | Fixed `TimeDelta` plus itemized calendar/clock deltas | `DurationField` stores `timedelta` (`interval` on PostgreSQL, microseconds on most other backends) | No | No new duration type |
| Forms / DRF | Django form fields for all types; optional DRF fields and automatic mappings | Model fields provide form/admin integration; DRF belongs to the separate DRF project | Dedicated model, form, and DRF serializer fields | Inherits normal Django behavior from the concrete fields used by each mixin |
| ORM behavior | Standard lookups, date/time transforms, and typed projection/subtraction expressions | Django's native lookup, expression, and database-function ecosystem | Normal field storage/querying for zone identifiers | `TimeFramedModel` adds a prefiltered time-window manager |
| Timestamp / time-window conveniences | `WheneverNow`; explicit whenever defaults; no timestamp mixin | `auto_now`, `auto_now_add`, callable defaults, and `Now` | None; it models the zone identifier | `TimeStampedModel` adds `created`/`modified`; `TimeFramedModel` adds `start`/`end` and a manager |

## How to combine them

- Use **whenever-django alone** when the model should expose strict whenever
  values and a zoned timestamp should preserve its own IANA name.
- Add **django-timezone-field** when a user, organization, or schedule has a
  reusable preferred timezone independent of any one timestamp.
- Add **django-model-utils** when its lifecycle or time-window mixins match the
  model design; verify that their built-in `DateTimeField` attributes have the
  types your application expects.
- Keep **Django built-ins** for models and integrations that intentionally use
  standard-library values or require broader backend behavior.

## Sources

The matrix is based on the official documentation available on the verification
date:

- [Django 5.2 `DateTimeField` and `DurationField` documentation](https://docs.djangoproject.com/en/5.2/ref/models/fields/#datetimefield)
- [django-timezone-field documentation](https://pypi.org/project/django-timezone-field/)
- [django-model-utils 5.0 model documentation](https://django-model-utils.readthedocs.io/en/5.0.0/models.html)
