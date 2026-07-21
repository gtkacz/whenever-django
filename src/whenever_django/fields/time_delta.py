from __future__ import annotations

import datetime as _stdlib
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from django import forms as _django_forms

import whenever as _whenever

from ._base import WheneverField


class TimeDeltaField(WheneverField):
    """Stores a :class:`~whenever.TimeDelta` as microseconds in a BIGINT column.

    Compatible with Django's DurationField storage format.
    Nanosecond precision is silently truncated to microseconds.
    """

    whenever_type = _whenever.TimeDelta
    stdlib_type = _stdlib.timedelta

    def get_internal_type(self) -> str:
        return "BigIntegerField"

    def _from_db(self, value: Any, connection: Any) -> _whenever.TimeDelta:
        if isinstance(value, _stdlib.timedelta):
            return _whenever.TimeDelta(value)
        return _whenever.TimeDelta(microseconds=int(value))

    def _to_db(self, value: _whenever.TimeDelta) -> int:
        return int(value.total("microseconds"))

    def _parse(self, value: str) -> _whenever.TimeDelta:
        return _whenever.TimeDelta.parse_iso(value)

    def formfield(
        self,
        form_class: type[_django_forms.Field] | None = None,
        choices_form_class: type[_django_forms.ChoiceField] | None = None,
        **kwargs: Any,
    ) -> _django_forms.Field | None:
        from ..forms.fields import TimeDeltaFormField

        return super().formfield(
            form_class=form_class or TimeDeltaFormField,
            choices_form_class=choices_form_class,
            **kwargs,
        )
