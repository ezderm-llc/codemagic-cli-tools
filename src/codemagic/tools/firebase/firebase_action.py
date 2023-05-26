import logging
from abc import ABCMeta
from abc import abstractmethod
from typing import List

from codemagic.firebase.api_client import FirebaseApiClient
from codemagic.firebase.resource_managers.resource_manager import ResourceManager
from codemagic.firebase.resources import Release


class FirebaseAction(metaclass=ABCMeta):
    api_client: FirebaseApiClient
    logger: logging.Logger

    # Define signatures for self-reference to other action groups

    @property
    @abstractmethod
    def project_id(self):
        ...

    @classmethod
    def echo(cls, message: str, *args, **kwargs) -> None:
        ...

    # Action signatures in alphabetical order

    @abstractmethod
    def get_latest_build_version(self, app_id: str) -> int:
        from .actions import GetLatestBuildVersionAction
        _ = GetLatestBuildVersionAction.get_latest_build_version  # Implementation
        raise NotImplementedError()

    @abstractmethod
    def list_releases(
        self,
        app_id: str,
        limit: int = 25,
        order_by: ResourceManager.OrderBy = ResourceManager.OrderBy.create_time_desc,
        json_output: bool = False,
        should_print: bool = True,
    ) -> List[Release]:
        from .action_groups.releases_action_group import ReleasesActionGroup
        _ = ReleasesActionGroup.list_releases  # Implementation
        raise NotImplementedError()
