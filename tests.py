"""
Unit tests for pyco.py calculator functions.

coverage run tests.py
coverage report -m
"""

import unittest
import sys
import io
from unittest.mock import patch, MagicMock
import pyco

class TestPycoUtilityFunctions(unittest.TestCase):
    """Test utility functions in pyco.py"""
    
    def test_find_comprehensive(self):
        """Comprehensive test of the find function with all patterns"""
        # Helper to check if a name is in results (results now include docstrings)
        def has_name(results, name):
            return any(r.startswith(name + ' - ') or r == name for r in results)
        
        # Test simple string search (original behavior)
        results = pyco.find('convert')
        self.assertTrue(has_name(results, 'convert'))
        
        # Test finding functions that contain 'avg'
        results = pyco.find('avg')
        self.assertTrue(has_name(results, 'avg'))
        
        # Test finding non-existent term
        results = pyco.find('nonexistent')
        self.assertEqual(results, [])
        
        # Test wildcard patterns
        # Prefix matching (starts with)
        results = pyco.find('f*')
        self.assertTrue(has_name(results, 'fabs'))
        self.assertTrue(has_name(results, 'factorial'))
        
        # Suffix matching (ends with)
        results = pyco.find('*an')
        self.assertTrue(has_name(results, 'atan'))
        self.assertTrue(has_name(results, 'mean'))
        
        # Contains matching (surrounded by *)
        results = pyco.find('*ex*')
        self.assertTrue(has_name(results, 'exp'))
        self.assertTrue(has_name(results, 'frexp'))
        
        # Test pattern that should match nothing
        results = pyco.find('*xyz*')
        self.assertEqual(results, [])
        
        # Test case insensitivity (extract just the names for comparison)
        def get_names(results):
            return set(r.split(' - ')[0] for r in results)
        
        results_lower = pyco.find('*convert*')
        results_upper = pyco.find('*CONVERT*')
        results_mixed = pyco.find('*Convert*')
        self.assertEqual(get_names(results_lower), get_names(results_upper))
        self.assertEqual(get_names(results_lower), get_names(results_mixed))
    
    def test_find_builtins(self):
        """Test that find() can find Python builtins"""
        # Helper to check if a name is in results (results now include docstrings)
        def has_name(results, name):
            return any(r.startswith(name + ' - ') or r == name for r in results)
        
        # Test finding builtins with simple search
        results = pyco.find('print')
        self.assertTrue(has_name(results, 'print'))
        
        results = pyco.find('len')
        self.assertTrue(has_name(results, 'len'))
        
        # Test finding builtins with wildcard patterns (use functions, not types)
        results = pyco.find('print*')
        self.assertTrue(has_name(results, 'print'))
        
        results = pyco.find('sum*')
        self.assertTrue(has_name(results, 'sum'))
        
        # Test finding builtins with suffix pattern
        results = pyco.find('*put')
        self.assertTrue(has_name(results, 'input'))
        
        # Test finding builtins with contains pattern (use functions, not types like range)
        results = pyco.find('*rand*')
        self.assertTrue(has_name(results, 'randint'))
    
    def test_find_includes_docstrings(self):
        """Test that find() includes docstring summaries in results"""
        # Test a builtin with a known docstring
        results = pyco.find('len')
        # Should have at least one result with a docstring
        has_docstring = any(' - ' in r for r in results)
        self.assertTrue(has_docstring, "find() should include docstring summaries")
        
        # Test that the format is "name - docstring summary"
        len_result = [r for r in results if r.startswith('len')][0]
        self.assertIn(' - ', len_result)
        
        # Test with wildcard pattern
        results = pyco.find('tan*')
        tan_results = [r for r in results if r.startswith('tan')]
        self.assertTrue(len(tan_results) > 0)
        # tanh should have its docstring
        tanh_result = [r for r in results if r.startswith('tanh')]
        if tanh_result:
            self.assertIn(' - ', tanh_result[0])
    
    def test_find_excludes_exceptions(self):
        """Test that find() excludes Python exceptions and errors from results"""
        # Test that common exceptions are not found
        results = pyco.find('*Error*')
        for result in results:
            # None of the results should be exception class names
            self.assertNotIn('ValueError', result)
            self.assertNotIn('TypeError', result)
            self.assertNotIn('KeyError', result)
            self.assertNotIn('PythonFinalizationError', result)
        
        # Test that searching for "Error" doesn't return exception classes
        results = pyco.find('Error')
        exception_names = ['ValueError', 'TypeError', 'KeyError', 'IndexError', 
                          'RuntimeError', 'AttributeError', 'NameError']
        for exc_name in exception_names:
            self.assertNotIn(exc_name, results, 
                           f"Exception '{exc_name}' should not appear in find() results")
        
        # Test that warnings are also excluded
        results = pyco.find('*Warning*')
        warning_names = ['UserWarning', 'DeprecationWarning', 'RuntimeWarning']
        for warn_name in warning_names:
            self.assertNotIn(warn_name, results,
                           f"Warning '{warn_name}' should not appear in find() results")
        
        # Test wildcard patterns also exclude exceptions
        results = pyco.find('*Exception*')
        self.assertNotIn('Exception', results)
        self.assertNotIn('BaseException', results)
    
    def test_find_searches_docstrings(self):
        """Test that find() searches within docstrings/definitions"""
        # Helper to check if a name is in results
        def has_name(results, name):
            return any(r.startswith(name + ' - ') or r == name for r in results)
        
        # Test finding by docstring content - 'hyperbolic' should find tanh, sinh, cosh
        results = pyco.find('hyperbolic')
        self.assertTrue(has_name(results, 'tanh'), 
                       "find('hyperbolic') should find tanh (docstring contains 'hyperbolic')")
        self.assertTrue(has_name(results, 'sinh'),
                       "find('hyperbolic') should find sinh (docstring contains 'hyperbolic')")
        self.assertTrue(has_name(results, 'cosh'),
                       "find('hyperbolic') should find cosh (docstring contains 'hyperbolic')")
        
        # Test finding by docstring with wildcard contains pattern
        results = pyco.find('*tangent*')
        # Should find atan, tanh etc because their docstrings contain 'tangent'
        self.assertTrue(has_name(results, 'atan') or has_name(results, 'tanh'),
                       "find('*tangent*') should find functions with 'tangent' in docstring")
        
        # Test that search term in docstring but not name still works
        results = pyco.find('cosine')
        self.assertTrue(has_name(results, 'acos') or has_name(results, 'cos'),
                       "find('cosine') should find cos/acos (docstring contains 'cosine')")
        
        # Test that prefix/suffix wildcards only match names, not docstrings
        results = pyco.find('hyper*')
        # Should NOT find tanh just because docstring starts with something
        # (prefix matching is name-only)
        self.assertFalse(has_name(results, 'tanh'),
                        "find('hyper*') should not match tanh (prefix is name-only)")
    
    def test_find_object_method_patterns(self):
        """Test the find function with object.method patterns"""
        # Helper to check if a name is in results (results now include docstrings)
        def has_name(results, name):
            return any(r.startswith(name + ' - ') or r == name for r in results)
        
        # Test math module methods starting with 's'
        results = pyco.find('math.s*')
        math_results = [r for r in results if r.startswith('math:')]
        self.assertTrue(len(math_results) > 0)
        
        # Check that sin and sqrt are included in math methods
        if math_results:
            methods_str = ' '.join(math_results)
            self.assertIn('sin', methods_str)
            self.assertIn('sqrt', methods_str)

        # Test object matching with different patterns
        # Note: simple 'math' search won't find 'math' module (modules are excluded)
        # but it may find functions with 'math' in their docstrings
        results = pyco.find('math')
        # The math module itself is excluded, but we should get some results
        # from functions that mention 'math' in their docstrings
        self.assertIsInstance(results, list)
        
        # Object.method patterns (these don't include docstrings, just method lists)
        test_patterns = [
            ['mat*.sin', ['math: sin']],   # starts with
            ['*ath.sin', ['math: sin']],   # ends with
            ['*math*.sin', ['math: sin']]  # contains
        ]
        
        for pattern in test_patterns:
            results = pyco.find(pattern[0])
            self.assertEqual(results, pattern[1])

        # Method patterns
        test_patterns = [
            ['math.si*', ['math: sin sinh']],   # starts with
            ['math.*in', ['math: asin sin']],   # ends with
            ['math.*sin*', ['math: asin asinh isinf sin sinh']]  # contains
        ]
        
        for pattern in test_patterns:
            results = pyco.find(pattern[0])
            self.assertEqual(results, pattern[1])

    def test_find_edge_cases(self):
        """Test edge cases and boundary conditions for the find function"""
        # Test empty string
        results = pyco.find('')
        self.assertIsInstance(results, list)
        
        # Test single asterisk (should return all globals)
        results = pyco.find('*')
        self.assertIsInstance(results, list)
        self.assertGreater(len(results), 0)
        
        # Test multiple asterisks
        results = pyco.find('***')
        self.assertIsInstance(results, list)
        
        # Test just a dot
        results = pyco.find('.')
        self.assertIsInstance(results, list)
        
        # Test pattern with dot but no object part
        results = pyco.find('.method*')
        self.assertIsInstance(results, list)
            
    def test_find_performance(self):
        """Test that wildcard searches complete in reasonable time"""
        import time
        
        # Test patterns that might be expensive
        expensive_patterns = [
            '*',      # Match everything
            '*a*',    # Very common letter
            '**',     # Double wildcards
            '*.*',    # All object.method patterns
        ]
        
        for pattern in expensive_patterns:
            start_time = time.time()
            results = pyco.find(pattern)
            end_time = time.time()
            
            # Should complete in under 1 second
            self.assertLess(end_time - start_time, 1.0, 
                          f"Pattern '{pattern}' took too long to execute")
            self.assertIsInstance(results, list)
    
    def test_find_excludes_underscore_prefix(self):
        """Test that find function excludes functions starting with underscore"""
        # Helper to extract name from result (results now include docstrings)
        def get_name(result):
            return result.split(' - ')[0]
        
        # Test direct search for underscore-prefixed functions should return empty
        underscore_results = pyco.find('_*')
        self.assertEqual(underscore_results, [], 
                        "find('_*') should return empty list - underscore functions should be excluded")
        
        # Test that functions containing but not starting with underscore are still found
        underscore_containing = pyco.find('*_*')
        underscore_starting = [get_name(r) for r in underscore_containing if get_name(r).startswith('_')]
        self.assertEqual(underscore_starting, [], 
                        "No functions starting with underscore should be in '*_*' search results")
        
        # Verify that some functions with underscores (but not starting) are found
        self.assertGreater(len(underscore_containing), 0, 
                          "Should find functions containing underscores (like geometric_mean)")
        
        # Test simple search for underscore should not return underscore-prefixed functions
        simple_underscore = pyco.find('_')
        underscore_prefixed = [get_name(r) for r in simple_underscore if get_name(r).startswith('_')]
        self.assertEqual(underscore_prefixed, [], 
                        "Simple underscore search should not return underscore-prefixed functions")
    
    def test_get_printable_char(self):
        """Test the get_printable_char function"""
        # Test printable ASCII characters
        self.assertEqual(pyco._get_printable_char(65), 'A')
        self.assertEqual(pyco._get_printable_char(97), 'a')
        self.assertEqual(pyco._get_printable_char(48), '0')
        self.assertEqual(pyco._get_printable_char(32), ' ')
        self.assertEqual(pyco._get_printable_char(126), '~')
        
        # Test non-printable characters (should return '.')
        self.assertEqual(pyco._get_printable_char(0), '.')
        self.assertEqual(pyco._get_printable_char(31), '.')
        self.assertEqual(pyco._get_printable_char(127), '.')
        self.assertEqual(pyco._get_printable_char(159), '.')
    
    @patch('builtins.input', side_effect=['1','2', ''])
    def test_inputlist(self, mock_input):
        """Test the inputlist function"""
        with patch('builtins.print'):  # Suppress print output
            result = pyco.inputlist()
        self.assertEqual(result, [1, 2])
    
    @patch('builtins.input', return_value='test')
    def test_tally(self, mock_input):
        """Test the tally function"""
        result = pyco.tally()
        self.assertEqual(result, 4)  # 'test' has 4 characters
    
    @patch('builtins.input', return_value='')
    def test_tally_empty(self, mock_input):
        """Test the tally function with empty input"""
        result = pyco.tally()
        self.assertEqual(result, 0)
    
    @patch('builtins.input', side_effect=['123', '45.67', 'invalid', ''])
    @patch('builtins.print')
    def test_inputlist_with_invalid_input(self, mock_print, mock_input):
        """Test inputlist function with invalid input that can't be converted to float"""
        # This should raise an exception when trying to convert 'invalid' to float
        with self.assertRaises(ValueError):
            pyco.inputlist()

    def test_human_large_numbers(self):
        """Test human function with large numbers"""
        # Test billions and trillions
        result = pyco.human(1234567890)
        expected = {'billion': 1, 'million': 234, 'thousand': 567, 'one': 890}
        self.assertEqual(result, expected)
        
        # Test exact units
        self.assertEqual(pyco.human(1000000000), {'billion': 1})
        self.assertEqual(pyco.human(1000000000000), {'trillion': 1})

    def test_human_edge_cases(self):
        """Test human function with edge cases"""
        # Test negative numbers (should use absolute value)
        result = pyco.human(-1234567)
        expected = {'million': 1, 'thousand': 234, 'one': 567}
        self.assertEqual(result, expected)
        
        # Test float inputs (should convert to int)
        result = pyco.human(1234567.89)
        expected = {'million': 1, 'thousand': 234, 'one': 567}
        self.assertEqual(result, expected)

    def test_human_small_numbers(self):
        """Test human function with small numbers"""
        # Test single digits
        for i in range(1, 10):
            self.assertEqual(pyco.human(i), {'one': i})
    
class TestPycoStatisticsFunctions(unittest.TestCase):
    """Test statistics functions in pyco.py"""
    
    def test_average(self):
        """Test the average function"""
        self.assertEqual(pyco.average([1, 2, 3, 4, 5]), 3.0)
        self.assertEqual(pyco.average([10, 20, 30]), 20.0)
        self.assertEqual(pyco.average([5]), 5.0)
        self.assertAlmostEqual(pyco.average([1.5, 2.5, 3.5]), 2.5)
    

class TestPycoTemperatureConversions(unittest.TestCase):
    """Test temperature conversion functions in pyco.py"""
    
    def test_convert_celsius_fahrenheit(self):
        """Test Celsius to Fahrenheit conversion"""
        self.assertEqual(pyco.convert('c', 'f', 0), 32.0)
        self.assertEqual(pyco.convert('c', 'f', 100), 212.0)
        self.assertEqual(pyco.convert('c', 'f', -40), -40.0)
        self.assertAlmostEqual(pyco.convert('c', 'f', 37), 98.6)
    
    def test_convert_fahrenheit_celsius(self):
        """Test Fahrenheit to Celsius conversion"""
        self.assertEqual(pyco.convert('f', 'c', 32), 0.0)
        self.assertEqual(pyco.convert('f', 'c', 212), 100.0)
        self.assertEqual(pyco.convert('f', 'c', -40), -40.0)
        self.assertAlmostEqual(pyco.convert('f', 'c', 98.6), 37.0)

class TestPycoDistanceConversions(unittest.TestCase):
    """Test distance conversion functions in pyco.py"""
    
    def test_convert_miles_kilometers(self):
        """Test miles to kilometers conversion"""
        self.assertAlmostEqual(pyco.convert('mi', 'km', 1), 1.609344)
        self.assertAlmostEqual(pyco.convert('mi', 'km', 0), 0.0)
        self.assertAlmostEqual(pyco.convert('mi', 'km', 5), 8.04672)
    

    
    def test_convert_kilometers_miles(self):
        """Test kilometers to miles conversion"""
        self.assertAlmostEqual(pyco.convert('km', 'mi', 1.609344), 1.0)
        self.assertAlmostEqual(pyco.convert('km', 'mi', 0), 0.0)
        self.assertAlmostEqual(pyco.convert('km', 'mi', 8.04672), 5.0)
    

    
    def test_convert_miles_feet(self):
        """Test miles to feet conversion"""
        self.assertAlmostEqual(pyco.convert('mi', 'ft', 1), 5280, places=10)
        self.assertEqual(pyco.convert('mi', 'ft', 0), 0)
        self.assertAlmostEqual(pyco.convert('mi', 'ft', 0.5), 2640, places=10)
    

    
    def test_convert_feet_miles(self):
        """Test feet to miles conversion"""
        self.assertAlmostEqual(pyco.convert('ft', 'mi', 5280), 1.0, places=10)
        self.assertEqual(pyco.convert('ft', 'mi', 0), 0.0)
        self.assertAlmostEqual(pyco.convert('ft', 'mi', 2640), 0.5, places=10)
    

    
    def test_convert_inches_feet(self):
        """Test inches to feet conversion"""
        self.assertEqual(pyco.convert('in', 'ft', 12), 1.0)
        self.assertEqual(pyco.convert('in', 'ft', 0), 0.0)
        self.assertEqual(pyco.convert('in', 'ft', 24), 2.0)
        self.assertEqual(pyco.convert('in', 'ft', 6), 0.5)
    
    def test_convert_feet_inches(self):
        """Test feet to inches conversion"""
        self.assertEqual(pyco.convert('ft', 'in', 1), 12)
        self.assertEqual(pyco.convert('ft', 'in', 0), 0)
        self.assertEqual(pyco.convert('ft', 'in', 2), 24)
        self.assertEqual(pyco.convert('ft', 'in', 0.5), 6)
    
    def test_convert_feet_centimeters(self):
        """Test feet to centimeters conversion"""
        self.assertAlmostEqual(pyco.convert('ft', 'cm', 1), 30.48)
        self.assertAlmostEqual(pyco.convert('ft', 'cm', 0), 0.0)
        self.assertAlmostEqual(pyco.convert('ft', 'cm', 2), 60.96)
        self.assertAlmostEqual(pyco.convert('ft', 'cm', 0.5), 15.24)

    def test_convert_feet_millimeters(self):
        """Test feet to millimeters conversion"""
        self.assertAlmostEqual(pyco.convert('ft', 'mm', 1), 304.8)
        self.assertAlmostEqual(pyco.convert('ft', 'mm', 0), 0.0)
        self.assertAlmostEqual(pyco.convert('ft', 'mm', 2), 609.6)
        self.assertAlmostEqual(pyco.convert('ft', 'mm', 0.5), 152.4)  
    
    def test_convert_feet_meters(self):
        """Test feet to meters conversion"""
        self.assertAlmostEqual(pyco.convert('ft', 'm', 3), 0.9144)
        self.assertAlmostEqual(pyco.convert('ft', 'm', 0), 0.0)
        self.assertAlmostEqual(pyco.convert('ft', 'm', 1), 0.3048)

    

    
    def test_convert_inches_centimeters(self):
        """Test inches to centimeters conversion"""
        self.assertAlmostEqual(pyco.convert('in', 'cm', 1), 2.54)
        self.assertAlmostEqual(pyco.convert('in', 'cm', 0), 0.0)
        self.assertAlmostEqual(pyco.convert('in', 'cm', 12), 30.48)
        self.assertAlmostEqual(pyco.convert('in', 'cm', 6), 15.24)
    
    def test_convert_centimeters_inches(self):
        """Test centimeters to inches conversion"""
        self.assertAlmostEqual(pyco.convert('cm', 'in', 2.54), 1.0)
        self.assertAlmostEqual(pyco.convert('cm', 'in', 0), 0.0)
        self.assertAlmostEqual(pyco.convert('cm', 'in', 30.48), 12.0)
        self.assertAlmostEqual(pyco.convert('cm', 'in', 15.24), 6.0)
    
class TestPycoWeightConversions(unittest.TestCase):
    """Test weight conversion functions in pyco.py"""
    
    def test_convert_pounds_kilograms(self):
        """Test pounds to kilograms conversion"""
        self.assertAlmostEqual(pyco.convert('lb', 'kg', 1), 0.453592)
        self.assertAlmostEqual(pyco.convert('lb', 'kg', 0), 0.0)
        self.assertAlmostEqual(pyco.convert('lb', 'kg', 2.20462), 1.0, places=5)
        self.assertAlmostEqual(pyco.convert('lb', 'kg', 100), 45.3592)
    
    def test_convert_kilograms_pounds(self):
        """Test kilograms to pounds conversion"""
        self.assertAlmostEqual(pyco.convert('kg', 'lb', 0.453592), 1.0)
        self.assertAlmostEqual(pyco.convert('kg', 'lb', 0), 0.0)
        self.assertAlmostEqual(pyco.convert('kg', 'lb', 1), 2.20462, places=5)
        self.assertAlmostEqual(pyco.convert('kg', 'lb', 45.3592), 100.0)
    
class TestPycoVolumeConversions(unittest.TestCase):
    """Test volume conversion functions in pyco.py"""
    
    def test_convert_ounces_milliliters(self):
        """Test fluid ounces to milliliters conversion"""
        self.assertAlmostEqual(pyco.convert('floz', 'ml', 1), 29.5735)
        self.assertAlmostEqual(pyco.convert('floz', 'ml', 0), 0.0)
        self.assertAlmostEqual(pyco.convert('floz', 'ml', 8), 236.588)
        self.assertAlmostEqual(pyco.convert('floz', 'ml', 0.5), 14.78675)
    
    def test_convert_milliliters_ounces(self):
        """Test milliliters to fluid ounces conversion"""
        self.assertAlmostEqual(pyco.convert('ml', 'floz', 29.5735), 1.0)
        self.assertAlmostEqual(pyco.convert('ml', 'floz', 0), 0.0)
        self.assertAlmostEqual(pyco.convert('ml', 'floz', 236.588), 8.0)
        self.assertAlmostEqual(pyco.convert('ml', 'floz', 14.78675), 0.5)
    
    def test_convert_cups_ounces(self):
        """Test cups to fluid ounces conversion"""
        self.assertEqual(pyco.convert('cup', 'floz', 1), 8)
        self.assertEqual(pyco.convert('cup', 'floz', 0), 0)
        self.assertEqual(pyco.convert('cup', 'floz', 2), 16)
        self.assertEqual(pyco.convert('cup', 'floz', 0.5), 4)
    
    def test_convert_ounces_cups(self):
        """Test fluid ounces to cups conversion"""
        self.assertEqual(pyco.convert('floz', 'cup', 8), 1.0)
        self.assertEqual(pyco.convert('floz', 'cup', 0), 0.0)
        self.assertEqual(pyco.convert('floz', 'cup', 16), 2.0)
        self.assertEqual(pyco.convert('floz', 'cup', 4), 0.5)
    
    def test_convert_cups_milliliters(self):
        """Test cups to milliliters conversion"""
        self.assertAlmostEqual(pyco.convert('cup', 'ml', 1), 236.588)
        self.assertAlmostEqual(pyco.convert('cup', 'ml', 0), 0.0)
        self.assertAlmostEqual(pyco.convert('cup', 'ml', 2), 473.176)
        self.assertAlmostEqual(pyco.convert('cup', 'ml', 0.5), 118.294)
    
    def test_convert_milliliters_cups(self):
        """Test milliliters to cups conversion"""
        self.assertAlmostEqual(pyco.convert('ml', 'cup', 236.588), 1.0)
        self.assertAlmostEqual(pyco.convert('ml', 'cup', 0), 0.0)
        self.assertAlmostEqual(pyco.convert('ml', 'cup', 473.176), 2.0)
        self.assertAlmostEqual(pyco.convert('ml', 'cup', 118.294), 0.5)
    
class TestPycoSpeedConversions(unittest.TestCase):
    """Test speed conversion functions in pyco.py"""
    
    def test_convert_mph_kph(self):
        """Test miles per hour to kilometers per hour conversion"""
        self.assertAlmostEqual(pyco.convert('mph', 'kph', 1), 1.609344)
        self.assertAlmostEqual(pyco.convert('mph', 'kph', 0), 0.0)
        self.assertAlmostEqual(pyco.convert('mph', 'kph', 60), 96.56064)
        self.assertAlmostEqual(pyco.convert('mph', 'kph', 100), 160.9344)
    
    def test_convert_kph_mph(self):
        """Test kilometers per hour to miles per hour conversion"""
        self.assertAlmostEqual(pyco.convert('kph', 'mph', 1.609344), 1.0)
        self.assertAlmostEqual(pyco.convert('kph', 'mph', 0), 0.0)
        self.assertAlmostEqual(pyco.convert('kph', 'mph', 96.5606), 60.0, places=4)
        self.assertAlmostEqual(pyco.convert('kph', 'mph', 160.9344), 100.0)
    
    def test_convert_knots_mph(self):
        """Test knots to miles per hour conversion"""
        self.assertAlmostEqual(pyco.convert('kn', 'mph', 1), 1.15078)
        self.assertAlmostEqual(pyco.convert('kn', 'mph', 0), 0.0)
        self.assertAlmostEqual(pyco.convert('kn', 'mph', 10), 11.5078)
        self.assertAlmostEqual(pyco.convert('kn', 'mph', 100), 115.078)
    
    def test_convert_mph_knots(self):
        """Test miles per hour to knots conversion"""
        self.assertAlmostEqual(pyco.convert('mph', 'kn', 1.15078), 1.0)
        self.assertAlmostEqual(pyco.convert('mph', 'kn', 0), 0.0)
        self.assertAlmostEqual(pyco.convert('mph', 'kn', 11.5078), 10.0, places=4)
        self.assertAlmostEqual(pyco.convert('mph', 'kn', 115.078), 100.0, places=4)
    
    def test_convert_knots_kph(self):
        """Test knots to kilometers per hour conversion"""
        self.assertAlmostEqual(pyco.convert('kn', 'kph', 1), 1.852)
        self.assertAlmostEqual(pyco.convert('kn', 'kph', 0), 0.0)
        self.assertAlmostEqual(pyco.convert('kn', 'kph', 10), 18.52)
        self.assertAlmostEqual(pyco.convert('kn', 'kph', 100), 185.2)
    
    def test_convert_kph_knots(self):
        """Test kilometers per hour to knots conversion"""
        self.assertAlmostEqual(pyco.convert('kph', 'kn', 1.852), 1.0)
        self.assertAlmostEqual(pyco.convert('kph', 'kn', 0), 0.0)
        self.assertAlmostEqual(pyco.convert('kph', 'kn', 18.52), 10.0, places=4)
        self.assertAlmostEqual(pyco.convert('kph', 'kn', 185.2), 100.0, places=4)
    
    def test_convert_mph_mps(self):
        """Test miles per hour to meters per second conversion"""
        self.assertAlmostEqual(pyco.convert('mph', 'mps', 1), 0.44704)
        self.assertAlmostEqual(pyco.convert('mph', 'mps', 0), 0.0)
        self.assertAlmostEqual(pyco.convert('mph', 'mps', 60), 26.8224)
        self.assertAlmostEqual(pyco.convert('mph', 'mps', 100), 44.704)
    
    def test_convert_mps_mph(self):
        """Test meters per second to miles per hour conversion"""
        self.assertAlmostEqual(pyco.convert('mps', 'mph', 0.44704), 1.0)
        self.assertAlmostEqual(pyco.convert('mps', 'mph', 0), 0.0)
        self.assertAlmostEqual(pyco.convert('mps', 'mph', 26.8224), 60.0, places=4)
        self.assertAlmostEqual(pyco.convert('mps', 'mph', 44.704), 100.0, places=4)
    
    def test_convert_kph_mps(self):
        """Test kilometers per hour to meters per second conversion"""
        self.assertAlmostEqual(pyco.convert('kph', 'mps', 1), 0.277778, places=6)
        self.assertAlmostEqual(pyco.convert('kph', 'mps', 0), 0.0)
        self.assertAlmostEqual(pyco.convert('kph', 'mps', 36), 10.0, places=3)
        self.assertAlmostEqual(pyco.convert('kph', 'mps', 100), 27.7778, places=4)
    
    def test_convert_mps_kph(self):
        """Test meters per second to kilometers per hour conversion"""
        self.assertAlmostEqual(pyco.convert('mps', 'kph', 0.277778), 1.0, places=5)
        self.assertAlmostEqual(pyco.convert('mps', 'kph', 0), 0.0)
        self.assertAlmostEqual(pyco.convert('mps', 'kph', 10), 36.0, places=4)
        self.assertAlmostEqual(pyco.convert('mps', 'kph', 27.7778), 100.0, places=3)
    
class TestPycoTimeConversions(unittest.TestCase):
    """Test time conversion functions"""
    
    def test_hours_minutes_conversion(self):
        """Test hours to minutes conversion"""
        self.assertAlmostEqual(pyco.convert('h', 'min', 1), 60, places=5)
        self.assertAlmostEqual(pyco.convert('h', 'min', 2.5), 150, places=5)
        self.assertAlmostEqual(pyco.convert('min', 'h', 60), 1, places=5)
        self.assertAlmostEqual(pyco.convert('min', 'h', 90), 1.5, places=5)
    
    def test_minutes_seconds_conversion(self):
        """Test minutes to seconds conversion"""
        self.assertAlmostEqual(pyco.convert('min', 's', 1), 60, places=5)
        self.assertAlmostEqual(pyco.convert('min', 's', 1.5), 90, places=5)
        self.assertAlmostEqual(pyco.convert('s', 'min', 60), 1, places=5)
        self.assertAlmostEqual(pyco.convert('s', 'min', 120), 2, places=5)
    
    def test_hours_seconds_conversion(self):
        """Test hours to seconds conversion"""
        self.assertAlmostEqual(pyco.convert('h', 's', 1), 3600, places=5)
        self.assertAlmostEqual(pyco.convert('h', 's', 0.5), 1800, places=5)
        self.assertAlmostEqual(pyco.convert('s', 'h', 3600), 1, places=5)
        self.assertAlmostEqual(pyco.convert('s', 'h', 7200), 2, places=5)
    
    def test_days_hours_conversion(self):
        """Test days to hours conversion"""
        self.assertAlmostEqual(pyco.convert('d', 'h', 1), 24, places=5)
        self.assertAlmostEqual(pyco.convert('d', 'h', 2.5), 60, places=5)
        self.assertAlmostEqual(pyco.convert('h', 'd', 24), 1, places=5)
        self.assertAlmostEqual(pyco.convert('h', 'd', 48), 2, places=5)
    
    def test_weeks_days_conversion(self):
        """Test weeks to days conversion"""
        self.assertAlmostEqual(pyco.convert('wk', 'd', 1), 7, places=5)
        self.assertAlmostEqual(pyco.convert('wk', 'd', 2), 14, places=5)
        self.assertAlmostEqual(pyco.convert('d', 'wk', 7), 1, places=5)
        self.assertAlmostEqual(pyco.convert('d', 'wk', 14), 2, places=5)
    
    def test_years_days_conversion(self):
        """Test years to days conversion (accounting for leap years)"""
        self.assertAlmostEqual(pyco.convert('yr', 'd', 1), 365.25, places=5)
        self.assertAlmostEqual(pyco.convert('yr', 'd', 4), 1461, places=5)
        self.assertAlmostEqual(pyco.convert('d', 'yr', 365.25), 1, places=5)
        self.assertAlmostEqual(pyco.convert('d', 'yr', 730.5), 2, places=5)
    
class TestPycoAdditionalWeightConversions(unittest.TestCase):
    """Test additional weight conversion functions"""
    
    def test_ounces_grams_conversion(self):
        """Test ounces to grams conversion"""
        self.assertAlmostEqual(pyco.convert('oz', 'g', 1), 28.3495, places=4)
        self.assertAlmostEqual(pyco.convert('oz', 'g', 16), 453.592, places=3)
        self.assertAlmostEqual(pyco.convert('g', 'oz', 28.3495), 1, places=4)
        self.assertAlmostEqual(pyco.convert('g', 'oz', 100), 3.52740, places=4)
    
    def test_grams_pounds_conversion(self):
        """Test grams to pounds conversion"""
        self.assertAlmostEqual(pyco.convert('g', 'lb', 453.592), 1, places=3)
        self.assertAlmostEqual(pyco.convert('g', 'lb', 1000), 2.20462, places=4)
        self.assertAlmostEqual(pyco.convert('lb', 'g', 1), 453.592, places=3)
        self.assertAlmostEqual(pyco.convert('lb', 'g', 2.2), 997.902, places=2)
    
    def test_ounces_pounds_conversion(self):
        """Test ounces to pounds conversion"""
        self.assertAlmostEqual(pyco.convert('oz', 'lb', 16), 1, places=5)
        self.assertAlmostEqual(pyco.convert('oz', 'lb', 8), 0.5, places=5)
        self.assertAlmostEqual(pyco.convert('lb', 'oz', 1), 16, places=5)
        self.assertAlmostEqual(pyco.convert('lb', 'oz', 2.5), 40, places=5)
    
    def test_grams_kilograms_conversion(self):
        """Test grams to kilograms conversion"""
        self.assertAlmostEqual(pyco.convert('g', 'kg', 1000), 1, places=5)
        self.assertAlmostEqual(pyco.convert('g', 'kg', 500), 0.5, places=5)
        self.assertAlmostEqual(pyco.convert('kg', 'g', 1), 1000, places=5)
        self.assertAlmostEqual(pyco.convert('kg', 'g', 2.5), 2500, places=5)
    
    def test_tons_pounds_conversion(self):
        """Test US tons to pounds conversion"""
        self.assertAlmostEqual(pyco.convert('t', 'lb', 1), 2000, places=5)
        self.assertAlmostEqual(pyco.convert('t', 'lb', 0.5), 1000, places=5)
        self.assertAlmostEqual(pyco.convert('lb', 't', 2000), 1, places=5)
        self.assertAlmostEqual(pyco.convert('lb', 't', 4000), 2, places=5)
    
    def test_stone_pounds_conversion(self):
        """Test stone to pounds conversion"""
        self.assertAlmostEqual(pyco.convert('st', 'lb', 1), 14, places=5)
        self.assertAlmostEqual(pyco.convert('st', 'lb', 10), 140, places=5)
        self.assertAlmostEqual(pyco.convert('lb', 'st', 14), 1, places=5)
        self.assertAlmostEqual(pyco.convert('lb', 'st', 28), 2, places=5)
    
class TestPycoAdditionalVolumeConversions(unittest.TestCase):
    """Test additional volume conversion functions"""
    
    def test_gallons_liters_conversion(self):
        """Test US gallons to liters conversion"""
        self.assertAlmostEqual(pyco.convert('gal', 'l', 1), 3.78541, places=4)
        self.assertAlmostEqual(pyco.convert('gal', 'l', 5), 18.9271, places=3)
        self.assertAlmostEqual(pyco.convert('l', 'gal', 3.78541), 1, places=4)
        self.assertAlmostEqual(pyco.convert('l', 'gal', 10), 2.64172, places=4)
    
    def test_quarts_liters_conversion(self):
        """Test US quarts to liters conversion"""
        self.assertAlmostEqual(pyco.convert('qt', 'l', 1), 0.946353, places=5)
        self.assertAlmostEqual(pyco.convert('qt', 'l', 4), 3.78541, places=4)
        self.assertAlmostEqual(pyco.convert('l', 'qt', 0.946353), 1, places=5)
        self.assertAlmostEqual(pyco.convert('l', 'qt', 2), 2.11338, places=4)
    
    def test_pints_liters_conversion(self):
        """Test US pints to liters conversion"""
        self.assertAlmostEqual(pyco.convert('pt', 'l', 1), 0.473176, places=5)
        self.assertAlmostEqual(pyco.convert('pt', 'l', 2), 0.946353, places=5)
        self.assertAlmostEqual(pyco.convert('l', 'pt', 0.473176), 1, places=5)
        self.assertAlmostEqual(pyco.convert('l', 'pt', 1), 2.11338, places=4)
    
    def test_tablespoons_teaspoons_conversion(self):
        """Test tablespoons to teaspoons conversion"""
        self.assertAlmostEqual(pyco.convert('tbsp', 'tsp', 1), 3, places=5)
        self.assertAlmostEqual(pyco.convert('tbsp', 'tsp', 2), 6, places=5)
        self.assertAlmostEqual(pyco.convert('tsp', 'tbsp', 3), 1, places=5)
        self.assertAlmostEqual(pyco.convert('tsp', 'tbsp', 6), 2, places=5)
    
    def test_tablespoons_milliliters_conversion(self):
        """Test tablespoons to milliliters conversion"""
        self.assertAlmostEqual(pyco.convert('tbsp', 'ml', 1), 14.7868, places=4)
        self.assertAlmostEqual(pyco.convert('tbsp', 'ml', 2), 29.5736, places=3)
        self.assertAlmostEqual(pyco.convert('ml', 'tbsp', 14.7868), 1, places=4)
        self.assertAlmostEqual(pyco.convert('ml', 'tbsp', 30), 2.02884, places=4)
    
    def test_teaspoons_milliliters_conversion(self):
        """Test teaspoons to milliliters conversion"""
        self.assertAlmostEqual(pyco.convert('tsp', 'ml', 1), 4.92892, places=4)
        self.assertAlmostEqual(pyco.convert('tsp', 'ml', 3), 14.7868, places=4)
        self.assertAlmostEqual(pyco.convert('ml', 'tsp', 4.92892), 1, places=4)
        self.assertAlmostEqual(pyco.convert('ml', 'tsp', 15), 3.04326, places=4)
    
class TestPycoAdditionalTemperatureConversions(unittest.TestCase):
    """Test additional temperature conversion functions"""
    
    def test_kelvin_celsius_conversion(self):
        """Test Kelvin to Celsius conversion"""
        self.assertAlmostEqual(pyco.convert('k', 'c', 273.15), 0, places=2)
        self.assertAlmostEqual(pyco.convert('k', 'c', 373.15), 100, places=2)
        self.assertAlmostEqual(pyco.convert('c', 'k', 0), 273.15, places=2)
        self.assertAlmostEqual(pyco.convert('c', 'k', 100), 373.15, places=2)
    
    def test_kelvin_fahrenheit_conversion(self):
        """Test Kelvin to Fahrenheit conversion"""
        self.assertAlmostEqual(pyco.convert('k', 'f', 273.15), 32, places=2)
        self.assertAlmostEqual(pyco.convert('k', 'f', 373.15), 212, places=2)
        self.assertAlmostEqual(pyco.convert('f', 'k', 32), 273.15, places=2)
        self.assertAlmostEqual(pyco.convert('f', 'k', 212), 373.15, places=2)
    
class TestPycoAreaConversions(unittest.TestCase):
    """Test area conversion functions"""
    
    def test_square_feet_square_meters_conversion(self):
        """Test square feet to square meters conversion"""
        self.assertAlmostEqual(pyco.convert('ft2', 'm2', 1), 0.092903, places=5)
        self.assertAlmostEqual(pyco.convert('ft2', 'm2', 100), 9.2903, places=4)
        self.assertAlmostEqual(pyco.convert('m2', 'ft2', 1), 10.7639, places=4)
        self.assertAlmostEqual(pyco.convert('m2', 'ft2', 10), 107.639, places=3)
    
    def test_acres_square_feet_conversion(self):
        """Test acres to square feet conversion"""
        self.assertAlmostEqual(pyco.convert('ac', 'ft2', 1), 43560, places=1)
        self.assertAlmostEqual(pyco.convert('ac', 'ft2', 0.5), 21780, places=1)
        self.assertAlmostEqual(pyco.convert('ft2', 'ac', 43560), 1, places=5)
        self.assertAlmostEqual(pyco.convert('ft2', 'ac', 87120), 2, places=5)
    
    def test_square_inches_square_centimeters_conversion(self):
        """Test square inches to square centimeters conversion"""
        self.assertAlmostEqual(pyco.convert('in2', 'cm2', 1), 6.4516, places=4)
        self.assertAlmostEqual(pyco.convert('in2', 'cm2', 10), 64.516, places=3)
        self.assertAlmostEqual(pyco.convert('cm2', 'in2', 6.4516), 1, places=4)
        self.assertAlmostEqual(pyco.convert('cm2', 'in2', 20), 3.10001, places=4)
    
class TestPycoPowerConversions(unittest.TestCase):
    """Test power conversion functions"""
    
    def test_watts_horsepower_conversion(self):
        """Test watts to horsepower conversion"""
        self.assertAlmostEqual(pyco.convert('w', 'hp', 745.7), 1, places=4)
        self.assertAlmostEqual(pyco.convert('w', 'hp', 1491.4), 2, places=3)
        self.assertAlmostEqual(pyco.convert('hp', 'w', 1), 745.7, places=1)
        self.assertAlmostEqual(pyco.convert('hp', 'w', 2), 1491.4, places=1)
    
class TestPycoMultiStepConversions(unittest.TestCase):
    """Test multi-step conversions using the new dynamic programming system"""
    
    def test_indirect_conversions(self):
        """Test conversions that require multiple steps through intermediate units"""
        # Test miles to inches via feet (miles -> feet -> inches)
        self.assertAlmostEqual(pyco.convert('mi', 'in', 1), 63360, places=5)
        
        # Test grams to ounces via pounds (grams -> pounds -> ounces)
        self.assertAlmostEqual(pyco.convert('g', 'oz', 453.592), 16, places=5)
        
        # Test hours to years via days (hours -> days -> years)
        self.assertAlmostEqual(pyco.convert('h', 'yr', 8760), 0.999315537303217, places=10)
        
        # Test complex path: square inches to square meters via square feet
        # (square_inches -> square_feet -> square_meters)
        self.assertAlmostEqual(pyco.convert('in2', 'm2', 144), 0.092903, places=5)
    
    def test_same_unit_conversion(self):
        """Test that converting a unit to itself returns the same value"""
        self.assertEqual(pyco.convert('mi', 'mi', 5), 5)
        self.assertEqual(pyco.convert('c', 'c', 25), 25)
        self.assertEqual(pyco.convert('lb', 'lb', 10), 10)
    
    def test_invalid_conversion_path(self):
        """Test that invalid conversion paths return None with helpful messages"""
        # Invalid units now return None instead of raising ValueError
        result1 = pyco.convert('nonexistent_unit', 'mi', 5)
        self.assertIsNone(result1)
        
        result2 = pyco.convert('mi', 'nonexistent_unit', 5)
        self.assertIsNone(result2)
    
    def test_matrix_non_redundancy(self):
        """Test that the conversion matrix has no redundant entries except for function-based conversions"""
        # Verify that each unit pair appears at most once in the matrix
        # Exception: Temperature conversions use functions in both directions
        seen_pairs = set()
        for (unit1, unit2), factor_or_func in pyco._CONVERSION_MATRIX.items():
            # Skip function-based conversions (like temperature) which need bidirectional entries
            if callable(factor_or_func):
                continue
                
            # Normalize the pair order to check for duplicates
            normalized_pair = tuple(sorted([unit1, unit2]))
            self.assertNotIn(normalized_pair, seen_pairs, 
                           f"Redundant entry found for {unit1}-{unit2}")
            seen_pairs.add(normalized_pair)

class TestPycoConstants(unittest.TestCase):
    """Test constants defined in pyco.py"""
    
    def test_byte_constants(self):
        """Test byte size constants"""
        self.assertEqual(pyco.kb, 1024)
        self.assertEqual(pyco.mb, 1024 * 1024)
        self.assertEqual(pyco.gb, 1024 * 1024 * 1024)
        self.assertEqual(pyco.tb, 1024 * 1024 * 1024 * 1024)

    def test_large_number_constants(self):
        """Test that large number constants have correct values."""
        self.assertEqual(pyco.thousand, 1000)
        self.assertEqual(pyco.million, 1000000)
        self.assertEqual(pyco.billion, 1000000000)
        self.assertEqual(pyco.trillion, 1000000000000)

class TestPycoConversionChains(unittest.TestCase):
    """Test conversion chains to ensure mathematical consistency"""
    
    def test_temperature_conversion_chain(self):
        """Test that temperature conversions are mathematically consistent"""
        # Test C -> F -> C
        celsius = 25.0
        fahrenheit = pyco.convert('c', 'f', celsius)
        back_to_celsius = pyco.convert('f', 'c', fahrenheit)
        self.assertAlmostEqual(celsius, back_to_celsius, places=10)
        
        # Test F -> C -> F
        fahrenheit = 77.0
        celsius = pyco.convert('f', 'c', fahrenheit)
        back_to_fahrenheit = pyco.convert('c', 'f', celsius)
        self.assertAlmostEqual(fahrenheit, back_to_fahrenheit, places=10)
    
    def test_distance_conversion_chain(self):
        """Test that distance conversions are mathematically consistent"""
        # Test miles -> km -> miles
        miles = 10.0
        kilometers = pyco.convert('mi', 'km', miles)
        back_to_miles = pyco.convert('km', 'mi', kilometers)
        self.assertAlmostEqual(miles, back_to_miles, places=10)
        
        # Test miles -> feet -> miles
        miles = 2.0
        feet = pyco.convert('mi', 'ft', miles)
        back_to_miles = pyco.convert('ft', 'mi', feet)
        self.assertAlmostEqual(miles, back_to_miles, places=10)
        
        # Test feet -> inches -> feet
        feet = 3.0
        inches = pyco.convert('ft', 'in', feet)
        back_to_feet = pyco.convert('in', 'ft', inches)
        self.assertAlmostEqual(feet, back_to_feet, places=10)
        

        
        # Test inches -> centimeters -> inches
        inches = 12.0
        centimeters = pyco.convert('in', 'cm', inches)
        back_to_inches = pyco.convert('cm', 'in', centimeters)
        self.assertAlmostEqual(inches, back_to_inches, places=10)
    
    def test_weight_conversion_chain(self):
        """Test that weight conversions are mathematically consistent"""
        # Test pounds -> kg -> pounds
        pounds = 150.0
        kilograms = pyco.convert('lb', 'kg', pounds)
        back_to_pounds = pyco.convert('kg', 'lb', kilograms)
        self.assertAlmostEqual(pounds, back_to_pounds, places=10)
    
    def test_volume_conversion_chain(self):
        """Test that volume conversions are mathematically consistent"""
        # Test ounces -> milliliters -> ounces
        ounces = 16.0
        milliliters = pyco.convert('floz', 'ml', ounces)
        back_to_ounces = pyco.convert('ml', 'floz', milliliters)
        self.assertAlmostEqual(ounces, back_to_ounces, places=10)
        
        # Test cups -> ounces -> cups
        cups = 2.0
        ounces = pyco.convert('cup', 'floz', cups)
        back_to_cups = pyco.convert('floz', 'cup', ounces)
        self.assertAlmostEqual(cups, back_to_cups, places=10)
        
        # Test cups -> milliliters -> cups
        cups = 3.0
        milliliters = pyco.convert('cup', 'ml', cups)
        back_to_cups = pyco.convert('ml', 'cup', milliliters)
        self.assertAlmostEqual(cups, back_to_cups, places=10)
    
    def test_speed_conversion_chain(self):
        """Test that speed conversions are mathematically consistent"""
        # Test mph -> kph -> mph
        mph = 60.0
        kph = pyco.convert('mph', 'kph', mph)
        back_to_mph = pyco.convert('kph', 'mph', kph)
        self.assertAlmostEqual(mph, back_to_mph, places=10)
        
        # Test knots -> mph -> knots
        knots = 100.0
        mph = pyco.convert('kn', 'mph', knots)
        back_to_knots = pyco.convert('mph', 'kn', mph)
        self.assertAlmostEqual(knots, back_to_knots, places=10)
        
        # Test knots -> kph -> knots
        knots = 50.0
        kph = pyco.convert('kn', 'kph', knots)
        back_to_knots = pyco.convert('kph', 'kn', kph)
        self.assertAlmostEqual(knots, back_to_knots, places=10)
        
        # Test mph -> mps -> mph
        mph = 100.0
        mps = pyco.convert('mph', 'mps', mph)
        back_to_mph = pyco.convert('mps', 'mph', mps)
        self.assertAlmostEqual(mph, back_to_mph, places=10)
        
        # Test kph -> mps -> kph
        kph = 72.0
        mps = pyco.convert('kph', 'mps', kph)
        back_to_kph = pyco.convert('mps', 'kph', mps)
        self.assertAlmostEqual(kph, back_to_kph, places=10)

class TestPycoEdgeCases(unittest.TestCase):
    """Test edge cases and error conditions"""
    
    def test_zero_conversions(self):
        """Test conversions with zero values"""
        self.assertEqual(pyco.convert('c', 'f', 0), 32.0)
        self.assertAlmostEqual(pyco.convert('f', 'c', 0), -17.77777777777778, places=13)
        self.assertEqual(pyco.convert('mi', 'km', 0), 0.0)
        self.assertEqual(pyco.convert('km', 'mi', 0), 0.0)
        self.assertEqual(pyco.convert('mi', 'ft', 0), 0)
        self.assertEqual(pyco.convert('ft', 'mi', 0), 0.0)
        self.assertEqual(pyco.convert('in', 'ft', 0), 0.0)
        self.assertEqual(pyco.convert('ft', 'in', 0), 0)
        # New conversion functions
        self.assertEqual(pyco.convert('ft', 'cm', 0), 0.0)
        self.assertEqual(pyco.convert('ft', 'm', 0), 0.0)
        self.assertEqual(pyco.convert('in', 'cm', 0), 0.0)
        self.assertEqual(pyco.convert('cm', 'in', 0), 0.0)
        self.assertEqual(pyco.convert('lb', 'kg', 0), 0.0)
        self.assertEqual(pyco.convert('kg', 'lb', 0), 0.0)
        self.assertEqual(pyco.convert('floz', 'ml', 0), 0.0)
        self.assertEqual(pyco.convert('ml', 'floz', 0), 0.0)
        self.assertEqual(pyco.convert('cup', 'floz', 0), 0)
        self.assertEqual(pyco.convert('floz', 'cup', 0), 0.0)
        self.assertEqual(pyco.convert('cup', 'ml', 0), 0.0)
        self.assertEqual(pyco.convert('ml', 'cup', 0), 0.0)
        # Speed conversion functions
        self.assertEqual(pyco.convert('mph', 'kph', 0), 0.0)
        self.assertEqual(pyco.convert('kph', 'mph', 0), 0.0)
        self.assertEqual(pyco.convert('kn', 'mph', 0), 0.0)
        self.assertEqual(pyco.convert('mph', 'kn', 0), 0.0)
        self.assertEqual(pyco.convert('kn', 'kph', 0), 0.0)
        self.assertEqual(pyco.convert('kph', 'kn', 0), 0.0)
        self.assertEqual(pyco.convert('mph', 'mps', 0), 0.0)
        self.assertEqual(pyco.convert('mps', 'mph', 0), 0.0)
        self.assertEqual(pyco.convert('kph', 'mps', 0), 0.0)
        self.assertEqual(pyco.convert('mps', 'kph', 0), 0.0)
    
    def test_negative_conversions(self):
        """Test conversions with negative values"""
        self.assertEqual(pyco.convert('c', 'f', -10), 14.0)
        self.assertAlmostEqual(pyco.convert('f', 'c', -10), -23.333333333333332, places=13)
        self.assertEqual(pyco.convert('mi', 'km', -5), -8.04672)
        self.assertEqual(pyco.convert('km', 'mi', -8.04672), -5.0)
        # New conversion functions with negative values
        self.assertAlmostEqual(pyco.convert('ft', 'cm', -3), -91.44)
        self.assertAlmostEqual(pyco.convert('in', 'cm', -6), -15.24)
        self.assertAlmostEqual(pyco.convert('cm', 'in', -15.24), -6.0)
        # Weight and volume with negative values (though physically meaningless)
        self.assertAlmostEqual(pyco.convert('lb', 'kg', -10), -4.53592)
        self.assertAlmostEqual(pyco.convert('kg', 'lb', -5), -11.0231221)
        self.assertAlmostEqual(pyco.convert('floz', 'ml', -8), -236.588)
        self.assertAlmostEqual(pyco.convert('ml', 'floz', -236.588), -8.0)
        self.assertEqual(pyco.convert('cup', 'floz', -2), -16)
        self.assertEqual(pyco.convert('floz', 'cup', -16), -2.0)
        # Speed conversions with negative values (though physically meaningless for speeds)
        self.assertAlmostEqual(pyco.convert('mph', 'kph', -60), -96.56064)
        self.assertAlmostEqual(pyco.convert('kph', 'mph', -100), -62.1371, places=4)
        self.assertAlmostEqual(pyco.convert('kn', 'mph', -10), -11.5078)
        self.assertAlmostEqual(pyco.convert('mph', 'kn', -115.078), -100.0, places=4)
        self.assertAlmostEqual(pyco.convert('kn', 'kph', -50), -92.6)
        self.assertAlmostEqual(pyco.convert('kph', 'kn', -185.2), -100.0, places=4)
        self.assertAlmostEqual(pyco.convert('mph', 'mps', -60), -26.8224)
        self.assertAlmostEqual(pyco.convert('mps', 'mph', -44.704), -100.0, places=4)
        self.assertAlmostEqual(pyco.convert('kph', 'mps', -36), -10.0, places=3)
        self.assertAlmostEqual(pyco.convert('mps', 'kph', -10), -36.0, places=4)
    
    def test_large_number_conversions(self):
        """Test conversions with large numbers"""
        large_num = 1000000.0
        
        # Test that large numbers don't cause overflow
        result = pyco.convert('c', 'f', large_num)
        self.assertIsInstance(result, float)
        self.assertGreater(result, large_num)
        
        result = pyco.convert('mi', 'km', large_num)
        self.assertIsInstance(result, float)
        self.assertGreater(result, large_num)
        
        # Test new conversion functions with large numbers
        result = pyco.convert('ft', 'cm', large_num)
        self.assertIsInstance(result, float)
        self.assertGreater(result, large_num)
        
        result = pyco.convert('lb', 'kg', large_num)
        self.assertIsInstance(result, float)
        self.assertLess(result, large_num)  # kg is smaller unit
        
        result = pyco.convert('floz', 'ml', large_num)
        self.assertIsInstance(result, float)
        self.assertGreater(result, large_num)
        
        # Test speed conversion functions with large numbers
        result = pyco.convert('mph', 'kph', large_num)
        self.assertIsInstance(result, float)
        self.assertGreater(result, large_num)
        
        result = pyco.convert('kn', 'mph', large_num)
        self.assertIsInstance(result, float)
        self.assertGreater(result, large_num)
        
        result = pyco.convert('mph', 'mps', large_num)
        self.assertIsInstance(result, float)
        self.assertLess(result, large_num)  # m/s is smaller unit than mph

class TestPycoAliases(unittest.TestCase):
    """Test that all aliases work correctly"""
    
class TestPycoWildcardSearch(unittest.TestCase):
    """Test wildcard search functionality in the find function"""
       
    def test_object_method_wildcard_search(self):
        """Test wildcard search for object methods"""
        # Test finding math functions starting with 's'
        results = pyco.find('math.s*')
        math_results = [r for r in results if r.startswith('math:')]
        self.assertTrue(len(math_results) > 0)
        
        # Verify common math functions are found
        if math_results:
            methods_str = ' '.join(math_results)
            self.assertIn('sin', methods_str)
            self.assertIn('sqrt', methods_str)
    
    def test_wildcard_boundary_conditions(self):
        """Test boundary conditions for wildcard patterns"""
        # Test single character patterns
        results = pyco.find('*c*')
        self.assertGreater(len(results), 0)  # Should find many functions containing 'c'
        
        # Helper to check if a name is in results (results now include docstrings)
        def has_name(results, name):
            return any(r.startswith(name + ' - ') or r == name for r in results)
        
        # Test very specific patterns
        results = pyco.find('avg')
        self.assertTrue(has_name(results, 'avg'))
        
        results = pyco.find('*avg*')
        self.assertTrue(has_name(results, 'avg'))
    
    def test_no_match_patterns(self):
        """Test patterns that should return no matches"""
        # Test patterns that shouldn't match anything
        no_match_patterns = [
            '*xyz123*',
            'nonexistent*',
            '*nonexistent',
            'xyz.abc*',
            '*impossible*function*'
        ]
        
        for pattern in no_match_patterns:
            results = pyco.find(pattern)
            self.assertEqual(results, [], f"Pattern '{pattern}' should return no matches")
    
class TestPycoAsciiTable(unittest.TestCase):
    """Test the asciitable and related functions"""
    
    @patch('builtins.input', side_effect=['', '', '', ''])
    @patch('builtins.print')
    def test_asciitable_output_format(self, mock_print, mock_input):
        """Test that asciitable produces the correct output format"""
        # Call asciitable function
        pyco.asciitable()
        
        # Get all the print calls
        print_calls = [call.args[0] for call in mock_print.call_args_list]
        
        # Find the header line
        header_found = False
        row_40_found = False
        
        for call in print_calls:
            if "Dec Hx C | Dec Hx C | Dec Hx C | Dec Hx C" in str(call):
                header_found = True
            # Look for the line with characters 40-43 (the 11th row)
            if " 40 28 ( |  41 29 ) |  42 2A * |  43 2B +" in str(call):
                row_40_found = True
        
        self.assertTrue(header_found, "ASCII table header not found in output")
        self.assertTrue(row_40_found, "Row 40-43 not found with correct formatting")
    
    @patch('builtins.input', side_effect=['', '', ''])  # Multiple empty inputs to continue
    @patch('builtins.print')
    def test_asciitable_pagination(self, mock_print, mock_input):
        """Test that asciitable handles pagination correctly"""
        # Call asciitable function
        pyco.asciitable()
        
        # Get all the print calls
        print_calls = [call.args[0] for call in mock_print.call_args_list]
        
        # Should have multiple header lines due to pagination
        header_count = sum(1 for call in print_calls if "Dec Hx C | Dec Hx C | Dec Hx C | Dec Hx C" in str(call))
        self.assertGreater(header_count, 1, "Should have multiple headers due to pagination")

class TestPycoDisplayHook(unittest.TestCase):
    """Test the display hook functionality"""
    
    def test_displayhook_callable_function(self):
        """Test displayhook with callable functions"""
        # Test that displayhook calls functions when they're callable
        def test_function():
            return "test_result"
        
        # Mock the original displayhook to capture calls
        with patch('sys.__displayhook__') as mock_displayhook:
            pyco._displayhook(test_function)
            # Should call the function and pass result to original displayhook
            mock_displayhook.assert_called_once_with("test_result")
    
    def test_displayhook_non_callable_value(self):
        """Test displayhook with non-callable values"""
        # Test that displayhook passes non-callable values directly
        test_value = "not_callable"
        
        with patch('sys.__displayhook__') as mock_displayhook:
            pyco._displayhook(test_value)
            # Should pass the value directly to original displayhook
            mock_displayhook.assert_called_once_with(test_value)
    
    def test_displayhook_with_lambda(self):
        """Test displayhook with lambda functions"""
        test_lambda = lambda: 42
        
        with patch('sys.__displayhook__') as mock_displayhook:
            pyco._displayhook(test_lambda)
            # Should call the lambda and pass result to original displayhook
            mock_displayhook.assert_called_once_with(42)

class TestPycoExceptionHandlerCoverage(unittest.TestCase):
    """Test exception handler code coverage"""
    
    def test_exception_handler_non_syntax_error(self):
        """Test exception handler with non-SyntaxError exceptions"""
        # Test that non-SyntaxError exceptions are passed through
        with patch('sys.__excepthook__') as mock_excepthook:
            pyco._my_except_hook(ValueError, ValueError("test"), None)
            # Should pass through to original exception handler
            mock_excepthook.assert_called_once()
    
    def test_exception_handler_syntax_error_no_wildcards(self):
        """Test exception handler with SyntaxError that doesn't have wildcards"""
        # Create a mock SyntaxError without wildcards
        mock_error = MagicMock()
        mock_error.text = "normal_syntax_error"
        mock_error.strip.return_value = "normal_syntax_error"
        
        with patch('sys.__excepthook__') as mock_excepthook:
            pyco._my_except_hook(SyntaxError, mock_error, None)
            # Should pass through to original exception handler
            mock_excepthook.assert_called_once_with(SyntaxError, mock_error, None)
    
    @patch('builtins.print')
    def test_exception_handler_wildcard_no_results(self, mock_print):
        """Test exception handler with wildcard pattern that returns no results"""
        # Create a mock SyntaxError with wildcard that won't match anything
        mock_error = MagicMock()
        mock_error.text.strip.return_value = "nonexistent_xyz*"
        
        pyco._my_except_hook(SyntaxError, mock_error, None)
        
        # Should print "No matches found."
        mock_print.assert_called_with("No matches found.")
    
    @patch('builtins.print')
    def test_exception_handler_wildcard_with_results(self, mock_print):
        """Test exception handler with wildcard pattern that returns results"""
        # Create a mock SyntaxError with wildcard that will match
        mock_error = MagicMock()
        mock_error.text.strip.return_value = "convert*"
        
        pyco._my_except_hook(SyntaxError, mock_error, None)
        
        # Should print each result
        self.assertTrue(mock_print.called)
        # Check that some conversion functions were printed
        print_calls = [str(call) for call in mock_print.call_args_list]
        found_convert = any("convert" in call for call in print_calls)
        self.assertTrue(found_convert, "Should print conversion functions")

class TestPycoCategoryConversions(unittest.TestCase):
    """Generic test that validates all conversions within each category automatically"""
    
    def test_all_category_conversions(self):
        """Test that every unit in each category can convert to all other units in that category"""
        categories = pyco._get_all_categories()
        
        for category in categories:
            with self.subTest(category=category):
                units = pyco._get_units_by_category(category)
                
                # Skip categories with only one unit
                if len(units) <= 1:
                    continue
                
                # Test all pairs of units within the category
                for from_unit in units:
                    for to_unit in units:
                        if from_unit == to_unit:
                            continue
                        
                        with self.subTest(from_unit=from_unit, to_unit=to_unit):
                            try:
                                # Test conversion with a reasonable test value
                                test_value = 1.0 if category != 'temperature' else 0.0
                                result = pyco.convert(from_unit, to_unit, test_value)
                                
                                # Verify the result is a number
                                self.assertIsInstance(result, (int, float), 
                                    f"Conversion from {from_unit} to {to_unit} should return a number")
                                
                                # For non-temperature conversions, verify round-trip accuracy
                                if category != 'temperature':
                                    # Convert back and check if we get approximately the original value
                                    back_result = pyco.convert(to_unit, from_unit, result)
                                    # Use relative tolerance for floating-point comparison
                                    relative_error = abs((test_value - back_result) / test_value) if test_value != 0 else abs(back_result)
                                    self.assertLess(relative_error, 1e-5,
                                        msg=f"Round-trip conversion {from_unit} -> {to_unit} -> {from_unit} failed. "
                                            f"Expected: {test_value}, Got: {back_result}, Relative error: {relative_error}")
                                
                            except ValueError as e:
                                self.fail(f"No conversion path from {from_unit} to {to_unit} in category {category}: {e}")
                            except Exception as e:
                                self.fail(f"Unexpected error converting {from_unit} to {to_unit}: {e}")
    
    def test_category_completeness(self):
        """Test that all categories have at least 2 units and form connected graphs"""
        categories = pyco._get_all_categories()
        
        for category in categories:
            with self.subTest(category=category):
                units = pyco._get_units_by_category(category)
                
                if category == 'unknown':
                    continue  # Skip unknown category
                
                # Each category should have at least 2 units to be meaningful
                self.assertGreaterEqual(len(units), 2, 
                    f"Category {category} should have at least 2 units, found: {units}")
                
                # Test that the category forms a connected graph
                # (every unit can reach every other unit through some path)
                base_unit = units[0]
                for target_unit in units[1:]:
                    try:
                        test_value = 1.0 if category != 'temperature' else 0.0
                        pyco.convert(base_unit, target_unit, test_value)
                    except ValueError:
                        self.fail(f"Units in category {category} are not fully connected: "
                                f"cannot convert {base_unit} to {target_unit}")

class TestPycoUnitNames(unittest.TestCase):
    """Test unit name mapping and Units function"""
    
    def test_unit_names_completeness(self):
        """Test that UNIT_NAMES contains all units from the conversion matrix and no extras"""
        # Get all units from the conversion matrix
        matrix_units = set()
        for (unit1, unit2), _ in pyco._CONVERSION_MATRIX.items():
            # Extract unit names from category.unit format
            if '.' in unit1:
                matrix_units.add(pyco._get_unit_name(unit1))
            if '.' in unit2:
                matrix_units.add(pyco._get_unit_name(unit2))
        
        # Add temperature units (handled separately)
        matrix_units.update(['c', 'f', 'k'])
        
        # Get units from UNIT_NAMES dictionary
        unit_names_keys = set(pyco._UNIT_NAMES.keys())
        
        # Check that all matrix units have names
        missing_names = matrix_units - unit_names_keys
        self.assertEqual(missing_names, set(), 
                        f"UNIT_NAMES missing definitions for: {missing_names}")
        
        # Check that no extra names exist
        extra_names = unit_names_keys - matrix_units
        self.assertEqual(extra_names, set(),
                        f"UNIT_NAMES has extra definitions for: {extra_names}")
        
        # Verify exact match
        self.assertEqual(matrix_units, unit_names_keys,
                        "UNIT_NAMES should contain exactly the same units as the conversion matrix")
    
    def test_unit_names_not_empty(self):
        """Test that all unit names are non-empty strings"""
        for unit, name in pyco._UNIT_NAMES.items():
            self.assertIsInstance(name, str, f"Name for unit '{unit}' should be a string")
            self.assertTrue(len(name) > 0, f"Name for unit '{unit}' should not be empty")
            self.assertNotEqual(name.strip(), '', f"Name for unit '{unit}' should not be just whitespace")
    
    def test_unit_names_format(self):
        """Test that unit names follow expected formatting"""
        for unit, name in pyco._UNIT_NAMES.items():
            # Names should be lowercase except for proper nouns (Celsius, Fahrenheit, Kelvin)
            if unit not in ['c', 'f', 'k']:  # Temperature units use short names now
                self.assertEqual(name, name.lower(), 
                               f"Unit name for '{unit}' should be lowercase: '{name}'")
            
            # Names should not start or end with whitespace
            self.assertEqual(name, name.strip(), 
                           f"Unit name for '{unit}' should not have leading/trailing whitespace")
    
    def test_units_function_exists(self):
        """Test that the units function exists and is callable"""
        self.assertTrue(hasattr(pyco, 'units'), "pyco should have a units function")
        self.assertTrue(callable(pyco.units), "units should be callable")
    
    def test_units_function_output(self):
        """Test that the units function produces expected output"""
        # Capture stdout to test the output and mock input for paging
        captured_output = io.StringIO()
        with patch('sys.stdout', captured_output), patch('builtins.input', return_value=''):
            pyco.units()
        
        output = captured_output.getvalue()
        
        # Check that output contains expected sections with new compact format
        self.assertIn("AREA:", output)
        self.assertIn("DISTANCE:", output) 
        self.assertIn("POWER:", output)
        self.assertIn("SPEED:", output)
        self.assertIn("TEMPERATURE:", output)
        self.assertIn("TIME:", output)
        self.assertIn("VOLUME:", output)
        self.assertIn("WEIGHT:", output)
        
        # Check that specific units and their full names appear
        self.assertIn("cm", output)
        self.assertIn("centimeters", output)
        self.assertIn("c", output)  # Temperature units now use short names
        self.assertIn("Celsius", output)
        self.assertIn("kg", output)
        self.assertIn("kilograms", output)
        self.assertIn("ft", output)
        self.assertIn("feet", output)
        
        # Verify the output stays within width limit (each line should be <= 37 chars)
        lines = output.split('\n')
        for line in lines:
            if line.strip() and not line.startswith('='):  # Skip empty lines and header
                self.assertLessEqual(len(line), 37, f"Line too long: '{line}' ({len(line)} chars)")
    
    def test_temperature_units_handling(self):
        """Test that temperature units are properly handled in UNIT_NAMES"""
        # Temperature units should be present with short names
        self.assertIn('c', pyco._UNIT_NAMES)
        self.assertIn('f', pyco._UNIT_NAMES)
        self.assertIn('k', pyco._UNIT_NAMES)
        
        # Temperature unit names should be capitalized (proper nouns)
        self.assertEqual(pyco._UNIT_NAMES['c'], 'Celsius')
        self.assertEqual(pyco._UNIT_NAMES['f'], 'Fahrenheit')
        self.assertEqual(pyco._UNIT_NAMES['k'], 'Kelvin')

class TestPycoCaseInsensitive(unittest.TestCase):
    """Test case insensitive functionality of the convert function"""
    
    def test_case_insensitive_distance_conversions(self):
        """Test distance conversions with various case combinations"""
        # Test all uppercase
        self.assertAlmostEqual(pyco.convert('MI', 'KM', 1), 1.609344)
        self.assertAlmostEqual(pyco.convert('KM', 'MI', 1.609344), 1.0)
        
        # Test mixed case
        self.assertAlmostEqual(pyco.convert('Mi', 'Km', 1), 1.609344)
        self.assertAlmostEqual(pyco.convert('Ft', 'In', 1), 12.0)
        
        # Test lowercase (should still work)
        self.assertAlmostEqual(pyco.convert('cm', 'in', 2.54), 1.0)
    
    def test_case_insensitive_temperature_conversions(self):
        """Test temperature conversions with various case combinations"""
        # Test all uppercase
        self.assertEqual(pyco.convert('C', 'F', 0), 32.0)
        self.assertEqual(pyco.convert('F', 'C', 32), 0.0)
        
        # Test mixed case
        self.assertEqual(pyco.convert('c', 'f', 0), 32.0)
        self.assertEqual(pyco.convert('f', 'c', 32), 0.0)
        
        # Test with Kelvin
        self.assertAlmostEqual(pyco.convert('K', 'c', 273.15), 0.0, places=2)
    
    def test_case_insensitive_weight_conversions(self):
        """Test weight conversions with various case combinations"""
        # Test all uppercase
        self.assertAlmostEqual(pyco.convert('LB', 'KG', 1), 0.453592)
        self.assertAlmostEqual(pyco.convert('G', 'OZ', 1000), 35.274, places=2)
        
        # Test mixed case
        self.assertAlmostEqual(pyco.convert('Lb', 'Kg', 2.20462), 1.0, places=4)
    
    def test_case_insensitive_volume_conversions(self):
        """Test volume conversions with various case combinations"""
        # Test all uppercase
        self.assertEqual(pyco.convert('CUP', 'FLOZ', 1), 8.0)
        self.assertAlmostEqual(pyco.convert('ML', 'L', 1000), 1.0)
        
        # Test mixed case
        self.assertEqual(pyco.convert('Cup', 'Floz', 2), 16.0)
    
    def test_case_insensitive_power_conversions(self):
        """Test power conversions with various case combinations"""
        # Test uppercase W (should map to lowercase w internally)
        self.assertAlmostEqual(pyco.convert('W', 'HP', 745.7), 1, places=4)
        self.assertAlmostEqual(pyco.convert('HP', 'W', 1), 745.7, places=1)
    
    def test_case_insensitive_same_unit(self):
        """Test that same units with different cases return the original value"""
        self.assertEqual(pyco.convert('KM', 'km', 5), 5)
        self.assertEqual(pyco.convert('c', 'C', 25), 25)
        self.assertEqual(pyco.convert('W', 'w', 100), 100)

class TestPycoUnitAbbreviationConflicts(unittest.TestCase):
    """Test that there are no conflicting unit abbreviations across categories"""
    
    def test_no_duplicate_abbreviations(self):
        """Test that each unit abbreviation is unique across all categories"""
        # Get all external unit names from the conversion matrix
        external_units = set()
        mapping = pyco._get_external_to_internal_mapping()
        
        # Add all external unit names from the mapping
        for external_name in mapping.keys():
            external_units.add(external_name)
        
        # Add temperature units (handled separately)
        external_units.update(['c', 'f', 'k'])
        
        # Convert to list to check for duplicates
        unit_list = list(external_units)
        unique_units = set(unit_list)
        
        # Check that no duplicates exist
        self.assertEqual(len(unit_list), len(unique_units), 
                        f"Duplicate unit abbreviations found: {[unit for unit in unit_list if unit_list.count(unit) > 1]}")
    
    def test_no_case_insensitive_conflicts(self):
        """Test that unit abbreviations don't conflict when case is ignored"""
        # Get all external unit names
        external_units = set()
        mapping = pyco._get_external_to_internal_mapping()
        
        # Add all external unit names from the mapping
        for external_name in mapping.keys():
            external_units.add(external_name)
        
        # Add temperature units (handled separately)
        external_units.update(['c', 'f', 'k'])
        
        # Check for case-insensitive conflicts
        lowercase_units = {}
        conflicts = []
        
        for unit in external_units:
            unit_lower = unit.lower()
            if unit_lower in lowercase_units:
                conflicts.append(f"'{lowercase_units[unit_lower]}' and '{unit}' conflict when case-insensitive")
            else:
                lowercase_units[unit_lower] = unit
        
        self.assertEqual(len(conflicts), 0, 
                        f"Case-insensitive conflicts found: {conflicts}")
    
    def test_unit_names_coverage_matches_available_units(self):
        """Test that UNIT_NAMES dictionary covers exactly the available units"""
        # Get all external unit names from conversion system
        external_units = set()
        mapping = pyco._get_external_to_internal_mapping()
        
        # Add all external unit names from the mapping
        for external_name in mapping.keys():
            external_units.add(external_name)
        
        # Add temperature units (handled separately)
        external_units.update(['c', 'f', 'k'])
        
        # Get all units from UNIT_NAMES dictionary
        unit_names_keys = set(pyco._UNIT_NAMES.keys())
        
        # Check that they match exactly
        missing_from_unit_names = external_units - unit_names_keys
        extra_in_unit_names = unit_names_keys - external_units
        
        self.assertEqual(len(missing_from_unit_names), 0,
                        f"Units missing from UNIT_NAMES: {missing_from_unit_names}")
        self.assertEqual(len(extra_in_unit_names), 0,
                        f"Extra units in UNIT_NAMES: {extra_in_unit_names}")
    
    def test_conversion_matrix_symmetry(self):
        """Test that conversion matrix doesn't have conflicting bidirectional entries"""
        conflicts = []
        
        for (unit1, unit2), factor1 in pyco._CONVERSION_MATRIX.items():
            # Check if reverse entry exists
            if (unit2, unit1) in pyco._CONVERSION_MATRIX:
                factor2 = pyco._CONVERSION_MATRIX[(unit2, unit1)]
                
                # Skip function-based conversions (like temperature) as they have explicit bidirectional entries
                if callable(factor1) or callable(factor2):
                    continue
                    
                expected_factor2 = 1 / factor1
                
                # Allow small floating point errors
                if abs(factor2 - expected_factor2) > 1e-10:
                    conflicts.append(f"Inconsistent factors: ({unit1}, {unit2}): {factor1}, ({unit2}, {unit1}): {factor2}, expected: {expected_factor2}")
        
        self.assertEqual(len(conflicts), 0,
                        f"Conversion matrix conflicts found: {conflicts}")
    
    def test_all_categories_have_units(self):
        """Test that all categories returned by get_all_categories() have at least one unit"""
        categories = pyco._get_all_categories()
        
        for category in categories:
            units = pyco._get_units_by_category(category)
            self.assertGreater(len(units), 0, 
                              f"Category '{category}' has no units")
    
    def test_category_unit_format_consistency(self):
        """Test that all units in conversion matrix follow category.unit format (except temperature)"""
        invalid_formats = []
        
        for (unit1, unit2), _ in pyco._CONVERSION_MATRIX.items():
            # Check unit1 format
            if '.' not in unit1:
                invalid_formats.append(f"Unit '{unit1}' doesn't follow category.unit format")
            else:
                category, unit_name = unit1.split('.', 1)
                if not category or not unit_name:
                    invalid_formats.append(f"Unit '{unit1}' has invalid category.unit format")
            
            # Check unit2 format
            if '.' not in unit2:
                invalid_formats.append(f"Unit '{unit2}' doesn't follow category.unit format")
            else:
                category, unit_name = unit2.split('.', 1)
                if not category or not unit_name:
                    invalid_formats.append(f"Unit '{unit2}' has invalid category.unit format")
        
        self.assertEqual(len(invalid_formats), 0,
                        f"Invalid unit formats found: {invalid_formats}")

class TestPycoConvertDefaultParameters(unittest.TestCase):
    """Test convert function with default parameters and usage display"""
    
    def test_convert_no_parameters_displays_usage(self):
        """Test that convert() with no parameters displays usage and units"""
        # Capture stdout to test the printed output and mock input for paging
        captured_output = io.StringIO()
        with patch('sys.stdout', captured_output), patch('builtins.input', return_value=''):
            result = pyco.convert()
        
        output = captured_output.getvalue()
        
        # Check that the function returns None (since units() prints and returns None)
        self.assertIsNone(result)
        
        # Check that the usage message is displayed
        self.assertIn("Convert - convert values between two units.", output)
        self.assertIn("Usage: convert(from, to, value)", output)
        self.assertIn("Available units are:", output)
        
        # Check that units are displayed
        self.assertIn("DISTANCE:", output)
        self.assertIn("TEMPERATURE:", output)
        
    def test_convert_empty_from_unit_displays_usage(self):
        """Test that convert('', 'miles', 5) displays usage and units"""
        captured_output = io.StringIO()
        with patch('sys.stdout', captured_output), patch('builtins.input', return_value=''):
            result = pyco.convert('', 'miles', 5)
        
        output = captured_output.getvalue()
        
        # Check that the function returns None
        self.assertIsNone(result)
        
        # Check that the usage message is displayed
        self.assertIn("Convert - convert values between two units.", output)
        self.assertIn("Usage: convert(from, to, value)", output)
        self.assertIn("Available units are:", output)
        
    def test_convert_empty_to_unit_displays_usage(self):
        """Test that convert('miles', '', 5) displays usage and units"""
        captured_output = io.StringIO()
        with patch('sys.stdout', captured_output), patch('builtins.input', return_value=''):
            result = pyco.convert('miles', '', 5)
        
        output = captured_output.getvalue()
        
        # Check that the function returns None
        self.assertIsNone(result)
        
        # Check that the usage message is displayed
        self.assertIn("Convert - convert values between two units.", output)
        self.assertIn("Usage: convert(from, to, value)", output)
        self.assertIn("Available units are:", output)
        
    def test_convert_both_empty_units_displays_usage(self):
        """Test that convert('', '', 5) displays usage and units"""
        captured_output = io.StringIO()
        with patch('sys.stdout', captured_output), patch('builtins.input', return_value=''):
            result = pyco.convert('', '', 5)
        
        output = captured_output.getvalue()
        
        # Check that the function returns None
        self.assertIsNone(result)
        
        # Check that the usage message is displayed
        self.assertIn("Convert - convert values between two units.", output)
        self.assertIn("Usage: convert(from, to, value)", output)
        self.assertIn("Available units are:", output)
        
    def test_convert_default_value_parameter(self):
        """Test that the default value parameter (0) works correctly"""
        # Test with explicit zero value
        result = pyco.convert('mi', 'km', 0)
        self.assertEqual(result, 0.0)
        
        # Test normal operation with default parameters shouldn't be affected
        # (this test ensures default value=0 doesn't interfere with normal usage)
        result = pyco.convert('ft', 'in', 12)  # 12 feet should be 144 inches
        self.assertEqual(result, 144.0)

class TestPycoUnitsSearch(unittest.TestCase):
    """Test units function with search parameter and fuzzy matching"""
    
    def test_units_no_search_shows_all(self):
        """Test that units() with no search parameter shows all categories"""
        captured_output = io.StringIO()
        with patch('sys.stdout', captured_output), patch('builtins.input', return_value=''):
            pyco.units()
        
        output = captured_output.getvalue()
        
        # Should show all major categories
        self.assertIn("AREA:", output)
        self.assertIn("DISTANCE:", output)
        self.assertIn("TEMPERATURE:", output)
        self.assertIn("WEIGHT:", output)
        
    def test_units_empty_search_shows_all(self):
        """Test that units('') shows all categories"""
        captured_output = io.StringIO()
        with patch('sys.stdout', captured_output), patch('builtins.input', return_value=''):
            pyco.units('')
        
        output = captured_output.getvalue()
        
        # Should show all major categories
        self.assertIn("AREA:", output)
        self.assertIn("DISTANCE:", output)
        self.assertIn("TEMPERATURE:", output)
        self.assertIn("WEIGHT:", output)
        
    def test_units_exact_match_abbreviation(self):
        """Test exact match on unit abbreviation"""
        captured_output = io.StringIO()
        with patch('sys.stdout', captured_output):
            pyco.units('kg')
        
        output = captured_output.getvalue()
        
        # Should only show WEIGHT category with kg
        self.assertIn("WEIGHT:", output)
        self.assertIn("kg", output)
        self.assertIn("kilograms", output)
        # Should not show other categories
        self.assertNotIn("AREA:", output)
        self.assertNotIn("DISTANCE:", output)
        
    def test_units_exact_match_full_name(self):
        """Test exact match on full unit name"""
        captured_output = io.StringIO()
        with patch('sys.stdout', captured_output):
            pyco.units('celsius')
        
        output = captured_output.getvalue()
        
        # Should only show TEMPERATURE category
        self.assertIn("TEMPERATURE:", output)
        self.assertIn("Celsius", output)
        # Should not show other categories  
        self.assertNotIn("AREA:", output)
        self.assertNotIn("WEIGHT:", output)
        
    def test_units_partial_match(self):
        """Test partial string matching"""
        captured_output = io.StringIO()
        with patch('sys.stdout', captured_output):
            pyco.units('meter')
        
        output = captured_output.getvalue()
        
        # Should show categories with meter-related units
        self.assertIn("DISTANCE:", output)
        self.assertIn("meters", output)
        self.assertIn("centimeters", output)
        self.assertIn("kilometers", output)
        
    def test_units_fuzzy_match_typo(self):
        """Test fuzzy matching catches common typos"""
        captured_output = io.StringIO()
        with patch('sys.stdout', captured_output):
            pyco.units('celcius')  # Common typo for celsius
        
        output = captured_output.getvalue()
        
        # Should find Celsius despite the typo
        self.assertIn("TEMPERATURE:", output)
        self.assertIn("Celsius", output)
        
    def test_units_fuzzy_match_alternate_spelling(self):
        """Test fuzzy matching catches alternate spellings"""
        captured_output = io.StringIO()
        with patch('sys.stdout', captured_output):
            pyco.units('metre')  # British spelling
        
        output = captured_output.getvalue()
        
        # Should find meter-related units
        self.assertIn("meters", output)
        
    def test_units_no_matches_empty_output(self):
        """Test that searching for non-existent units shows no categories"""
        captured_output = io.StringIO()
        with patch('sys.stdout', captured_output):
            pyco.units('xyz123')  # Non-existent unit
        
        output = captured_output.getvalue()
        
        # Should not show any category headers
        self.assertNotIn("AREA:", output)
        self.assertNotIn("DISTANCE:", output)
        self.assertNotIn("TEMPERATURE:", output)
        self.assertNotIn("WEIGHT:", output)
        # Should only have blank line
        self.assertEqual(output.strip(), "")
        
    def test_units_case_insensitive_search(self):
        """Test that search is case insensitive"""
        captured_output1 = io.StringIO()
        with patch('sys.stdout', captured_output1):
            pyco.units('CELSIUS')
        
        captured_output2 = io.StringIO()
        with patch('sys.stdout', captured_output2):
            pyco.units('celsius')
            
        # Both should produce the same output
        self.assertEqual(captured_output1.getvalue(), captured_output2.getvalue())
        
    def test_units_multiple_category_matches(self):
        """Test search term that matches units in multiple categories"""
        captured_output = io.StringIO()
        with patch('sys.stdout', captured_output):
            pyco.units('feet')  # Should match both area (feet^2) and distance (feet)
        
        output = captured_output.getvalue()
        
        # Should show both AREA and DISTANCE categories
        self.assertIn("AREA:", output)
        self.assertIn("DISTANCE:", output) 
        self.assertIn("feet", output)

class TestPycoConvertErrorHandling(unittest.TestCase):
    """Test convert function error handling with helpful suggestions"""
    
    def test_convert_both_units_invalid(self):
        """Test convert with both units invalid shows generic error message"""
        captured_output = io.StringIO()
        with patch('sys.stdout', captured_output):
            result = pyco.convert('xyz', 'abc', 5)
        
        output = captured_output.getvalue()
        
        # Should return None
        self.assertIsNone(result)
        
        # Should show generic error message
        self.assertIn("No conversion from 'xyz' to 'abc'", output)
        self.assertIn("Type 'units' to see available conversions", output)
        
        # Should not call units() function with search
        self.assertNotIn("DISTANCE:", output)
        self.assertNotIn("WEIGHT:", output)
        
    def test_convert_invalid_from_unit_with_suggestions(self):
        """Test convert with invalid from_unit shows suggestions"""
        captured_output = io.StringIO()
        with patch('sys.stdout', captured_output):
            result = pyco.convert('kilo', 'lb', 5)
        
        output = captured_output.getvalue()
        
        # Should return None
        self.assertIsNone(result)
        
        # Should show specific error message for from_unit
        self.assertIn("Could not convert the unit 'kilo'", output)
        self.assertIn("Did you mean one of the following?", output)
        
        # Should show suggestions (units containing "kilo")
        self.assertIn("kg", output)
        self.assertIn("kilograms", output)
        self.assertIn("km", output)
        self.assertIn("kilometers", output)
        
    def test_convert_invalid_to_unit_with_suggestions(self):
        """Test convert with invalid to_unit shows suggestions"""
        captured_output = io.StringIO()
        with patch('sys.stdout', captured_output):
            result = pyco.convert('kg', 'poun', 5)  # typo for pound
        
        output = captured_output.getvalue()
        
        # Should return None
        self.assertIsNone(result)
        
        # Should show specific error message for to_unit
        self.assertIn("Could not convert the unit 'poun'", output)
        self.assertIn("Did you mean one of the following?", output)
        
        # Should show suggestions for weight units similar to "poun"
        self.assertIn("lb", output)
        self.assertIn("pounds", output)
        
    def test_convert_invalid_unit_no_suggestions(self):
        """Test convert with invalid unit that has no similar matches"""
        captured_output = io.StringIO()
        with patch('sys.stdout', captured_output):
            result = pyco.convert('xyz123', 'kg', 5)
        
        output = captured_output.getvalue()
        
        # Should return None
        self.assertIsNone(result)
        
        # Should show error message
        self.assertIn("Could not convert the unit 'xyz123'", output)
        self.assertIn("Did you mean one of the following?", output)
        
        # Output should be relatively short since no matches found
        # (only the error message and blank line from units function)
        
    def test_convert_case_insensitive_validation(self):
        """Test that unit validation is case insensitive"""
        # Test with uppercase units
        result1 = pyco.convert('KG', 'LB', 1)
        result2 = pyco.convert('kg', 'lb', 1)
        
        # Both should work and give same result
        self.assertIsNotNone(result1)
        self.assertIsNotNone(result2)
        self.assertEqual(result1, result2)
        
    def test_convert_temperature_validation(self):
        """Test that temperature units are properly validated"""
        # Valid temperature conversion should work
        result = pyco.convert('c', 'f', 0)
        self.assertAlmostEqual(result, 32.0, places=1)
        
        # Invalid temperature unit should show suggestions
        captured_output = io.StringIO()
        with patch('sys.stdout', captured_output):
            result = pyco.convert('celciu', 'f', 0)  # typo
        
        output = captured_output.getvalue()
        self.assertIsNone(result)
        self.assertIn("Could not convert the unit 'celciu'", output)

if __name__ == '__main__':
    # Create a test suite
    suite = unittest.TestLoader().loadTestsFromModule(sys.modules[__name__])
    
    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"PYCO TEST SUITE RESULTS")
    print(f"{'='*60}")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    if result.failures:
        print(f"\nFAILURES:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback.split('AssertionError:')[-1].strip()}")
    
    if result.errors:
        print(f"\nERRORS:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback.split('Error:')[-1].strip()}")
    
