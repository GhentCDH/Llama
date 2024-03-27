import locale
from .api import NodegoatAPI
from .type import *
from slugify import slugify


class ObjectFormatter():
        
    def __init__(self, api: NodegoatAPI, mapper: dict = {}, project_id: int = None) -> None:
        self._api = api
        self._mapper = mapper
        
    def format(self, object: Object):       
        # load model
        type = self._api.get_object_type(object.metadata.type_id)
        res = {
            "id": object.metadata.id,
        }
        
        type_mapper = self._mapper.types.get(object.metadata.type_id, TypeMapper())
        
        # classifications fields can be empty
        # use name 
        if len(object.fields.values()) == 0:
            res["label"] = object.metadata.name_plain
            return res
            
        for field in object.fields.values():
            field_definition = type.fields[str(field.description_id)]
            field_mapper = type_mapper.fields.get(field.description_id, FieldMapper())
            field_name = field.system_name = self._field_system_name(field_mapper, field_definition.label)
            field_traverse_config = "traverse_" + field_definition.value_type_base
            
            if len(type_mapper.include_fields) and field_name not in type_mapper.include_fields:
                continue
            elif len(type_mapper.exclude_fields) and field_name in type_mapper.exclude_fields:
                continue
            
            # print(field_definition.label, field_name, field, field_traverse_config)
            
            # empty value?
            if field.value is None:
                res[field_name] = None
                continue
                        
            # process value
            field_values = self._to_list(field.value)

            match field_definition.value_type_base:
                case "classification" | "type":
                    refs = self._to_list(field.ref_object_id)
                    if refs:
                        field_traverse_config = "traverse_" + field_definition.value_type_base
                        traverse = self._first_true([
                                field_mapper.traverse,
                                getattr(type_mapper.defaults, field_traverse_config), 
                                getattr(self._mapper.defaults, field_traverse_config)
                            ],
                            False,
                            lambda x: x is not None
                        )
                        if traverse:
                            ref_objects = self._api.get_object(type_id=field_definition.ref_type_id, object_id=refs)
                            field_values = [self.format(ref_object) for ref_object in ref_objects]
                case "media":
                        field_traverse_config = "traverse_" + field_definition.value_type_base
                        traverse = self._first_true([
                                field_mapper.traverse,
                                getattr(type_mapper.defaults, field_traverse_config), 
                                getattr(self._mapper.defaults, field_traverse_config)
                            ],
                            False,
                            lambda x: x is not None
                        )
                        if traverse:
                            field_values = [self._api.get_media(media_id) for media_id in field_values]                                
                case _:
                    # cast values
                    field_values = list(map(lambda x: self._cast_value(x, field_definition, field_mapper), field_values))
                
            # multiple values allowed?            
            res[field_name] = field_values if field_definition.has_multi else field_values[0]
            
        return res
                                         
    def _field_system_name(self, field_mapper: FieldMapper, field_label: str):
        return field_mapper.system_name or \
            slugify(field_label, separator="_", regex_pattern=r'[^a-z0-9_]+')
           
    def _cast_value(self, value: any, field_definition: ObjectFieldDefinition, field_mapper: FieldMapper) -> any:
        match field_definition.value_type_base:
            case "int":
                return locale.atoi(str(value))
            case "numeric":
                return locale.atoi(str(value)) / (10**10)
            case "boolean":
                return bool(int(value))
            case "media":
                return value
            case _:
                return value
    
    def _to_list(self, value: any) -> list[any]|None:
        if value is None:
            return []
        return value if isinstance(value, list) else [ value ]
    
    def _first_true(self, iterable, default=False, pred=None):
        return next(filter(pred, iterable), default)
