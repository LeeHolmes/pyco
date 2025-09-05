# pyco calculator customizations
import sys
import math
from math import *

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
            if term in current:
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

def asciitable():
    """Display a formatted ASCII table with decimal, hexadecimal, and character representations."""
    for i in range(0, 255, 4):
        if (i > 0) and (i % 72) == 0:
            input("Press ENTER to continue...")
        if i % 72 == 0:
            print("Dec Hx C | Dec Hx C | Dec Hx C | Dec Hx C")
        print("{:3d} {:02X} {} | {:3d} {:02X} {} | {:3d} {:02X} {} | {:3d} {:02X} {}".format(
            i, i, get_printable_char(i),
            (i + 1), (i + 1), get_printable_char(i + 1),
            (i + 2), (i + 2), get_printable_char(i + 2),
            (i + 3), (i + 3), get_printable_char(i + 3)))
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

def convert_celsius_fahrenheit(celsius):
    """Convert temperature from Celsius to Fahrenheit."""
    return (celsius * 9 / 5) + 32

def convert_fahrenheit_celsius(fahrenheit):
    """Convert temperature from Fahrenheit to Celsius."""
    return (fahrenheit - 32) * 5 / 9

def convert_miles_kilometers(miles):
    """Convert distance from miles to kilometers."""
    return miles * 1.609344

def convert_kilometers_miles(kilometers):
    """Convert distance from kilometers to miles."""
    return kilometers / 1.609344

def convert_miles_feet(miles):
    """Convert distance from miles to feet."""
    return miles * 5280

def convert_feet_miles(feet):
    """Convert distance from feet to miles."""
    return feet / 5280

def convert_inches_feet(inches):
    """Convert distance from inches to feet."""
    return inches / 12

def convert_feet_inches(feet):
    """Convert distance from feet to inches."""
    return feet * 12

def convert_feet_centimeters(feet, inches=0):
    """Convert distance from feet (and optional inches) to centimeters."""
    total_inches = (feet * 12) + inches
    return total_inches * 2.54

def convert_centimeters_feet(centimeters):
    """Convert distance from centimeters to feet (returns tuple of feet, inches)."""
    total_inches = centimeters / 2.54
    feet = int(total_inches // 12)
    inches = total_inches % 12
    return (feet, inches)

def convert_feet_meters(feet, inches=0):
    """Convert distance from feet (and optional inches) to meters."""
    total_inches = (feet * 12) + inches
    return total_inches * 0.0254

def convert_meters_feet(meters):
    """Convert distance from meters to feet (returns tuple of feet, inches)."""
    total_inches = meters / 0.0254
    feet = int(total_inches // 12)
    inches = total_inches % 12
    return (feet, inches)

def convert_inches_centimeters(inches):
    """Convert distance from inches to centimeters."""
    return inches * 2.54

def convert_centimeters_inches(centimeters):
    """Convert distance from centimeters to inches."""
    return centimeters / 2.54

def convert_pounds_kilograms(pounds):
    """Convert weight from pounds to kilograms."""
    return pounds * 0.453592

def convert_kilograms_pounds(kilograms):
    """Convert weight from kilograms to pounds."""
    return kilograms / 0.453592

def convert_ounces_milliliters(ounces):
    """Convert volume from fluid ounces to milliliters."""
    return ounces * 29.5735

def convert_milliliters_ounces(milliliters):
    """Convert volume from milliliters to fluid ounces."""
    return milliliters / 29.5735

def convert_cups_ounces(cups):
    """Convert volume from cups to fluid ounces."""
    return cups * 8

def convert_ounces_cups(ounces):
    """Convert volume from fluid ounces to cups."""
    return ounces / 8

def convert_cups_milliliters(cups):
    """Convert volume from cups to milliliters."""
    return cups * 236.588

def convert_milliliters_cups(milliliters):
    """Convert volume from milliliters to cups."""
    return milliliters / 236.588

def convert_mph_kph(mph):
    """Convert speed from miles per hour to kilometers per hour."""
    return mph * 1.609344

def convert_kph_mph(kph):
    """Convert speed from kilometers per hour to miles per hour."""
    return kph / 1.609344

def convert_knots_mph(knots):
    """Convert speed from knots to miles per hour."""
    return knots * 1.15078

def convert_mph_knots(mph):
    """Convert speed from miles per hour to knots."""
    return mph / 1.15078

def convert_knots_kph(knots):
    """Convert speed from knots to kilometers per hour."""
    return knots * 1.852

def convert_kph_knots(kph):
    """Convert speed from kilometers per hour to knots."""
    return kph / 1.852

def convert_mph_mps(mph):
    """Convert speed from miles per hour to meters per second."""
    return mph * 0.44704

def convert_mps_mph(mps):
    """Convert speed from meters per second to miles per hour."""
    return mps / 0.44704

def convert_kph_mps(kph):
    """Convert speed from kilometers per hour to meters per second."""
    return kph * 0.277778

def convert_mps_kph(mps):
    """Convert speed from meters per second to kilometers per hour."""
    return mps / 0.277778

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

# Generate aliases
# Temperature conversions
c_c_f = convert_celsius_fahrenheit
c_f = convert_celsius_fahrenheit
c_f_c = convert_fahrenheit_celsius
f_c = convert_fahrenheit_celsius

# Distance conversions
c_mi_km = convert_miles_kilometers
mi_km = convert_miles_kilometers
c_km_mi = convert_kilometers_miles
km_mi = convert_kilometers_miles
c_mi_ft = convert_miles_feet
mi_ft = convert_miles_feet
c_ft_mi = convert_feet_miles
ft_mi = convert_feet_miles
c_in_ft = convert_inches_feet
in_ft = convert_inches_feet
c_ft_in = convert_feet_inches
ft_in = convert_feet_inches
c_ft_cm = convert_feet_centimeters
ft_cm = convert_feet_centimeters
c_cm_ft = convert_centimeters_feet
cm_ft = convert_centimeters_feet
c_ft_m = convert_feet_meters
ft_m = convert_feet_meters
c_m_ft = convert_meters_feet
m_ft = convert_meters_feet
c_in_cm = convert_inches_centimeters
in_cm = convert_inches_centimeters
c_cm_in = convert_centimeters_inches
cm_in = convert_centimeters_inches

# Weight conversions
c_lb_kg = convert_pounds_kilograms
lb_kg = convert_pounds_kilograms
c_kg_lb = convert_kilograms_pounds
kg_lb = convert_kilograms_pounds

# Volume conversions
c_oz_ml = convert_ounces_milliliters
oz_ml = convert_ounces_milliliters
c_ml_oz = convert_milliliters_ounces
ml_oz = convert_milliliters_ounces
c_cup_oz = convert_cups_ounces
cup_oz = convert_cups_ounces
c_oz_cup = convert_ounces_cups
oz_cup = convert_ounces_cups
c_cup_ml = convert_cups_milliliters
cup_ml = convert_cups_milliliters
c_ml_cup = convert_milliliters_cups
ml_cup = convert_milliliters_cups

# Speed conversions
c_mph_kph = convert_mph_kph
mph_kph = convert_mph_kph
c_kph_mph = convert_kph_mph
kph_mph = convert_kph_mph
c_knots_mph = convert_knots_mph
knots_mph = convert_knots_mph
c_mph_knots = convert_mph_knots
mph_knots = convert_mph_knots
c_knots_kph = convert_knots_kph
knots_kph = convert_knots_kph
c_kph_knots = convert_kph_knots
kph_knots = convert_kph_knots
c_mph_mps = convert_mph_mps
mph_mps = convert_mph_mps
c_mps_mph = convert_mps_mph
mps_mph = convert_mps_mph
c_kph_mps = convert_kph_mps
kph_mps = convert_kph_mps
c_mps_kph = convert_mps_kph
mps_kph = convert_mps_kph

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
             ┌────────────┐
             │┌───────8< ┐│
             ││ pyco 0.1 ││
             │└──────────┘│
             │ ░ ░ ░ ░ ░  │
             │  ░ ░ ░ ░ ░ │
             └────────────┘
           Happy Calculating!
""")

## Determine if pyco has been embedded via py2exe. If so,
## host the interactive console ourselves.
compiled_pyco = False
for arg in sys.argv:
    if "pyco.exe" in arg:
        compiled_pyco = True
        break
if compiled_pyco:
    import code

    vars = globals()
    vars.update(locals())
    code.interact(local = vars, banner = "")