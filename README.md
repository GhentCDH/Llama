# Melkschaap

A python library for [Nodegoat](https://nodegoat.net). This library eats models and objects from the Nodegoat API and spits readable json data.

## Features

- model and object API requests
- cached classification requests
- json formatter for Nodegoat object responses
    - convert field description ids to names
    - cast field values to associated field type
    - traverse references to classifications, objects and media

## Installation

First install the dependencies with a command similar to the command below. Here the installation is done for the user and not global. It uses `pip` and not `pip3` which may be the same on your system.

```pip install --user -r requirements.txt```



## API

```python
from melkschaap import NodegoatAPI

nodegoat_api = NodegoatAPI('https://api.nodegoat.net', 
                  'my_very_secret_api_token',
                  project_id=1701)

## raw api requests (uncached)
# get project model
model_response = nodegoat_api.model_request()
# get type specific model
model_response = nodegoat_api.model_request(type_id=1234)
# get objects of type 1234
data_response = nodegoat_api.object_request(type_id=1234)
# get specific object(s)
data_response = nodegoat_api.object_request(object_id=456789)

## cached data/type requests
object_description = nodegoat_api.get_object_type(type_id=1234)

objects = nodegoat_api.get_object(object_id=56789) # single object
objects = nodegoat_api.get_object(type_id=1234) # all results for type 1234
```

## Formatter

The Nodegoat API returns raw data in a format that reflects the internal database structure, making the data hard to read and process. Furthermore, Nodegoat outputs all primitive type values (int, float, bool) as strings, requiring extra processing to cast the values to their associated type.

Example: the string value "1" can be the string value "1", a boolean True, the integer number 1 or the floating point number $`10^{-10}`$.

The formatter can fix these problemes and convert the output to a more readable json object. The formatter can also traverse references to other data (objects, classifications or media). Some options can be configured using an optional Mapper object.

### Usage

```python
from melkschaap import NodegoatAPI, ObjectFormatter, MapperDefaults, ObjectMapper, FieldMapper, TypeMapper

mapper = ModelMapper(
    defaults=MapperDefaults(traverse_classification=True, traverse_type=False, cast_values=True),
    types={
        1286: ObjectMapper(
            fields={
                4732: FieldMapper(traverse=True),
                5040: FieldMapper(traverse=True),
            },
        ),
        1292: ObjectMapper(
            exclude_fields={'sequence'},
        ),
    }
)
formatter = ObjectFormatter(api=nodegoat_api, mapper=mapper)

object = nodegoat_api.get_object(object_id=456789)
output = formatter.format(object)
```

### Example

**Nodegoat output**

```json
{
    "2484072": {
        "object": {
            "type_id": 1286,
            "nodegoat_id": "ngGN7K27sINasHdHzGBKquNxdRU",
            "object_id": 2484072,
            "object_name": "<span style=\"font-style: italic; opacity: 0.8;\">No Name<\/span>",
            "object_name_plain": null,
            "object_name_style": [],
            "object_style": [],
            "object_sources": [],
            "object_version": "",
            "object_dating": "2024-03-26T19:48:49Z"
        },
        "object_definitions": {
            "4677": {
                "object_description_id": 4677,
                "object_definition_ref_object_id": [
                    2480431
                ],
                "object_definition_value": [
                    "clay"
                ],
                "object_definition_sources": [],
                "object_definition_style": []
            },
            "4731": {
                "object_description_id": 4731,
                "object_definition_ref_object_id": [
                    2480363
                ],
                "object_definition_value": [
                    "baked"
                ],
                "object_definition_sources": [],
                "object_definition_style": []
            },
            "4732": {
                "object_description_id": 4732,
                "object_definition_ref_object_id": 2480382,
                "object_definition_value": "complete",
                "object_definition_sources": [],
                "object_definition_style": []
            },
            "4733": {
                "object_description_id": 4733,
                "object_definition_ref_object_id": 2480383,
                "object_definition_value": "Excellent",
                "object_definition_sources": [],
                "object_definition_style": []
            },
            "4734": {
                "object_description_id": 4734,
                "object_definition_ref_object_id": 2483824,
                "object_definition_value": "MRD Tall Ṣadūm",
                "object_definition_sources": [],
                "object_definition_style": []
            },
            ...
```

**melkschaap output**

```json
{
    "id": 2484072,
    "material": [
        {
            "id": 2480431,
            "label": "clay",
            "cdli_id": 1
        }
    ],
    "material_aspect": [
        {
            "id": 2480363,
            "label": "baked",
            "cdli_id": 10
        }
    ],
    "artifact_preservation": {
        "id": 2480382,
        "label": "complete"
    },
    "surface_preservation": {
        "id": 2480383,
        "label": "Excellent"
    },
    "provenience": "MRD Tall \u1e62ad\u016bm",
    "period": [
        {
            "id": 2480348,
            "label": "Old Babylonian (ca. 1900-1600 BC)",
            "cdli_id": 18
        }
    ],
    "written_in": "MRD Tall \u1e62ad\u016bm",
    "museum_number": "O.223",
    "accession_number": "NA",
    ...
```

## Credits

Development by [GhentCDH - Ghent University](https://www.ghentcdh.ugent.be/). Funded by the [GhentCDH research projects](https://www.ghentcdh.ugent.be/projects).
