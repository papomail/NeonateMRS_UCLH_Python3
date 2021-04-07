from setuptools import setup, find_packages

setup(
    name='MRS_convert',
    version='1.4.0',
    description='Setting up a python package',
    author='Patxi Torrealdea and Alan Bainbridge',
    author_email='francisco.torrealdea@nhs.net',
    url='https://github.com/papomail/NeonateMRS_UCLH_Python3',
    packages=find_packages(include=['MRS_convert']),
    install_requires=[
        'cycler==0.10.0',
        'fpdf==1.7.2',
        'future==0.18.2',
        'kiwisolver==1.3.1',
        'matplotlib==3.4.1',
        'numpy==1.20.2',
        'pathlib==1.0.1',
        'pydicom==1.4.1',# do not update to pydicom version 2
        'pyparsing==2.4.7',
        'PyPDF2==1.26.0',
        'PyQt5==5.15.4',
        'PyQt5-Qt5==5.15.2',
        'PyQt5-sip==12.8.1',
        'pyqtgraph==0.12.0',
        'python-dateutil==2.8.1',
        'six==1.15.0',
    ],
    setup_requires=['pytest-runner', 'flake8'],
    tests_require=['pytest'],

)