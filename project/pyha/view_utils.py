def get_int_query_param(http_request, param):
    string_value = http_request.GET.get(param)
    if string_value is not None and string_value.isnumeric():
        return int(string_value)

def convert_to_camel_case(obj):
    if isinstance(obj, list) and len(obj) > 0 and isinstance(obj[0], dict):
        return _convert_dict_array_key_names_to_camel_case(obj)
    elif isinstance(obj, dict):
        return _convert_dict_key_names_to_camel_case(obj)
    else:
        return obj

def _convert_dict_array_key_names_to_camel_case(obj_list):
    result = []

    for obj in obj_list:
        result.append(_convert_dict_key_names_to_camel_case(obj))

    return result


def _convert_dict_key_names_to_camel_case(obj):
    result = {}

    for key, value in obj.items():
        result[_underscore_to_camel_case(key)] = convert_to_camel_case(value)

    return result


def _underscore_to_camel_case(word):
    return word.split('_')[0] + ''.join(x.capitalize() for x in word.split('_')[1:])