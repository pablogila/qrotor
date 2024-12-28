'''
This script is used to update Maat documentation automatically.
Requires pdoc, install it with `pip install pdoc`.
It also requires Thoth, get it here: https://github.com/pablogila/Thoth
Run this script as `python3 makedocs.py`.
'''

try:
    import thoth as th
except:
    raise RuntimeError("Aborting... You need Thoth to compile the documentation! https://github.com/pablogila/Thoth")

readme = './README.md'
temp_readme = './_README_temp.md'
version_path = './qrotor/constants.py'

fix_dict = {
    '[classes](https://pablogila.github.io/QRotor/qrotor/classes.html)'       : '`qrotor.classes`',
    '[constants](https://pablogila.github.io/QRotor/qrotor/constants.html)'   : '`qrotor.constants`',
    '[file](https://pablogila.github.io/QRotor/qrotor/file.html)'             : '`qrotor.file`',
    '[plot](https://pablogila.github.io/QRotor/qrotor/plot.html)'             : '`qrotor.plot`',
    '[potentials](https://pablogila.github.io/QRotor/qrotor/potentials.html)' : '`qrotor.potentials`',
    '[solve](https://pablogila.github.io/QRotor/qrotor/solve.html)'           : '`qrotor.solve`',
}

version = th.find.lines(r"version\s*=", version_path, -1, 0, False, True)[0]
version = th.extract.string(version, 'version', None, True)

print(f'Updating README to {version}...')
th.text.replace_line(f'# QRotor {version}', '# QRotor v', readme, 1)

print('Updating docs with Pdoc...')
cwd = th.call.here()
th.file.from_template(readme, temp_readme, None, fix_dict)
completed_process = th.call.bash(f"pdoc ./qrotor/ -o ./docs --mermaid --math --footer-text='QRotor {version} documentation'", cwd)
th.file.remove(temp_readme)
print('Done!')

