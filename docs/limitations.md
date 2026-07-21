(limitations)=
# Limitations and backend support

## Backend support

| Feature | PostgreSQL | SQLite | Notes |
|---|---|---|---|
| All 11 model fields | Yes | Yes | Microsecond database precision |
| Standard comparison/range/in/null lookups | Yes | Yes | Uses field preparation and native columns |
| `date` / `time` transforms | Yes | Yes | Backend/session timezone rules apply |
| `WheneverNow()` | Yes | Yes | Returns `whenever.Instant` |
| `ToInstant()` | Yes | Yes | Identity timestamp SQL; Python result conversion |
| `ToZoned()` | Yes | Yes | Fixed validated IANA zone; Python result conversion |
| `DurationBetween()` | Yes | Yes | Native interval vs. integer-microsecond result |
| Automatic `F()` temporal arithmetic | Not guaranteed | Not guaranteed | Use `DurationBetween` for timestamp subtraction |
| `__in_tz` lookup/transform | No | No | Not implemented |
| Itemized-delta SQL arithmetic | No | No | JSON storage preserves components |
| MySQL / MariaDB | No | No | Outside the current backend scope |

No library-owned SQLite function is registered for the query expressions.
`ToInstant` and `ToZoned` leave the timestamp untouched in SQL, and
`DurationBetween` uses Django's backend function. There is consequently no
custom SQLite UDF cache to configure or warm.

## Precision

Database timestamp and fixed-duration storage is microsecond precision.
Nanoseconds are truncated when values cross a stdlib/database boundary.

## Composite field schema changes

`RenameField` on `ZonedDateTimeField` or `OffsetDateTimeField` does not
automatically rename its paired `_tz` or `_offset` column. Add an explicit
operation for the paired column and inspect the migration SQL.

Changing between a composite and non-composite field requires a data migration.
The database cannot infer a missing IANA name or fixed offset from a timestamp.

## Composite querying

The declared composite field column contains the exact UTC timestamp. Standard
lookups on that field compare instants. The paired metadata column is a separate
model field. Use `ToInstant` for typed instant annotations and `ToZoned` for a
fixed-zone result projection.

## Itemized deltas

`ItemizedDeltaField` and `ItemizedDateDeltaField` use JSON text so calendar
components survive round trips. They cannot participate in native database
arithmetic. Perform itemized arithmetic after loading values.

## Conversion throughput

Django's supported field converter API operates one value at a time. Bulk
`from_db_value` optimization is deferred until Django exposes a contained batch
hook or benchmarks justify query-compiler customization.

## Supported timezone projection

`ToZoned` accepts one IANA timezone string at expression construction. It is a
Python-result projection and does not transform a timestamp into local wall
time in SQL. Per-row timezone expressions and an `__in_tz` transform remain
future work.
