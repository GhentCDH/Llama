import locale
from .api import NodegoatAPI
from .types.data import Object, ObjectField, SubObject
from .types.model import ObjectFieldDescription, ObjectType, SubObjectType
from .types.data_mapper import FieldMapper, MapperDefaults, ModelMapper, ObjectMapper
from slugify import slugify


class ObjectFormatter():
        
    def __init__(self, api: NodegoatAPI, mapper: ModelMapper = None, project_id: int = None) -> None:
        self._api = api
        self._mapper = mapper if mapper is not None else ModelMapper()
        
    def format(self, object: Object) -> dict:       
        # load model
        object_model = self._api.get_object_type(object.metadata.type_id)
        res = {
            "id": object.metadata.id,
        }

        # get object mapper        
        type_mapper = self._get_object_mapper(object.metadata.type_id)
        type_mapper_defaults = type_mapper.defaults
        
        # fields?           
        for field in object.fields.values():
            field_description = object_model.fields[str(field.description_id)]
            field_mapper = type_mapper.fields.get(field.description_id, FieldMapper())
            field_system_name = field.system_name = self._field_system_name(field_description, field_mapper)
            
            # include field in output?
            if len(type_mapper.include_fields) and field_system_name not in type_mapper.include_fields:
                continue
            elif len(type_mapper.exclude_fields) and field_system_name in type_mapper.exclude_fields:
                continue
                        
            # empty value?
            if field.value is None:
                res[field_system_name] = None
                continue
                        
            # format value
            res[field_system_name] = self._format_field(field, field_description, field_mapper, type_mapper_defaults)

        # classifications fields can be empty
        # use name 
        if len(object.fields.values()) == 0:
            res["label"] = object.metadata.name_plain
        
        #  subobjects?
        for sub_object in object.sub_objects.values():
            
            sub_object_model = object_model.sub_objects[str(sub_object.metadata.type_id)]
            sub_object_name = sub_object_model.type.system_name = self._object_system_name(sub_object_model, field_mapper)
            
            res.setdefault(sub_object_name, [])
            res[sub_object_name].append(self._format_sub_object(sub_object, sub_object_model, type_mapper.defaults))
                    
        return res
    
    def _format_sub_object(self, object: SubObject, object_model: SubObjectType, type_mapper_defaults: MapperDefaults) -> dict:

        # get object mapper
        type_mapper = self._get_object_mapper(object.metadata.type_id)
        
        # merge sub object mapper defaults with object mapper defaults
        mapperlist =  [type_mapper_defaults, type_mapper.defaults]
        type_mapper_defaults = self._merge_object_mapper_defaults(mapperlist)

        return_object = {
            "id": object.metadata.id,
        }
        
        # date/daterange?
        if object_model.type.has_date:
            # todo: format date/daterange data
            pass

        # location?        
        if object_model.type.has_location:
            # todo: format location data
            pass
        
        # fields?           
        for field in object.fields.values():
            field_description = object_model.fields[str(field.description_id)]
            field_mapper = type_mapper.fields.get(field.description_id, FieldMapper())
            field_system_name = field.system_name = self._field_system_name(field_description, field_mapper)
            
            # include field in output?            
            if len(type_mapper.include_fields) and field_system_name not in type_mapper.include_fields:
                continue
            elif len(type_mapper.exclude_fields) and field_system_name in type_mapper.exclude_fields:
                continue
                        
            # empty value?
            if field.value is None:
                return_object[field_system_name] = None
                continue
            
            # format value
            return_object[field_system_name] = self._format_field(field, field_description, field_mapper, type_mapper_defaults)            

        return return_object
    
    
    def _format_field(self, field: ObjectField, field_description: ObjectFieldDescription, field_mapper: FieldMapper, type_mapper_defaults: MapperDefaults) -> dict:

        # field_mapper = type_mapper.fields.get(field.description_id, FieldMapper())
        field_traverse_config = "traverse_" + field_description.value_type_base

        # process value
        field_values = self._to_list(field.value)

        match field_description.value_type_base:
            case "classification" | "type":
                refs = self._to_list(field.ref_object_id)
                if refs:
                    # field_traverse_config = "traverse_" + field_description.value_type_base
                    traverse = self._first_true([
                            field_mapper.traverse,
                            getattr(type_mapper_defaults, field_traverse_config), 
                        ],
                        False,
                        lambda x: x is not None
                    )
                    if traverse:
                        ref_objects = self._api.get_object(type_id=field_description.ref_type_id, object_id=refs)
                        field_values = [self.format(ref_object) for ref_object in ref_objects]
            case "media":
                    # field_traverse_config = "traverse_" + field_description.value_type_base
                    traverse = self._first_true([
                            field_mapper.traverse,
                            getattr(type_mapper_defaults, field_traverse_config), 
                        ],
                        False,
                        lambda x: x is not None
                    )
                    if traverse:
                        field_values = [self._api.get_media(media_id) for media_id in field_values]                                
            case _:
                # cast values
                cast_values = self._first_true([
                        field_mapper.cast_values,
                        getattr(type_mapper_defaults, "cast_values"), 
                    ],
                    False,
                    lambda x: x is not None
                )
                if cast_values:
                    field_values = list(map(lambda x: self._cast_value(x, field_description, field_mapper), field_values))
            
        # multiple values allowed?
        return field_values if (hasattr(field_description, "has_multi") and field_description.has_multi) else field_values[0]
                                             
    def _field_system_name(self, field_description: ObjectFieldDescription, field_mapper: FieldMapper) -> str:
        return field_mapper.system_name or \
            slugify(field_description.label, separator="_", regex_pattern=r'[^a-z0-9_]+')
            
    def _object_system_name(self, object_model: ObjectType | SubObjectType, object_mapper: ObjectMapper) -> str:
        return object_mapper.system_name or \
            slugify(object_model.type.label, separator="_", regex_pattern=r'[^a-z0-9_]+')
           
    def _cast_value(self, value: any, field_definition: ObjectFieldDescription, field_mapper: FieldMapper) -> any:
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
    
    def _first_true(self, iterable, default=False, pred=None) -> bool:
        return next(filter(pred, iterable), default)
    
    def _get_object_mapper(self, object_id: int) -> ObjectMapper:
        return self._mapper.types.get(object_id, ObjectMapper())

    def _merge_object_mapper_defaults(self, objects: list[MapperDefaults]) -> MapperDefaults:
        merged_object = MapperDefaults()
        for obj in objects:
            for key, value in obj.to_dict().items():
                if value:= getattr(obj, key) is not None:
                    setattr(merged_object, key, value)
        return merged_object