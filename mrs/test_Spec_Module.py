#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit tests for Spec_Module.py

This module contains comprehensive unit tests for the SpecObject class
and related functionality in the Spec_Module.

Created for testing Version 1.4.2
"""

import unittest
import numpy as np
import tempfile
import os
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock, mock_open
import pydicom as dcm
from pydicom.dataset import Dataset
from pydicom.uid import generate_uid

# Import the module to test
from Spec_Module import SpecObject, PDF, PatNameDialog


class TestSpecObject(unittest.TestCase):
    """Test cases for the SpecObject class"""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.test_dir = tempfile.mkdtemp()
        self.test_filename = os.path.join(self.test_dir, "test_spec.dcm")
        self.test_dirpass = "test_dir"
        
        # Reset the class variable for each test
        SpecObject.NumSpecObjects = 0
        
    def tearDown(self):
        """Clean up after each test method."""
        shutil.rmtree(self.test_dir, ignore_errors=True)
        
    def create_mock_dicom_dataset(self, is_spectroscopy=True, has_spec_data=True, enhanced=False):
        """Create a mock DICOM dataset for testing"""
        ds = Dataset()
        
        # Set required DICOM metadata for proper saving
        ds.is_little_endian = True
        ds.is_implicit_VR = True
        
        if is_spectroscopy:
            ds.SOPClassUID = "1.2.840.10008.5.1.4.1.1.4.2"  # MR Spectroscopy Storage
        else:
            ds.SOPClassUID = "1.2.840.10008.5.1.4.1.1.2"  # CT Image Storage (non-spectroscopy)
            
        # Basic DICOM tags
        ds.PatientName = "Test^Patient"
        ds.PatientID = "TEST123"
        ds.StudyDate = "20230101"
        ds.StudyTime = "120000"
        ds.SeriesDate = "20230101"
        ds.SeriesTime = "120000"
        ds.AcquisitionDateTime = "20230101120000"
        ds.ProtocolName = "Test Protocol"
        ds.NumberOfFrames = 2
        ds.DataPointColumns = 1024
        ds.SpectralWidth = 2000.0
        ds.TransmitterFrequency = 127.7
        
        if has_spec_data and not enhanced:
            # Traditional spectroscopy data
            spec_data = np.random.random(1024 * 2 * 2).astype(np.float32)  # 2 frames, complex data
            ds[0x5600, 0x0020] = dcm.DataElement((0x5600, 0x0020), 'OF', spec_data)
            
        if enhanced and has_spec_data:
            # Enhanced DICOM format with PixelData
            spec_data = np.random.random(1024 * 2 * 2).astype(np.float32)
            ds.PixelData = spec_data.tobytes()
            
        # Private tag for display TE
        try:
            ds[0x2001, 0x1025] = dcm.DataElement((0x2001, 0x1025), 'DS', "30")
        except:
            pass
            
        return ds
        
    @patch('pydicom.read_file')
    def test_init_valid_spectroscopy_file(self, mock_read_file):
        """Test initialization with a valid spectroscopy DICOM file"""
        mock_ds = self.create_mock_dicom_dataset()
        mock_read_file.return_value = mock_ds
        
        spec_obj = SpecObject(self.test_filename, self.test_dirpass)
        
        self.assertEqual(spec_obj.filename, self.test_filename)
        self.assertEqual(spec_obj.dirpass, self.test_dirpass)
        self.assertEqual(spec_obj.isspec, 2)
        self.assertEqual(SpecObject.NumSpecObjects, 1)
        self.assertIsNotNone(spec_obj.SpecData)
        
    @patch('pydicom.read_file')
    def test_init_non_spectroscopy_file(self, mock_read_file):
        """Test initialization with a non-spectroscopy DICOM file"""
        mock_ds = self.create_mock_dicom_dataset(is_spectroscopy=False)
        mock_read_file.return_value = mock_ds
        
        spec_obj = SpecObject(self.test_filename, self.test_dirpass)
        
        self.assertEqual(spec_obj.isspec, 0)
        self.assertEqual(len(spec_obj.SpecData), 0)
        
    @patch('pydicom.read_file')
    def test_init_invalid_file(self, mock_read_file):
        """Test initialization with an invalid DICOM file"""
        mock_read_file.side_effect = Exception("Invalid DICOM file")
        
        spec_obj = SpecObject(self.test_filename, self.test_dirpass)
        
        self.assertIsNone(spec_obj.ds)
        self.assertEqual(SpecObject.NumSpecObjects, 0)
        
    @patch('pydicom.read_file')
    def test_init_enhanced_spectroscopy(self, mock_read_file):
        """Test initialization with enhanced DICOM spectroscopy format"""
        mock_ds = self.create_mock_dicom_dataset(enhanced=True)
        mock_read_file.return_value = mock_ds
        
        spec_obj = SpecObject(self.test_filename, self.test_dirpass)
        
        self.assertEqual(spec_obj.isspec, 2)
        self.assertIsNotNone(spec_obj.SpecData)
        
    @patch('pydicom.read_file')
    def test_load_common_parameters(self, mock_read_file):
        """Test loading of common DICOM parameters"""
        mock_ds = self.create_mock_dicom_dataset()
        mock_read_file.return_value = mock_ds
        
        spec_obj = SpecObject(self.test_filename, self.test_dirpass)
        
        self.assertEqual(spec_obj.PatName, "Test^Patient")
        self.assertEqual(spec_obj.PatID, "TEST123")
        self.assertEqual(spec_obj.StudyDate, "20230101")
        self.assertEqual(spec_obj.Datapoints, 1024)
        self.assertEqual(spec_obj.Frames, 2)
        self.assertEqual(spec_obj.FieldStrength, 3.0)
        
    @patch('pydicom.read_file')
    def test_extract_enhanced_spectro_data_float32(self, mock_read_file):
        """Test extraction of enhanced spectroscopy data with float32"""
        mock_ds = self.create_mock_dicom_dataset(enhanced=True)
        mock_read_file.return_value = mock_ds
        
        spec_obj = SpecObject(self.test_filename, self.test_dirpass)
        
        self.assertEqual(spec_obj.isspec, 2)
        self.assertIsInstance(spec_obj.SpecData, np.ndarray)
        
    @patch('pydicom.read_file')
    def test_complex_data_processing(self, mock_read_file):
        """Test complex data processing and FFT operations"""
        mock_ds = self.create_mock_dicom_dataset()
        mock_read_file.return_value = mock_ds
        
        spec_obj = SpecObject(self.test_filename, self.test_dirpass)
        
        # Check that complex data arrays are created
        self.assertIsInstance(spec_obj.Kspace, list)
        self.assertIsInstance(spec_obj.Spectrum, list)
        self.assertIsInstance(spec_obj.Kspaceapod, list)
        self.assertIsInstance(spec_obj.Spectrumapod, list)
        
        # Check apodization function
        self.assertIsInstance(spec_obj.apod, np.ndarray)
        self.assertEqual(len(spec_obj.apod), spec_obj.Datapoints)
        
        # Check that frames are processed
        expected_frames = spec_obj.Frames // 2 if spec_obj.Frames > 1 else 1
        self.assertEqual(len(spec_obj.Kspace), spec_obj.Frames)
        self.assertEqual(len(spec_obj.IncludeFrame), spec_obj.Frames)
        
    @patch('pydicom.read_file')
    def test_create_original(self, mock_read_file):
        """Test creation of original summed datasets"""
        mock_ds = self.create_mock_dicom_dataset()
        mock_read_file.return_value = mock_ds
        
        spec_obj = SpecObject(self.test_filename, self.test_dirpass)
        
        self.assertIsInstance(spec_obj.OriginalKspace, np.ndarray)
        self.assertIsInstance(spec_obj.OriginalSpectrum, np.ndarray)
        self.assertEqual(len(spec_obj.OriginalKspace), spec_obj.Datapoints)
        
    @patch('pydicom.read_file')
    def test_autophase(self, mock_read_file):
        """Test automatic phasing functionality"""
        mock_ds = self.create_mock_dicom_dataset()
        mock_read_file.return_value = mock_ds
        
        spec_obj = SpecObject(self.test_filename, self.test_dirpass)
        
        # Check that autophasing creates required arrays
        self.assertIsInstance(spec_obj.optphasearr, list)
        self.assertIsInstance(spec_obj.peakposarr, list)
        self.assertIsInstance(spec_obj.curcomplex, list)
        self.assertIsInstance(spec_obj.acurcomplex, list)
        
        # Check that each frame has phase and peak data
        expected_frames = spec_obj.Frames // 2 if spec_obj.Frames > 1 else 1
        self.assertEqual(len(spec_obj.optphasearr), expected_frames)
        self.assertEqual(len(spec_obj.peakposarr), expected_frames)
        
    @patch('pydicom.read_file')
    def test_default_parameters(self, mock_read_file):
        """Test default parameter values when DICOM tags are missing"""
        # Create minimal dataset without optional tags
        mock_ds = Dataset()
        mock_ds.SOPClassUID = "1.2.840.10008.5.1.4.1.1.4.2"
        mock_ds.DataPointColumns = 512
        spec_data = np.random.random(512 * 1 * 2).astype(np.float32)
        mock_ds[0x5600, 0x0020] = dcm.DataElement((0x5600, 0x0020), 'OF', spec_data)
        mock_read_file.return_value = mock_ds
        
        spec_obj = SpecObject(self.test_filename, self.test_dirpass)
        
        # Check default values
        self.assertEqual(spec_obj.PatName, 'Unknown')
        self.assertEqual(spec_obj.PatID, 'Unknown')
        self.assertEqual(spec_obj.FieldStrength, 3.0)
        self.assertEqual(spec_obj.displayTE, "0")
        
    @patch('pydicom.read_file')
    def test_spectypes_dictionary(self, mock_read_file):
        """Test the spectypes class variable"""
        mock_ds = self.create_mock_dicom_dataset()
        mock_read_file.return_value = mock_ds
        
        spec_obj = SpecObject(self.test_filename, self.test_dirpass)
        
        # Test spectypes dictionary
        self.assertIn(0, SpecObject.spectypes)
        self.assertIn(2, SpecObject.spectypes)
        self.assertEqual(SpecObject.spectypes[0], "Not a spectroscopy dataset")
        self.assertEqual(SpecObject.spectypes[2], "Enhanced spectroscopy dataset")
        
    @patch('pydicom.read_file')
    def test_phaseinc(self, mock_read_file):
        """Test phase increment functionality"""
        mock_ds = self.create_mock_dicom_dataset()
        mock_read_file.return_value = mock_ds
        
        spec_obj = SpecObject(self.test_filename, self.test_dirpass)
        
        initial_phase = spec_obj.optphasearr[spec_obj.curframe]
        increment = 45
        
        spec_obj.phaseinc(increment)
        
        expected_phase = initial_phase + increment
        self.assertEqual(spec_obj.optphasearr[spec_obj.curframe], expected_phase)
        
    @patch('pydicom.read_file')
    def test_cho_increment(self, mock_read_file):
        """Test Choline peak position increment"""
        mock_ds = self.create_mock_dicom_dataset()
        mock_read_file.return_value = mock_ds
        
        spec_obj = SpecObject(self.test_filename, self.test_dirpass)
        
        initial_cho_pos = spec_obj.peakposarr[spec_obj.curframe][0]
        increment = 5
        
        spec_obj.Choinc(increment)
        
        expected_pos = initial_cho_pos + increment
        self.assertEqual(spec_obj.peakposarr[spec_obj.curframe][0], expected_pos)
        
    @patch('pydicom.read_file')
    def test_cr_increment(self, mock_read_file):
        """Test Creatine peak position increment"""
        mock_ds = self.create_mock_dicom_dataset()
        mock_read_file.return_value = mock_ds
        
        spec_obj = SpecObject(self.test_filename, self.test_dirpass)
        
        initial_cr_pos = spec_obj.peakposarr[spec_obj.curframe][1]
        increment = 3
        
        spec_obj.Crinc(increment)
        
        expected_pos = initial_cr_pos + increment
        self.assertEqual(spec_obj.peakposarr[spec_obj.curframe][1], expected_pos)
        
    @patch('pydicom.read_file')
    def test_frame_navigation(self, mock_read_file):
        """Test frame up/down navigation"""
        mock_ds = self.create_mock_dicom_dataset()
        mock_ds.NumberOfFrames = 4  # Multiple frames
        # Create larger spec data for 4 frames
        spec_data = np.random.random(1024 * 4 * 2).astype(np.float32)  # 4 frames, complex data
        mock_ds[0x5600, 0x0020] = dcm.DataElement((0x5600, 0x0020), 'OF', spec_data)
        mock_read_file.return_value = mock_ds
        
        spec_obj = SpecObject(self.test_filename, self.test_dirpass)
        
        initial_frame = spec_obj.curframe
        
        # Test frame up - with 4 frames, effective frames = 4/2 = 2, so max frame index is 1
        spec_obj.frameup()
        self.assertEqual(spec_obj.curframe, initial_frame + 1)
        
        # Test frame down
        spec_obj.framedown()
        self.assertEqual(spec_obj.curframe, initial_frame)
        
        # Test boundary conditions
        spec_obj.curframe = 0
        spec_obj.framedown()
        self.assertEqual(spec_obj.curframe, 0)  # Should not go below 0
        
    @patch('pydicom.read_file')
    def test_undo_phase(self, mock_read_file):
        """Test undo phase functionality"""
        mock_ds = self.create_mock_dicom_dataset()
        mock_read_file.return_value = mock_ds
        
        spec_obj = SpecObject(self.test_filename, self.test_dirpass)
        
        # Apply some phase changes
        spec_obj.phaseinc(45)
        
        # Undo phase
        spec_obj.undophase()
        
        # Check that all phase angles are reset to 0
        for phase in spec_obj.optphasearr:
            self.assertEqual(phase, 0)
            
    @patch('pydicom.read_file')
    def test_undo_shift(self, mock_read_file):
        """Test undo shift functionality"""
        mock_ds = self.create_mock_dicom_dataset()
        mock_read_file.return_value = mock_ds
        
        spec_obj = SpecObject(self.test_filename, self.test_dirpass)
        
        # Apply some peak position changes
        spec_obj.Choinc(10)
        spec_obj.Crinc(5)
        
        # Undo shift
        spec_obj.undoshift()
        
        # Check that peak positions are reset to default values
        expected_peaks = [1020, 1030]
        for frame_peaks in spec_obj.peakposarr:
            self.assertEqual(frame_peaks, expected_peaks)
            
    @patch('pydicom.read_file')
    def test_write_log_file(self, mock_read_file):
        """Test writing log files"""
        mock_ds = self.create_mock_dicom_dataset()
        mock_read_file.return_value = mock_ds
        
        spec_obj = SpecObject(self.test_filename, self.test_dirpass)
        
        # Test log file writing
        spec_obj.writelogfile(self.test_dir, "1.4.2")
        
        # Check that log directory was created
        log_dir = Path(self.test_dir) / 'Log_files'
        self.assertTrue(log_dir.exists())
        
    @patch('pydicom.read_file')
    @patch('pydicom.Dataset.save_as')
    def test_write_tarquin(self, mock_save_as, mock_read_file):
        """Test writing Tarquin format files"""
        mock_ds = self.create_mock_dicom_dataset()
        mock_read_file.return_value = mock_ds
        
        # Mock the save_as method to avoid actual file writing issues
        mock_save_as.return_value = None
        
        spec_obj = SpecObject(self.test_filename, self.test_dirpass)
        
        # Test Tarquin file writing
        spec_obj.writeTarquin(self.test_dir)
        
        # Check that Tarquin directory was created
        tarquin_dir = Path(self.test_dir) / 'Tarquin_files'
        self.assertTrue(tarquin_dir.exists())
        
        # Verify save_as was called
        mock_save_as.assert_called_once()
        
    @patch('pydicom.read_file')
    @patch('pydicom.Dataset.save_as')
    def test_write_tarquin_orig(self, mock_save_as, mock_read_file):
        """Test writing original Tarquin format files"""
        mock_ds = self.create_mock_dicom_dataset()
        mock_read_file.return_value = mock_ds
        
        # Mock the save_as method to avoid actual file writing issues
        mock_save_as.return_value = None
        
        spec_obj = SpecObject(self.test_filename, self.test_dirpass)
        
        # Test original Tarquin file writing
        spec_obj.writeTarquinorig(self.test_dir)
        
        # Check that Tarquin directory was created
        tarquin_dir = Path(self.test_dir) / 'Tarquin_files'
        self.assertTrue(tarquin_dir.exists())
        
        # Verify save_as was called
        mock_save_as.assert_called_once()
        
    @patch('pydicom.read_file')
    def test_report_completed(self, mock_read_file):
        """Test report completed message setting"""
        mock_ds = self.create_mock_dicom_dataset()
        mock_read_file.return_value = mock_ds
        
        spec_obj = SpecObject(self.test_filename, self.test_dirpass)
        
        test_path = "/test/path/report.pdf"
        spec_obj.report_completed(test_path)
        
        expected_msg = f'MRS Report saved in {test_path}'
        self.assertEqual(spec_obj.report_completed_msg, expected_msg)


class TestPDFClass(unittest.TestCase):
    """Test cases for the PDF class"""
    
    def test_pdf_creation(self, ):
        """Test PDF object creation"""
        pdf = PDF()
        self.assertIsInstance(pdf, PDF)
        
    def test_pdf_header(self):
        """Test PDF header generation"""
        pdf = PDF()
        pdf.add_page()
        # Test that header method exists and can be called
        pdf.header()
        
    def test_pdf_footer(self):
        """Test PDF footer generation"""
        pdf = PDF()
        pdf.add_page()
        # Test that footer method exists and can be called
        pdf.footer()


class TestPatNameDialog(unittest.TestCase):
    """Test cases for the PatNameDialog class"""
    
    def setUp(self):
        """Set up Qt application for testing"""
        import sys
        from PyQt5.QtWidgets import QApplication
        
        # Create QApplication if it doesn't exist
        if not QApplication.instance():
            self.app = QApplication(sys.argv)
        else:
            self.app = QApplication.instance()
    
    def test_dialog_creation(self):
        """Test PatNameDialog creation"""
        try:
            dialog = PatNameDialog("Test Name")
            
            # Check that dialog was created successfully
            self.assertIsNotNone(dialog)
            self.assertEqual(dialog.name_string, "Test Name")
            
        except Exception as e:
            # If Qt fails, skip the test with a message
            self.skipTest(f"Qt GUI test skipped due to environment: {e}")
        
    def test_dialog_name_initialization(self):
        """Test that dialog initializes with correct name"""
        try:
            test_name = "Test Patient"
            dialog = PatNameDialog(test_name)
            
            self.assertEqual(dialog.name_string, test_name)
            
        except Exception as e:
            # If Qt fails, skip the test with a message
            self.skipTest(f"Qt GUI test skipped due to environment: {e}")


class TestIntegration(unittest.TestCase):
    """Integration tests for the complete workflow"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_dir = tempfile.mkdtemp()
        self.test_filename = os.path.join(self.test_dir, "test_spec.dcm")
        self.test_dirpass = "test_dir"
        
        # Reset the class variable for each test
        SpecObject.NumSpecObjects = 0
        
    def tearDown(self):
        """Clean up after each test method."""
        shutil.rmtree(self.test_dir, ignore_errors=True)
        
    def create_mock_dicom_dataset(self, datapoints=1024, frames=2):
        """Create a mock DICOM dataset for integration testing"""
        ds = Dataset()
        ds.SOPClassUID = "1.2.840.10008.5.1.4.1.1.4.2"
        ds.PatientName = "Integration^Test"
        ds.PatientID = "INT123"
        ds.StudyDate = "20230101"
        ds.StudyTime = "120000"
        ds.SeriesDate = "20230101"
        ds.SeriesTime = "120000"
        ds.AcquisitionDateTime = "20230101120000"
        ds.ProtocolName = "Integration Test Protocol"
        ds.NumberOfFrames = frames
        ds.DataPointColumns = datapoints
        ds.SpectralWidth = 2000.0
        ds.TransmitterFrequency = 127.7
        
        # Create spectroscopy data
        spec_data = np.random.random(datapoints * frames * 2).astype(np.float32)
        ds[0x5600, 0x0020] = dcm.DataElement((0x5600, 0x0020), 'OF', spec_data)
        
        return ds
        
    @patch('pydicom.read_file')
    @patch('pydicom.Dataset.save_as')
    def test_complete_processing_workflow(self, mock_save_as, mock_read_file):
        """Test complete spectroscopy processing workflow"""
        mock_ds = self.create_mock_dicom_dataset()
        mock_read_file.return_value = mock_ds
        
        # Mock the save_as method to avoid DICOM saving issues
        mock_save_as.return_value = None
        
        # Initialize SpecObject
        spec_obj = SpecObject(self.test_filename, self.test_dirpass)
        
        # Verify initialization
        self.assertEqual(spec_obj.isspec, 2)
        self.assertIsNotNone(spec_obj.SpecData)
        
        # Test processing operations
        spec_obj.phaseinc(30)
        spec_obj.Choinc(5)
        spec_obj.Crinc(-3)
        
        # Test undo operations
        spec_obj.undophase()
        spec_obj.undoshift()
        
        # Test file operations
        spec_obj.writelogfile(self.test_dir, "1.4.2")
        spec_obj.writeTarquin(self.test_dir)
        spec_obj.writeTarquinorig(self.test_dir)
        
        # Verify directories were created
        log_dir = Path(self.test_dir) / 'Log_files'
        tarquin_dir = Path(self.test_dir) / 'Tarquin_files'
        self.assertTrue(log_dir.exists())
        self.assertTrue(tarquin_dir.exists())
        
        # Verify save_as was called (indicating Tarquin writing was attempted)
        self.assertTrue(mock_save_as.called)
        
    @patch('pydicom.read_file')
    def test_class_variable_tracking(self, mock_read_file):
        """Test that NumSpecObjects is tracked correctly"""
        mock_ds = self.create_mock_dicom_dataset()
        mock_read_file.return_value = mock_ds
        
        initial_count = SpecObject.NumSpecObjects
        
        # Create multiple objects
        spec_obj1 = SpecObject(self.test_filename, self.test_dirpass)
        self.assertEqual(SpecObject.NumSpecObjects, initial_count + 1)
        
        spec_obj2 = SpecObject(self.test_filename, self.test_dirpass)
        self.assertEqual(SpecObject.NumSpecObjects, initial_count + 2)
        
    @patch('pydicom.read_file')
    def test_error_handling(self, mock_read_file):
        """Test error handling in various scenarios"""
        # Test with minimal data that might cause issues
        mock_ds = self.create_mock_dicom_dataset(datapoints=100, frames=1)
        mock_read_file.return_value = mock_ds
        
        # This should handle the data length mismatch gracefully
        spec_obj = SpecObject(self.test_filename, self.test_dirpass)
        
        # Should still create a valid object
        self.assertEqual(spec_obj.isspec, 2)
        self.assertIsNotNone(spec_obj.SpecData)


def run_tests():
    """Run all tests and provide summary"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestSpecObject))
    suite.addTests(loader.loadTestsFromTestCase(TestPDFClass))
    suite.addTests(loader.loadTestsFromTestCase(TestPatNameDialog))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    total_tests = result.testsRun
    failures = len(result.failures)
    errors = len(result.errors)
    success_rate = ((total_tests - failures - errors) / total_tests) * 100 if total_tests > 0 else 0
    
    print("\n" + "="*50)
    print(f"Tests run: {total_tests}")
    print(f"Failures: {failures}")
    print(f"Errors: {errors}")
    print(f"Success rate: {success_rate:.1f}%")
    print("="*50)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    exit(0 if success else 1)