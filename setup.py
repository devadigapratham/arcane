from setuptools import setup, find_packages

setup(
    name="arcane",
    version="0.1.0",
    description="Arcane: A distributed training CLI tool for machine learning models",
    author="Prathamesh",
    packages=find_packages(),
    install_requires=[
        "Click>=8.0",
        "PyYAML>=5.4",
        "typer>=0.4.1",
        "psutil>=5.8",
        "asyncio>=3.4",
    ],
    entry_points={
        'console_scripts': [
            'arcane = arcane.cli:app',
        ],
    },
    python_requires='>=3.8',
)

