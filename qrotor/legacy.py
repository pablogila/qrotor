## Deprecated in v3.0.0


def write(data:Data, out_file=None, verbose:bool=True):
    write_summary(data, out_file, verbose)
    write_json(data, out_file)


def write_json(data:Data, out_file=None):
    print('Saving data as json...')
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


def read_json(input_file):
    print(f'Loading data from {input_file} ...')
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
    
    print('Data loaded succesfully')
    return data


def compress(filename, delete_original=True, original_extension='.json'):
    print('Compressing file...')
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


    ## Data() method
    def group_by_potential_and_atoms(self):
        '''Returns an array of grouped Data objects with the same potential_values and different atom_type'''
        grouped_data = []
        for new_variables, new_solutions in zip(self.variables, self.solutions):
            new_data = Data()
            new_data.comment = self.comment
            new_data.variables.append(new_variables)
            new_data.solutions.append(new_solutions)
            has_been_grouped = False
            for group in grouped_data:
                can_be_grouped = True
                for variable in group.variables:
                    if not np.array_equal(new_variables.potential_values, variable.potential_values) or (new_variables.atom_type == variable.atom_type):
                        can_be_grouped = False
                        break
                if can_be_grouped:
                    group.variables.append(new_variables)
                    group.solutions.append(new_solutions)
                    has_been_grouped = True
                    break
            if not has_been_grouped:
                grouped_data.append(new_data)
        return grouped_data


## Deprecated in v2.0.1


def grid_2pi(variables:Variables):
    variables.grid = np.linspace(0, 2*np.pi, variables.gridsize)
    return variables


def energies_OLD(variables:Variables, out_file=None):
    data = Data()

    if variables.set_of_constants is None:
        variables.set_of_constants = [[0]]
        if variables.potential_constants is not None:
            variables.set_of_constants = [variables.potential_constants]

    for constants in variables.set_of_constants:
        variables.potential_constants = constants
        variables = potential(variables)

        solutions = schrodinger(variables)
        # solutions.comment = f'{i+1}'

        stored_variables = deepcopy(variables)

        data.variables.append(stored_variables)
        data.solutions.append(solutions)

        if out_file:
            stored_data = Data()
            stored_data.variables.append(stored_variables)
            stored_data.solutions.append(solutions)
            file.write(stored_data, out_file)

    return data

