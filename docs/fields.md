(fields)=
# Fields

## Model fields

### Core temporal fields

| Field | Python value | Database storage | Meaning |
|---|---|---|---|
| `InstantField` | `whenever.Instant` | timestamp | A unique moment, stored in UTC |
| `PlainDateTimeField` | `whenever.PlainDateTime` | naive timestamp | A wall-clock date and time without a zone |
| `WheneverDateField` | `whenever.Date` | date | A calendar date |
| `WheneverTimeField` | `whenever.Time` | time | A wall-clock time |

### Composite timestamp fields

| Field | Python value | Columns | Preserved metadata |
|---|---|---|---|
| `ZonedDateTimeField` | `whenever.ZonedDateTime` | timestamp + `<name>_tz` | IANA timezone name |
| `OffsetDateTimeField` | `whenever.OffsetDateTime` | timestamp + `<name>_offset` | Fixed UTC offset |

The declared field stores the UTC timestamp. An automatically managed string
column stores the zone name or offset. The model descriptor combines both
columns when the attribute is read.

Composite fields work with `.only()`, `.defer()`, `.values()`, and
`bulk_create()`, but schema renames need special care. See
[limitations](limitations.md#composite-field-schema-changes).

### Extended calendar fields

| Field | Python value | Database storage |
|---|---|---|
| `YearMonthField` | `whenever.YearMonth` | packed integer `YYYYMM` |
| `MonthDayField` | `whenever.MonthDay` | packed integer `MMDD` |

### Duration fields

| Field | Python value | Database storage | Use case |
|---|---|---|---|
| `TimeDeltaField` | `whenever.TimeDelta` | integer microseconds | Fixed elapsed time |
| `ItemizedDeltaField` | `whenever.ItemizedDelta` | JSON text | Calendar and clock components |
| `ItemizedDateDeltaField` | `whenever.ItemizedDateDelta` | JSON text | Calendar-date components |

`TimeDeltaField` uses the same integer-microsecond representation Django uses
for `DurationField` on SQLite and other non-native-interval backends. Query
results from PostgreSQL intervals are converted from `datetime.timedelta`.
Nanoseconds are truncated to microseconds when stored.

## Strict writes and `from_stdlib`

Model fields accept their matching whenever type and `None` when nullable.
Passing a standard-library value raises `TypeError` unless the field supports
and enables `from_stdlib=True`.

The compatibility option is available for fields with a direct standard
library equivalent:

- `InstantField`, `PlainDateTimeField`, `WheneverDateField`, and
  `WheneverTimeField`
- `TimeDeltaField`

Composite, extended-calendar, and itemized-delta fields have no lossless
single-value standard-library equivalent and reject `from_stdlib=True`.

## Django form fields

Every model field selects its corresponding form field through `formfield()`.
They parse ISO 8601 strings and return whenever values.

| Model field | Form field |
|---|---|
| `InstantField` | `InstantFormField` |
| `PlainDateTimeField` | `PlainDateTimeFormField` |
| `ZonedDateTimeField` | `ZonedDateTimeFormField` |
| `OffsetDateTimeField` | `OffsetDateTimeFormField` |
| `WheneverDateField` | `WheneverDateFormField` |
| `WheneverTimeField` | `WheneverTimeFormField` |
| `YearMonthField` | `YearMonthFormField` |
| `MonthDayField` | `MonthDayFormField` |
| `TimeDeltaField` | `TimeDeltaFormField` |
| `ItemizedDeltaField` | `ItemizedDeltaFormField` |
| `ItemizedDateDeltaField` | `ItemizedDateDeltaFormField` |

```python
from django import forms
from whenever_django.forms import InstantFormField, WheneverDateFormField


class ScheduleForm(forms.Form):
    opens_at = InstantFormField()
    business_date = WheneverDateFormField()
```

## Optional DRF serializer fields

Install the `drf` extra to enable serializer fields. When
`whenever_django` is in `INSTALLED_APPS`, `ModelSerializer` automatically maps
all eleven model fields.

| Model field | Serializer field |
|---|---|
| `InstantField` | `InstantSerializerField` |
| `PlainDateTimeField` | `PlainDateTimeSerializerField` |
| `ZonedDateTimeField` | `ZonedDateTimeSerializerField` |
| `OffsetDateTimeField` | `OffsetDateTimeSerializerField` |
| `WheneverDateField` | `WheneverDateSerializerField` |
| `WheneverTimeField` | `WheneverTimeSerializerField` |
| `YearMonthField` | `YearMonthSerializerField` |
| `MonthDayField` | `MonthDaySerializerField` |
| `TimeDeltaField` | `TimeDeltaSerializerField` |
| `ItemizedDeltaField` | `ItemizedDeltaSerializerField` |
| `ItemizedDateDeltaField` | `ItemizedDateDeltaSerializerField` |

```python
from rest_framework import serializers


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = "__all__"
```

Serialization uses each whenever object's ISO representation. Zoned datetimes
include the IANA name using RFC 9557 syntax, such as
`2026-04-06T10:00:00-04:00[America/New_York]`.
