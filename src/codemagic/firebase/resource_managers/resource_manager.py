from __future__ import annotations

import traceback
from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING
from typing import Generic
from typing import List
from typing import Optional
from typing import Type

from googleapiclient.errors import Error as GoogleApiClientError
from httplib2.error import HttpLib2Error
from oauth2client.client import Error as OAuth2ClientError

from codemagic.utilities import log

from ..api_error import FirebaseApiClientError
from ..resources.identifiers import ResourceIdentifierT
from ..resources.resource import ResourceT

if TYPE_CHECKING:
    from googleapiclient._apis.firebaseappdistribution.v1.resources import FirebaseAppDistributionResource
    from googleapiclient.http import HttpRequest


class ResourceManager(Generic[ResourceT], ABC):
    class OrderBy(Enum):
        create_time_desc = 'createTimeDesc'
        create_time_asc = 'createTime'

    def __init__(self, firebase_app_distribution: FirebaseAppDistributionResource):
        self._firebase_app_distribution = firebase_app_distribution

    @property
    @abstractmethod
    def resource_type(self) -> Type[ResourceT]:
        ...


class ListableResourceManagerMixin(Generic[ResourceT, ResourceIdentifierT], ABC):
    resource_type: Type[ResourceT]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._logger = log.get_logger(self.__class__)

    @dataclass
    class PageRequestArguments:
        order_by: ResourceManager.OrderBy
        page_size: int
        page_token: Optional[str]
        parent_uri: str

        def as_request_kwargs(self):
            return {
                'orderBy': self.order_by.value,
                'pageSize': self.page_size,
                'pageToken': self.page_token,
                'parent': self.parent_uri,
            }

    @abstractmethod
    def _get_resources_page_request(self, arguments: PageRequestArguments) -> HttpRequest:
        raise NotImplementedError()

    def list(
        self,
        parent_identifier: ResourceIdentifierT,
        order_by: ResourceManager.OrderBy = ResourceManager.OrderBy.create_time_desc,
        limit: Optional[int] = None,
        page_size: int = 25,
    ) -> List[ResourceT]:
        page_request_args = self.PageRequestArguments(
            order_by=order_by,
            page_size=min(limit, page_size) if limit else page_size,
            page_token=None,
            parent_uri=parent_identifier.uri,
        )

        resources = []
        while True:
            request = self._get_resources_page_request(page_request_args)
            try:
                response = request.execute()
            except (HttpLib2Error, OAuth2ClientError, GoogleApiClientError) as e:
                message = f'Failed to list Firebase {self.resource_type.get_label()}: {e}'
                traceback_str = traceback.format_exc()
                self._logger.debug(f'{message}\n{traceback_str}')
                raise FirebaseApiClientError(message) from e

            page_resources = [self.resource_type(**item) for item in response[self.resource_type.get_label()]]
            resources.extend(page_resources)
            page_request_args.page_token = response.get('nextPageToken')

            if limit and len(resources) > limit:
                break
            if not page_request_args.page_token:
                break
        return resources[:limit]
