# Pyco
_Your fully featured EDC - Every Day Calculator_

## Introduction
Pyco is a fully featured and extremely portable calculator designed for calculators with keyboards - including the [Clockwork Pi PicoCalc](https://www.clockworkpi.com/picocalc), [uConsole](https://www.clockworkpi.com/home-uconsole), and of course desktop computers.

Unlike calculators that have buttons for each operation, pyco gives each operation a name. Where in a regular calculator you might type `90` and then push the `sin` button, in pyco you would type `sin(90)`. This lets you easily type longer and more complicated expressions all at once, such as `5*sin(90) + 1`.

When you open pyco, you will see the following:

```
             ┌────────────┐
             │┌───────8< ┐│
             ││ pyco 0.1 ││
             │└──────────┘│
             │ ░ ░ ░ ░ ░  │
             │  ░ ░ ░ ░ ░ │
             └────────────┘
           Happy Calculating!

>>>
```

The three little arrows are where your journey begins :)

## Simple Calculations
For basic calculations, type them directly into pyco. You do not type the arrows. These are known as the _prompt_ and are displayed by pyco to tell you it is ready for input. The symbols for mathematical operations are often used to write math on computers, but don't worry if they are new to you:

| Operator | Meaning | Example | Result |
|----------|---------|---------|--------|
| + | Addition | 1+1 | 2 |
| - | Subtraction | 5-2 | 3 |
| / | Division | 10/3 | 3.333... |
| * | Multiplication | 2*8 | 16 |
| ** | Exponentiation | 2**8 | 256 |
| () | Precedence | (1+2)*3 | 9 |

When you type them into pyco and press RETURN, pyco displays the result:

```
>>> 1+2
3
>>> 1+2*3
7
>>> (1+2)*3
9
>>> 2**8
256
```

### Example
You are at a dinner with friends and the bill is $113. You want to add a 20% tip and split it 4 ways. How much should each person pay?

In pyco you would type:

```
>>> (113*1.2)/4
33.9
```

## Using pyco
Pyco has many features to simplify your interactive experience.

You've already entered some simple calculations and might have already noticed some of these. While entering calculations, pyco lets you edit them in the way that you are used to with many other programs: _HOME_ and _END_ to go to the beginning and end of lines, arrow keys to move left and right, and even up and down to have pyco bring a calculation that you've previously entered.

### Example
From the previous calculation, what happens if you tipped at 15%? Press the _UP_ key and notice that pyco re-populates your calculation from what you previously typed. Use the left and right arrow keys (and backspace or delete) to change the 1.2 to 1.15. Then push ENTER.

```
>>> (113*1.2)/4
33.9
>>> [pushed UP key]
>>> (113*1.15)/4
32.4875
```

## Reusing results
While the UP and DOWN arrows are great for re-entering previous calculations, what if you want to re-use the value of a calculation many times?

Pyco makes this easy by letting you store results into _variables_. While some traditional calculators let you do this with a single value through the buttons for _memory store_, _memory recall_, and _memory clear_, pyco lets you give names to the numbers you store. These are called _variables_. For example:

```
>>> tip = 1.20
>>> (113 * tip)/4
33.9
```

When you are storing something, the name goes on the left of the equals sign, followed by the calculation or result on the right of the equals sign. Afterward, you can use the variable name wherever you might have otherwise used a number.

As the example above shows, you can give a specific number that you want to store in a variable. But you can also store the result of a calculation in a variable:

```
>>> each = (113*1.15)/4
>>> each
32.4875
```

If you only realize _after_ doing a calculation that you want to reuse its result, pyco always stores the last result in a special variable called "_". You usually type that by holding _SHIFT_ and then the key beside 0. For example, if you realized you wanted to actually split the bill 5 ways, you might type something like the following:

```
>>> (113*1.15)/4
32.4875
>>> (_ * 4)/5
25.99
```

In this calculation, you mulitiply the per-person cost by 4 again to get back to the original total, and then divide by 5.

### Numbered Results

In addition to the `_` variable which holds just the last result, pyco automatically stores _all_ of your results in numbered variables: `_1`, `_2`, `_3`, and so on. This makes it easy to reference any previous calculation:

```
>>> 100 + 50
150
>>> 200 * 3
600
>>> _1 + _2
750
```

To see your full calculation history along with the expressions that produced each result, use the `history` function:

```
>>> history()
_1: 100 + 50
    = 150
_2: 200 * 3
    = 600
_3: _1 + _2
    = 750
```


### Example
Your table is splitting the $113 bill (with 20% tip) 5 ways. But one friend is going to pay for 2 people. How much should they pay? There are always many ways to get to the answer, but your session might look something like this:

```
>>> each = (113*1.20)/5
>>> each
27.119999999999997
>>> each * 2
54.239999999999995
```

## Computer Math
When working with file sizes or large numbers, pyco makes it easy to work with common units. Instead of typing out all those zeros, you can use these convenient shortcuts:

```
>>> 5*gb
5368709120
>>> 10*mb
10485760
>>> 1*tb + 500*gb
1649267441664
```

The available units are:
- `kb` - Kilobytes (1,024 bytes)
- `mb` - Megabytes (1,024 kilobytes)
- `gb` - Gigabytes (1,024 megabytes)  
- `tb` - Terabytes (1,024 gigabytes)

You can also work with large numbers using familiar terms:
- `thousand` - 1,000
- `million` - 1,000,000
- `billion` - 1,000,000,000
- `trillion` - 1,000,000,000,000

```
>>> 2.5*million
2500000
>>> 1.2*billion/300*million
4.0
```

## Working with Lists
Sometimes you need to perform calculations on a series of numbers. Pyco lets you enter lists of numbers using square brackets, just like you might write them on paper:

```
>>> [1, 2, 3, 4, 5]
[1, 2, 3, 4, 5]
>>> sum([10, 20, 30])
60
>>> avg([85, 92, 78, 96])
87.75
```

For longer lists of numbers, pyco provides a convenient way to enter them one at a time. Type `inputlist` (or just `il` for short) and pyco will prompt you to enter numbers:

```
>>> il

0: 85
1: 92
2: 78
3: 96
4: [press ENTER with no number to finish]
[85.0, 92.0, 78.0, 96.0]
```

The list gets stored in a special variable called `_list` that you can use in subsequent calculations. This is similar to the `_` variable you already know about, but only gets overwritten when you enter new lists:

```
>>> avg(_list)
87.75
>>> max(_list) - min(_list)
18.0
```

Of course, you can still use the `_` variable:

```
>>> avg(_)
87.75
```

## Calling other functions
Functions are like _formulas_ in regular math: built-in calculators for specific tasks. Some are as simple as taking two numbers and returning their sum. Others can be more complex. They take information (called _arguments_) and give you back a result. To use a function, type its name followed by parentheses containing the information it needs:

```
>>> sqrt(16)
4.0
>>> sin(90)
0.8939966636005579
```

Some functions can take multiple pieces of information. You separate these by commas:

```
>>> round(3.14159, 3)
3.142
>>> pow(2, 8)
256
```

## Finding functions
With so many functions available, pyco makes it easy to find what you're looking for. Use the star symbol (`*`) as a wildcard to search:

```
>>> *sin*
sin asin sinh arcsin
>>> sqr*
sqrt
```

You can search at the beginning or end of function names:
- `sin*` - finds functions starting with "sin"
- `*sin` - finds functions ending with "sin"  
- `*sin*` - finds functions containing "sin" anywhere

You can also use the TAB key. This is called tab completion, and is like auto-complete:

```
>>> s[TAB]
set setattr sin sinh slice ...
```

## Creating your own functions
You can create your own functions to simplify calculations you do frequently. Use the `def` keyword followed by your function name:

```
>>> def tip_calculator(bill, percent):
...     return bill * (1 + percent/100)
...
>>> tip_calculator(50, 18)
59.0
>>> tip_calculator(113, 20)
135.6
```

## Built-in variables
Pyco comes with several useful variables already defined:

- `_` - The result of your last calculation
- `_1`, `_2`, `_3`, ... - All previous calculation results, numbered in order
- `_list` - The last list you input
- `pi` - The mathematical constant π (3.14159...)
- `e` - The mathematical constant e (2.71828...)

```
>>> 2 * pi * 5
31.41592653589793
>>> e ** 2
7.3890560989306504
>>> 10 + 5
15
>>> _ * 2
30
```

## Utility functions
These functions help with everyday tasks:

- `tally` - Type a letter for everything you want to count. Will tell you how many things you typed in total.
- `human(number)` - Break down large numbers into readable parts
- `history` - Display all previous calculations and their results
- `asciitable` or `at` - Display a table of ASCII characters

```
>>> human(1234567)
{'million': 1, 'thousand': 234, 'one': 567}
>>> tally()
Tally: aaaaaaaaaaaa
12
```

## Programmer's functions
For those working with computers and programming:

- Data size constants: `kb`, `mb`, `gb`, `tb`
- Number formatting: `bin()`, `hex()`, `oct()`
- Character codes: `ord()`, `chr()`

```
>>> bin(42)
'0b101010'
>>> hex(255)
'0xff'
>>> ord('A')
65
>>> chr(65)
'A'
```

## Unit conversions
Pyco lets you convert values between various units, such as miles to kilometers and more. To convert values, call the `convert` function with the units you care about and the value:

`convert(from_unit, to_unit, value)`

For example:

```
>>> convert('f', 'c', 72)
22.22222222222222
>>> convert('mi', 'km', 100)
160.9344
>>> convert('lb', 'kg', 150)
68.0388555
>>> convert('cups', 'ml', 2)
473.176
```

### Combined unit conversions

Pyco can also handle combined units using `/` for ratios and `*` for products. This is useful for converting rates and compound measurements:

```
>>> convert('mi/h', 'km/h', 60)
96.56064
>>> convert('$cad/l', '$usd/gal', 1.50)
4.29
>>> convert('ft*lb', 'm*kg', 10)
1.3825495
```

Pyco will automatically find the conversion path through intermediate units when needed, so you do not need to convert each unit separately.

**What units are available?**
Type `units` to see all available units, or `units('search_term')` to find specific ones:

```
>>> units('meter')

AREA:
  cm2  centimeters^2 m2   meters^2

DISTANCE:
  cm   centimeters   km   kilometers
  m    meters

SPEED:
  kph  kilometers/h
  mps  meters/second
```

The units function is smart about typos too - try searching for "celcius" or "metre" and it will still find what you're looking for!

**Supported conversions:**
- **Temperature:** Celsius (c), Fahrenheit (f), Kelvin (k)
- **Distance:** meters (m), feet (ft), inches (in), miles (mi), kilometers (km), centimeters (cm)
- **Weight:** grams (g), kilograms (kg), pounds (lb), ounces (oz), tons (t), stone (st)
- **Volume:** liters (l), milliliters (ml), cups, pints (pt), quarts (qt), gallons (gal), fluid ounces (floz), tablespoons (tbsp), teaspoons (tsp)
- **Area:** square inches (in2), square feet (ft2), square meters (m2), square centimeters (cm2), acres (ac)
- **Speed:** meters/second (mps), kilometers/hour (kph), miles/hour (mph), knots (kn)
- **Power:** watts (w), horsepower (hp)
- **Time:** seconds (s), minutes (min), hours (h), days (d), weeks (wk), years (yr)

## Currency conversions
Pyco can convert between currencies using the same `convert` function. Currency codes are prefixed with a dollar sign ($):

```
>>> convert('$usd', '$eur', 100)
92.15
>>> convert('$gbp', '$jpy', 50)
9847.5
>>> convert('$cad', '$usd', 200)
147.06
```

To see all available currencies, use the `currencies` function:

```
>>> currencies()

CURRENCIES:
  $AUD Australia Dollar
  $CAD Canada Dollar
  $EUR Euro
  $GBP United Kingdom Pound
  $JPY Japan Yen
  $USD United States Dollar
  ...
```

You can also search for specific currencies:

```
>>> currencies('euro')

CURRENCIES:
  $EUR Euro
```

## Timezone conversions
Convert times between timezones using the same `convert` function:

```
>>> convert('pst', 'est', 9)
12
>>> convert('gmt', 'jst', 14.5)
23.5
>>> convert('utc', 'pst', 20)
12
```

Times are in 24-hour format. You can use decimal hours for minutes (e.g., 14.5 for 2:30 PM).

To see all available timezones, use the `timezones` function:

```
>>> timezones()

TIMEZONES:
  EST   Eastern Standard Time (UTC-05:00)
  PST   Pacific Standard Time (UTC-08:00)
  UTC   Coordinated Universal Time (UTC+00:00)
  ...
```

You can search for timezones by name or location:

```
>>> timezones('pacific')

TIMEZONES:
  PST   Pacific Standard Time (UTC-08:00)
```

## Statistical functions
When working with lists of numbers, these functions help you understand your data:

- `avg(list)` or `mean(list)` - Average of the numbers
- `median(list)` - Middle value when sorted
- `mode(list)` - Most frequently occurring value
- `stdev(list)` - Standard deviation
- `sum(list)` - Add all numbers together
- `min(list)` - Smallest number
- `max(list)` - Largest number

```
>>> grades = [85, 92, 78, 96, 88]
>>> avg(grades)
87.8
>>> median(grades)
88
>>> max(grades) - min(grades)
18
```

## Mathematical functions
For more advanced calculations:

**Basic Math:**
- `sqrt(x)` - Square root
- `pow(x, y)` - x raised to the power of y (you can also type x**y directly)
- `abs(x)` - Absolute value
- `round(x, digits)` - Round to specified decimal places

**Logarithms:**
- `log(x)` - Natural logarithm
- `log10(x)` - Base-10 logarithm
- `log2(x)` - Base-2 logarithm

```
>>> sqrt(144)
12.0
>>> log10(1000)
3.0
>>> abs(-15)
15
```

## Trigonometric functions
For angles and triangles (angles are in radians unless noted):

**Basic trigonometry:**
- `sin(x)` - Sine
- `cos(x)` - Cosine  
- `tan(x)` - Tangent

**Inverse functions:**
- `asin(x)` - Arcsine
- `acos(x)` - Arccosine
- `atan(x)` - Arctangent

**Hyperbolic functions:**
- `sinh(x)` - Hyperbolic sine
- `cosh(x)` - Hyperbolic cosine
- `tanh(x)` - Hyperbolic tangent

**Angle conversion:**
- `degrees(x)` - Convert radians to degrees
- `radians(x)` - Convert degrees to radians

```
>>> sin(radians(90))
1.0
>>> degrees(pi)
180.0
>>> tan(radians(45))
0.9999999999999999
```