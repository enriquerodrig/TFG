import json

def read_json(file_path: str):
    """ 
    Extract input and output parameters from a json file
    :file_path: path to json file:
    :return: metadata, input and output data
    """
    with open(file_path) as f:
        # Assuming the json file always contains a tuple of input and output dictionaries
        meta, input, output = json.load(f)
        return meta, input, output

def write_json(file_path: str, meta: dict, input: dict, output: dict):
    """
    Write input and (new) output parameters to a json file.
    :param file_path: path to json file
    :param meta: metadata
    :param input: input parameters
    :param output: output parameters
    """
    with open(file_path, 'w') as f:
        json.dump((meta, input, output), f)

def json_to_csv(json):
    """
    Convert list of json to csv format.
    :param json: json data
    :return: data in csv format
    """
    csv = {key: [] for item in json for key in item}
    for item in json:
        for key, value in item.items():
            csv[key].append(value)
        
    headers = list(csv.keys())
    rows = zip(*csv.values())
    return headers, rows

def write_csv(file_path:str, data, headers=[], separator=','):
    """
    Write data to csv file.
    :param file_path: path to csv file
    :param data: data to write
    :param headers: headers of the csv file
    """
    with open(file_path, 'w', encoding='utf-8') as f:
        if len(headers) > 0: f.write(separator.join(headers) + '\n')
        for row in data:
            f.write(separator.join(row) + '\n')

if __name__ == '__main__':
    in_path = 'data.json'

    # Read input parameters and output template
    meta, input, output = read_json(in_path)
    # Any operations with the input
    output['passwords'].append('new_password')
    # Write the new output
    write_json(in_path, meta, input, output)


