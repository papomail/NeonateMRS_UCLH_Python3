from setuptools import setup, find_packages

setup(
    name='mrs',
    version='1.5.2',
    description='Software to process and produce PDF reports from NMR spectra acquired at 1.5T and 3T MRI scanners. Supports Philips and Siemens DICOM formats with enhanced spectroscopy processing capabilities.',
    long_description="""
# Neonate MRS UCLH (Python3)

## Overview
Advanced software for processing and generating automated reports of neonatal NMR spectra acquired at 1.5T and 3T MRI scanners at University College London Hospital. This package provides robust DICOM format support for both Philips and Siemens scanners with enhanced spectroscopy processing capabilities.

## Key Features

### Multi-Vendor Support
- **Philips DICOM4 MRS**: Full support for traditional and Enhanced DICOM MR Spectroscopy formats
- **Siemens SPEC NUM 4**: Beta support for Siemens IMA files with CSA header parsing
- **Automatic Scanner Detection**: Intelligent field strength detection (1.5T vs 3T) with parameter adjustment

### Enhanced Compatibility (Version 1.5.2)
- **Modern Package Support**: Compatible with NumPy 1.24.4+, PyDICOM 2.4.4+, PyQt5, and PyQtGraph
- **Robust Data Loading**: Multiple data type fallbacks for bytes conversion (float32 → float64 → int16)
- **PyQt5 Migration**: Complete widget migration from QtGui to QtWidgets for modern PyQt5 compatibility
- **Enhanced Error Handling**: Comprehensive error handling with detailed diagnostics

### Processing Capabilities
- **Automatic Phasing**: Intelligent spectrum phasing with manual adjustment options
- **Peak Detection**: Automated Choline and Creatine peak identification
- **Frame Processing**: Multi-frame acquisition support with quality assessment
- **Data Validation**: Comprehensive parameter validation and bounds checking

### Output Formats
- **TARQUIN Integration**: Direct export to TARQUIN format for quantitative analysis
- **JMRUI Support**: Export to JMRUI format for advanced processing
- **PDF Reports**: Automated generation of clinical reports with quality metrics
- **Diagnostic Tools**: Comprehensive diagnostic scripts for troubleshooting

## Recent Updates

### Version 1.5.2 (26/05/2025) - Siemens Support & Enhanced Compatibility
- Added support for Siemens SPEC NUM 4 format (beta)
- Automatic display adjustment for 1.5T vs 3T scanners (beta)
- Enhanced field strength detection and parameter adjustment
- Integrated read_dicom_siemens module for CSA header parsing
- Maintains compatibility with NumPy 1.24.4+, PyDICOM 2.4.4+, PyQt5, and PyQtGraph
- Full backward compatibility with all previous formats

### Version 1.5.1 (26/05/2025) - PyQt5 Compatibility & Data Loading Fixes
- Fixed PyQt5 widget imports (moved from QtGui to QtWidgets)
- Fixed bytes data conversion for newer PyDICOM versions
- Enhanced error handling for DICOM data loading
- Maintains full backward compatibility with all previous versions

### Version 1.5.0 (26/05/2025) - Enhanced DICOM Format Support
- Added support for Enhanced DICOM MR Spectroscopy format (new Philips scanners)
- Implemented safe DICOM attribute access to prevent crashes on missing tags
- Enhanced error handling throughout the processing pipeline
- Maintains full backward compatibility with traditional DICOM4 MRS format

## Compatibility Fixes Applied

### PyQt5 Migration
- Complete migration of widget classes from QtGui to QtWidgets
- Maintains graphics-related classes in QtGui (QFont, QPixmap, QIcon, etc.)
- Enhanced PatNameDialog with proper widget imports

### Data Loading Robustness
- Multiple data type fallbacks for bytes conversion
- Enhanced parameter extraction with DICOM tag fallbacks
- Improved data validation and automatic adjustment
- Comprehensive error handling and diagnostics

### PDF Generation Fixes
- Fixed TypeError in PDF generation by ensuring string conversion for displayTE
- Enhanced FPDF compatibility with proper data type handling
- Robust cell content formatting

## Installation Requirements

### System Requirements
- Python 3.7+
- TARQUIN 4.3.10+ (for quantitative analysis)
- Git (for installation)

### Package Dependencies
- NumPy ≥1.24.4 (scientific computing)
- PyDICOM ≥2.4.4 (DICOM processing)
- PyQt5 ≥5.15.4 (GUI framework)
- PyQtGraph ≥0.12.0 (plotting)
- Matplotlib ≥3.4.1 (additional plotting)
- FPDF ≥1.7.2 (PDF generation)
- PyPDF2 ≥1.27.5 (PDF processing)

## Usage

### Clinical Workflow
1. **Data Loading**: Select input folder with DICOM files
2. **Quality Assessment**: Review individual frames for quality
3. **Manual Adjustment**: Fine-tune phasing and peak positions if needed
4. **Processing**: Convert to TARQUIN/JMRUI formats
5. **Report Generation**: Generate automated PDF reports
6. **Clinical Review**: Review reports with MRI Clinical Scientist

### Diagnostic Tools
- `diagnose_mrs_data.py`: Comprehensive data analysis
- `test_compatibility.py`: Package compatibility testing
- `debug_data_loading.py`: DICOM loading diagnostics

## Important Notes

### Clinical Use
- **NOT intended as unsupervised processing solution**
- **Reports must be approved by MRI Clinical Scientist**
- Designed for use by qualified MRI Clinical Scientists
- Requires expertise in neonatal MR spectroscopy

### Data Compatibility
- Supports traditional DICOM4 MRS format
- Enhanced DICOM MR Spectroscopy format support
- Siemens IMA file support (beta)
- Maintains backward compatibility with existing data

## Support and Documentation

### Documentation
- Complete API documentation in Doc/Documentation.md
- Data flow diagrams and processing pipeline details
- Troubleshooting guides and diagnostic tools

### Testing
- Comprehensive test suite with 29 unit tests
- Compatibility validation scripts
- Real-world data processing verification

## License
BSD 2-Clause License - See LICENSE.md for details

## Authors
- Patxi Torrealdea (francisco.torrealdea@nhs.net)
- Alan Bainbridge
- University College London Hospital
- Department of Medical Physics and Biomedical Engineering
""",
    long_description_content_type='text/markdown',
    author='Patxi Torrealdea and Alan Bainbridge',
    author_email='francisco.torrealdea@nhs.net',
    url='https://github.com/papomail/NeonateMRS_UCLH_Python3',
    
    # Additional metadata
    license='BSD-2-Clause',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Healthcare Industry',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Medical Science Apps.',
        'Topic :: Scientific/Engineering :: Image Processing',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
    keywords='MRS, spectroscopy, DICOM, medical imaging, Philips, Siemens, neonatal, TARQUIN, JMRUI, PyQt5, clinical',
    python_requires='>=3.7',
    
    # Project URLs
    project_urls={
        'Bug Reports': 'https://github.com/papomail/NeonateMRS_UCLH_Python3/issues',
        'Source': 'https://github.com/papomail/NeonateMRS_UCLH_Python3',
        'Documentation': 'https://github.com/papomail/NeonateMRS_UCLH_Python3/blob/main/Doc/Documentation.md',
    },
    # Package discovery
    packages=find_packages(),

    install_requires=[
        # Core scientific computing packages
        'numpy>=1.24.4',
        'matplotlib>=3.4.1',
        
        # DICOM processing
        'pydicom>=2.4.4',
        
        # GUI framework
        'PyQt5>=5.15.4',
        'PyQt5-Qt5>=5.15.2',
        'PyQt5-sip>=12.8.1',
        'pyqtgraph>=0.12.0',
        
        # PDF generation and processing
        'fpdf>=1.7.2',
        'PyPDF2>=1.27.5',
        
        # Utility packages
        'future>=0.18.2',
        'pathlib>=1.0.1',
        'python-dateutil>=2.8.1',
        
        # Dependencies for matplotlib and other packages
        'cycler>=0.10.0',
        'kiwisolver>=1.3.1',
        'pyparsing>=2.4.7',
        'six>=1.15.0',
    ],
    setup_requires=['pytest-runner', 'flake8'],
    tests_require=['pytest'],
    package_dir={'mrs':'mrs'},
    package_data={
        'mrs.3_0T_basis_threonine_no_MM': ['*.csv'],
        'mrs.Icons': ['*.png', '*.icns', '*.jpg'],
    },
    include_package_data=True,
    entry_points={
        'console_scripts': ['mrs=mrs.MRS_convert:main']
    }    

)
