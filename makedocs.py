'''
This script is used to update Maat documentation automatically.
Requires pdoc, install it with `pip install pdoc`.
It also requires Thoth, get it here: https://github.com/pablogila/Thoth
Run this script as `python3 makedocs.py`.
'''

try:
    import thoth as th
except:
    print("Aborting... You need Thoth to compile the documentation! https://github.com/pablogila/Thoth")

readme = './README.md'
#temp_readme = './_README_temp.md'
version_path = './qrotor/constants.py'

#fix_dict ={
#    '[alias](https://pablogila.github.io/Maat/maat/alias.html)'             : '`maat.alias`',
#    '[classes](https://pablogila.github.io/Maat/maat/classes.html)'         : '`maat.classes`',
#    '[constants](https://pablogila.github.io/Maat/maat/constants.html)'     : '`maat.constants`',
#    '[atoms](https://pablogila.github.io/Maat/maat/atoms.html)'             : '`maat.atoms`',
#    '[elements](https://pablogila.github.io/Maat/maat/elements.html)'       : '`maat.elements`',
#    '[fit](https://pablogila.github.io/Maat/maat/fit.html)'                 : '`maat.fit`',
#    '[normalize](https://pablogila.github.io/Maat/maat/normalize.html)'     : '`maat.normalize`',
#    '[plot](https://pablogila.github.io/Maat/maat/plot.html)'               : '`maat.plot`',
#    '[deuteration](https://pablogila.github.io/Maat/maat/deuteration.html)' : '`maat.deuteration`',
#    '[sample](https://pablogila.github.io/Maat/maat/sample.html)'           : '`maat.sample`',
#}

version = th.text.find(r"version\s*=", version_path, -1, 0, False, True)[0]
version = th.extract.string(version, 'version', None, True)

print(f'Updating README to {version}...')
th.text.replace_line(f'# QRotor {version}', '# QRotor v', readme, 1)

print('Updating docs with Pdoc...')
cwd = th.call.here()
#th.file.from_template(readme, temp_readme, None, fix_dict)
completed_process = th.call.bash(f"pdoc ./qrotor/ -o ./docs --mermaid --math --footer-text='QRotor {version} documentation'", cwd)
if completed_process.returncode != 0:
    print(completed_process.stderr)
#th.file.remove(temp_readme)
print('Done!')

