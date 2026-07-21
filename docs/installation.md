(installation)=
# Installation

Install the core integration from PyPI:

```bash
pip install whenever-django
```

Install the optional Django REST Framework integration with:

```bash
pip install "whenever-django[drf]"
```

Add the application to Django settings. Its `AppConfig` registers the query
transforms and, when DRF is installed, the serializer mappings.

```python
INSTALLED_APPS = [
    # ...
    "whenever_django",
]
```

## Requirements

- Python 3.10 or newer
- Django 4.2 or newer
- whenever 0.10.0 or newer
- PostgreSQL or SQLite

MySQL and MariaDB are not supported yet. See [backend support](limitations.md)
before selecting fields that need composite storage or database arithmetic.
