"""
Synapse Team services outlined here
https://rest-docs.synapse.org/rest/#org.sagebionetworks.repo.web.controller.TeamController
"""
from typing import Union

from spccore.client import SynapseBaseClient


class TeamsService(SynapseBaseClient):
    """Synapse Team services"""

    def get_teams(self) -> Union[dict, str]:
        """Get teams"""
        return self.rest_get(endpoint_path="/teams")

    def get_team(self, team_id: Union[str, int]) -> Union[dict, str]:
        """Get Synapse Team metadata

        Args:
            team_id (str): Synapse team Id

        Returns:
            dict: Synapse team metadata
        """
        return self.rest_get(endpoint_path=f"/team/{team_id}")
