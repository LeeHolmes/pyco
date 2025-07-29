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

def tally():
    """Count the number of characters in user input (useful for tallying)."""
    tallyCounter = input("Tally: ")
    return len(tallyCounter)

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

# Other aliases
at = asciitable
il = inputlist
avg = average

# Define constants for data sizes
kb = 1024
mb = kb * kb
gb = kb * mb
tb = kb * gb

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