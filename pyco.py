# pyco calculator customizations
import sys
import math
from math import *
import difflib

if sys.implementation.name == 'cpython':
    import statistics
    from statistics import *

    def displayhook(value):
        if callable(value):
            displayhook(value())
        else:
            sys.__displayhook__(value)
    sys.displayhook = displayhook

    def my_except_hook(exctype, value, traceback):
        if exctype == SyntaxError:
            cleanvalue = value.text.strip()
            if(cleanvalue.endswith("*") or cleanvalue.startswith("*")):
                results = find(cleanvalue)
                if results:
                    for result in results:
                        print(result)
                else:
                    print("No matches found.")
            else:
                sys.__excepthook__(exctype, value, traceback)
        else:
            sys.__excepthook__(exctype, value, traceback)
    sys.excepthook = my_except_hook

elif sys.implementation.name == 'micropython':
    __original_repl_print__ = __repl_print__
    def displayhook(value):
        if callable(value):
            displayhook(value())
        else:
            __original_repl_print__(value)
    __repl_print__ = displayhook

def find(term):
    """Find all global variables or functions that match the given term pattern.
    
    Supports wildcard patterns:
    - term* : finds items starting with 'term'
    - *term : finds items ending with 'term'
    - *term* : finds items containing 'term'
    - obj.method* : finds methods in 'obj' starting with 'method'
    - *obj*.method* : finds methods matching 'method*' in objects matching '*obj*'
    """
    # Handle simple string search (no wildcards)
    if not "*" in term:
        found = []
        for current in globals():
            if term in current and not current.startswith('_'):
                found.append(current)
        return found
    
    # Handle wildcard patterns
    lastDot = term.rfind('.')
    filter = ""
    results = []
    
    if lastDot != -1:
        # Handle object.method patterns
        object_part = term[:lastDot]
        method_part = term[lastDot+1:]
        
        # Determine wildcard patterns for both parts
        obj_starts_with_star = object_part.startswith("*")
        obj_ends_with_star = object_part.endswith("*")
        method_starts_with_star = method_part.startswith("*")
        method_ends_with_star = method_part.endswith("*")
        
        # Extract object filter
        if obj_starts_with_star and obj_ends_with_star:
            obj_filter = object_part[1:-1]  # Remove both * characters
        elif obj_starts_with_star and not obj_ends_with_star:
            obj_filter = object_part[1:]    # Remove leading *
        elif obj_ends_with_star:
            obj_filter = object_part[:-1]   # Remove trailing *
        else:
            obj_filter = object_part
        
        # Extract method filter
        if method_starts_with_star and method_ends_with_star:
            method_filter = method_part[1:-1]  # Remove both * characters
        elif method_starts_with_star and not method_ends_with_star:
            method_filter = method_part[1:]    # Remove leading *
        elif method_ends_with_star:
            method_filter = method_part[:-1]   # Remove trailing *
        else:
            method_filter = method_part

        # Find matching objects
        matching_objects = []
        for obj_name in globals().keys():
            if obj_name.startswith('_'):
                continue
            obj_match = False
            if obj_starts_with_star and obj_ends_with_star:
                obj_match = obj_filter.lower() in obj_name.lower()
            elif obj_starts_with_star and not obj_ends_with_star:
                obj_match = obj_name.lower().endswith(obj_filter.lower())
            elif obj_ends_with_star:
                obj_match = obj_name.lower().startswith(obj_filter.lower())
            else:
                obj_match = obj_name.lower() == obj_filter.lower()
            
            if obj_match:
                matching_objects.append(obj_name)
        
        # For each matching object, find matching methods
        found_results = []
        for obj_name in matching_objects:
            try:
                obj_methods = dir(eval(obj_name))
                matching_methods = []
                
                for method_name in obj_methods:
                    method_match = False
                    if method_starts_with_star and method_ends_with_star:
                        method_match = method_filter.lower() in method_name.lower()
                    elif method_starts_with_star and not method_ends_with_star:
                        method_match = method_name.lower().endswith(method_filter.lower())
                    elif method_ends_with_star:
                        method_match = method_name.lower().startswith(method_filter.lower())
                    else:
                        method_match = method_name.lower() == method_filter.lower()
                    
                    if method_match:
                        matching_methods.append(method_name)
                
                if matching_methods:
                    found_results.append(f"{obj_name}: {' '.join(matching_methods)}")
            except:
                pass
        
        return found_results
    else:
        # Determine wildcard pattern
        starts_with_star = term.startswith("*")
        ends_with_star = term.endswith("*")
        
        # Handle *filter*, *filter, or filter* patterns
        if starts_with_star and ends_with_star:
            filter = term[1:-1]  # Remove both * characters
        elif starts_with_star:
            filter = term[1:]    # Remove leading *
        else:  # ends_with_star
            filter = term[:-1]   # Remove trailing *
        
        results = globals().keys()

        # Handle simple wildcard patterns (no dot)
        found_results = []
        for current in results:
            if current.startswith('_'):
                continue
            match = False
            if starts_with_star and ends_with_star:
                # Contains match
                match = filter.lower() in current.lower()
            elif starts_with_star:
                # Ends with match
                match = current.lower().endswith(filter.lower())
            else:  # ends_with_star
                # Starts with match
                match = current.lower().startswith(filter.lower())
            
            if match:
                found_results.append(current)
        
        return found_results

def print_buffered(lines):
    """
    Print an array of lines with paging support.
    
    Prints lines and prompts "Press ENTER to continue" every 18 lines.
    Gracefully handles cases where stdin is not available (like in tests).
    
    Args:
        lines (list): Array of strings to print
    """
    for i, line in enumerate(lines):
        if i > 0 and i % 18 == 0:
            try:
                input("Press ENTER to continue...")
            except (EOFError, OSError):
                # Handle case where stdin is not available (like in tests)
                pass
        print(line)

def asciitable():
    """Display a formatted ASCII table with decimal, hexadecimal, and character representations."""
    lines = []
    
    for i in range(0, 255, 4):
        if i % 72 == 0:
            lines.append("Dec Hx C | Dec Hx C | Dec Hx C | Dec Hx C")
        lines.append("{:3d} {:02X} {} | {:3d} {:02X} {} | {:3d} {:02X} {} | {:3d} {:02X} {}".format(
            i, i, get_printable_char(i),
            (i + 1), (i + 1), get_printable_char(i + 1),
            (i + 2), (i + 2), get_printable_char(i + 2),
            (i + 3), (i + 3), get_printable_char(i + 3)))
    
    print_buffered(lines)
    return

def get_printable_char(char):
    """Return a printable character representation for the given ASCII code."""
    if char < 32:
        return '.'
    elif char > 126 and char < 160:
        return '.'
    else:
        return chr(char)

def inputlist():
    """Read a list of numbers."""
    global _list
    _list = []
    inputCounter = 0
    print()
    while True:
        lastInput = input(str(inputCounter) + ": ")
        if(lastInput == ""):
            break
        _list.append(float(lastInput))
        inputCounter += 1
    return _list


def average(list):
    """Calculate the average (mean) of a list of numbers."""
    return mean(list)

# Conversion Matrix System
# This system stores conversion factors between units in a non-redundant matrix format.
# Each conversion relationship is stored only once (e.g., hours->minutes: 60), and the
# system automatically handles bidirectional conversions by inverting factors as needed.
# Dynamic programming finds conversion paths between any two units, even through intermediate units.

# Category information is encoded in unit names using the format: category.unit
# This eliminates the need for separate category metadata while maintaining type safety.

def get_unit_category(unit):
    """Extract the category from a unit name (category.unit format)."""
    if '.' in unit:
        return unit.split('.', 1)[0]
    # Temperature units are handled specially
    if unit in ['c', 'f', 'k']:
        return 'temperature'
    return 'unknown'

def get_unit_name(unit):
    """Extract the unit name from category.unit format."""
    if '.' in unit:
        return unit.split('.', 1)[1]
    return unit

# Cache for external to internal unit mapping (initialized lazily)
_external_to_internal_cache = None

def _get_external_to_internal_mapping():
    """Generate mapping from external unit names to internal category.unit format."""
    global _external_to_internal_cache
    
    if _external_to_internal_cache is None:
        mapping = {}
        
        # Extract all units from the conversion matrix
        for (unit1, unit2), _ in CONVERSION_MATRIX.items():
            # For each internal unit, map its external name to the internal format
            if '.' in unit1:  # category.unit format
                external_name = get_unit_name(unit1)  # Extract unit part
                mapping[external_name] = unit1
            if '.' in unit2:  # category.unit format
                external_name = get_unit_name(unit2)  # Extract unit part
                mapping[external_name] = unit2
        
        _external_to_internal_cache = mapping
    
    return _external_to_internal_cache

def _is_valid_unit(unit):
    """Check if a unit is valid and can be converted."""
    internal_unit = _to_internal_unit(unit)
    
    # Check if unit appears in conversion matrix
    for (unit1, unit2), _ in CONVERSION_MATRIX.items():
        if internal_unit == unit1 or internal_unit == unit2:
            return True
    return False

def _to_internal_unit(unit):
    """Convert external unit name to internal category.unit format (case insensitive)."""
    # If already in category.unit format, return as-is
    if '.' in unit:
        return unit
    
    # Convert to lowercase for case-insensitive matching
    unit_lower = unit.lower()
    
    # Temperature units get converted to category.unit format
    if unit_lower in ['c', 'f', 'k']:
        return f'temperature.{unit_lower}'
    
    # Use the dynamically generated mapping (case insensitive)
    mapping = _get_external_to_internal_mapping()
    
    # First try exact match
    if unit in mapping:
        return mapping[unit]
    
    # Then try case-insensitive match
    for key, value in mapping.items():
        if key.lower() == unit_lower:
            return value
    
    # If no match found, return original unit
    return unit

def get_units_by_category(category):
    """Get all units belonging to a specific category."""
    all_units = set()
    # Get units from conversion matrix (temperature units are now included)
    for (unit1, unit2), _ in CONVERSION_MATRIX.items():
        all_units.add(unit1)
        all_units.add(unit2)
    
    # Filter by category and return external unit names
    category_units = [unit for unit in all_units if get_unit_category(unit) == category]
    return [get_unit_name(unit) for unit in category_units]

def get_all_categories():
    """Get all available unit categories."""
    all_units = set()
    # Get units from conversion matrix (temperature units are now included)
    for (unit1, unit2), _ in CONVERSION_MATRIX.items():
        all_units.add(unit1)
        all_units.add(unit2)
    
    return list(set(get_unit_category(unit) for unit in all_units))

# Temperature conversion functions
def _celsius_to_fahrenheit(value):
    """Convert Celsius to Fahrenheit"""
    return value * 9/5 + 32

def _fahrenheit_to_celsius(value):
    """Convert Fahrenheit to Celsius"""
    return (value - 32) * 5/9

def _celsius_to_kelvin(value):
    """Convert Celsius to Kelvin"""
    return value + 273.15

def _kelvin_to_celsius(value):
    """Convert Kelvin to Celsius"""
    return value - 273.15

# Define conversion factors as a matrix where each relationship is stored only once
# Format: (unit1, unit2): conversion_factor means unit1 * conversion_factor = unit2
# For temperature conversions, functions are used instead of constants due to offsets
# Units use category.name format to encode category information directly in the data
CONVERSION_MATRIX = {
    # Time conversions (smaller -> larger)
    ('time.s', 'time.min'): 1/60,
    ('time.min', 'time.h'): 1/60,
    ('time.h', 'time.d'): 1/24,
    ('time.d', 'time.wk'): 1/7,
    ('time.d', 'time.yr'): 1/365.25,
    
    # Temperature conversions (using functions for offset calculations)
    # Minimum spanning tree: C as hub connecting to F and K
    ('temperature.c', 'temperature.f'): _celsius_to_fahrenheit,
    ('temperature.f', 'temperature.c'): _fahrenheit_to_celsius,
    ('temperature.c', 'temperature.k'): _celsius_to_kelvin,
    ('temperature.k', 'temperature.c'): _kelvin_to_celsius,
    
    # Distance conversions (smaller -> larger) - minimal spanning tree
    ('distance.in', 'distance.ft'): 1/12,
    ('distance.in', 'distance.cm'): 2.54,
    ('distance.mm', 'distance.cm'): 1/10,
    ('distance.cm', 'distance.m'): 1/100,
    ('distance.m', 'distance.km'): 1/1000,
    ('distance.km', 'distance.mi'): 1/1.609344,
    
    # Weight conversions (smaller -> larger)
    ('weight.oz', 'weight.lb'): 1/16,
    ('weight.g', 'weight.kg'): 1/1000,
    ('weight.lb', 'weight.kg'): 0.453592,
    ('weight.lb', 'weight.st'): 1/14,
    ('weight.lb', 'weight.t'): 1/2000,
    
    # Volume conversions (smaller -> larger)
    ('volume.tsp', 'volume.tbsp'): 1/3,
    ('volume.tsp', 'volume.ml'): 4.92892,
    ('volume.tbsp', 'volume.floz'): 1/2,
    ('volume.tbsp', 'volume.ml'): 14.7868,
    ('volume.ml', 'volume.floz'): 1/29.5735,
    ('volume.ml', 'volume.l'): 1/1000,
    ('volume.floz', 'volume.cup'): 1/8,
    ('volume.pt', 'volume.qt'): 1/2,
    ('volume.pt', 'volume.l'): 0.473176,
    ('volume.qt', 'volume.l'): 0.946353,
    ('volume.qt', 'volume.gal'): 1/4,
    ('volume.l', 'volume.gal'): 1/3.78541,
    
    # Speed conversions (smaller -> larger)
    ('speed.mps', 'speed.kph'): 3.6,
    ('speed.kph', 'speed.mph'): 1/1.609344,
    ('speed.kph', 'speed.kn'): 1/1.852,
    ('speed.mph', 'speed.kn'): 1/1.15078,
    
    # Area conversions (smaller -> larger)
    ('area.in2', 'area.ft2'): 1/144,
    ('area.in2', 'area.cm2'): 6.4516,
    ('area.cm2', 'area.m2'): 1/10000,
    ('area.ft2', 'area.m2'): 0.092903,
    ('area.ft2', 'area.ac'): 1/43560,
    
    # Power conversions
    ('power.w', 'power.hp'): 1/745.7,
}

# Unit abbreviation to full English name mapping
UNIT_NAMES = {
    # Time units
    's': 'seconds',
    'min': 'minutes', 
    'h': 'hours',
    'd': 'days',
    'wk': 'weeks',
    'yr': 'years',
    
    # Temperature units (handled separately)
    'c': 'Celsius',
    'f': 'Fahrenheit',
    'k': 'Kelvin',
    
    # Distance units
    'in': 'inches',
    'ft': 'feet',
    'mm': 'millimeters',
    'cm': 'centimeters',
    'm': 'meters',
    'km': 'kilometers',
    'mi': 'miles',
    
    # Weight units
    'oz': 'ounces',
    'lb': 'pounds',
    'g': 'grams', 
    'kg': 'kilograms',
    'st': 'stone',
    't': 'tons',
    
    # Volume units
    'tsp': 'teaspoons',
    'tbsp': 'tablespoons',
    'ml': 'milliliters',
    'l': 'liters',
    'floz': 'fluid ounces',
    'cup': 'cups',
    'pt': 'pints',
    'qt': 'quarts',
    'gal': 'gallons',
    
    # Speed units
    'mps': 'meters/second',
    'kph': 'kilometers/h',
    'mph': 'miles/h',
    'kn': 'knots',
    
    # Area units
    'in2': 'inches^2',
    'ft2': 'feet^2',
    'cm2': 'centimeters^2',
    'm2': 'meters^2',
    'ac': 'acres',
    
    # Power units
    'w': 'watts',
    'hp': 'horsepower',
}

def _generate_units_lines(search=""):
    """
    Generate lines for units display with optional search filtering.
    
    Args:
        search (str): Optional search term to filter units.
        
    Returns:
        list: Array of strings representing the units display
    """
    lines = [""]
    
    def _matches_search(unit_abbrev, unit_full_name, search_term):
        """Check if unit matches search term using fuzzy string matching for typos"""
        if not search_term:
            return True
        
        search_lower = search_term.lower()
        unit_abbrev_lower = unit_abbrev.lower()
        unit_full_name_lower = unit_full_name.lower()
        
        # Exact partial match (high priority)
        if (search_lower in unit_abbrev_lower or 
            search_lower in unit_full_name_lower):
            return True
        
        # Fuzzy matching for typos (similarity threshold of 0.6)
        abbrev_similarity = difflib.SequenceMatcher(None, search_lower, unit_abbrev_lower).ratio()
        name_similarity = difflib.SequenceMatcher(None, search_lower, unit_full_name_lower).ratio()
        
        # Also check if search term is similar to any word in the full name
        name_words = unit_full_name_lower.split()
        word_similarities = [difflib.SequenceMatcher(None, search_lower, word).ratio() for word in name_words]
        max_word_similarity = max(word_similarities) if word_similarities else 0
        
        # Return True if any similarity score is above threshold
        similarity_threshold = 0.6
        return (abbrev_similarity >= similarity_threshold or 
                name_similarity >= similarity_threshold or
                max_word_similarity >= similarity_threshold)
    
    # Get all categories
    categories = get_all_categories()
    categories.sort()  # Sort alphabetically
    
    for category in categories:
        # Get units for this category
        all_units = get_units_by_category(category)
        
        # Filter units based on search term
        if search:
            units = []
            for unit in all_units:
                full_name = UNIT_NAMES.get(unit, unit)
                if _matches_search(unit, full_name, search):
                    units.append(unit)
        else:
            units = all_units
            
        units.sort()  # Sort alphabetically
        
        # Skip empty categories when searching
        if not units:
            continue
            
        # Add category header only if we have units to show
        lines.append(f"{category.upper()}:")
        
        # Format units in 2-column layout
        i = 0
        while i < len(units):
            unit1 = units[i]
            full_name1 = UNIT_NAMES.get(unit1, unit1)
            
            # Format first column: "abbr full_name" (max 18 chars to fit in 37 total)
            col1 = f"{unit1:<4} {full_name1}"
            
            # Check if we have a second unit and if first column fits
            if len(col1) > 18:
                # First column too long, put on its own line
                lines.append(f"  {col1}")
                i += 1
            elif i + 1 < len(units):
                # Try to add second column
                unit2 = units[i + 1]
                full_name2 = UNIT_NAMES.get(unit2, unit2)
                col2 = f"{unit2:<4} {full_name2}"
                
                if len(col2) > 18:
                    # Second column too long, append first column alone
                    lines.append(f"  {col1}")
                    i += 1
                else:
                    # Both columns fit, append them together
                    total_line = f"  {col1:<18} {col2}"
                    if len(total_line) <= 37:
                        lines.append(total_line)
                        i += 2
                    else:
                        # Line too long, append first column alone
                        lines.append(f"  {col1}")
                        i += 1
            else:
                # Only one unit left, append it
                lines.append(f"  {col1}")
                i += 1
        
        lines.append("")  # Empty line between categories
    
    return lines

def units(search=""):
    """
    Print a compact 2-column summary of available units with their human-readable names.
    
    Args:
        search (str): Optional search term to filter units. If empty, shows all units.
                     Matches against both unit abbreviations and full names (case-insensitive).
    """
    lines = _generate_units_lines(search)
    print_buffered(lines)

def _get_conversion_factor(from_unit, to_unit):
    """
    Get the conversion factor between two units, checking both directions in the matrix.
    
    Args:
        from_unit (str): Source unit (category.unit format)
        to_unit (str): Target unit (category.unit format)
        
    Returns:
        float or function: Conversion factor or function, or None if no direct conversion exists
    """
    # Check forward direction
    if (from_unit, to_unit) in CONVERSION_MATRIX:
        return CONVERSION_MATRIX[(from_unit, to_unit)]
    
    # Check reverse direction (invert the factor or find reverse function)
    if (to_unit, from_unit) in CONVERSION_MATRIX:
        factor_or_func = CONVERSION_MATRIX[(to_unit, from_unit)]
        if callable(factor_or_func):
            # For functions, we need to look up the reverse function
            # This is handled in the conversion matrix with bidirectional entries
            return None  # Let the search continue to find the proper reverse function
        else:
            return 1 / factor_or_func
    
    return None

def _get_connected_units(unit):
    """
    Get all units that can be directly converted from the given unit.
    
    Args:
        unit (str): The unit to find connections for (category.unit format)
        
    Returns:
        list: List of (connected_unit, conversion_factor_or_function) tuples
    """
    connections = []
    
    # Check all matrix entries for connections
    for (unit1, unit2), factor_or_func in CONVERSION_MATRIX.items():
        if unit1 == unit:
            connections.append((unit2, factor_or_func))
        elif unit2 == unit:
            if callable(factor_or_func):
                # For functions, we don't invert - the reverse should be explicitly defined
                continue
            else:
                connections.append((unit1, 1/factor_or_func))
    
    return connections

def convert(from_unit="", to_unit="", value=0):
    """
    Convert a value from one unit to another using dynamic programming.
    
    This function can handle direct conversions or find multi-step conversion paths
    through intermediate units. For example:
    - Direct: miles -> kilometers 
    - Multi-step: miles -> feet -> inches
    - Complex: grams -> pounds -> ounces
    - Temperature: celsius -> fahrenheit (using conversion functions for offsets)
    
    If from_unit or to_unit are empty strings, displays available units instead.
    
    The algorithm uses a breadth-first search to find the shortest conversion path
    between any two units in the conversion matrix.
    
    Args:
        from_unit (str): The source unit
        to_unit (str): The target unit  
        value (float): The value to convert
        
    Returns:
        float: The converted value, or None if units are invalid
        
    Raises:
        ValueError: If no conversion path exists between valid units
        
    Examples:
        >>> convert('hours', 'minutes', 2)
        120.0
        >>> convert('miles', 'inches', 1)  # Multi-step: miles -> feet -> inches
        63360.0
        >>> convert('c', 'f', 0)  # Temperature: 0°C to 32°F
        32.0
        >>> convert()  # Display available units
    """
    # If from_unit or to_unit are empty, display available units
    if not from_unit or not to_unit:
        header_lines = [
            "Convert - convert values between two units.",
            "Usage: convert(from, to, value)",
            "",
            "Available units are:"
        ]
        units_lines = _generate_units_lines()
        all_lines = header_lines + units_lines
        print_buffered(all_lines)
        return None
    
    if from_unit.lower() == to_unit.lower():
        return value
    
    # Check if units are valid before attempting conversion
    from_unit_valid = _is_valid_unit(from_unit)
    to_unit_valid = _is_valid_unit(to_unit)
    
    # Handle invalid units with helpful error messages
    if not from_unit_valid and not to_unit_valid:
        error_lines = [f"No conversion from '{from_unit}' to '{to_unit}'. Type 'units' to see available conversions."]
        print_buffered(error_lines)
        return None
    elif not from_unit_valid:
        error_lines = [f"Could not convert the unit '{from_unit}'. Did you mean one of the following?"]
        units_lines = _generate_units_lines(from_unit)
        all_lines = error_lines + units_lines
        print_buffered(all_lines)
        return None
    elif not to_unit_valid:
        error_lines = [f"Could not convert the unit '{to_unit}'. Did you mean one of the following?"]
        units_lines = _generate_units_lines(to_unit)
        all_lines = error_lines + units_lines
        print_buffered(all_lines)
        return None
    
    # Convert to internal format
    from_unit_internal = _to_internal_unit(from_unit)
    to_unit_internal = _to_internal_unit(to_unit)
    
    # Check for direct conversion first
    conversion_factor_or_func = _get_conversion_factor(from_unit_internal, to_unit_internal)
    if conversion_factor_or_func is not None:
        if callable(conversion_factor_or_func):
            return conversion_factor_or_func(value)
        else:
            return value * conversion_factor_or_func
    
    # Use Dijkstra-like algorithm to find shortest conversion path
    visited = set()
    queue = [(from_unit_internal, value)]  # (current_unit, current_value)
    
    while queue:
        current_unit, current_value = queue.pop(0)
        
        if current_unit == to_unit_internal:
            return current_value
            
        if current_unit in visited:
            continue
            
        visited.add(current_unit)
        
        # Get all units connected to current_unit
        connected_units = _get_connected_units(current_unit)
        
        for next_unit, conversion_factor_or_func in connected_units:
            if next_unit not in visited:
                if callable(conversion_factor_or_func):
                    new_value = conversion_factor_or_func(current_value)
                else:
                    new_value = current_value * conversion_factor_or_func
                queue.append((next_unit, new_value))
    
    # If we get here, no conversion path was found
    raise ValueError(f"No conversion path found from '{from_unit}' to '{to_unit}'")



def tally():
    """Count the number of characters in user input (useful for tallying)."""
    tallyCounter = input("Tally: ")
    return len(tallyCounter)

def human(number):
    """Break down a number into its major constituents (trillions, billions, millions, etc.).
    
    Args:
        number: The number to break down (int or float)
        
    Returns:
        dict: A dictionary with the major constituents, e.g.:
              {'million': 1, 'thousand': 234, 'one': 567} for 1,234,567
    """
    # Convert to integer if it's a float (remove decimal part)
    num = int(abs(number))
    
    if num == 0:
        return {'zero': 0}
    
    result = {}
    
    # Define the units in descending order
    units = [
        ('trillion', 1_000_000_000_000),
        ('billion', 1_000_000_000),
        ('million', 1_000_000),
        ('thousand', 1_000),
        ('one', 1)
    ]
    
    for unit_name, unit_value in units:
        if num >= unit_value:
            count = num // unit_value
            num = num % unit_value
            
            result[unit_name] = count
    
    return result

# Other aliases
at = asciitable
il = inputlist
avg = average

# Define constants for data sizes
kb = 1024
mb = kb * kb
gb = kb * mb
tb = kb * gb

# Define constants for large numbers
thousand = 1_000
million = 1_000_000
billion = 1_000_000_000
trillion = 1_000_000_000_000

print("""
             +------------+
             |+-------8< +|
             || pyco 0.1 ||
             |+----------+|
             | # # # # #  |
             |  # # # # # |
             +------------+
           Happy Calculating!
""")