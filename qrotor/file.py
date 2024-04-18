from .common import *


def fix_extension(out_file, good_extension, bad_extensions=['.json.gz', '.tar.gz', '.gz', '.tar', '.txt', '.json', '.csv', '.dat', '.out']):
    if not out_file:
        return None
    if out_file.endswith(good_extension):
        return out_file
    for bad_extension in bad_extensions:
        if out_file.endswith(bad_extension):
            return out_file[:-len(bad_extension)] + good_extension
    return out_file + good_extension


def read(input_file):
    compressed = False
    if not os.path.exists(input_file):
        input_file = fix_extension(input_file, '.json')
    if not os.path.exists(input_file):
        file_gz = input_file + '.gz'
        if os.path.exists(file_gz):
            decompress(file_gz, delete_original=False)
            compressed = True
    if not os.path.exists(input_file):
        raise FileNotFoundError(f"Could not find input .json or .json.gz:  {input_file}")

    with open(input_file, 'r') as f:
        data_list = json.load(f)
    data = Data()
    for data_dict in data_list:
        data_obj = Data.from_dict(data_dict)
        data.add(data_obj)
    if compressed:
        os.remove(input_file)
        print(f'Deleted temporary decompressed file')
    return data


def write(data:Data, out_file=None):
    write_summary(data, out_file)
    write_json(data, out_file)


# Write a human-readable output file
def write_summary(data:Data, out_file=None):
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


def write_json(data:Data, out_file=None):
    if not out_file:
        return
    if not out_file.endswith('.json'):
        out_file = fix_extension(out_file, '.json')
    try:
        with open(out_file, 'r') as f:
            data_list = json.load(f)
    except:
        data_list = []
    data_list.append(data.to_dict())
    with open(out_file, 'w') as f:
        json.dump(data_list, f)
        print(f'Data saved at {out_file}')


def compress(filename, delete_original=True, original_extension='.json'):
    if not os.path.exists(filename):
        if not filename.endswith(original_extension):
            filename = fix_extension(filename, original_extension)
    if not os.path.exists(filename):
        print(f'Skipped compression of missing file  {filename}')
        return None
    try:
        with open(filename, 'rb') as f_in:
            with gzip.open(filename + '.gz', 'wb') as f_out:
                f_out.writelines(f_in)
        if delete_original:
            os.remove(filename)
        print(f'File compressed at {filename}.gz')
    except Exception as e:
        print(f'COMPRESSION ABORTED: {e}')


def decompress(filename, delete_original=False, file_extension='.json.gz'):
    if not filename.endswith(file_extension):
        filename = fix_extension(filename, file_extension)
    if not os.path.exists(filename):
        print(f'Skipped decompression of missing file  {filename}')
        return None
    try:
        with gzip.open(filename, 'rb') as f_in:
            with open(filename[:-3], 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        if delete_original:
            os.remove(filename)
        print(f'File decompressed at {filename[:-3]}')
    except Exception as e:
        print(f'DECOMPRESSION ABORTED: {e}')


################################################
##############  From InputMaker  ###############
################################################


def replace_line_with_keyword(new_text, keyword, filename):
    with open(filename, 'r') as f:
        lines = f.readlines()
    with open(filename, 'w') as f:
        for line in lines:
            if keyword in line:
                line = new_text + '\n'
            f.write(line)
    return

