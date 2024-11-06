import msgspec
import sys
import os

sys.path.insert(1, os.path.join(sys.path[0], '..'))


# check models
if __name__ == "__main__":   
    import tests.data.data_structs as data_structs
    import tests.data.model_structs as model_structs
    import melkschaap.types.model as model
    from melkschaap.types.response import ModelResponse, ObjectResponse
    
    # check subobjects model
    msgspec.json.decode(model_structs.sub_object_field_description, type=model.SubObjectFieldDescription)
    msgspec.json.decode(model_structs.sub_object_field_descriptions, type=model.SubObjectFieldDescriptions)    
    msgspec.json.decode(model_structs.sub_object_model, type=model.SubObjectType)

    # check object model
    msgspec.json.decode(model_structs.object_field_description, type=model.ObjectFieldDescription)
    msgspec.json.decode(model_structs.object_field_descriptions, type=model.ObjectFieldDescriptions)
    msgspec.json.decode(model_structs.object_model, type=model.ObjectType)
    
    # check model response
    msgspec.json.decode(model_structs.model_response_single, type=ModelResponse)
    msgspec.json.decode(model_structs.model_response_multiple, type=ModelResponse)
    msgspec.json.decode(model_structs.model_response_invalid, type=ModelResponse)

    # check object response
    msgspec.json.decode(data_structs.data_response_valid, type=ObjectResponse)