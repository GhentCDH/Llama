from .api import NodegoatAPI
from .type import *
from slugify import slugify


class JsonFormatter():
        
    def __init__(self, api: NodegoatAPI, mapper: dict = {}, project_id: int = None) -> None:
        self._api = api
        self._mapper = mapper

        self._model_cache = {}
        self._object_cache = {}
        self._representation_cache = {}

        # load models        
        self._load_project_model()
        
    def json(self, object: Object):       
        # load model
        model = self._get_object_model(object.metadata.type_id)
        res = {
            "id": object.metadata.id,
        }
        
        type_mapper = self._mapper.types.get(object.metadata.type_id, TypeMapperConfig())
        
        # classifications fields can be empty
        # use name 
        if len(object.fields.values()) == 0:
            res["label"] = object.metadata.name_plain
            return res
            
        for field in object.fields.values():
            field_definition = model.fields[str(field.description_id)]
            field_mapper = type_mapper.fields.get(field.description_id, FieldMapperConfig())
            field_name = field.system_name = self._field_system_name(field_mapper, field_definition.label)
            field_traverse_config = "traverse_" + field_definition.value_type_base

            
            # print(field_definition.label, field_name, field, field_traverse_config)
            
            # empty value?
            if field.value is None:
                res[field_name] = None
                continue
            
            # process value
            refs = self._to_list(field.ref_object_id)
            values = self._to_list(field.value)
            
            me = self
            # lookup refs?
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
                    field_values = []
                    ref_objects = list(self._api.object_request(object_id=refs, type_id=field_definition.ref_type_id).data.objects.values())
                    for ref_object in ref_objects:
                        field_values.append(self.json(ref_object))
                else:
                    field_values = values
            else:
                field_values = values
                
            # multiple values allowed?            
            res[field_name] = field_values if field_definition.has_multi else field_values[0]
            
        return res
                           
    def _field_system_name(self, field_mapper: FieldMapperConfig, field_label: str):
        return field_mapper.system_name or \
            slugify(field_label, separator="_", regex_pattern=r'[^a-z0-9_]+')
        
    def _load_project_model(self):
        response = self._api.model_request()
        for type_id, model in response.data.models.items():
            self._model_cache[int(type_id)] = model
        
    def _get_object_model(self, type_id: int) -> ObjectModel:
        return self._model_cache[type_id]
    
    def _to_list(self, value: any) -> list[any]|None:
        if value is None:
            return []
        return value if isinstance(value, list) else [ value ]
    
    def _first_true(self, iterable, default=False, pred=None):
        return next(filter(pred, iterable), default)