from setuptools import setup, find_packages

setup(
    name='arcane',
    version='0.1.0',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=[
        'pyyaml',
    ],
    entry_points={
        'console_scripts': [
            'arcane=src.cli:main',
        ],
    },
)