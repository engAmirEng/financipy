import zoneinfo

from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _


def validate_zoneinfo(value: str):
    try:
        zoneinfo.ZoneInfo(value)
    except zoneinfo.ZoneInfoNotFoundError:
        raise ValidationError(_('no time zone matches "{entered_value}"').format(entered_value=value))
