#!/usr/bin/python

import json

schema = {
    "fields": []
}

fields = []

with open("./harvest_fields", 'r') as o:
    field_names = o.read().split("\n")
    for field_name in field_names:
        if len(field_name) == 0:
            continue
        if field_name in fields:
            field_name = "locationaccordingto2"
        fields.append(field_name)
        field = {
            "name": field_name,
            "type": "STRING"
        }
        schema['fields'].append(field)

with open("./schema.json", 'w') as w:
    w.write(json.dumps(schema, indent=2))
