# whenever-django

`whenever-django` brings the type-safe temporal classes from
[`whenever`](https://whenever.readthedocs.io/) to Django models, forms,
admin, Django REST Framework, and ORM queries.

Use a field that matches the meaning of a value: an exact instant, a local
wall-clock time, a date, a time, a duration, or an instant whose IANA timezone
must survive a database round trip.

```{toctree}
:maxdepth: 2
:caption: Guide

installation
quickstart
fields
queries
migrations
cookbook
comparison
limitations
api_reference
```

## At a glance

- Strict whenever types on model writes by default.
- Eleven model fields with corresponding Django form fields.
- Optional DRF serializer fields and automatic `ModelSerializer` mapping.
- PostgreSQL and SQLite support.
- Exact IANA timezone preservation for composite zoned values.
- ORM lookups, transforms, and typed database expressions.

The project is alpha software. Review the [limitations](limitations.md) and
rehearse migrations against the same backend used in production.
