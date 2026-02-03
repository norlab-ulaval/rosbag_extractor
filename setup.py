from setuptools import setup, find_packages

# Function to read requirements.txt
def read_requirements():
    with open('requirements.txt') as req:
        return req.read().splitlines()

setup(
    name='rosbag_extractor',
    version='0.1',
    packages=find_packages(),
    package_dir={'': '.'},
    install_requires=read_requirements(),
    entry_points={
        'console_scripts': [
            'rosbag_extractor=src.main:main'
        ]
    }
)