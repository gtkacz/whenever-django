# Contributing

Contributions are welcome! Please read these guidelines before submitting a pull request.

## Before You Start

- **Non-trivial changes** should be discussed in an [issue](https://github.com/python-whenever/whenever-django/issues) first to avoid wasted effort.
- **Comment on an issue** before picking it up, so others know it's being worked on.

## Setting Up a Development Environment

```bash
# Clone the repository
git clone https://github.com/python-whenever/whenever-django.git
cd whenever-django

# Create a virtual environment and install dev dependencies
uv venv
source .venv/bin/activate
uv pip install -e ".[dev,docs,drf]"
```

## Running Tests

```bash
# Run the full test suite
uv run pytest

# Run with coverage
uv run pytest --cov=whenever_django --cov-report=term-missing

# Run a specific test file
uv run pytest tests/test_instant_field.py -v
```

Tests use SQLite by default. For PostgreSQL testing, set `DATABASE_URL` before running:

```bash
DATABASE_URL=postgres://user:pass@localhost/whenever_test uv run pytest
```

## Code Style

This project uses:

- **Ruff** for linting and formatting
- **mypy** in strict mode for type checking

```bash
# Format
uv run ruff format src/ tests/

# Lint
uv run ruff check src/ tests/

# Type check
uv run mypy src/
```

All public functions and classes must have type annotations.

## Building Documentation

The documentation uses Sphinx, MyST Markdown, and Furo. Build it locally with
warnings treated as errors:

```bash
make docs
```

The equivalent direct command is:

```bash
uv run sphinx-build -W --keep-going -b html docs docs/_build/html
```

Open `docs/_build/html/index.html` after a successful build. Add durable user
guidance to the Sphinx site and keep the README focused on installation and a
short quick start. Internal plans, brainstorms, and ideation notes must not be
added to the published toctree.

## Project Structure

```
src/whenever_django/
├── __init__.py              # Public API exports, version
├── apps.py                  # AppConfig (registers lookups, DRF mappings)
├── _compat.py               # Optional dependency detection (DRF)
├── fields/
│   ├── _base.py             # WheneverField base class
│   ├── instant.py           # InstantField
│   ├── plain_datetime.py    # PlainDateTimeField
│   ├── date.py              # WheneverDateField
│   ├── time.py              # WheneverTimeField
│   ├── zoned_datetime.py    # ZonedDateTimeField (composite)
│   ├── offset_datetime.py   # OffsetDateTimeField (composite)
│   ├── year_month.py        # YearMonthField
│   ├── month_day.py         # MonthDayField
│   ├── time_delta.py        # TimeDeltaField
│   ├── itemized_delta.py    # ItemizedDeltaField
│   └── itemized_date_delta.py
├── forms/
│   ├── fields.py            # Form field classes
│   └── widgets.py           # Widget classes
├── admin/                   # Admin filters and display helpers
├── contrib/
│   └── drf/
│       └── fields.py        # DRF serializer fields (optional)
├── lookups.py               # ORM lookups and transforms
├── functions.py             # Database functions (WheneverNow, etc.)
├── descriptors.py           # Descriptors for composite fields
└── management/
    └── commands/
        └── whenever_audit.py
```

## Architecture Decisions

Understanding these decisions will help you write consistent contributions:

### Strict by Default

Fields reject stdlib types unless `from_stdlib=True` is set. This mirrors whenever's own philosophy. Do not weaken this behavior.

### Composite Fields

`ZonedDateTimeField` and `OffsetDateTimeField` use auto-managed paired columns (datetime + metadata) via `contribute_to_class()` and a custom `CompositeFieldDescriptor`. This preserves database-native query capabilities that a single TEXT column would lose.

### DRF as Optional Extra

DRF is detected at runtime via `_compat.py`. All DRF imports are lazy. Serializer fields are registered in `AppConfig.ready()` only when DRF is installed. Do not add a hard import of `rest_framework` anywhere outside `contrib/drf/`.

### Delta Storage

`TimeDeltaField` stores microseconds as `BIGINT` (compatible with Django's `DurationField`). `ItemizedDeltaField` and `ItemizedDateDeltaField` use JSON to preserve full component fidelity that PostgreSQL `INTERVAL` would lose.

### Backend Support

PostgreSQL and SQLite only. Where SQLite lacks native support (e.g., `AT TIME ZONE`), provide a Python-level fallback or raise a clear error. Do not add MySQL support without a dedicated discussion.

## Adding a New Field

If whenever adds a new type and you want to add a corresponding Django field:

1. Create `src/whenever_django/fields/your_type.py` subclassing `WheneverField`
2. Implement `_from_db()`, `_to_db()`, `_parse()`, `get_internal_type()`, and `formfield()`
3. Add the field to `fields/__init__.py`
4. Add a form field in `forms/fields.py`
5. Add a DRF serializer field in `contrib/drf/fields.py` with field mapping registration
6. Write tests covering: None handling, round-trip, type rejection, `from_stdlib` (if applicable), `deconstruct()` stability

## Writing Tests

- Every field needs tests for: `None` handling, DB round-trip, type rejection, `from_stdlib` coercion, `deconstruct()` stability, and form field validation.
- Use `pytest-django` with in-memory SQLite for fast iteration.
- Composite fields additionally need tests for: `.only()`, `.defer()`, `.values()`, `bulk_create()`, and `deconstruct()` idempotency (no spurious migration generation).

## Pull Request Checklist

- [ ] Tests pass (`uv run pytest`)
- [ ] Types check (`uv run mypy src/`)
- [ ] Code is formatted (`uv run ruff format --check src/ tests/`)
- [ ] Lint passes (`uv run ruff check src/ tests/`)
- [ ] `deconstruct()` is stable (no spurious migrations)
- [ ] New public API has type annotations
- [ ] Commit messages follow [Conventional Commits](https://www.conventionalcommits.org/) (`feat:`, `fix:`, `docs:`, etc.)

## Reporting Issues

When reporting a bug, include:

- Python, Django, and whenever versions
- Database backend (PostgreSQL version or SQLite)
- Minimal reproduction case
- Full traceback
