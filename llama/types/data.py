import msgspec
from typing import Optional, Any

# SubObjectData
def _sub_object_field_definition_rename(name: str) -> Optional[str]:
    return "object_sub_definition_"+name    

class SubObjectField(msgspec.Struct, rename=_sub_object_field_definition_rename):
    description_id: int = msgspec.field(name="object_sub_description_id")
    ref_object_id: list[int]|dict|int|None
    value: list|int|str
    sources: list|dict # todo: type this!
    style: list|dict # todo: type this!
    system_name: Optional[str] = None    

SubObjectFields = dict[str, SubObjectField]|list

def _sub_object_metadata_rename(name: str) -> Optional[str]:
    return "object_sub_" + name

# todo: check geometry/location data
class SubObjectMetadata(msgspec.Struct, rename=_sub_object_metadata_rename):
    id: int
    type_id: int = msgspec.field(name="object_sub_details_id")
    date_start: Any|None
    date_end: Any|None
    date_chronology: Any|None
    location_geometry: Any|None
    location_geometry_ref_object_id: Any|None
    location_geometry_ref_type_id: Any|None
    location_ref_object_id: Any|None
    location_ref_type_id: Any|None
    location_ref_object_sub_details_id: Any|None
    location_ref_object_name: Any|None
    location_type: Any|None
    style: list
    sources: list
    version: str

class SubObject(msgspec.Struct):
    metadata: SubObjectMetadata = msgspec.field(name="object_sub")
    fields: SubObjectFields = msgspec.field(name="object_sub_definitions")
    
    def __post_init__(self):
        self.fields = {} if isinstance(self.fields, list) else self.fields
    
SubObjects = dict[str, SubObject]

# ObjectData
def _object_metadata_rename(name: str) -> Optional[str]:
    return "object_"+name if name not in ['nodegoat_id', 'type_id'] else None

class ObjectMetadata(msgspec.Struct, rename=_object_metadata_rename):
    id: int
    nodegoat_id: str
    type_id: int = msgspec.field(name="type_id")
    name: str
    name_plain: str|None
    name_style: list
    style: list
    sources: list
    version: str
    dating: str
    
def _object_field_definition_rename(name: str) -> Optional[str]:
    return "object_definition_"+name    

class ObjectField(msgspec.Struct, rename=_object_field_definition_rename):
    description_id: int = msgspec.field(name="object_description_id")
    ref_object_id: list[int]|dict|int|None
    value: list|int|str
    sources: list|dict # todo: type this!
    style: list|dict # todo: type this!
    system_name: Optional[str] = None    
    
ObjectFields = dict[str, ObjectField]|list

class Object(msgspec.Struct):
    metadata: ObjectMetadata = msgspec.field(name="object")
    fields: ObjectFields = msgspec.field(name="object_definitions")
    sub_objects: SubObjects|list = msgspec.field(name="object_subs")
    
    def __post_init__(self):
        self.fields = {} if isinstance(self.fields, list) else self.fields
        self.sub_objects = {} if isinstance(self.sub_objects, list) else self.sub_objects
    
Objects = dict[str, Object]
