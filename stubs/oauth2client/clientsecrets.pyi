from typing import Any
from typing import Optional

TYPE_WEB: str
TYPE_INSTALLED: str
VALID_CLIENT: Any

class Error(Exception): ...
class InvalidClientSecretsError(Error): ...

def _validate_clientsecrets(clientsecrets_dict: Any): ...
def load(fp: Any): ...
def loads(s: Any): ...
def _loadfile(filename: Any): ...
def loadfile(filename: Any, cache: Optional[Any] = ...): ...
