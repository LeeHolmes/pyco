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

You've already entered some simple calculations and might have already noticed some of these. While entering calculations, pyco lets you edit them in the way that you are used to with many other programs: _HOME_ and _END_ to go to the beginning and end of lines, arrow keys to move left and right, and even up and down to have pyco bring back a calculation that you've previously entered.

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


### Example
Your table is splitting the $113 bill (with 20% tip) 5 ways. But one friend is going to pay for 2 people. How much should they pay? There are always many ways to get to the answer, but your session might look something like this:

```
>>> each = (113*1.20)/5
>>> each
27.119999999999997
>>> each * 2
54.239999999999995
```

## TODO
- doing computer math (1\*gb, 10\*mb)
- entering lists
- calling functions
- finding functions
- getting help on functions
- defining your own functions
- list of built-in variables (_, pi, e)
- list of utility functions
- list of programmer's functions
- list of conversion functions
- list of statistical functions (avg etc.)
- list of mathematical functions
- list of trigonometric functions