'''
This module provides straightforward functions to save data, as well as to load data and/or potential `*.dat` files.
'''

from .classes import *
import os
import pickle
import gzip
import shutil
import json
import maat as mt
# Get Maat from:
# https://github.com/pablogila/Maat


################################################
##########  User-friendly operations  ##########
################################################
def save(data:Experiment, filename:str=None, discard_shit:bool=False,  verbose:bool=True):
    '''Save the data in the current working directory as a binary *.qrotor file.'''
    filename = 'out' if filename is None else filename
    filename = _fix_extension(filename, '.qrotor')
    file = os.path.join(os.getcwd(), filename)
    if discard_shit:
        data = data.discard_shit()
    with gzip.open(file, 'wb') as f:
        pickle.dump(data, f)
    if verbose:
        print(f"Experiment saved and compressed to {file}")


def load(file:str='out.qrotor'):
    '''Load the data from a binary `*.qrotor` file in the current working directory.'''
    if not os.path.exists(file):
        file = os.path.join(os.getcwd(), file)
    if not os.path.exists(file):
        raise FileNotFoundError(f"The file {file} does not exist.")

    with gzip.open(file, 'rb') as f:
        data = pickle.load(f)
    if isinstance(data, Experiment):
        info(data, verbose=True)
        return data
    else:
        try:
            version = data.version
            version_message = f' (Experiment version {version})'
        except:
            version_message = ''
        print('WARNING: Data integrity could not be ckecked!' + version_message)
        user_input = input("Continue anyway? ('y' or 'n', suggested: 'n')")
        if user_input in mt.confirmation_keys['yes']:
            print('Data was loaded anyways... Good luck!')
            return data
        else:
            raise ConnectionAbortedError


def load_potential(file, system=None, angle='deg', energy='ev'):
    '''
    Read a potential energy curve from a file and return it as a Variables object.\n
    The file should contain two columns:  angle and potential,\n
    with degrees and eV as default units.\n
    '''
    if not os.path.exists(file):
        file = os.path.join(os.getcwd(), file)
    if not os.path.exists(file):
        raise FileNotFoundError(f"The file {file} does not exist.")

    system = System() if system is None else system
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

    if angle in mt.unit_keys['deg']:
        positions = np.radians(positions)
    elif angle in mt.unit_keys['rad']:
        positions = np.array(positions)
    else:
        raise ValueError(f"Angle unit '{angle}' not recognized.")

    if energy in mt.unit_keys['mev']:
        potentials = np.array(potentials) * 1000
    elif energy in mt.unit_keys['ev']:
        potentials = np.array(potentials)
    else:
        raise ValueError(f"Energy unit '{energy}' not recognized.")

    system.grid = np.array(positions)
    system.gridsize = len(positions)
    system.potential_values = np.array(potentials)
    return system


def summary(data:Experiment, out_file=None, verbose:bool=True):
    summary = ''
    spacer = ', '
    if data.version:
        summary += f'Experiment created on version {data.version}\n'
    if data.comment:
        summary += data.comment + '\n'
    if data.version or data.comment:
        summary += '\n------------------------------------\n\n'

    for i, system in enumerate(data.system):
        system_summary_dict = system.summary()
        for key, value in system_summary_dict.items():
            if isinstance(value, list) or isinstance(value, np.ndarray):
                value = spacer.join(map(str, value))
            summary += f'{key:<28}  {value}\n'
        summary += '\n------------------------------------\n\n'

    if verbose:
        print(summary)

    if out_file:
        out_file = _fix_extension(out_file, '.txt')
        with open(out_file, 'a') as f:
            f.write(summary)
            print(f'Summary saved at {out_file}')


def info(experiment:Experiment, verbose:bool=True):
    '''Returns the following info about the Experiment object: `qr`'''
    info  = '------------------------------------\n'
    info += f'Comment: {experiment.comment}\n'
    info += f'Version: {experiment.version}\n'
    info += f'Number of systems: {len(experiment.system)}\n'
    info += '------------------------------------'
    if verbose:
        print(info)
    return info


def _fix_extension(out_file, good_extension, bad_extensions=['.qrotor', '.json.gz', '.tar.gz', '.gz', '.tar', '.txt', '.json', '.csv', '.dat', '.out']):
    if not out_file:
        return None
    if out_file.endswith(good_extension):
        return out_file
    for bad_extension in bad_extensions:
        if out_file.endswith(bad_extension):
            return out_file[:-len(bad_extension)] + good_extension
    return out_file + good_extension

