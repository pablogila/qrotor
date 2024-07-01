from .core import *


################################################
#############  Reading operations  #############
################################################


def read(input_file):
    is_compressed = False
    if input_file.endswith('.gz'):
        is_compressed = True
    elif not input_file.endswith('.json'):
        input_file = fix_extension(input_file, '.json')
        if not os.path.exists(input_file):
            input_file = fix_extension(input_file, '.json.gz')
            if os.path.exists(input_file):
                is_compressed = True
            else:
                raise FileNotFoundError(f"Could not find .json or .json.gz:  {input_file}")

    if is_compressed:
        with gzip.open(input_file, 'rt') as f:
            data_list = json.load(f)
    else:
        with open(input_file, 'r') as f:
            data_list = json.load(f)

    data = Data()
    for data_dict in data_list:
        data_obj = Data.from_dict(data_dict)
        data.add(data_obj)
    return data


def read_potential(variables=Variables, input_file=None, angle='deg', energy='ev'):
    if not input_file:
        return variables

    if not os.path.exists(input_file):
        print(f'File not found: {input_file}')
        return variables

    with open(input_file, 'r') as f:
        lines = f.readlines()
    positions = []
    potentials = []
    for line in lines:
        if line.startswith('#'):
            continue
        position, potential = line.split()
        positions.append(float(position))
        potentials.append(float(potential))

    if angle == 'deg':
        positions = np.radians(positions)
    elif angle == 'rad':
        positions = np.array(positions)

    if energy == 'mev':
        potentials = np.array(potentials) * 1000
    elif energy == 'ev':
        potentials = np.array(potentials)

    variables.grid = np.array(positions)
    variables.gridsize = len(positions)
    variables.potential_values = np.array(potentials)
    return variables


################################################
############  Writting operations  #############
################################################


def write(data:Data, out_file=None):
    write_summary(data, out_file)
    write_json(data, out_file)


def write_summary(data:Data, out_file=None):
    summary = ''
    spacer = ', '
    if data.version:
        summary += f'Data created on version {data.version}\n'
    if data.comment:
        summary += data.comment + '\n'
    if data.version or data.comment:
        summary += '\n------------------------------------\n\n'

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

    if (data.write_summary is not False) and out_file:
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


################################################
##############  File operations  ###############
################################################


def fix_extension(out_file, good_extension, bad_extensions=['.json.gz', '.tar.gz', '.gz', '.tar', '.txt', '.json', '.csv', '.dat', '.out']):
    if not out_file:
        return None
    if out_file.endswith(good_extension):
        return out_file
    for bad_extension in bad_extensions:
        if out_file.endswith(bad_extension):
            return out_file[:-len(bad_extension)] + good_extension
    return out_file + good_extension


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


# From InputMaker


def replace_line_with_keyword(new_text, keyword, filename):
    with open(filename, 'r') as f:
        lines = f.readlines()
    with open(filename, 'w') as f:
        for line in lines:
            if keyword in line:
                line = new_text + '\n'
            f.write(line)
    return


def rename_files(old_string, new_string):
    for file in os.listdir('.'):
        if old_string in file:
            os.rename(file, file.replace(old_string, new_string))


def get_files(folder, extensions, return_full_path=True):
    files = os.listdir(folder)
    target_files = []
    if not isinstance(extensions, list):
        extensions = [extensions]
    for extension in extensions:
        for file in files:
            if file.endswith(extension):
                if return_full_path:
                    file = os.path.join(folder, file)
                target_files.append(file)
        if target_files:
            return target_files
    return None

