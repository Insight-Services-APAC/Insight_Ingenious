import csv
import io
from enum import Enum
from typing import List

import markpickle
import yaml
from pydantic import BaseModel


class Output_Format(Enum):
    Markdown = "Markdown"
    Csv = "Csv"
    Json = "Json"
    Object = "Object"


# Checks if a field is a non-complex field using the value
def Is_Non_Complex_Field_Check_By_Value(value):
    return isinstance(value, (str, int, float, bool, type(None)))


# Checks if a field is a non-complex field using the type.. note this is not a foolproof method and is based on the assumption that the field is a complex type with RootModel in the name
def Is_Non_Complex_Field_Check_By_Type(field_type, root_model_name="RootModel"):
    if root_model_name in str(field_type):
        return False
    else:
        return True


class FieldData(BaseModel):
    FieldName: str
    FieldType: str


def Get_Model_Properties(model) -> List[FieldData]:
    properties: list[FieldData] = list()
    for field_name, field in model.model_fields.items():
        f: FieldData = FieldData(FieldName=field_name, FieldType=str(field.annotation))
        properties.append(f)
    return properties


def Dict_To_Csv(obj: dict, row_header_columns, name):
    output = "``` csv\n"
    csv_output = io.StringIO()
    writer = csv.writer(csv_output)
    writer.writerow(row_header_columns)
    for row in obj.values():
        writer.writerow([row[key] for key in row_header_columns])
    output += csv_output.getvalue() + "\n```"
    return output


def List_To_Csv(obj: List, row_header_columns, name):
    output = "``` csv\n"
    csv_output = io.StringIO()
    writer = csv.writer(csv_output)
    writer.writerow(row_header_columns)
    for row in obj:
        if not isinstance(row, dict):
            try:
                row = row.__dict__
            except AttributeError:
                print(f"Could not convert {row} to dictionary")
        writer.writerow([row[key] for key in row_header_columns])
    output += csv_output.getvalue() + "\n```"
    return output


def Listable_Object_To_Csv(obj, row_type):
    output = "``` csv\n"
    csv_output = io.StringIO()
    writer = csv.writer(csv_output)
    headers = [
        prop.FieldName
        for prop in Get_Model_Properties(row_type)
        if Is_Non_Complex_Field_Check_By_Type(prop.FieldType)
    ]
    writer.writerow(headers)
    for row in obj:
        writer.writerow([getattr(row, header, None) for header in headers])
    output += csv_output.getvalue() + "\n```"
    return output


def Object_To_Yaml(obj, strip_complex_fields=False):
    obj_dict = obj.__dict__
    output = "``` yaml\n"
    if strip_complex_fields:
        obj_dict = {
            k: v
            for k, v in obj.__dict__.items()
            if Is_Non_Complex_Field_Check_By_Value(v)
        }
    yaml_output = yaml.dump(obj_dict, default_flow_style=False)
    return output + yaml_output + "\n```"


def Object_To_Markdown(obj, name):
    val = markpickle.dumps(obj)
    return val
