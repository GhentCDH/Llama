import requests
from requests.auth import AuthBase
from .type import *

class TokenAuth(AuthBase):
    """Implements a token authentication scheme."""

    def __init__(self, token):
        self.token = token

    def __call__(self, request):
        """Attach an API token to the Authorization header."""
        request.headers["Authorization"] = f"Bearer {self.token}"
        return request

class NodegoatAPI():
    
    def __init__(self, api_endpoint: str, token: str, project_id: int = None) -> None:
        self._api = api_endpoint
        self._token = token
        self._project_id = project_id
        self._object_cache = {}
        self._model_cache = {}
    
    def _request(self, url: str) -> dict|None:
        request_url = self._api + '/' + url
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
        # print(json.dumps(response.content, indent=4))
        
        return msgspec.json.decode(response.content, type=ObjectResponse)  