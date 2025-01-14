from setuptools import setup
import re

DESCRIPTION = 'QRotor'
LONG_DESCRIPTION = 'QRotor'
AUTHOR = 'Pablo Gila-Herranz'
AUTHOR_EMAIL = 'pgila001@ikasle.ehu.eus'

def get_version():
    with open('qrotor/constants.py', 'r') as file:
        content = file.read()
        version_match = re.search(r"version\s*=\s*'([^']+)'", content)
        if version_match:
            return version_match.group(1)
        raise RuntimeError("Unable to find version.")

setup(
        name="qrotor", 
        version=get_version(),
        author=AUTHOR,
        author_email=AUTHOR_EMAIL,
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        packages=['qrotor'],
        install_requires=['aton',
                          'numpy',
                          'matplotlib',
                          'pandas',
                          'scipy'],
        keywords=['python', 'maat', 'INS', 'Raman', 'ATR', 'FTIR', 'spectroscopy', 'spectra', 'analysis'],
        classifiers= [
            "Development Status :: 5 - Production/Stable",
            "Intended Audience :: Science/Research",
            "Programming Language :: Python :: 3",
            "Operating System :: POSIX :: Linux",
            "Operating System :: Microsoft :: Windows",
            "Operating System :: Other OS",
        ]
)
