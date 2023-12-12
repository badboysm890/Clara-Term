from setuptools import setup, find_packages

with open('requirements.txt') as f:
    required = f.read().splitlines()
    print(type(required))

setup(
    name='clara',
    version='0.1',
    packages=find_packages(),
    install_requires=required,
    entry_points='''
        [console_scripts]
        clara=main:cli
    ''',
)