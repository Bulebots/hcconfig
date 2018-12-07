"""
Setup module.
"""
from setuptools import setup
from hcconfig import __version__


setup(
    name='hcconfig',
    version=__version__,
    description='Configure HC-05, HC-06 and other Bluetooth modules easily',
    long_description='''This tool allows you to easily configure HC-05,
        HC-06 and other Bluetooth modules easily through the serial port.''',
    url='https://github.com/Bulebots/hcconfig',
    author='Miguel Sánchez de León Peque',
    author_email='peque@neosit.es',
    license='BSD License',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Topic :: Utilities',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: Implementation :: CPython',
    ],
    keywords='hcconfig bluetooth configuration hc-05 hc-06 hc-0x',
    entry_points={
        'console_scripts': [
            'hcconfig = hcconfig.commands:run',
        ],
    },
    packages=['hcconfig'],
    install_requires=[
        'click',
        'pyserial',
    ],
)
