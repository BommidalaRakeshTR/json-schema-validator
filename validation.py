import json
import pandas as pa
import io
from genson import SchemaBuilder
from jsonschema import validate
import jsonschema


def validateJson_bySchema(final_verification, schema1):
    try:
        validate(instance=final_verification, schema=schema1)
    except jsonschema.exceptions.ValidationError as error:
        return False
    return True


def field_validation(verification_data,json_schema):
    schema = json.load(open(json_schema, 'r'))['properties']
    schema = pa.DataFrame.from_dict(schema, orient="index")
    schema.reset_index(inplace=True)
    buffer = io.StringIO()
    verification_data.info(buf=buffer)
    lines = buffer.getvalue().splitlines()
    verification_data_info = (pa.DataFrame([x.split() for x in lines[5:-2]], columns=lines[3].split())
                              .drop('Count', axis=1)
                              .rename(columns={'Non-Null': 'Non-Null Count'}))[["Column", "Dtype"]]
    verification_data_info.loc[verification_data_info['Column'] == "relatedCases", 'Dtype'] = "string"
    verification_data_info['Dtype'] = verification_data_info['Dtype'].replace(['float64'], 'string')
    verification_data_info.loc[verification_data_info['Column'] == "otherParties", 'Dtype'] = "string"
    verification_data_info.columns = ['index', 'type']
    verification_schema = schema.filter(['index', 'type'])
    verification_objects = pa.concat([verification_schema, verification_data_info])
    verification_object_key = pa.merge(verification_data_info, schema.filter(['index', 'type']), how='outer',
                                       suffixes=('', '_y'),
                                       indicator=True)
    verification_object_key = verification_object_key[verification_object_key['_merge'] == 'right_only'][
        verification_schema.columns]
    relatedCases_val = type_field_validation(verification_data)
    elements_result = []
    elements_val = ['plaintiffs', 'defendants', 'docketEntries']
    elements_result = []
    for i in range(len(elements_val)):
        final = name_field_validation(i, verification_data, elements_val,json_schema)
        elements_result.append(final)
    if len(verification_object_key) == 0:
        verification_object_key = (
            'Valid' if relatedCases_val == 'relatedCases valid' else 'relatedCases values are Null')
        verification_object_key = (verification_object_key if elements_result[0] == 'plaintiffs Valid' else (
            verification_object_key, 'plaintiffs values are Null'))
        verification_object_key = (verification_object_key if elements_result[1] == 'defendants Valid' else (
            verification_object_key, 'defendants values are Null'))
        verification_object_key = (verification_object_key if elements_result[2] == 'docketEntries Valid' else (
            verification_object_key, 'docketEntries values are Null'))
    else:
        verification_object_key = ("InValid missing objects are", list(verification_object_key['index']))
    return verification_object_key


def type_field_validation(verification_data):
    verification_relatedCases = verification_data.relatedCases[verification_data.relatedCases.notnull()]
    if len(verification_relatedCases) == 0:
        verification_Cases = 'relatedCases valid'
    else:
        ju_relatedCase = list(verification_relatedCases.relatedCase)
        verification_Cases = (
            "type is not present in relatedCases" if ju_relatedCase == ['type'] else 'relatedCases valid')
    return verification_Cases


def name_field_validation(i, verification_data, elements_val,json_schema):
    if elements_val[i] in 'plaintiffs':
        verification_elements = verification_data[verification_data.plaintiffs.notnull()].plaintiffs
    elif elements_val[i] in 'defendants':
        verification_elements = verification_data[verification_data.plaintiffs.notnull()].defendants
    else:
        verification_elements = verification_data[verification_data.plaintiffs.notnull()].docketEntries
    builder = SchemaBuilder()
    builder.add_object('Null') if len(verification_elements) == 0 else builder.add_object(verification_elements.party)
    elements_schema = builder.to_schema()
    schema1 = json.load(open(json_schema, 'r'))['properties'][elements_val[i]][
        'properties']
    isJsonValid = False if len(verification_elements) == 0 else validateJson_bySchema(elements_schema, schema1)
    if isJsonValid == True:
        verification_plaintiffs = (elements_val[i] + " Valid")
    else:
        verification_plaintiffs = (
            ('The ' + elements_val[i] + ' object is invalid') if isJsonValid == False else (elements_val[i] + " Valid"))
    return verification_plaintiffs
