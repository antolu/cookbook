from setuptools import setup
from glob import glob

data_files = []
directories = glob('cookbook/fonts/')
for directory in directories:
    files = glob(directory+'*')
    data_files.append(('fonts', files))

data_files.append(('latex-style', ['cookbook/cookbook.sty']))

setup(
    data_files=data_files
)
