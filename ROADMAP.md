# Roadmap

This document tracks planned work beyond the initial release. Items are grouped by milestone and roughly ordered by priority within each group. Priorities may shift.

## MySQL / MariaDB Support [Next up]

- [ ] **MySQL 8.0+ backend support** for all 11 field types
  - MySQL's `DATETIME(6)` for microsecond-precision timestamps
  - `TIMESTAMP` with `CONVERT_TZ()` for `__in_tz` transform
  - Integer and TEXT storage for extended/delta fields (same as SQLite)
- [ ] **MariaDB 10.6+ backend support** — same as MySQL where behavior overlaps; test and document divergences (e.g., MariaDB's extended `INTERVAL` syntax)
- [ ] Backend-specific `as_mysql()` methods on all lookups, transforms, and database functions
- [ ] CI matrix expansion: MySQL 8.0, MariaDB 10.6, across Python 3.10–3.14 and Django 4.2–6.0

## Migration Tooling

Improve the `whenever_audit` command from a read-only scanner to a migration assistant.

- [ ] **`--generate` flag**: produce Django migration files that convert stdlib datetime columns to whenever fields, with `RunPython` operations for data conversion
- [ ] **`--assume-tz` flag**: required when converting naive `DateTimeField` to `InstantField` — forces an explicit timezone decision for existing data instead of guessing
- [ ] **Reversible migrations**: generated migrations include reverse operations by default
- [ ] **Dry-run mode**: preview generated migration SQL without writing files

## Admin Enhancements

Initial release ships basic admin support via `formfield()`. This milestone adds dedicated widgets and filters.

- [ ] **`ZonedDateTimeWidget`**: `datetime-local` input paired with an IANA timezone selector `<select>` (populated from `whenever.available_timezones()`)
- [ ] **`OffsetDateTimeWidget`**: `datetime-local` input with UTC offset picker
- [ ] **`YearMonthWidget`**: HTML5 `<input type="month">`
- [ ] **`MonthDayWidget`**: paired month/day `<select>` inputs
- [ ] **`DeltaComponentWidget`**: multi-input widget for `ItemizedDeltaField` / `ItemizedDateDeltaField` (years, months, days, hours, minutes, seconds)
- [ ] **`WheneverDateListFilter`**: temporal range filters for admin list views (today, past 7 days, this month, this year) — registered on `InstantField`, `PlainDateTimeField`, `WheneverDateField`, `ZonedDateTimeField`
- [ ] **`list_display` helpers**: callables that format whenever types in human-readable form for admin list views

## IsoWeekDateField

- [ ] Field for `whenever.IsoWeekDate` — stores ISO week dates (year + week + weekday)
- Deferred because there is no natural SQL column type; likely requires a packed integer or composite storage. Low demand, niche use case.

## Database-Level CHECK Constraints

- [ ] Generate `CHECK` constraints that enforce temporal invariants at the database level (e.g., `end > start`, valid timezone strings, YearMonth range bounds)
- Deferred because Python-level validators cover most cases with lower complexity. PostgreSQL-only initially.

## Configurable Storage Backends

- [ ] Allow per-field storage strategy selection (e.g., PostgreSQL `INTERVAL` vs. `BIGINT` for `TimeDeltaField`, `TEXT` vs. `INTEGER` for `YearMonthField`)
- Deferred because a single good default per backend suffices for most users. Only pursue if real-world feedback surfaces a need.

## Timezone-Aware Model Mixins

- [ ] Opinionated mixins that auto-populate timezone fields based on a user-level or request-level timezone context
- Deferred as too opinionated for a library. `ZonedDateTimeField` covers the storage case; application-level timezone resolution is the user's responsibility.

## Mypy / Pyright Plugin

- [ ] Type checker plugin that narrows ORM queryset return types (e.g., `.values_list('instant', flat=True)` returns `list[Instant]` instead of `list[Any]`)
- Deferred due to complexity and the instability of mypy's plugin API. Revisit when `django-stubs` stabilizes its own plugin architecture.

## Query Enhancements

- [ ] **`ToInstant(expr)`**: database function converting `ZonedDateTimeField` expression to `Instant` (extract timestamp column)
- [ ] **`ToZoned(expr, tz_string)`**: project an `InstantField` expression into a `ZonedDateTime` in a given timezone (`AT TIME ZONE` on PostgreSQL, Python fallback on SQLite)
- [ ] **`DurationBetween(expr1, expr2)`**: subtract two `InstantField` expressions, returning `TimeDelta`
- [ ] **Full F-expression arithmetic**: `F('end') - F('start')` between two `InstantField` columns yields `TimeDelta`; `F('instant') + F('delta')` yields `Instant`. Register `Combinable` resolution on field output types.
- [ ] **`__in_tz` transform on SQLite**: improve the Python-level fallback to handle edge cases (DST transitions, historical timezone changes)

## Composite Field Migration Safety

- [ ] **Auto-rename paired columns**: detect `RenameField` on `ZonedDateTimeField` / `OffsetDateTimeField` and automatically generate a second `RenameField` for the `_tz` / `_offset` column
- [ ] **`AlterField` support**: handle composite field type changes (e.g., `ZonedDateTimeField` → `InstantField`) with data migration

## OpenAPI / drf-spectacular Integration

- [ ] **`@extend_schema_field` decorators** on all DRF serializer fields for first-class drf-spectacular support
- [ ] Correct OpenAPI format hints: `date-time` for `InstantSerializerField`, `date` for `WheneverDateSerializerField`, custom `x-format` for whenever-specific types

## Ecosystem Integrations

- [ ] **django-filter support**: `FilterSet` fields that accept whenever types in query parameters
- [ ] **django-import-export**: import/export handlers for whenever fields in CSV/Excel workflows
- [ ] **Celery task serialization**: JSON serializer hooks so whenever types can be passed as Celery task arguments without manual conversion
- [ ] **GraphQL (graphene-django / strawberry)**: type mappings for whenever fields in GraphQL schemas
- [ ] **Django Ninja support**: schema generation and parameter parsing for whenever types

## Performance

- [ ] **Bulk `from_db_value` optimization**: Django's supported field converter API is value-at-a-time. A batch implementation currently requires invasive query compiler or queryset customization, so this is deferred until Django exposes a contained hook or benchmarks justify that complexity.
- [ ] **Connection-level caching** for SQLite custom functions registered via `create_function()`

## Documentation and Developer Experience

- The initial step-by-step [`DateTimeField` migration guide](README.md#migrating-from-djangos-datetimefield) is available in the README.
- [ ] **Sphinx documentation site** with full API reference, migration guide, and cookbook
- [ ] **Comparison matrix**: feature comparison with `django-timezone-field`, `django-model-utils`, and stdlib `DateTimeField`

## Versioning Policy

This project follows [Semantic Versioning](https://semver.org/). Breaking changes to public API surfaces require a major version bump. Internal modules prefixed with `_` are not part of the public API.
