'''A convenience library for Ray that allows you to run a function on a remote
EC2 instance from JuPyter Notebook.'''

long_description = __doc__ + ''' It's a thin wrapper around Ray that
automatically sets up the cluster for you and allows you to run a function on
a remote instance with a single function call.
'''

from setuptools import setup

setup(
    name='raycut',
    version='0.0.3',
    description=__doc__,
    long_description=long_description,
    url='http://github.com/d33tah/raycut',
    author='Jacek "d33tah" Wielemborek',
    author_email='d33tah@gmail.com',
    license='WTFPL',
    packages=['raycut'],
    install_requires=[
        'ray',
        'boto3',
    ]
)
