
import msgspec
from typing import Optional

# Subobject definition
def _sub_object_field_description_rename(name: str) -> Optional[str]:
    return "object_sub_description_"+name if name not in ['label', 'label_prefix'] else None

class SubObjectFieldDescription(msgspec.Struct, rename=_sub_object_field_description_rename):
    id: int
    label: str = msgspec.field(name="object_sub_description_name")
    value_type_base: str
    value_type_settings: list|dict
    is_required: bool
    ref_type_id: bool|int
    use_object_description_id: bool|int # rename? not sure what this is
    in_name: bool
    in_search: bool
    in_overview: bool
    clearance_view: int
    clearance_edit: int
    system_name: Optional[str] = None

SubObjectFieldDescriptions = dict[str, SubObjectFieldDescription]|list

def _sub_object_type_definition_rename(name: str) -> Optional[str]:
    return "object_sub_details_"+name if name not in ['label', 'label_prefix'] else None

class SubObjectTypeDescription(msgspec.Struct, rename=_sub_object_type_definition_rename):
    id: int
    label: str = msgspec.field(name="object_sub_details_name")
    is_single: bool
    is_required: bool
    has_date: bool
    is_date_period: bool
    has_location: bool
    # add missing properties
    clearance_view: int
    clearance_edit: int
    system_name: Optional[str] = None

class SubObjectType(msgspec.Struct):
    type: SubObjectTypeDescription = msgspec.field(name="object_sub_details")
    fields: SubObjectFieldDescriptions = msgspec.field(name="object_sub_descriptions")
    
SubObjectTypes = dict[str, SubObjectType]|list

# Objects definitions

class ObjectTypeDescription(msgspec.Struct):
    id: int
    label: str = msgspec.field(name="name")
    is_classification: int = msgspec.field(name="class") # fix for invalid property "class"
    color: str
    use_object_name: bool
    object_name_in_overview: bool
    system_name: Optional[str] = None
    
def _object_field_description_rename(name: str) -> Optional[str]:
    return "object_description_"+name if name not in ['label', 'label_prefix'] else None

class ObjectFieldDescription(msgspec.Struct, rename=_object_field_description_rename):
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
    
ObjectFieldDescriptions = dict[str, ObjectFieldDescription]|list
    
class ObjectType(msgspec.Struct):
    type: ObjectTypeDescription = msgspec.field(name="type")
    fields: ObjectFieldDescriptions = msgspec.field(name="object_descriptions")
    sub_objects: Optional[SubObjectTypes] = msgspec.field(name="object_sub_details")
    
    def __post_init__(self):
        self.fields = {} if isinstance(self.fields, list) else self.fields
        self.sub_objects = {} if isinstance(self.sub_objects, list) else self.sub_objects
    
Model = dict[str, ObjectType]
