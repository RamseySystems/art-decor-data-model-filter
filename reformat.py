import json
import os
import functions as fn
import copy
import html
import re
from copy import copy
from jsonschema import validate
from jsonschema import Draft202012Validator
import sys

def save_obj_to_file(obj, save_path):
    with open(save_path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=4, ensure_ascii=False)

def filter(node, implementationGuidance: bool):
    if isinstance(node, dict):
        retVal = {}
        for key in node:
            if key == 'desc':
                if '#text' in node[key][0]:
                    retVal['description'] = html.unescape(node[key][0]['#text'])
            elif key == 'conformance':
                retVal['mro'] = node[key]
            elif key == 'shortName':
                retVal['name'] = node[key]
            elif key == 'operationalization':
                retVal['valueSets'] = re.sub(r'(?<=release=)[a-z][0-9]*', '', html.unescape(node[key][0]['#text'])).replace('&amp;','&')
            elif key == 'minimumMultiplicity':
                retVal[key] = node[key]
            elif key == 'maximumMultiplicity':
                retVal[key] = node[key]
            elif key == 'type': 
                retVal['type'] = node[key]
            elif key == 'valueDomain':
                if node[key][0]['type'] != 'code':
                    if node[key][0]['type'] != 'ordinal':
                        retVal[key] = copy(node[key])
            elif key == 'context':
                if implementationGuidance:
                    retVal['implementationGuidance'] = re.sub(r'(?<=release=)[a-z][0-9]*', '', html.unescape(node[key][0]['#text'])).replace('&amp;','&')
            elif isinstance(node[key], dict) or isinstance(node[key], list):
                if key not in ['relationship', 'implementation']:
                    child = filter(node[key], implementationGuidance)
                    if child:
                        retVal[key] = child
            
        if retVal:
            return retVal
        else:
            return None


    elif isinstance(node, list):
        retVal = []
        for entry in node:
            if isinstance(entry, str):
                retVal.append(entry)
            elif isinstance(entry, dict) or isinstance(entry, list):
                child = filter(entry, implementationGuidance)
                if child:
                    retVal.append(child)
        if retVal:
            return retVal
        else:
            return None


def validate(schema: dict, instance: dict):
    '''
    A function to validate the instance against a schema

    :param schema: the schema to validate against
    :param instance: the instance to validate
    '''
    validator = Draft202012Validator(schema)
    error_list = list(validator.iter_errors(instance))
    if error_list:
        return error_list
    else:
        return 'The instance is valid'


def main():
    
    path_to_raw_json = str(sys.argv[1])
    save_dir = str(sys.argv[2])
    

    '''
    path_to_raw_json = 'raw_art_decor'
    save_dir = 'filtered'
    '''


    for file in os.listdir(path_to_raw_json):
        path_to_file = f'{path_to_raw_json}/{file}'
        file_name = file.split('.')[0]

        with open(path_to_file) as f:
            data = json.load(f)

        # reformat
        reformatted = filter(data, implementationGuidance=True)
        save_obj_to_file(reformatted, f'{save_dir}/{file_name}_reformatted.json')

        reformatted = filter(data, implementationGuidance=False)
        save_obj_to_file(reformatted, f'{save_dir}/{file_name}_reformatted_no_implamentation_guidance.json')




if __name__ == '__main__':
    main()