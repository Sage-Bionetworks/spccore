"""User and Team models"""
from dataclasses import dataclass
from typing import Union, Optional

from spccore.models.base_model import SynapseModel


@dataclass
class Teams(SynapseModel):
    id: Union[str, int]
    name: str
    description: Optional[str] = None
    icon: Optional[str] = None
    canPublicJoin: Optional[bool] = False
    canRequestMembership: Optional[bool] = False

    def _get_url(self):
        """Get endpoint path"""
        return f"/team/{self.id}"

    def _post_url(self):
        """Post endpoint path"""
        return "/team"

    def _put_url(self):
        """Put endpoint path"""
        return "/team"

    def _delete_url(self):
        """Delete endpoint path"""
        return f"/team/{self.id}"
