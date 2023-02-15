import html
import re
import json
from copy import copy
import openpyxl
from jsonschema import validate
from jsonschema import Draft202012Validator

def save_obj_to_file(obj, save_path):
    with open(save_path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=4, ensure_ascii=False)

def filter(node):
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
                retVal['valueSets'] = html.unescape(node[key][0]['#text'])
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
                retVal['implementationGuidance'] = html.unescape(node[key][0]['#text'])
            elif isinstance(node[key], dict) or isinstance(node[key], list):
                if key not in ['relationship', 'implementation']:
                    child = filter(node[key])
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
                child = filter(entry)
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

def load_worksheet(path, sheet_name, data_only, ret_type):
    '''
    A function that loads a worksheet from a workbook and returns an iterable

    :param path: the path to the file
    :param sheet_name: name of the sheet to load
    :param data_only: boolian value. Weather to load the sheet with cell formulae or values
    :param ret_type: weather it should be a python list or an openpyxl iterable. (list, excel)

    :return list: The  sheet as an iterable
    '''
    # open work book object
    wb = openpyxl.load_workbook(path, data_only=data_only)

    if ret_type == 'list':
        # load work sheet
        ws = list(wb[sheet_name])

        # translate into python dict
        full_data = []
        for arr in ws:
            data_arr = []
            for data in arr:
                data_arr.append(data.value)
            full_data.append(data_arr)
        return full_data

    else:
        # return openpyxl worksheet object
        ws = wb[sheet_name]
        return ws

def validate_contents(node, ws):
    if isinstance(node, dict):
        for key in node:
            if not isinstance(node[key], (dict, list)):
                if isinstance(node[key], str):
                    raw = node[key].strip().replace(' ','').lower().replace('_','')
                    found = False
                    for arr in ws:
                        for item in arr:
                            if str(item) != 'None':
                                raw_item = item.strip().replace(' ','').lower()
                                if raw == raw_item:
                                    print(f'Found {raw}')
                                    found = True
                                    break
                        if found:
                            break
                        
                    if not found:
                        print(f'Not found {raw}')
                else:
                    found = False
                    for arr in ws:
                        for item in arr:
                            if str(item) != 'None':
                                raw_item = item.strip().replace(' ','').lower()
                                if node[key] == raw_item:
                                    print(f'Found {node[key]}')
                                    found = True
                                    break
                        if found:
                            break
                    if not found:
                        print(f'Not found {node[key]}')
            else:
                validate_contents(node[key], ws)
    elif isinstance(node, list):
        for item in node:
            validate_contents(item, ws)
