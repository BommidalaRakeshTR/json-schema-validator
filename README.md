# json-schema-validator


## Regarding json_schema.json, please provide appropriate file path

json_schema = 'json_schema.json'

## Provide complete path of JSON file

validation_path = 'C:/Users/C286515/Json_Files/'


## Call python file named jsonschema_validator.py
python jsonschema_validator.py


# list of Dependancy packages
from validation import field_validation
import pandas as pa
import os

# Importing JSON Schema 
json_schema = 'json_schema.json'

# Appropriate json file path
validation_path = 'C:/Users/C286515/Json_Files/'


def validate_json(i, json_data, json_schema):
    verification_data = pa.read_json(json_data[i])
    validation_final = field_validation(verification_data, json_schema)
    if validation_final == 'Valid' or validation_final in ['relatedCases values are Null',
                                                           'plaintiffs values are Null',
                                                           'defendants values are Null',
                                                           'docketEntries values are Null'
                                                           ]:
        msg_val = ("Given JSON data is Valid" if validation_final == 'Valid' else
                   ("Given JSON data is Valid " + validation_final))
    else:
        msg_val = validation_final
    return msg_val


validation_file = os.listdir(validation_path)
validation_data = map(lambda name: os.path.join(validation_path, name), validation_file)
dirs = []
files = []
validation_result = []

for file in validation_data:
    if os.path.isdir(file): dirs.append(file)
    if os.path.isfile(file): files.append(file)
    validation_data_list = list(files)

for i in range(len(validation_data_list)):
    print(validation_data_list[i])
    msg = validate_json(i, validation_data_list,json_schema)
    if msg == 'Given JSON data is Valid':
        validation_result.append(str(" ".join([validation_file[i], '--', msg])))
    else:
        validation_result.append((validation_file[i], '--', msg))

print(*validation_result, sep="\n")
