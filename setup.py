from setuptools import setup

setup(
    name='Transpose',
    version='0.0.2',
    packages=['transpose', ],
    entry_points={
        'console_scripts': [
            'transpose = transpose.__main__:_main'
        ]
    },
    author='amirbou'
)
