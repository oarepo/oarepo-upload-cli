from setuptools import setup

setup(
    name='oarepo-upload-cli',
    version='0.0.1',
    install_requires=[
        'argparse',
        'pyenv',
        'requests',
        'importlib-metadata; python_version == "3.9"',
    ],
    entry_points={
        'console_scripts': [
            'upload = upload:main'
        ]
    }
)