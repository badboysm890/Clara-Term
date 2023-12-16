from setuptools import setup, find_packages

# Read the contents of your README file
with open('README.md', encoding='utf-8') as f:
    long_description = f.read()

with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(
    name='claraterm',
    version='0.3.5',
    author='BadBoy17G',
    author_email='praveensm890@gmail.com',
    description='let AI do the heavy lifting in terminal, CoPilot for your Terminal',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/badboysm890/Clara-Term.git',
    packages=find_packages(),
    install_requires=required,
    entry_points={
       'console_scripts': [
           'clara=claraterm.main:cli'
       ]
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)