from .common import *
#from . import constants


def fix_extension(out_file, good_extension, bad_extensions=['.txt', '.json', '.csv', '.dat', '.out']):
    if not out_file:
        return None
    if out_file.endswith(good_extension):
        return out_file
    for bad_extension in bad_extensions:
        if out_file.endswith(bad_extension):
            return out_file[:-len(bad_extension)] + good_extension
    return out_file + good_extension


def data(data:Data, out_file=None):
    data_summary(data, out_file)
    data_json(data, out_file)


# Write a human-readable output file
def data_summary(data:Data, out_file=None):
    summary = ''
    spacer = ', '
    if data.comment:
        summary += data.comment + '\n\n'

    for i, variable in enumerate(data.variables):
        var_summary_dict = variable.summary()
        for key, value in var_summary_dict.items():
            if isinstance(value, list) or isinstance(value, np.ndarray):
                value = spacer.join(map(str, value))
            summary += f'{key:<28}  {value}\n'
        summary += '\n'
        
        sol_summary_dict = data.solutions[i].summary()
        for key, value in sol_summary_dict.items():
            if isinstance(value, list) or isinstance(value, np.ndarray):
                value = spacer.join(map(str, value))
            summary += f'{key:<28}  {value}\n'

        summary += '\n------------------------------------\n\n'

    print(summary)

    if (data.variables[0].write_summary is not False) and out_file:
        out_file = fix_extension(out_file, '.txt')
        with open(out_file, 'a') as f:
            f.write(summary)
            print(f'Summary saved at {out_file}')


def data_json(data:Data, out_file=None):
    if not out_file:
        return
    if not out_file.endswith('.json'):
        out_file += '.json'
    try:
        with open(out_file, 'r') as f:
            data_list = json.load(f)
    except:
        data_list = []
    data_list.append(data.to_dict())
    with open(out_file, 'w') as f:
        json.dump(data_list, f)
        print(f'Data saved at {out_file}')

