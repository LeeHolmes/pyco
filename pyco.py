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
            if(value.text.strip().endswith("*")):
                term = value.text.strip()
                lastDot = term.rfind('.')
                filter = ""
                results = []
                
                if lastDot != -1:
                    filter = term[lastDot+1:-1]
                    term = term[:lastDot]

                    try:
                        results = dir(eval(term))
                    except:
                        results = []
                else:
                    filter = term[:-1]
                    results = globals().keys()

                found = False
                for current in results:
                    if current.lower().startswith(filter.lower()):
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
    found = []
    for current in globals():
        if term in current:
            found.append(current)
    return found

def asciitable():
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
    return asciitable()

def get_printable_char(char):
    if char < 32:
        return '.'
    elif char > 126 and char < 160:
        return '.'
    else:
        return chr(char)

def inputlist():
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
    return inputlist()


def average(list):
    return mean(list)
def avg(list):
    return average(list)

def convert_celsius_fahrenheit(celsius):
    return (celsius * 9 / 5) + 32
def c_c_f(celsius):
    return convert_celsius_fahrenheit(celsius)
def c_f(celsius):
    return c_c_f(celsius)

def convert_fahrenheit_celsius(fahrenheit):
    return (fahrenheit - 32) * 5 / 9
def c_f_c(fahrenheit):
    return convert_fahrenheit_celsius(fahrenheit)
def f_c(fahrenheit):
    return c_f_c(fahrenheit)

def tally():
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