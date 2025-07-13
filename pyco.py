# pyco calculator customizations
import sys
import math
import statistics
from math import *
from statistics import *

if sys.implementation.name == 'cpython':
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
                term = cleanvalue
                lastDot = term.rfind('.')
                filter = ""
                results = []
                
                # Determine wildcard pattern
                starts_with_star = term.startswith("*")
                ends_with_star = term.endswith("*")
                
                if lastDot != -1:
                    # Handle object.method* or *object.method or *object.method* patterns
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
                    elif obj_starts_with_star:
                        obj_filter = object_part[1:]    # Remove leading *
                    elif obj_ends_with_star:
                        obj_filter = object_part[:-1]   # Remove trailing *
                    else:
                        obj_filter = object_part
                    
                    # Extract method filter
                    if method_starts_with_star and method_ends_with_star:
                        method_filter = method_part[1:-1]  # Remove both * characters
                    elif method_starts_with_star:
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
                        elif obj_starts_with_star:
                            obj_match = obj_name.lower().endswith(obj_filter.lower())
                        elif obj_ends_with_star:
                            obj_match = obj_name.lower().startswith(obj_filter.lower())
                        else:
                            obj_match = obj_name.lower() == obj_filter.lower()
                        
                        if obj_match:
                            matching_objects.append(obj_name)
                    
                    # For each matching object, find matching methods
                    found = False
                    for obj_name in matching_objects:
                        try:
                            obj_methods = dir(eval(obj_name))
                            matching_methods = []
                            
                            for method_name in obj_methods:
                                method_match = False
                                if method_starts_with_star and method_ends_with_star:
                                    method_match = method_filter.lower() in method_name.lower()
                                elif method_starts_with_star:
                                    method_match = method_name.lower().endswith(method_filter.lower())
                                elif method_ends_with_star:
                                    method_match = method_name.lower().startswith(method_filter.lower())
                                else:
                                    method_match = method_name.lower() == method_filter.lower()
                                
                                if method_match:
                                    matching_methods.append(method_name)
                            
                            if matching_methods:
                                print(f"{obj_name}: ", end="")
                                print(" ".join(matching_methods))
                                found = True
                        except:
                            pass
                else:
                    # Handle *filter*, *filter, or filter* patterns
                    if starts_with_star and ends_with_star:
                        filter = term[1:-1]  # Remove both * characters
                    elif starts_with_star:
                        filter = term[1:]    # Remove leading *
                    else:  # ends_with_star
                        filter = term[:-1]   # Remove trailing *
                    
                    results = globals().keys()

                # Handle simple wildcard patterns (no dot)
                found = False
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
                        print(current, end = " ")
                        found = True
                if found:
                    print()
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
    """Find all global variables or functions that contain the given term in their name."""
    found = []
    for current in globals():
        if term in current:
            found.append(current)
    return found

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
def at():
    """Alias for asciitable() - Display ASCII table."""
    return asciitable()

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
def il():
    """Alias for inputlist() - Read a list of numbers."""
    return inputlist()


def average(list):
    """Calculate the average (mean) of a list of numbers."""
    return mean(list)
def avg(list):
    """Alias for average() - Calculate the average of a list."""
    return average(list)

def convert_celsius_fahrenheit(celsius):
    """Convert temperature from Celsius to Fahrenheit."""
    return (celsius * 9 / 5) + 32
def c_c_f(celsius):
    """Alias for convert_celsius_fahrenheit() - Convert Celsius to Fahrenheit."""
    return convert_celsius_fahrenheit(celsius)
def c_f(celsius):
    """Short alias for convert_celsius_fahrenheit() - Convert Celsius to Fahrenheit."""
    return c_c_f(celsius)

def convert_fahrenheit_celsius(fahrenheit):
    """Convert temperature from Fahrenheit to Celsius."""
    return (fahrenheit - 32) * 5 / 9
def c_f_c(fahrenheit):
    """Alias for convert_fahrenheit_celsius() - Convert Fahrenheit to Celsius."""
    return convert_fahrenheit_celsius(fahrenheit)
def f_c(fahrenheit):
    """Short alias for convert_fahrenheit_celsius() - Convert Fahrenheit to Celsius."""
    return c_f_c(fahrenheit)

def convert_miles_kilometers(miles):
    """Convert distance from miles to kilometers."""
    return miles * 1.609344
def c_mi_km(miles):
    """Alias for convert_miles_kilometers() - Convert miles to kilometers."""
    return convert_miles_kilometers(miles)
def mi_km(miles):
    """Short alias for convert_miles_kilometers() - Convert miles to kilometers."""
    return c_mi_km(miles)

def convert_kilometers_miles(kilometers):
    """Convert distance from kilometers to miles."""
    return kilometers / 1.609344
def c_km_mi(kilometers):
    """Alias for convert_kilometers_miles() - Convert kilometers to miles."""
    return convert_kilometers_miles(kilometers)
def km_mi(kilometers):
    """Short alias for convert_kilometers_miles() - Convert kilometers to miles."""
    return c_km_mi(kilometers)

def convert_miles_feet(miles):
    """Convert distance from miles to feet."""
    return miles * 5280
def c_mi_ft(miles):
    """Alias for convert_miles_feet() - Convert miles to feet."""
    return convert_miles_feet(miles)
def mi_ft(miles):
    """Short alias for convert_miles_feet() - Convert miles to feet."""
    return c_mi_ft(miles)

def convert_feet_miles(feet):
    """Convert distance from feet to miles."""
    return feet / 5280
def c_ft_mi(feet):
    """Alias for convert_feet_miles() - Convert feet to miles."""
    return convert_feet_miles(feet)
def ft_mi(feet):
    """Short alias for convert_feet_miles() - Convert feet to miles."""
    return c_ft_mi(feet)

def convert_inches_feet(inches):
    """Convert distance from inches to feet."""
    return inches / 12
def c_in_ft(inches):
    """Alias for convert_inches_feet() - Convert inches to feet."""
    return convert_inches_feet(inches)
def in_ft(inches):
    """Short alias for convert_inches_feet() - Convert inches to feet."""
    return c_in_ft(inches)

def convert_feet_inches(feet):
    """Convert distance from feet to inches."""
    return feet * 12
def c_ft_in(feet):
    """Alias for convert_feet_inches() - Convert feet to inches."""
    return convert_feet_inches(feet)
def ft_in(feet):
    """Short alias for convert_feet_inches() - Convert feet to inches."""
    return c_ft_in(feet)

def tally():
    """Count the number of characters in user input (useful for tallying)."""
    tallyCounter = input("Tally: ")
    return len(tallyCounter)

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