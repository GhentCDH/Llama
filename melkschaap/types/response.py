import msgspec
from typing import Optional

from .model import Model
from .data import Objects


class ModelData(msgspec.Struct):
    models: Optional[Model] = msgspec.field(name="types")

class ObjectData(msgspec.Struct):
    objects: Optional[Objects]

class Response(msgspec.Struct):
    info: str
    timestamp: str
    authenticated: Optional[bool] = None
    error: Optional[str] = None
    error_message: Optional[str] = None

class ObjectResponse(Response):
    data: Optional[ObjectData] = {}

class ModelResponse(Response):
    data: Optional[ModelData] = {}