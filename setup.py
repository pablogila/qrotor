from setuptools import setup, find_packages

DESCRIPTION = "QRotor"

exec(open('qrotor/_version.py').read())

with open('README.md', 'r') as f:
    LONG_DESCRIPTION = f.read()

setup(
    name = 'qrotor', 
    version = __version__,
    author = 'Pablo Gila-Herranz',
    author_email = 'pgila001@ikasle.ehu.eus',
    description = DESCRIPTION,
    long_description = LONG_DESCRIPTION,
    long_description_content_type = 'text/markdown',
    packages = find_packages(),
    install_requires = ['scipy', 'pandas', 'numpy', 'matplotlib', 'aton', 'periodictable'],
    extras_requires = {'dev': ['pytest', 'twine', 'build']},
    python_requires = '>=3',
    license = 'AGPL-3.0',
    keywords = ['QRotor', 'Molecular rotations', 'Quantum rotations', 'Quantum', 'Molecular', 'Rotations', 'Neutrons', 'Research', 'Ab-initio', 'DFT', 'Density Functional Theory', 'Quantum ESPRESSO', 'Phonons', 'Electronic structure'],
    classifiers = [
        "Development Status :: 5 - Production/Stable",
        "Natural Language :: English",
        "Intended Audience :: Science/Research",
        "Programming Language :: Python :: 3",
        "Operating System :: POSIX :: Linux",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: Other OS",
    ]
)
