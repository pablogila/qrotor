from .common import *

'''
def data(input_file):
    if not os.path.exists(input_file):
        if not input_file.endswith('.json'):
            input_file += '.json'
        else:
            raise FileNotFoundError(f"Could not find input .json:  {input_file}")

    with open(input_file, 'r') as f:
        data_list = json.load(f)
    data = Data()
    for data_dict in data_list:
        data_obj = Data.from_dict(data_dict)
        data.add(data_obj)
        #data.variables.extend(data_obj.variables)
        #data.solutions.extend(data_obj.solutions)
    return data

'''