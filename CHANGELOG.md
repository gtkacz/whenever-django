# Changelog

## Unreleased

### Added

- `ToInstant`, `ToZoned`, and `DurationBetween` ORM expressions with typed
  whenever results on PostgreSQL and SQLite
- A Sphinx/MyST/Furo documentation site with guides, cookbook, comparison
  matrix, limitations, and generated API reference
- GitHub Pages publishing and ready-to-connect Read the Docs configuration

### Changed

- `TimeDeltaField` now converts PostgreSQL `datetime.timedelta` query results
- The README is now a concise project landing page linked to the canonical
  documentation
- Retired the SQLite custom-function cache roadmap item because the new query
  expressions register no library-owned SQLite function

## 0.0.1a0 (2026-04-06)

### Added

- Initial package structure
- Package name reserved on PyPI
- GitHub Actions CI and trusted publishing workflows

### Note

This is an alpha release. The package is under development and not ready for production use.
