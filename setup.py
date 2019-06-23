from setuptools import setup, find_packages

setup(
    name='twine',
    version='0.1',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Click',
        'gitdb2',
        'GitPython',
        'pudb',
        'Pygments',
        'smmap2',
        'urwid',
        'structlogger',
        'structlog',
    ],
    entrypoints='''
        [console_scripts]
        twine=twine.twine:twine
    ''',
)
