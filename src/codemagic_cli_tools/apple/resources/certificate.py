from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field
from datetime import datetime
from typing import Optional

from .bundle_id import BundleIdPlatform
from .enums import CertificateType
from .resource import Resource


class Certificate(Resource):
    """
    https://developer.apple.com/documentation/appstoreconnectapi/certificate
    """

    @dataclass
    class Attributes(Resource.Attributes):
        displayName: str
        expirationDate: datetime
        name: str
        platform: BundleIdPlatform
        serialNumber: str
        certificateType: CertificateType
        certificateContent: str = field(metadata={'hide': True})
        csrContent: Optional[str] = field(metadata={'hide': True})

        def __post_init__(self):
            if isinstance(self.expirationDate, str):
                self.expirationDate = Resource.from_iso_8601(self.expirationDate)
            if isinstance(self.platform, str):
                self.platform = BundleIdPlatform(self.platform)
            if isinstance(self.certificateType, str):
                self.certificateType = CertificateType(self.certificateType)

    def get_display_info(self) -> str:
        attributes = self.attributes
        return f'{attributes.certificateType} certificate {attributes.serialNumber} {attributes.displayName}'
