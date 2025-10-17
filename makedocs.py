"""
This script is used to update the documentation automatically.
Requires pdoc and ATON, install with `pip install pdoc aton`.
Run this script as `python3 makedocs.py`.
"""

import shutil
import aton

readme = './README.md'
temp_readme = './_README_temp.md'
# Update links from the README
fix_dict ={
    '[qrotor](https://pablogila.github.io/qrotor/qrotor.html)'                            : '`qrotor`',
    '[qrotor.system](https://pablogila.github.io/qrotor/qrotor/system.html)'              : '`qrotor.system`',
    '[qrotor.systems](https://pablogila.github.io/qrotor/qrotor/systems.html)'            : '`qrotor.systems`',
    '[qrotor.constants](https://pablogila.github.io/qrotor/qrotor/constants.html)'        : '`qrotor.constants`',
    '[qrotor.rotation](https://pablogila.github.io/qrotor/qrotor/rotation.html)'          : '`qrotor.rotation`',
    '[qrotor.potential](https://pablogila.github.io/qrotor/qrotor/potential.html)'        : '`qrotor.potential`',
    '[qrotor.solve](https://pablogila.github.io/qrotor/qrotor/solve.html)'                : '`qrotor.solve`',
    '[qrotor.plot](https://pablogila.github.io/qrotor/qrotor/plot.html)'                  : '`qrotor.plot`',
    'Check the [full documentation online](https://pablogila.github.io/qrotor/).'         : '',
    '[system](https://pablogila.github.io/qrotor/qrotor/system.html)'                     : '`qrotor.system`',
    '[cosine potential](https://pablogila.github.io/qrotor/qrotor/potential.html#cosine)' : 'cosine potential (`qrotor.potential.cosine`)',
    '`System.deg`'                                                                        : '`qrotor.system.System.deg`',
}

# Get the package version as __version__
exec(open('qrotor/_version.py').read())
print(f'Updating docs to {__version__}...')
# Copy the pics folder
shutil.copytree('pics', 'docs/pics', dirs_exist_ok=True)
# Fix the README
aton.txt.edit.from_template(readme, temp_readme, fix_dict)
# Run Pdoc with the dark theme template from the ./css/ folder
aton.call.bash(f"pdoc ./qrotor/ -o ./docs/ --mermaid --math --footer-text='QRotor {__version__} documentation' -t ./css/")
aton.file.remove(temp_readme)
# Include google search verification  ## TO-UPDATE
#search_verification_tag = '    <meta name="google-site-verification" content="u0Be1NUH4ztGm5rr5f_YFt6hqoqMJ-j9h7rk3wEJAUo" />'
#aton.txt.edit.insert_under('docs/aton.html', '<head>', search_verification_tag)

