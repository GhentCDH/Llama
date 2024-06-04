import msgspec

class MapperDefaults(msgspec.Struct):
    traverse_type: bool = None
    traverse_classification: bool = None
    traverse_media: bool = None
    
    def to_dict(self):
        return {f: getattr(self, f) for f in self.__struct_fields__}
    
class FieldMapper(msgspec.Struct):
    traverse: bool = None
    system_name: str = None

class ObjectMapper(msgspec.Struct):
    defaults: MapperDefaults = msgspec.field(default_factory=lambda: MapperDefaults())
    system_name: str = None
    fields: dict[int, FieldMapper] = {}
    exclude_fields: set = msgspec.field(default_factory=set)
    include_fields: set = msgspec.field(default_factory=set)

class ModelMapper(msgspec.Struct):
    defaults: MapperDefaults = msgspec.field(default_factory=lambda: MapperDefaults())
    types: dict[int, ObjectMapper] = {}
