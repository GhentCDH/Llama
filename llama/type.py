import msgspec
from typing import Optional

class ObjectTypeDefinition(msgspec.Struct):
    id: int
    is_classification: int = msgspec.field(name="class") # fix for invalid property "class"
    label: str = msgspec.field(name="name")
    color: str
    use_object_name: bool
    object_name_in_overview: bool
    system_name: Optional[str] = None
    
def _object_field_description_rename(name: str) -> Optional[str]:
    return "object_description_"+name if name not in ['label', 'label_prefix'] else None

class ObjectFieldDefinition(msgspec.Struct, rename=_object_field_description_rename):
    id: int
    label: str = msgspec.field(name="object_description_name")
    value_type_base: str
    value_type_settings: list|dict
    is_required: bool
    is_unique: bool
    is_identifier: bool
    has_multi: bool
    ref_type_id: bool|int
    in_name: bool
    in_search: bool
    in_overview: bool
    clearance_view: int
    clearance_edit: int
    system_name: Optional[str] = None
    
ObjectFieldDefinitions = dict[str, ObjectFieldDefinition]|list
    
class ObjectType(msgspec.Struct):
    metadata: ObjectTypeDefinition = msgspec.field(name="type")
    fields: ObjectFieldDefinitions = msgspec.field(name="object_descriptions")
    sub_objects: Optional[list] = msgspec.field(name="object_sub_details")
    
    def __post_init__(self):
        self.fields = {} if isinstance(self.fields, list) else self.fields    
    
Model = dict[str, ObjectType]

def _object_metadata_rename(name: str) -> Optional[str]:
    return "object_"+name if name not in ['nodegoat_id', 'type_id'] else None

class ObjectMetadata(msgspec.Struct, rename=_object_metadata_rename):
    nodegoat_id: str
    type_id: int = msgspec.field(name="type_id")
    id: int
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
    ref_object_id: list[int]|int|None
    value: list|int|str
    sources: list
    style: list
    system_name: Optional[str] = None    
    
ObjectFields = dict[str, ObjectField]|list

class Object(msgspec.Struct):
    metadata: ObjectMetadata = msgspec.field(name="object")
    fields: ObjectFields = msgspec.field(name="object_definitions")
    sub_objects: Optional[list] = msgspec.field(name="object_subs")
    
    def __post_init__(self):
        self.fields = {} if isinstance(self.fields, list) else self.fields
    
Objects = dict[str, Object]

# Responses

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

class MapperDefaults(msgspec.Struct):
    traverse_type: bool = None
    traverse_classification: bool = None
    traverse_media: bool = None
    
class FieldMapper(msgspec.Struct):
    traverse: bool = None
    system_name: str = None

class TypeMapper(msgspec.Struct):
    defaults: MapperDefaults = msgspec.field(default_factory=lambda: MapperDefaults())
    fields: dict[int, FieldMapper] = {}
    exclude_fields: set = msgspec.field(default_factory=set)
    include_fields: set = msgspec.field(default_factory=set)

class ObjectMapper(msgspec.Struct):
    defaults: MapperDefaults = msgspec.field(default_factory=lambda: MapperDefaults())
    types: dict[int, TypeMapper] = {}
