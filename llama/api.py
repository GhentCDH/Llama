import requests
import msgspec
import json
from requests.auth import AuthBase
from .types.response import ModelResponse, ObjectResponse
from .types.model import ObjectType

class TokenAuth(AuthBase):
    """Implements a token authentication scheme."""

    def __init__(self, token):
        self.token = token

    def __call__(self, request):
        """Attach an API token to the Authorization header."""
        request.headers["Authorization"] = f"Bearer {self.token}"
        return request

class NodegoatAPI():
    
    def __init__(self, api_endpoint: str, token: str, project_id: int = None, debug: bool = False) -> None:
        self._api = api_endpoint.strip('/')
        self._token = token
        self._project_id = project_id
        self._debug = debug
        
        self._type_cache = {}
        self._object_cache = {}        
    
    def _request(self, url: str) -> dict|None:
        request_url = "/".join([self._api, url.strip('/')])
        self._log(f"Requesting {request_url}")
        response = requests.get(
            url=request_url,
            headers={
                'accept': 'application/json',
            },
            auth=TokenAuth(self._token)
        )
        response.raise_for_status()
        return response
    
    def model_request(self, type_id: int = None, project_id: int = None) -> ModelResponse:
        
        project_id = project_id or self._project_id
        
        # check arguments
        if not type_id and not project_id:
            raise Exception('Model request is missing project/type argument')

        # build url
        url_parts = [
            'project',
            str(project_id) if project_id else None,
            'model',
            'type',
            str(type_id) if type_id else None,
        ]
        url = '/'.join([part for part in url_parts if part is not None])
        
        # request
        response = self._request(url)
        return msgspec.json.decode(response.content, type=ModelResponse)
            
                
    def object_request(self, type_id: int = None, object_id: int|str|list = None, project_id: int = None, scope_id: int = None, filter_id: int = None, component: dict = None) -> ObjectResponse:

        project_id = project_id or self._project_id
        object_id = ','.join([str(id) for id in object_id]) if isinstance(object_id, list) else object_id

        # check arguments and build url
        needle = (bool(type_id), bool(object_id), bool(project_id), bool(scope_id), bool(filter_id), bool(component))
        if needle == (False, False, False, False, False, False):
            raise Exception('Object request is missing essential project/type/object_id arguments')

        match needle:
            case (False, True, False, False, False, False):
                url_parts = [object_id]
            case (False, True, True, False, False, False):
                url_parts = ['project', project_id, object_id]
            case _:
                url_parts = ['project', project_id]
                
                url_parts.append('data')
                # B: type
                url_parts.append('type')
                url_parts.append(type_id)
                # C: scope
                if filter_id:
                    url_parts.append('filter')
                    url_parts.append(type_id)
                # C: scope
                if scope_id:
                    url_parts.append('scope')
                    url_parts.append(type_id)
                # D: object
                url_parts.append('object')
                if object_id:
                    url_parts.append(object_id)
                
        # build url
        url = '/'.join([str(part) for part in url_parts if part is not None])

        # request
        response = self._request(url)
        # print(json.dumps(str(response.content), indent=4))
        
        return msgspec.json.decode(response.content, type=ObjectResponse)
    
    
    def get_object_type(self, type_id: int) -> ObjectType:
        # preload model
        if not self._type_cache:
            self._log("Loading project model ...")
            self._load_project_model()
            self._log("Done loading.")
        # type should be in cache
        if not type_id in self._type_cache:
            raise Exception(f"Type with id {type_id} not found in project model.")
        # return type
        return self._type_cache[type_id]
    
    def get_object(self, type_id: int, object_id: int|list[int]):        
        # preload classification?
        if self.get_object_type(type_id).type.is_classification:
            if not type_id in self._object_cache:
                self._log(f"Preloading classification {type_id} ...")
                objects = list(self.object_request(type_id=type_id).data.objects.values())
                self._log("Done loading.")
                self._object_cache[type_id] = {int(object.metadata.id): object for object in objects}
        # init cache
        self._object_cache.setdefault(type_id, {})
        
        result = []
        request_ids = []
        # get from cache
        if object_id:
            object_id = object_id if isinstance(object_id, list) else [ object_id ]
            for id in object_id:
                if id in self._object_cache[type_id]:
                    self._log(f"Cache hit for object id {id}")
                    result.append(self._object_cache[type_id][id])
                else:
                    request_ids.append(id)
        # fetch remaining objects
        if len(request_ids):
            self._log(f"Cache miss for object id(s) {request_ids}")
            objects = list(self.object_request(type_id=type_id, object_id=object_id).data.objects.values())
            for object in objects:
                self._object_cache[type_id][object.metadata.id] = object        
            result.extend(objects)            

        return result

    def get_media(self, media_id):
        response = self._request('/'.join(['upload', 'media', media_id]))
        if response.headers.get('Content-Type') not in {'application/json', 'text/csv', 'text/txt', 'application/xml', 'text/xml'}:
            raise Exception(f"Unsupported content type: {response.headers.get('Content-Type')}")
        return response.text
    
    def _load_project_model(self):
        response = self.model_request()
        for type_id, model in response.data.models.items():
            self._type_cache[int(type_id)] = model
            
    def _log(self, message: str):
        if self._debug:
            print(message)