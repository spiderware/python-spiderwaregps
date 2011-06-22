from setuptools import setup, find_packages
import os

version = '0.1a1'

def read(fname):
    # read the contents of a text file
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

install_requires = [
    'setuptools',
]

setup(
    name = "pyhton-spiderwaregps",
    version = version,
    url = 'http://github.com/spiderware/pyhton-spiderwaregps',
    license = 'BSD',
    platforms=['OS Independent'],
    description = "A converter for the custom binary format of the spiderware gps tracker.",
    long_description = read('README.rst'),
    author = 'Stefan Foulis',
    author_email = 'stefan.foulis@gmail.com',
    packages=find_packages('src'),
    install_requires = install_requires,
    include_package_data=True,
    zip_safe=False,
    classifiers = [
    ]
)
