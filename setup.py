from setuptools import setup, find_packages

setup(
    name='mrs',
    version='1.4.3',
    description='Software to process and produce PDF reports from NMR spectra acquired at 3T MRI scanners at University College London Hospital',
    author='Patxi Torrealdea and Alan Bainbridge',
    author_email='francisco.torrealdea@nhs.net',
    url='https://github.com/papomail/NeonateMRS_UCLH_Python3',
    # packages=find_packages(include=['MRS_convert']),
    packages=find_packages(),
    # packages=['mrs','mrs.Icons','mrs.3_0T_basis_threonine_no_MM','mrs.UnittestFiles'],

    install_requires=[
        'wheel==0.38.1',
        'cycler==0.10.0',
        'fpdf==1.7.2',
        'future==0.18.2',
        'kiwisolver==1.3.1',
        'matplotlib==3.4.1',
        'numpy==1.21.0',
        'pathlib==1.0.1',
        'pydicom==1.4.1',# do not update to pydicom version 2
        'pyparsing==2.4.7',
        'PyPDF2==1.27.5',
        'PyQt5==5.15.4',
        'PyQt5-Qt5==5.15.2',
        'PyQt5-sip==12.8.1',
        'pyqtgraph==0.12.0',
        'python-dateutil==2.8.1',
        'six==1.15.0',
    ],
    setup_requires=['pytest-runner', 'flake8'],
    tests_require=['pytest'],
    package_dir={'mrs':'mrs'},
    package_data={
        'mrs.3_0T_basis_threonine_no_MM':['*.csv'],
        'mrs.Icons': ['*.png'],
    },
    include_package_data=True,
    entry_points={
        'console_scripts': ['mrs=mrs.MRS_convert:main']
    }    

)
