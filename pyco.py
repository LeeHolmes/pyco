# pyco calculator customizations
import sys
import difflib
import builtins
import math
import inspect
import gzip
import base64

from math import *
from random import *

if sys.implementation.name == 'cpython':
    import statistics
    from statistics import *

    def _displayhook(value):
        if callable(value):
            _displayhook(value())
        else:
            sys.__displayhook__(value)
    sys.displayhook = _displayhook

    def _my_except_hook(exctype, value, traceback):
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
    sys.excepthook = _my_except_hook

elif sys.implementation.name == 'micropython':
    __original_repl_print__ = __repl_print__
    def _displayhook(value):
        if callable(value):
            _displayhook(value())
        else:
            __original_repl_print__(value)
    __repl_print__ = _displayhook

import types

def _get_useful_builtins():
    """Get builtins that are useful for a calculator, excluding exceptions, warnings, and modules."""
    useful = []
    for name in dir(builtins):
        if name.startswith('_'):
            continue
        obj = getattr(builtins, name, None)
        # Exclude exception and warning classes
        if isinstance(obj, type) and issubclass(obj, BaseException):
            continue
        # Exclude modules
        if isinstance(obj, types.ModuleType):
            continue
        useful.append(name)
    return useful

def _get_docstring_summary(obj):
    """Get the first line of an object's docstring as a brief summary."""
    try:
        doc = getattr(obj, '__doc__', None)
        if doc:
            # Get first non-empty line
            first_line = doc.strip().split('\n')[0].strip()
            return first_line
    except:
        pass
    return None

def _format_with_docstring(name, obj):
    """Format a name with its docstring summary or type info for variables.
    Returns a tuple of (name, description, kind) where kind is 'function', 'function_noargs', or 'variable'."""
    # For non-callable objects (variables/constants), show type info
    if not callable(obj):
        type_name = type(obj).__name__
        return (name, f"variable of type {type_name}", "variable")
    
    # For callable objects, determine if it takes arguments
    kind = "function"
    try:
        sig = inspect.signature(obj)
        # Check if all parameters have defaults or if there are no parameters
        params = list(sig.parameters.values())
        if len(params) == 0:
            kind = "function_noargs"
    except (ValueError, TypeError):
        # Some builtins don't support signature inspection
        pass
    
    # Show docstring summary
    summary = _get_docstring_summary(obj)
    if summary:
        return (name, summary, kind)
    return (name, "", kind)

def _matches_term(name, obj, term):
    """Check if term matches the name or the docstring of an object."""
    term_lower = term.lower()
    # Match against name
    if term_lower in name.lower():
        return True
    # Match against docstring
    doc = _get_docstring_summary(obj)
    if doc and term_lower in doc.lower():
        return True
    return False

def _findGlobals(term):
    """Find all global variables or functions that match the given term pattern.
    
    Returns a list of (name, description, kind) tuples.
    
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
        # Search globals (excluding modules, exceptions, and classes)
        for current in globals():
            if current.startswith('_'):
                continue
            obj = globals()[current]
            if isinstance(obj, types.ModuleType):
                continue
            # Exclude all classes
            if isinstance(obj, type):
                continue
            if _matches_term(current, obj, term):
                found.append(_format_with_docstring(current, obj))
        # Search builtins (excluding exceptions and classes)
        for current in _get_useful_builtins():
            if any(current == f[0] for f in found):
                continue
            obj = getattr(builtins, current, None)
            # Exclude classes
            if isinstance(obj, type):
                continue
            if _matches_term(current, obj, term):
                found.append(_format_with_docstring(current, obj))
        return sorted(found, key=lambda x: x[0].lower())
    
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

        # Find matching objects (search both globals and builtins)
        matching_objects = []
        all_names = set(globals().keys()) | set(_get_useful_builtins())
        for obj_name in all_names:
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
                    found_results.append((obj_name + ":", ' '.join(sorted(matching_methods)), "method"))
            except:
                pass
        
        return sorted(found_results, key=lambda x: x[0].lower())
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
        
        # Search both globals and builtins (excluding exceptions)
        results = set(globals().keys()) | set(_get_useful_builtins())

        # Handle simple wildcard patterns (no dot)
        found_results = []
        for current in results:
            if current.startswith('_'):
                continue
            
            # Get the object first for docstring matching
            if current in globals():
                obj = globals()[current]
            else:
                obj = getattr(builtins, current, None)
            
            # Skip modules
            if isinstance(obj, types.ModuleType):
                continue
            
            # Exclude all classes
            if isinstance(obj, type):
                continue
            
            # Get docstring for matching
            doc = _get_docstring_summary(obj) or ""
            
            match = False
            if starts_with_star and ends_with_star:
                # Contains match - check both name and docstring
                match = filter.lower() in current.lower() or filter.lower() in doc.lower()
            elif starts_with_star:
                # Ends with match - name only (docstring ending match doesn't make sense)
                match = current.lower().endswith(filter.lower())
            else:  # ends_with_star
                # Starts with match - name only
                match = current.lower().startswith(filter.lower())
            
            if match:
                found_results.append(_format_with_docstring(current, obj))
        
        return sorted(found_results, key=lambda x: x[0].lower())

def find(term="*"):
    """Find all global variables or functions that match the given term pattern.
    
    Supports wildcard patterns:
    - term* : finds items starting with 'term'
    - *term : finds items ending with 'term'
    - *term* : finds items containing 'term'
    - obj.method* : finds methods in 'obj' starting with 'method'
    - *obj*.method* : finds methods matching 'method*' in objects matching '*obj*'
    
    Returns a list of strings in the format "name - description".
    """
    results = _findGlobals(term)
    output = []
    for item in results:
        name = item[0]
        desc = item[1]
        if name.endswith(':'):
            # Object method pattern: "obj: method1 method2"
            output.append(f"{name} {desc}")
        elif desc:
            output.append(f"{name} - {desc}")
        else:
            output.append(name)
    return output

def _print_buffered(lines):
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
        if i % 68 == 0:
            lines.append("Dec Hx C | Dec Hx C | Dec Hx C | Dec Hx C")
        lines.append("{:3d} {:02X} {} | {:3d} {:02X} {} | {:3d} {:02X} {} | {:3d} {:02X} {}".format(
            i, i, _get_printable_char(i),
            (i + 1), (i + 1), _get_printable_char(i + 1),
            (i + 2), (i + 2), _get_printable_char(i + 2),
            (i + 3), (i + 3), _get_printable_char(i + 3)))
    
    _print_buffered(lines)
    return

def _get_printable_char(char):
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

def _get_unit_category(unit):
    """Extract the category from a unit name (category.unit format)."""
    if '.' in unit:
        return unit.split('.', 1)[0]
    # Temperature units are handled specially
    if unit in ['c', 'f', 'k']:
        return 'temperature'
    return 'unknown'

def _get_unit_name(unit):
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
        for (unit1, unit2), _ in _CONVERSION_MATRIX.items():
            # For each internal unit, map its external name to the internal format
            if '.' in unit1:  # category.unit format
                external_name = _get_unit_name(unit1)  # Extract unit part
                mapping[external_name] = unit1
            if '.' in unit2:  # category.unit format
                external_name = _get_unit_name(unit2)  # Extract unit part
                mapping[external_name] = unit2
        
        _external_to_internal_cache = mapping
    
    return _external_to_internal_cache

def _is_valid_unit(unit):
    """Check if a unit is valid and can be converted."""
    internal_unit = _to_internal_unit(unit)
    
    # Check if unit appears in conversion matrix
    for (unit1, unit2), _ in _CONVERSION_MATRIX.items():
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

def _get_units_by_category(category):
    """Get all units belonging to a specific category."""
    all_units = set()
    # Get units from conversion matrix (temperature units are now included)
    for (unit1, unit2), _ in _CONVERSION_MATRIX.items():
        all_units.add(unit1)
        all_units.add(unit2)
    
    # Filter by category and return external unit names
    category_units = [unit for unit in all_units if _get_unit_category(unit) == category]
    return [_get_unit_name(unit) for unit in category_units]

def _get_all_categories():
    """Get all available unit categories."""
    all_units = set()
    # Get units from conversion matrix (temperature units are now included)
    for (unit1, unit2), _ in _CONVERSION_MATRIX.items():
        all_units.add(unit1)
        all_units.add(unit2)
    
    return list(set(_get_unit_category(unit) for unit in all_units))

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
_CONVERSION_MATRIX = {
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

_CURRENCY_DATA = "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"

# Unit abbreviation to full English name mapping
_UNIT_NAMES = {
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

# Timezone data: key -> (full_name, UTC offset in hours)
# Keys use underscores for multi-word names (e.g., 'china_cst')
# Ambiguous abbreviations are disambiguated with a prefix (e.g., 'china_cst' vs 'cuba_cst')
# All ambiguous codes require disambiguation - there are no "default" versions
_TIMEZONE_DATA = {
    # North America (unambiguous)
    'pst': ('Pacific Standard Time', -8),
    'pdt': ('Pacific Daylight Time', -7),
    'mst': ('Mountain Standard Time', -7),
    'mdt': ('Mountain Daylight Time', -6),
    'cdt': ('Central Daylight Time', -5),
    'est': ('Eastern Standard Time', -5),
    'edt': ('Eastern Daylight Time', -4),
    'akst': ('Alaska Standard Time', -9),
    'akdt': ('Alaska Daylight Time', -8),
    'hst': ('Hawaii Standard Time', -10),
    
    # CST variants (all disambiguated)
    'central_cst': ('Central Standard Time', -6),
    'china_cst': ('China Standard Time', 8),
    'cuba_cst': ('Cuba Standard Time', -5),
    
    # Europe (unambiguous)
    'gmt': ('Greenwich Mean Time', 0),
    'utc': ('Coordinated Universal Time', 0),
    'wet': ('Western European Time', 0),
    'west': ('Western European Summer Time', 1),
    'cet': ('Central European Time', 1),
    'cest': ('Central European Summer Time', 2),
    'eet': ('Eastern European Time', 2),
    'eest': ('Eastern European Summer Time', 3),
    'msk': ('Moscow Time', 3),
    
    # BST variants (all disambiguated)
    'british_bst': ('British Summer Time', 1),
    'bangladesh_bst': ('Bangladesh Standard Time', 6),
    
    # IST variants (all disambiguated)
    'indian_ist': ('Indian Standard Time', 5.5),
    'irish_ist': ('Irish Standard Time', 1),
    'israel_ist': ('Israel Standard Time', 2),
    
    # Asia/Pacific (unambiguous)
    'jst': ('Japan Standard Time', 9),
    'kst': ('Korea Standard Time', 9),
    'hkt': ('Hong Kong Time', 8),
    'sgt': ('Singapore Time', 8),
    'pht': ('Philippine Time', 8),
    'wib': ('Western Indonesian Time', 7),
    'wita': ('Central Indonesian Time', 8),
    'wit': ('Eastern Indonesian Time', 9),
    'ict': ('Indochina Time', 7),
    'npt': ('Nepal Time', 5.75),
    'pkt': ('Pakistan Standard Time', 5),
    
    # Australia/NZ (unambiguous)
    'aest': ('Australian Eastern Standard Time', 10),
    'aedt': ('Australian Eastern Daylight Time', 11),
    'acst': ('Australian Central Standard Time', 9.5),
    'acdt': ('Australian Central Daylight Time', 10.5),
    'awst': ('Australian Western Standard Time', 8),
    'nzst': ('New Zealand Standard Time', 12),
    'nzdt': ('New Zealand Daylight Time', 13),
    
    # Other (unambiguous)
    'ast': ('Atlantic Standard Time', -4),
    'adt': ('Atlantic Daylight Time', -3),
    'nst': ('Newfoundland Standard Time', -3.5),
    'ndt': ('Newfoundland Daylight Time', -2.5),
    'art': ('Argentina Time', -3),
    'brt': ('Brasilia Time', -3),
    'cat': ('Central Africa Time', 2),
    'eat': ('East Africa Time', 3),
    'wat': ('West Africa Time', 1),
    'sast': ('South African Standard Time', 2),
    'gulf_gst': ('Gulf Standard Time', 4),
    'aft': ('Afghanistan Time', 4.5),
    'irst': ('Iran Standard Time', 3.5),
    'irdt': ('Iran Daylight Time', 4.5),
    'akt': ('Arabia Standard Time', 3),
    'uzt': ('Uzbekistan Time', 5),
    'get': ('Georgia Standard Time', 4),
    'amt': ('Armenia Time', 4),
    'azt': ('Azerbaijan Time', 4),
    'fjt': ('Fiji Time', 12),
    'tot': ('Tonga Time', 13),
    'sst': ('Samoa Standard Time', -11),
    'chst': ('Chamorro Standard Time', 10),
    'wst': ('Western Standard Time', 8),
}

# Top timezones to show in units() when not searching (common world clock cities)
# NYC, LA, London, Paris, Dubai, Mumbai, Hong Kong, Tokyo, Sydney
_TOP_TIMEZONES = ['est', 'pst', 'gmt', 'cet', 'gulf_gst', 'indian_ist', 'hkt', 'jst', 'aest']

def _normalize_timezone_input(unit_str):
    """Convert user input like 'China CST' to internal key 'china_cst'."""
    return unit_str.lower().replace(' ', '_').replace('-', '_')

def _get_timezone_display(tz_key):
    """Get display format for a timezone key. Shows just the abbreviation (e.g., 'china_cst' -> 'CST')."""
    if '_' in tz_key:
        # Just show the abbreviation part for clean UI
        abbrev = tz_key.split('_')[-1].upper()
        return abbrev
    return tz_key.upper()

def _get_timezone_input_format(tz_key):
    """Get the user input format for a timezone key. E.g., 'china_cst' -> 'China CST'."""
    if '_' in tz_key:
        parts = tz_key.split('_')
        # Last part is the abbreviation (uppercase), rest is qualifier (title case)
        qualifier = ' '.join(p.title() for p in parts[:-1])
        abbrev = parts[-1].upper()
        return f"{qualifier} {abbrev}"
    return tz_key.upper()

def _format_utc_offset(offset):
    """Format a UTC offset as a string like 'UTC+05:30' or 'UTC-08:00'."""
    sign = '+' if offset >= 0 else '-'
    abs_offset = abs(offset)
    hours = int(abs_offset)
    minutes = int((abs_offset - hours) * 60)
    if minutes:
        return f"UTC{sign}{hours:02d}:{minutes:02d}"
    return f"UTC{sign}{hours}"

def _is_timezone(unit_str):
    """Check if a unit string refers to a timezone."""
    normalized = _normalize_timezone_input(unit_str)
    return normalized in _TIMEZONE_DATA

def _get_timezone_offset(unit_str):
    """Get the UTC offset for a timezone. Returns None if not a timezone."""
    normalized = _normalize_timezone_input(unit_str)
    if normalized in _TIMEZONE_DATA:
        return _TIMEZONE_DATA[normalized][1]
    return None

def _matches_search(unit_abbrev, unit_full_name, search_term):
    """Check if unit matches search term using fuzzy string matching for typos."""
    if not search_term:
        return True
    
    search_lower = search_term.lower()
    unit_abbrev_lower = unit_abbrev.lower() if unit_abbrev else ''
    unit_full_name_lower = unit_full_name.lower() if unit_full_name else ''
    
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

# Top currencies to show in units() when not searching
_TOP_CURRENCIES = ['$usd', '$eur', '$gbp', '$jpy', '$cad', '$aud', '$chf', '$cny']

def _generate_units_lines(search="", categories=None):
    """
    Generate lines for units display with optional search filtering.
    
    Args:
        search (str): Optional search term to filter units.
        categories (list): Optional list of categories to include. If None, includes all.
        
    Returns:
        list: Array of strings representing the units display
    """
    lines = [""]
    
    # Get all categories plus timezone
    if categories is None:
        categories = _get_all_categories()
        if 'timezone' not in categories:
            categories.append('timezone')
        categories.sort()  # Sort alphabetically
    
    for category in categories:
        # Get all units for this category
        if category == 'currency':
            # Country-specific entries for searching: $eur_germany, $usd_united_states, etc.
            all_units = [k for k in _UNIT_NAMES.keys() if k.startswith('$') and '_' in k]
        elif category == 'timezone':
            all_units = list(_TIMEZONE_DATA.keys())
        else:
            all_units = _get_units_by_category(category)
        
        # Filter based on search term
        if search:
            units = []
            for unit in all_units:
                if category == 'timezone':
                    tz_name, tz_offset = _TIMEZONE_DATA[unit]
                    input_format = _get_timezone_input_format(unit)
                    full_name = f"{tz_name} ({_format_utc_offset(tz_offset)})"
                    if _matches_search(input_format, full_name, search):
                        units.append(unit)
                else:
                    full_name = _UNIT_NAMES.get(unit, unit)
                    if _matches_search(unit, full_name, search):
                        units.append(unit)
        else:
            if category == 'currency':
                # Show only top currencies (base codes) when not searching
                units = [c for c in _TOP_CURRENCIES if c in _UNIT_NAMES]
            elif category == 'timezone':
                # Show only top timezones when not searching
                units = [tz for tz in _TOP_TIMEZONES if tz in _TIMEZONE_DATA]
            else:
                units = all_units
        
        units.sort()
        
        if not units:
            continue
        
        lines.append(f"{category.upper()}:")
        
        # Format units in 2-column layout
        i = 0
        while i < len(units):
            unit1 = units[i]
            if category == 'timezone':
                tz_name1, tz_offset1 = _TIMEZONE_DATA[unit1]
                display_unit1 = _get_timezone_display(unit1)
                full_name1 = f"{tz_name1} ({_format_utc_offset(tz_offset1)})"
            elif category == 'currency':
                full_name1 = _UNIT_NAMES.get(unit1, unit1)
                display_unit1 = unit1.split('_')[0].upper() if '_' in unit1 else unit1.upper()
            else:
                full_name1 = _UNIT_NAMES.get(unit1, unit1)
                display_unit1 = unit1
            col1 = f"{display_unit1:<5} {full_name1}"
            
            if len(col1) > 18:
                lines.append(f"  {col1}")
                i += 1
            elif i + 1 < len(units):
                unit2 = units[i + 1]
                if category == 'timezone':
                    tz_name2, tz_offset2 = _TIMEZONE_DATA[unit2]
                    display_unit2 = _get_timezone_display(unit2)
                    full_name2 = f"{tz_name2} ({_format_utc_offset(tz_offset2)})"
                elif category == 'currency':
                    full_name2 = _UNIT_NAMES.get(unit2, unit2)
                    display_unit2 = unit2.split('_')[0].upper() if '_' in unit2 else unit2.upper()
                else:
                    full_name2 = _UNIT_NAMES.get(unit2, unit2)
                    display_unit2 = unit2
                col2 = f"{display_unit2:<5} {full_name2}"
                
                if len(col2) > 18:
                    lines.append(f"  {col1}")
                    i += 1
                else:
                    total_line = f"  {col1:<18} {col2}"
                    if len(total_line) <= 37:
                        lines.append(total_line)
                        i += 2
                    else:
                        lines.append(f"  {col1}")
                        i += 1
            else:
                lines.append(f"  {col1}")
                i += 1
        
        if category == 'currency' and not search:
            lines.append("  Use currencies() to see more.")
        
        if category == 'timezone' and not search:
            lines.append("  Use timezones() to see more.")
        
        lines.append("")
    
    return lines

def units(search=""):
    """
    Print a compact 2-column summary of available units with their human-readable names.
    
    Args:
        search (str): Optional search term to filter units. If empty, shows all units.
                     Matches against both unit abbreviations and full names (case-insensitive).
    """
    _ensure_currency_data_loaded()
    lines = _generate_units_lines(search)
    _print_buffered(lines)

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
    if (from_unit, to_unit) in _CONVERSION_MATRIX:
        return _CONVERSION_MATRIX[(from_unit, to_unit)]
    
    # Check reverse direction (invert the factor or find reverse function)
    if (to_unit, from_unit) in _CONVERSION_MATRIX:
        factor_or_func = _CONVERSION_MATRIX[(to_unit, from_unit)]
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
    for (unit1, unit2), factor_or_func in _CONVERSION_MATRIX.items():
        if unit1 == unit:
            connections.append((unit2, factor_or_func))
        elif unit2 == unit:
            if callable(factor_or_func):
                # For functions, we don't invert - the reverse should be explicitly defined
                continue
            else:
                connections.append((unit1, 1/factor_or_func))
    
    return connections

import ast
import keyword
import re

def _escape_keywords(unit_str):
    """Escape Python keywords and special characters in a unit string for parsing."""
    escaped_str = unit_str
    escaped_keywords = {}
    
    # Escape $ (currency prefix) - replace $xxx with _dollar_xxx
    dollar_pattern = r'\$([a-zA-Z]+)'
    for match in re.finditer(dollar_pattern, escaped_str):
        original = match.group(0)  # e.g., $USD
        code = match.group(1)  # e.g., USD
        replacement = f'_dollar_{code}'
        escaped_keywords[replacement] = original
    escaped_str = re.sub(dollar_pattern, r'_dollar_\1', escaped_str)
    
    # Escape Python keywords
    for kw in keyword.kwlist:
        pattern = r'\b' + kw + r'\b'
        if re.search(pattern, escaped_str):
            replacement = f'{kw}_escaped_unit_'
            escaped_keywords[replacement] = kw
            escaped_str = re.sub(pattern, replacement, escaped_str)
    return escaped_str, escaped_keywords

def _unescape_keywords(text, escaped_keywords):
    """Restore escaped keywords and special characters back to their original form."""
    for replacement, original in escaped_keywords.items():
        text = text.replace(replacement, original)
    return text

def _get_unit_conversion_factor(from_unit, to_unit):
    """
    Get the conversion factor from one simple unit to another.
    Returns the factor such that: from_value * factor = to_value
    Returns None if conversion is not possible.
    
    For function-based conversions (like temperature), computes the scale factor
    using f(1) - f(0), which gives the rate of change.
    """
    from_unit = from_unit.strip()
    to_unit = to_unit.strip()
    
    if from_unit.lower() == to_unit.lower():
        return 1.0
    
    if not _is_valid_unit(from_unit) or not _is_valid_unit(to_unit):
        return None
    
    try:
        from_internal = _to_internal_unit(from_unit)
        to_internal = _to_internal_unit(to_unit)
        
        # Check for direct conversion first
        factor = _get_conversion_factor(from_internal, to_internal)
        if factor is not None:
            if callable(factor):
                # For function-based conversions (like temperature with offset),
                # compute the scale factor: f(1) - f(0) gives the rate of change
                return factor(1) - factor(0)
            return factor
        
        # Try multi-step conversion
        visited = set()
        queue = [(from_internal, 1.0)]
        
        while queue:
            current_unit, current_factor = queue.pop(0)
            
            if current_unit == to_internal:
                return current_factor
            
            if current_unit in visited:
                continue
            
            visited.add(current_unit)
            
            connected = _get_connected_units(current_unit)
            for next_unit, conv in connected:
                if next_unit not in visited:
                    if callable(conv):
                        # Compute scale factor from function
                        scale = conv(1) - conv(0)
                        queue.append((next_unit, current_factor * scale))
                    else:
                        queue.append((next_unit, current_factor * conv))
        
        return None
    except:
        return None

def _evaluate_unit_expression(expr_str):
    """
    Parse a unit expression and return a function that computes the conversion factor.
    
    Returns a tuple: (is_valid, eval_func) where eval_func takes a target expression
    and returns the conversion factor, or None if not computable.
    """
    escaped_str, escaped_keywords = _escape_keywords(expr_str)
    
    try:
        tree = ast.parse(escaped_str, mode='eval')
    except SyntaxError:
        return (False, None)
    
    def get_unit_from_node(node):
        """Extract unit name from an AST node."""
        if isinstance(node, ast.Name):
            return _unescape_keywords(node.id, escaped_keywords)
        elif isinstance(node, ast.BinOp):
            # Return the unparsed expression
            unparsed = ast.unparse(node) if hasattr(ast, 'unparse') else None
            if unparsed:
                return _unescape_keywords(unparsed, escaped_keywords)
        return None
    
    return (True, tree.body)

def _compute_conversion_factor(from_expr, to_expr):
    """
    Compute the conversion factor between two unit expressions.
    
    Recursively handles expressions like "(ft*in)/h" -> "(m*cm)/s"
    
    Returns the conversion factor, or None if conversion is not possible.
    """
    from_escaped, from_keywords = _escape_keywords(from_expr)
    to_escaped, to_keywords = _escape_keywords(to_expr)
    
    try:
        from_tree = ast.parse(from_escaped, mode='eval').body
        to_tree = ast.parse(to_escaped, mode='eval').body
    except SyntaxError:
        return None
    
    def get_factor(from_node, to_node):
        """Recursively compute conversion factor between two AST nodes."""
        # Both are simple names (base case)
        if isinstance(from_node, ast.Name) and isinstance(to_node, ast.Name):
            from_unit = _unescape_keywords(from_node.id, from_keywords)
            to_unit = _unescape_keywords(to_node.id, to_keywords)
            return _get_unit_conversion_factor(from_unit, to_unit)
        
        # Both are binary operations
        if isinstance(from_node, ast.BinOp) and isinstance(to_node, ast.BinOp):
            # Must have the same operator type
            if type(from_node.op) != type(to_node.op):
                return None
            
            # Recursively compute factors for left and right operands
            left_factor = get_factor(from_node.left, to_node.left)
            right_factor = get_factor(from_node.right, to_node.right)
            
            if left_factor is None or right_factor is None:
                return None
            
            # Combine based on operator
            if isinstance(from_node.op, ast.Mult):
                # (A * B) -> (C * D): factor = (C/A) * (D/B)
                return left_factor * right_factor
            elif isinstance(from_node.op, ast.Div):
                # (A / B) -> (C / D): factor = (C/A) / (D/B) = (C/A) * (B/D)
                return left_factor / right_factor
            else:
                return None
        
        # Mismatched structures
        return None
    
    return get_factor(from_tree, to_tree)

def _is_combined_unit(unit_str):
    """Check if a unit string represents a combined unit (e.g., "mi/h" or "ft*lb")."""
    escaped_str, _ = _escape_keywords(unit_str)
    try:
        tree = ast.parse(escaped_str, mode='eval')
        return isinstance(tree.body, ast.BinOp)
    except SyntaxError:
        return False

def _get_all_units_in_expression(expr_str):
    """Extract all unit names from a unit expression."""
    escaped_str, escaped_keywords = _escape_keywords(expr_str)
    
    try:
        tree = ast.parse(escaped_str, mode='eval')
    except SyntaxError:
        return [expr_str]
    
    units = []
    
    def extract_names(node):
        if isinstance(node, ast.Name):
            units.append(_unescape_keywords(node.id, escaped_keywords))
        elif isinstance(node, ast.BinOp):
            extract_names(node.left)
            extract_names(node.right)
    
    extract_names(tree.body)
    return units

def _convert_simple(from_unit, to_unit, value):
    """
    Convert a value from one simple unit to another.
    
    This is the internal conversion function that handles single units only.
    Uses BFS to find conversion path, applying functions directly for 
    conversions with offsets (like temperature).
    
    Args:
        from_unit (str): The source unit
        to_unit (str): The target unit  
        value (float): The value to convert
        
    Returns:
        float: The converted value, or None if units are invalid
        
    Raises:
        ValueError: If no conversion path exists between valid units
    """
    if from_unit.lower() == to_unit.lower():
        return value
    
    # Check if units are valid before attempting conversion
    from_unit_valid = _is_valid_unit(from_unit)
    to_unit_valid = _is_valid_unit(to_unit)
    
    if not from_unit_valid or not to_unit_valid:
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
    
    # Use BFS to find conversion path, applying functions/factors to the value
    visited = set()
    queue = [(from_unit_internal, value)]
    
    while queue:
        current_unit, current_value = queue.pop(0)
        
        if current_unit == to_unit_internal:
            return current_value
        
        if current_unit in visited:
            continue
        
        visited.add(current_unit)
        
        connected = _get_connected_units(current_unit)
        for next_unit, conv in connected:
            if next_unit not in visited:
                if callable(conv):
                    new_value = conv(current_value)
                else:
                    new_value = current_value * conv
                queue.append((next_unit, new_value))
    
    # If we get here, no conversion path was found
    raise ValueError(f"No conversion path found from '{from_unit}' to '{to_unit}'")

def convert(from_unit="", to_unit="", value=0):
    """
    Convert a value from one unit to another using dynamic programming.
    
    This function can handle direct conversions or find multi-step conversion paths
    through intermediate units. It also supports combined units:
    - Ratio units like "mi/h" or "m/s" (division)
    - Product units like "ft*lb" or "m*kg" (multiplication)
    
    For example:
    - Direct: miles -> kilometers 
    - Multi-step: miles -> feet -> inches
    - Complex: grams -> pounds -> ounces
    - Temperature: celsius -> fahrenheit (using conversion functions for offsets)
    - Ratio units: mi/h -> m/s, km/h -> mph
    - Product units: ft*lb -> m*kg, in*oz -> cm*g
    
    If from_unit or to_unit are empty strings, displays available units instead.
    
    The algorithm uses a breadth-first search to find the shortest conversion path
    between any two units in the conversion matrix.
    
    Args:
        from_unit (str): The source unit (can be simple like "mi", ratio like "mi/h", or product like "ft*lb")
        to_unit (str): The target unit (can be simple like "km", ratio like "m/s", or product like "m*kg")
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
        >>> convert('mi/h', 'm/s', 10)  # Ratio units: 10 mph to m/s
        4.4704
        >>> convert('ft*lb', 'm*kg', 1)  # Product units: foot-pounds to meter-kg
        0.1382549544
        >>> convert()  # Display available units
    """
    # If from_unit or to_unit are empty, display available units
    if not from_unit or not to_unit:
        header_lines = [
            "Convert - convert values between two units.",
            "Usage: convert(from, to, value)",
            "",
            "Supports combined units:",
            "  Ratio units (/):",
            "    convert('mi/h', 'm/s', 60)  # 60 mph to m/s",
            "    convert('km/h', 'mi/h', 100)  # 100 km/h to mph",
            "  Product units (*):",
            "    convert('ft*lb', 'm*kg', 1)  # foot-pounds to meter-kg",
            "    convert('in*oz', 'cm*g', 10)  # inch-ounces to cm-grams",
            "",
            "Available units are:"
        ]
        units_lines = _generate_units_lines()
        all_lines = header_lines + units_lines
        _print_buffered(all_lines)
        return None
    
    # Lazy-load currency data for currency conversions
    _ensure_currency_data_loaded()
    
    if from_unit.lower() == to_unit.lower():
        return value
    
    # Handle timezone conversions (additive offset, not multiplicative)
    from_is_tz = _is_timezone(from_unit)
    to_is_tz = _is_timezone(to_unit)
    
    if from_is_tz or to_is_tz:
        if not from_is_tz:
            # Check if from_unit looks like a timezone attempt - suggest close matches
            error_lines = [f"Could not convert the timezone '{from_unit}'. Did you mean one of the following?"]
            units_lines = _generate_units_lines(from_unit, categories=['timezone'])
            all_lines = error_lines + units_lines
            _print_buffered(all_lines)
            return None
        if not to_is_tz:
            # Check if to_unit looks like a timezone attempt - suggest close matches
            error_lines = [f"Could not convert the timezone '{to_unit}'. Did you mean one of the following?"]
            units_lines = _generate_units_lines(to_unit, categories=['timezone'])
            all_lines = error_lines + units_lines
            _print_buffered(all_lines)
            return None
        
        from_offset = _get_timezone_offset(from_unit)
        to_offset = _get_timezone_offset(to_unit)
        
        # Timezone conversion: add the difference in offsets
        # If PST (-8) to China CST (+8), difference is +16
        offset_diff = to_offset - from_offset
        return value + offset_diff
    
    # Check if we're dealing with combined units (expressions with * or /)
    from_is_combined = _is_combined_unit(from_unit)
    to_is_combined = _is_combined_unit(to_unit)
    
    # Handle combined unit conversions (e.g., mi/h -> m/s or ft*lb -> m*kg or (ft*in)/h -> (m*cm)/s)
    if from_is_combined or to_is_combined:
        # Both must be combined units for combined conversion
        if from_is_combined != to_is_combined:
            error_lines = [f"Cannot convert between simple and combined units: '{from_unit}' to '{to_unit}'"]
            _print_buffered(error_lines)
            return None
        
        # Check if all component units are valid
        from_units = _get_all_units_in_expression(from_unit)
        to_units = _get_all_units_in_expression(to_unit)
        
        invalid_units = []
        for unit in from_units + to_units:
            if not _is_valid_unit(unit):
                invalid_units.append(unit)
        
        if invalid_units:
            error_lines = [f"Invalid unit(s): {', '.join(invalid_units)}. Type 'units' to see available conversions."]
            _print_buffered(error_lines)
            return None
        
        # Compute the conversion factor using recursive AST evaluation
        factor = _compute_conversion_factor(from_unit, to_unit)
        
        if factor is None:
            error_lines = [f"Cannot convert '{from_unit}' to '{to_unit}'. Expressions must have matching structure."]
            _print_buffered(error_lines)
            return None
        
        return value * factor
    
    # Handle simple unit conversion
    # Check if units are valid before attempting conversion
    from_unit_valid = _is_valid_unit(from_unit)
    to_unit_valid = _is_valid_unit(to_unit)
    
    # Handle invalid units with helpful error messages
    if not from_unit_valid and not to_unit_valid:
        error_lines = [f"No conversion from '{from_unit}' to '{to_unit}'. Type 'units' to see available conversions."]
        _print_buffered(error_lines)
        return None
    elif not from_unit_valid:
        error_lines = [f"Could not convert the unit '{from_unit}'. Did you mean one of the following?"]
        units_lines = _generate_units_lines(from_unit)
        all_lines = error_lines + units_lines
        _print_buffered(all_lines)
        return None
    elif not to_unit_valid:
        error_lines = [f"Could not convert the unit '{to_unit}'. Did you mean one of the following?"]
        units_lines = _generate_units_lines(to_unit)
        all_lines = error_lines + units_lines
        _print_buffered(all_lines)
        return None
    
    try:
        return _convert_simple(from_unit, to_unit, value)
    except ValueError as e:
        raise e



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

# Flag to track if currency data has been loaded
_CURRENCY_DATA_LOADED = False

def _ensure_currency_data_loaded():
    """Lazy-load currency data on first use."""
    global _CURRENCY_DATA_LOADED
    if _CURRENCY_DATA_LOADED:
        return
    _CURRENCY_DATA_LOADED = True
    _load_currency_data()

def _load_currency_data():
    """Decode and load currency exchange rates into the conversion matrix and unit names."""
    try:
        import json
        # Decode base64 and decompress gzip
        compressed = base64.b64decode(_CURRENCY_DATA)
        json_bytes = gzip.decompress(compressed)
        data = json.loads(json_bytes.decode('utf-8'))
        
        records = data.get('data', [])
        
        # Track seen codes for conversion matrix (only add once per code)
        seen_codes = set()
        
        # Add each currency to the conversion matrix and unit names
        # Currency codes are prefixed with "$" to avoid conflicts (e.g., $CAD, $CUP)
        for record in records:
            currency_code = record.get('currency_code')
            exchange_rate = record.get('exchange_rate')
            country = record.get('country') or ''
            currency = record.get('currency') or ''
            
            if currency_code:
                code_lower = currency_code.lower()
                prefixed_code = f"${code_lower}"
                
                # Store country-specific entry for display/search: $eur_germany -> "Germany (Euro)"
                country_key = country.lower().replace(' ', '_').replace('-', '_')
                display_key = f"{prefixed_code}_{country_key}"
                _UNIT_NAMES[display_key] = f"{country} ({currency})"
                
                # Add to conversion matrix only once per code
                if code_lower not in seen_codes:
                    seen_codes.add(code_lower)
                    
                    # Also store the base code for conversion lookups
                    _UNIT_NAMES[prefixed_code] = f"{country} ({currency})"
                    
                    if exchange_rate and currency_code.upper() != 'USD':
                        try:
                            rate = float(exchange_rate)
                            # USD to foreign currency: 1 USD = rate foreign
                            _CONVERSION_MATRIX[('currency.$usd', f'currency.{prefixed_code}')] = rate
                        except (ValueError, TypeError):
                            pass
        
        # Make sure USD is in unit names
        _UNIT_NAMES['$usd'] = 'United States (Dollar)'
        _UNIT_NAMES['$usd_united_states'] = 'United States (Dollar)'
            
    except Exception:
        # Silently ignore errors loading currency data
        pass

def currencies(search=""):
    """
    Print available currencies. Convenience function that shows only currency units.
    
    Args:
        search (str): Optional search term to filter currencies.
    """
    _ensure_currency_data_loaded()
    
    lines = ["", "CURRENCIES:"]
    
    # Get all currency entries from _UNIT_NAMES (keys with $code_country pattern)
    entries = []  # List of (code, full_name) tuples
    for unit_key, full_name in _UNIT_NAMES.items():
        if unit_key.startswith('$') and '_' in unit_key:
            base_code = unit_key.split('_')[0]  # $eur
            if search:
                if _matches_search(unit_key, full_name, search):
                    entries.append((base_code, full_name))
            else:
                entries.append((base_code, full_name))
    
    if not entries:
        lines.append("  No matching currencies found.")
    else:
        entries.sort(key=lambda x: x[1])  # Sort by full_name (country)
        for code, full_name in entries:
            display_code = code.upper()
            lines.append(f"  {display_code:<5} {full_name}")
    
    lines.append("")
    _print_buffered(lines)

def timezones(search=""):
    """
    Print available timezones. Convenience function that shows all timezone units.
    
    Args:
        search (str): Optional search term to filter timezones.
    """
    lines = ["", "TIMEZONES:"]
    
    entries = []  # List of (display, full_name) tuples
    for tz_key, (tz_name, tz_offset) in _TIMEZONE_DATA.items():
        display = _get_timezone_display(tz_key)
        input_format = _get_timezone_input_format(tz_key)
        full_name = f"{tz_name} ({_format_utc_offset(tz_offset)})"
        if search:
            if _matches_search(input_format, full_name, search):
                entries.append((display, full_name))
        else:
            entries.append((display, full_name))
    
    if not entries:
        lines.append("  No matching timezones found.")
    else:
        entries.sort(key=lambda x: x[1])  # Sort by full name
        for display, full_name in entries:
            lines.append(f"  {display:<6} {full_name}")
    
    lines.append("")
    _print_buffered(lines)

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