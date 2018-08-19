# kut
Spiced-up version of the cut(1) command.

## Introduction
This command extracts columns from the specified files (or standard input
if no filenames are specified) and prints them to standard output. Wanted 
columns are specified using the -f option, and are printed in the order in 
which they are specified (contrast this with the cut command, which always 
prints them in their original order).

## Usage

```
  kut [options] filenames...
```

The following command-line options are supported:

Option | Description
---------------|------------
 -f C1,...,Cn | Specifies wanted columns. See below for possible values for C.
 -d D         | Set delimiter to D (default: tab).
 -e E         | Set output delimited to E (default: same as -d).
 -q Q         | Set quote character to Q (default: None).
 -m M         | Use M in place of missing values, e.g. if a line is shorter than the rest (default: '???').

Each column specification C can be:

* A column number (1-based).
* A range of the form p-q, meaning columns from p to q inclusive;
  * if p is omitted it defaults to the first column;
  * if q is omitted it defaults to the last column in the file (recomputed for each file).
* The string '-', interpreted as all columns in reverse order.

Note that in a range `p-q`, `p` can be larger than `q`, and that columns
can be repeated. Also, the -f option can be specified more than once
for readability. 

A delimiter specification (for -d and -e) can be a single character,
or the special strings 'tab' (tab), 'sp' (one space), 'nl' (newline).

## Examples
Some examples, assuming that file test.csv has five columns:

Invocation | Result
-----------|-------
kut -f 1,5,3 test.csv   | Columns 1, 5, and 3 in this order
kut -f 2-4 test.csv     | Columns 2, 3, and 4
kut -f -2 test.csv      | Columns 1 and 2
kut -f 2- test.csv      | Columns 2, 3, 4, and 5
kut -f 3-1 test.csv     | Columns 3, 2, and 1
kut -f 3-1,2-4 test.csv | Columns 3, 2, 1, 2, 3, and 4
kut -f - test.csv       | Columns 5, 4, 3, 2, and 1
