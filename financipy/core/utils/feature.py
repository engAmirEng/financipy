from typing import TYPE_CHECKING

from django.utils.translation import gettext as _

if TYPE_CHECKING:
    from ..models import BaseFeatureModel


def make_feature_status_text(text: str, feature_type: type["BaseFeatureModel"], feature: "BaseFeatureModel") -> str:
    if feature.status is None or feature.status == feature_type.Status.INACTIVE_BY_CHOICE:
        status_part_symbol = "❌"
        status_part_text = _("inactive")
    elif feature.status == feature_type.Status.ACTIVE:
        status_part_symbol = "✅"
        status_part_text = _("active")
    else:
        raise NotImplementedError
    res = f"{text}   |{status_part_text}-{status_part_symbol}"
    return res
