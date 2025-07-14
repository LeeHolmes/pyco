"""
Unit tests for pyco.py calculator functions.
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
        # Test simple string search (original behavior)
        results = pyco.find('convert')
        self.assertIn('convert_celsius_fahrenheit', results)
        self.assertIn('convert_fahrenheit_celsius', results)
        self.assertIn('convert_miles_kilometers', results)
        
        # Test finding functions that contain 'avg'
        results = pyco.find('avg')
        self.assertIn('avg', results)
        
        # Test finding non-existent term
        results = pyco.find('nonexistent')
        self.assertEqual(results, [])
        
        # Test wildcard patterns
        # Prefix matching (starts with)
        results = pyco.find('convert*')
        self.assertIn('convert_celsius_fahrenheit', results)
        self.assertIn('convert_fahrenheit_celsius', results)
        self.assertIn('convert_miles_kilometers', results)
        
        # Suffix matching (ends with)
        results = pyco.find('*fahrenheit')
        self.assertIn('convert_celsius_fahrenheit', results)
        self.assertNotIn('convert_fahrenheit_celsius', results)
        
        # Contains matching (surrounded by *)
        results = pyco.find('*celsius*')
        self.assertIn('convert_celsius_fahrenheit', results)
        self.assertIn('convert_fahrenheit_celsius', results)
        
        # Test short aliases with wildcards
        results = pyco.find('c_*')
        expected_aliases = ['c_c_f', 'c_f_c', 'c_mi_km', 'c_km_mi', 'c_mi_ft', 'c_ft_mi', 'c_in_ft', 'c_ft_in']
        for alias in expected_aliases:
            self.assertIn(alias, results)
        
        # Test aliases ending with '_f'
        results = pyco.find('*_f')
        self.assertIn('c_c_f', results)
        
        # Test aliases containing '_mi_'
        results = pyco.find('*_mi_*')
        self.assertIn('c_mi_km', results)
        self.assertIn('c_mi_ft', results)
        
        # Test pattern that should match nothing
        results = pyco.find('*xyz*')
        self.assertEqual(results, [])
        
        # Test case insensitivity
        results_lower = pyco.find('*convert*')
        results_upper = pyco.find('*CONVERT*')
        results_mixed = pyco.find('*Convert*')
        self.assertEqual(set(results_lower), set(results_upper))
        self.assertEqual(set(results_lower), set(results_mixed))
    
    def test_find_object_method_patterns(self):
        """Test the find function with object.method patterns"""
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
        # First, object patterns
        test_patterns = [
            ['math', ['math']],  # exact match
            ['mat*.sin', ['math: sin']],   # starts with
            ['*ath.sin', ['math: sin']],   # ends with
            ['*math*.sin', ['math: sin']]  # contains
        ]
        
        for pattern in test_patterns:
            results = pyco.find(pattern[0])
            self.assertEqual(results, pattern[1])

        # Method patterns
        test_patterns = [
            ['math', ['math']],  # exact match
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
    
    def test_get_printable_char(self):
        """Test the get_printable_char function"""
        # Test printable ASCII characters
        self.assertEqual(pyco.get_printable_char(65), 'A')
        self.assertEqual(pyco.get_printable_char(97), 'a')
        self.assertEqual(pyco.get_printable_char(48), '0')
        self.assertEqual(pyco.get_printable_char(32), ' ')
        self.assertEqual(pyco.get_printable_char(126), '~')
        
        # Test non-printable characters (should return '.')
        self.assertEqual(pyco.get_printable_char(0), '.')
        self.assertEqual(pyco.get_printable_char(31), '.')
        self.assertEqual(pyco.get_printable_char(127), '.')
        self.assertEqual(pyco.get_printable_char(159), '.')
    
    @patch('builtins.input', side_effect=['1','2', ''])
    def test_inputlist(self, mock_input):
        """Test the inputlist function"""
        with patch('builtins.print'):  # Suppress print output
            result = pyco.inputlist()
        self.assertEqual(result, [1, 2])
    
    @patch('builtins.input', side_effect=['3', '4', ''])
    def test_il_alias(self, mock_input):
        """Test the il alias for inputlist"""
        with patch('builtins.print'):  # Suppress print output
            result = pyco.il()
        self.assertEqual(result, [3, 4])
    
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
    
class TestPycoStatisticsFunctions(unittest.TestCase):
    """Test statistics functions in pyco.py"""
    
    def test_average(self):
        """Test the average function"""
        self.assertEqual(pyco.average([1, 2, 3, 4, 5]), 3.0)
        self.assertEqual(pyco.average([10, 20, 30]), 20.0)
        self.assertEqual(pyco.average([5]), 5.0)
        self.assertAlmostEqual(pyco.average([1.5, 2.5, 3.5]), 2.5)
    
    def test_avg_alias(self):
        """Test the avg alias for average"""
        self.assertEqual(pyco.avg([1, 2, 3, 4, 5]), 3.0)
        self.assertEqual(pyco.avg([10, 20, 30]), 20.0)


class TestPycoTemperatureConversions(unittest.TestCase):
    """Test temperature conversion functions in pyco.py"""
    
    def test_convert_celsius_fahrenheit(self):
        """Test Celsius to Fahrenheit conversion"""
        self.assertEqual(pyco.convert_celsius_fahrenheit(0), 32.0)
        self.assertEqual(pyco.convert_celsius_fahrenheit(100), 212.0)
        self.assertEqual(pyco.convert_celsius_fahrenheit(-40), -40.0)
        self.assertAlmostEqual(pyco.convert_celsius_fahrenheit(37), 98.6)
    
    def test_convert_fahrenheit_celsius(self):
        """Test Fahrenheit to Celsius conversion"""
        self.assertEqual(pyco.convert_fahrenheit_celsius(32), 0.0)
        self.assertEqual(pyco.convert_fahrenheit_celsius(212), 100.0)
        self.assertEqual(pyco.convert_fahrenheit_celsius(-40), -40.0)
        self.assertAlmostEqual(pyco.convert_fahrenheit_celsius(98.6), 37.0)


class TestPycoDistanceConversions(unittest.TestCase):
    """Test distance conversion functions in pyco.py"""
    
    def test_convert_miles_kilometers(self):
        """Test miles to kilometers conversion"""
        self.assertAlmostEqual(pyco.convert_miles_kilometers(1), 1.609344)
        self.assertAlmostEqual(pyco.convert_miles_kilometers(0), 0.0)
        self.assertAlmostEqual(pyco.convert_miles_kilometers(5), 8.04672)
    
    def test_c_mi_km_alias(self):
        """Test c_mi_km alias for convert_miles_kilometers"""
        self.assertAlmostEqual(pyco.c_mi_km(1), 1.609344)
    
    def test_mi_km_alias(self):
        """Test mi_km alias for convert_miles_kilometers"""
        self.assertAlmostEqual(pyco.mi_km(1), 1.609344)
    
    def test_convert_kilometers_miles(self):
        """Test kilometers to miles conversion"""
        self.assertAlmostEqual(pyco.convert_kilometers_miles(1.609344), 1.0)
        self.assertAlmostEqual(pyco.convert_kilometers_miles(0), 0.0)
        self.assertAlmostEqual(pyco.convert_kilometers_miles(8.04672), 5.0)
    
    def test_c_km_mi_alias(self):
        """Test c_km_mi alias for convert_kilometers_miles"""
        self.assertAlmostEqual(pyco.c_km_mi(1.609344), 1.0)
    
    def test_km_mi_alias(self):
        """Test km_mi alias for convert_kilometers_miles"""
        self.assertAlmostEqual(pyco.km_mi(1.609344), 1.0)
    
    def test_convert_miles_feet(self):
        """Test miles to feet conversion"""
        self.assertEqual(pyco.convert_miles_feet(1), 5280)
        self.assertEqual(pyco.convert_miles_feet(0), 0)
        self.assertEqual(pyco.convert_miles_feet(0.5), 2640)
    
    def test_c_mi_ft_alias(self):
        """Test c_mi_ft alias for convert_miles_feet"""
        self.assertEqual(pyco.c_mi_ft(1), 5280)
    
    def test_mi_ft_alias(self):
        """Test mi_ft alias for convert_miles_feet"""
        self.assertEqual(pyco.mi_ft(1), 5280)
    
    def test_convert_feet_miles(self):
        """Test feet to miles conversion"""
        self.assertEqual(pyco.convert_feet_miles(5280), 1.0)
        self.assertEqual(pyco.convert_feet_miles(0), 0.0)
        self.assertEqual(pyco.convert_feet_miles(2640), 0.5)
    
    def test_c_ft_mi_alias(self):
        """Test c_ft_mi alias for convert_feet_miles"""
        self.assertEqual(pyco.c_ft_mi(5280), 1.0)
    
    def test_ft_mi_alias(self):
        """Test ft_mi alias for convert_feet_miles"""
        self.assertEqual(pyco.ft_mi(5280), 1.0)
    
    def test_convert_inches_feet(self):
        """Test inches to feet conversion"""
        self.assertEqual(pyco.convert_inches_feet(12), 1.0)
        self.assertEqual(pyco.convert_inches_feet(0), 0.0)
        self.assertEqual(pyco.convert_inches_feet(24), 2.0)
        self.assertEqual(pyco.convert_inches_feet(6), 0.5)
    
    def test_c_in_ft_alias(self):
        """Test c_in_ft alias for convert_inches_feet"""
        self.assertEqual(pyco.c_in_ft(12), 1.0)
    
    def test_in_ft_alias(self):
        """Test in_ft alias for convert_inches_feet"""
        self.assertEqual(pyco.in_ft(12), 1.0)
    
    def test_convert_feet_inches(self):
        """Test feet to inches conversion"""
        self.assertEqual(pyco.convert_feet_inches(1), 12)
        self.assertEqual(pyco.convert_feet_inches(0), 0)
        self.assertEqual(pyco.convert_feet_inches(2), 24)
        self.assertEqual(pyco.convert_feet_inches(0.5), 6)
    
    def test_c_ft_in_alias(self):
        """Test c_ft_in alias for convert_feet_inches"""
        self.assertEqual(pyco.c_ft_in(1), 12)
    
    def test_ft_in_alias(self):
        """Test ft_in alias for convert_feet_inches"""
        self.assertEqual(pyco.ft_in(1), 12)


class TestPycoConstants(unittest.TestCase):
    """Test constants defined in pyco.py"""
    
    def test_byte_constants(self):
        """Test byte size constants"""
        self.assertEqual(pyco.kb, 1024)
        self.assertEqual(pyco.mb, 1024 * 1024)
        self.assertEqual(pyco.gb, 1024 * 1024 * 1024)
        self.assertEqual(pyco.tb, 1024 * 1024 * 1024 * 1024)


class TestPycoConversionChains(unittest.TestCase):
    """Test conversion chains to ensure mathematical consistency"""
    
    def test_temperature_conversion_chain(self):
        """Test that temperature conversions are mathematically consistent"""
        # Test C -> F -> C
        celsius = 25.0
        fahrenheit = pyco.convert_celsius_fahrenheit(celsius)
        back_to_celsius = pyco.convert_fahrenheit_celsius(fahrenheit)
        self.assertAlmostEqual(celsius, back_to_celsius, places=10)
        
        # Test F -> C -> F
        fahrenheit = 77.0
        celsius = pyco.convert_fahrenheit_celsius(fahrenheit)
        back_to_fahrenheit = pyco.convert_celsius_fahrenheit(celsius)
        self.assertAlmostEqual(fahrenheit, back_to_fahrenheit, places=10)
    
    def test_distance_conversion_chain(self):
        """Test that distance conversions are mathematically consistent"""
        # Test miles -> km -> miles
        miles = 10.0
        kilometers = pyco.convert_miles_kilometers(miles)
        back_to_miles = pyco.convert_kilometers_miles(kilometers)
        self.assertAlmostEqual(miles, back_to_miles, places=10)
        
        # Test miles -> feet -> miles
        miles = 2.0
        feet = pyco.convert_miles_feet(miles)
        back_to_miles = pyco.convert_feet_miles(feet)
        self.assertAlmostEqual(miles, back_to_miles, places=10)
        
        # Test feet -> inches -> feet
        feet = 3.0
        inches = pyco.convert_feet_inches(feet)
        back_to_feet = pyco.convert_inches_feet(inches)
        self.assertAlmostEqual(feet, back_to_feet, places=10)


class TestPycoEdgeCases(unittest.TestCase):
    """Test edge cases and error conditions"""
    
    def test_zero_conversions(self):
        """Test conversions with zero values"""
        self.assertEqual(pyco.convert_celsius_fahrenheit(0), 32.0)
        self.assertEqual(pyco.convert_fahrenheit_celsius(0), -17.77777777777778)
        self.assertEqual(pyco.convert_miles_kilometers(0), 0.0)
        self.assertEqual(pyco.convert_kilometers_miles(0), 0.0)
        self.assertEqual(pyco.convert_miles_feet(0), 0)
        self.assertEqual(pyco.convert_feet_miles(0), 0.0)
        self.assertEqual(pyco.convert_inches_feet(0), 0.0)
        self.assertEqual(pyco.convert_feet_inches(0), 0)
    
    def test_negative_conversions(self):
        """Test conversions with negative values"""
        self.assertEqual(pyco.convert_celsius_fahrenheit(-10), 14.0)
        self.assertEqual(pyco.convert_fahrenheit_celsius(-10), -23.333333333333332)
        self.assertEqual(pyco.convert_miles_kilometers(-5), -8.04672)
        self.assertEqual(pyco.convert_kilometers_miles(-8.04672), -5.0)
    
    def test_large_number_conversions(self):
        """Test conversions with large numbers"""
        large_num = 1000000.0
        
        # Test that large numbers don't cause overflow
        result = pyco.convert_celsius_fahrenheit(large_num)
        self.assertIsInstance(result, float)
        self.assertGreater(result, large_num)
        
        result = pyco.convert_miles_kilometers(large_num)
        self.assertIsInstance(result, float)
        self.assertGreater(result, large_num)


class TestPycoAliases(unittest.TestCase):
    """Test that all aliases work correctly"""
    
    def test_all_temperature_aliases(self):
        """Test that all temperature conversion aliases produce same results"""
        celsius = 25.0
        
        # Test Celsius to Fahrenheit aliases
        result1 = pyco.convert_celsius_fahrenheit(celsius)
        result2 = pyco.c_c_f(celsius)
        result3 = pyco.c_f(celsius)
        
        self.assertEqual(result1, result2)
        self.assertEqual(result2, result3)
        
        fahrenheit = 77.0
        
        # Test Fahrenheit to Celsius aliases
        result1 = pyco.convert_fahrenheit_celsius(fahrenheit)
        result2 = pyco.c_f_c(fahrenheit)
        result3 = pyco.f_c(fahrenheit)
        
        self.assertEqual(result1, result2)
        self.assertEqual(result2, result3)
    
    def test_all_distance_aliases(self):
        """Test that all distance conversion aliases produce same results"""
        miles = 5.0
        
        # Test miles to kilometers aliases
        result1 = pyco.convert_miles_kilometers(miles)
        result2 = pyco.c_mi_km(miles)
        result3 = pyco.mi_km(miles)
        
        self.assertEqual(result1, result2)
        self.assertEqual(result2, result3)
        
        kilometers = 8.0
        
        # Test kilometers to miles aliases
        result1 = pyco.convert_kilometers_miles(kilometers)
        result2 = pyco.c_km_mi(kilometers)
        result3 = pyco.km_mi(kilometers)
        
        self.assertEqual(result1, result2)
        self.assertEqual(result2, result3)
        
        # Test miles to feet aliases
        result1 = pyco.convert_miles_feet(miles)
        result2 = pyco.c_mi_ft(miles)
        result3 = pyco.mi_ft(miles)
        
        self.assertEqual(result1, result2)
        self.assertEqual(result2, result3)
        
        feet = 1000.0
        
        # Test feet to miles aliases
        result1 = pyco.convert_feet_miles(feet)
        result2 = pyco.c_ft_mi(feet)
        result3 = pyco.ft_mi(feet)
        
        self.assertEqual(result1, result2)
        self.assertEqual(result2, result3)
        
        inches = 36.0
        
        # Test inches to feet aliases
        result1 = pyco.convert_inches_feet(inches)
        result2 = pyco.c_in_ft(inches)
        result3 = pyco.in_ft(inches)
        
        self.assertEqual(result1, result2)
        self.assertEqual(result2, result3)
        
        feet = 3.0
        
        # Test feet to inches aliases
        result1 = pyco.convert_feet_inches(feet)
        result2 = pyco.c_ft_in(feet)
        result3 = pyco.ft_in(feet)
        
        self.assertEqual(result1, result2)
        self.assertEqual(result2, result3)
    
    def test_utility_aliases(self):
        """Test that utility function aliases work correctly"""
        # Test average aliases
        test_list = [1, 2, 3, 4, 5]
        result1 = pyco.average(test_list)
        result2 = pyco.avg(test_list)
        
        self.assertEqual(result1, result2)
        
        # Test inputlist aliases would require mocking input


class TestPycoWildcardSearch(unittest.TestCase):
    """Test wildcard search functionality in the find function"""
    
    def test_simple_wildcard_patterns(self):
        """Test basic wildcard patterns"""
        # Test prefix matching (ends with *)
        results = pyco.find('convert_celsius*')
        self.assertIn('convert_celsius_fahrenheit', results)
        self.assertNotIn('convert_fahrenheit_celsius', results)
        
        # Test suffix matching (starts with *)
        results = pyco.find('*fahrenheit')
        self.assertIn('convert_celsius_fahrenheit', results)
        self.assertNotIn('convert_fahrenheit_celsius', results)
        
        # Test contains matching (surrounded by *)
        results = pyco.find('*miles*')
        self.assertIn('convert_miles_kilometers', results)
        self.assertIn('convert_kilometers_miles', results)
        self.assertIn('convert_miles_feet', results)
        self.assertIn('convert_feet_miles', results)
    
    def test_alias_wildcard_patterns(self):
        """Test wildcard patterns on function aliases"""
        # Test short aliases starting with 'c_'
        results = pyco.find('c_*')
        expected_aliases = ['c_c_f', 'c_f_c', 'c_mi_km', 'c_km_mi', 'c_mi_ft', 'c_ft_mi', 'c_in_ft', 'c_ft_in']
        for alias in expected_aliases:
            self.assertIn(alias, results)
        
        # Test aliases ending with '_f'
        results = pyco.find('*_f')
        self.assertIn('c_c_f', results)
        
        # Test aliases containing '_mi_'
        results = pyco.find('*_mi_*')
        self.assertIn('c_mi_km', results)
        self.assertIn('c_mi_ft', results)
    
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
        
        # Test very specific patterns
        results = pyco.find('avg')
        self.assertIn('avg', results)
        
        results = pyco.find('*avg*')
        self.assertIn('avg', results)
    
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
            pyco.displayhook(test_function)
            # Should call the function and pass result to original displayhook
            mock_displayhook.assert_called_once_with("test_result")
    
    def test_displayhook_non_callable_value(self):
        """Test displayhook with non-callable values"""
        # Test that displayhook passes non-callable values directly
        test_value = "not_callable"
        
        with patch('sys.__displayhook__') as mock_displayhook:
            pyco.displayhook(test_value)
            # Should pass the value directly to original displayhook
            mock_displayhook.assert_called_once_with(test_value)
    
    def test_displayhook_with_lambda(self):
        """Test displayhook with lambda functions"""
        test_lambda = lambda: 42
        
        with patch('sys.__displayhook__') as mock_displayhook:
            pyco.displayhook(test_lambda)
            # Should call the lambda and pass result to original displayhook
            mock_displayhook.assert_called_once_with(42)


class TestPycoExceptionHandlerCoverage(unittest.TestCase):
    """Test exception handler code coverage"""
    
    def test_exception_handler_non_syntax_error(self):
        """Test exception handler with non-SyntaxError exceptions"""
        # Test that non-SyntaxError exceptions are passed through
        with patch('sys.__excepthook__') as mock_excepthook:
            pyco.my_except_hook(ValueError, ValueError("test"), None)
            # Should pass through to original exception handler
            mock_excepthook.assert_called_once()
    
    def test_exception_handler_syntax_error_no_wildcards(self):
        """Test exception handler with SyntaxError that doesn't have wildcards"""
        # Create a mock SyntaxError without wildcards
        mock_error = MagicMock()
        mock_error.text = "normal_syntax_error"
        mock_error.strip.return_value = "normal_syntax_error"
        
        with patch('sys.__excepthook__') as mock_excepthook:
            pyco.my_except_hook(SyntaxError, mock_error, None)
            # Should pass through to original exception handler
            mock_excepthook.assert_called_once_with(SyntaxError, mock_error, None)
    
    @patch('builtins.print')
    def test_exception_handler_wildcard_no_results(self, mock_print):
        """Test exception handler with wildcard pattern that returns no results"""
        # Create a mock SyntaxError with wildcard that won't match anything
        mock_error = MagicMock()
        mock_error.text.strip.return_value = "nonexistent_xyz*"
        
        pyco.my_except_hook(SyntaxError, mock_error, None)
        
        # Should print "No matches found."
        mock_print.assert_called_with("No matches found.")
    
    @patch('builtins.print')
    def test_exception_handler_wildcard_with_results(self, mock_print):
        """Test exception handler with wildcard pattern that returns results"""
        # Create a mock SyntaxError with wildcard that will match
        mock_error = MagicMock()
        mock_error.text.strip.return_value = "convert*"
        
        pyco.my_except_hook(SyntaxError, mock_error, None)
        
        # Should print each result
        self.assertTrue(mock_print.called)
        # Check that some conversion functions were printed
        print_calls = [str(call) for call in mock_print.call_args_list]
        found_convert = any("convert" in call for call in print_calls)
        self.assertTrue(found_convert, "Should print conversion functions")

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
    