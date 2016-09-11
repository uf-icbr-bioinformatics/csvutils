# cols.py
Report number and names of columns.

## Introduction
This tool prints information about the number (and optionally the names) of
columns in a delimited file.

## Usage
*cols.py* examines one or more delimited files and reports one of the following:

* number of columns in the first line (default)
* numbered list of entries in the first line (-c, --colnames)
* number of lines matching the number of columns in the first line (-m, --matches)
 
Delimiter is **tab** by default, but can be changed with -d
option. Numbering starts at 1, unless -0 is specified, in which case
it is zero-based.

The program uses the first line of each file (or the line specified
with the -s option) as the header line. If -S is used instead of -s,
the program prints the contents of the specified line using the
contents of the first line as column names instead of progressive
numbers.

If no filename is specified, *cols.py* will read its input from standard input.

## Syntax

```
  cols.py [-h] [-c] [-0] [-m] [-d D] [-s N] [-S N] files...
```

The following table describes all options in detail.

Option | Description
---------------|------------
-h             | Print this help message.
-c, --colnames | Display the elements in the header line of the file as a numbered list. Numbering starts at 1 unless -0 is specified.
-m, --matches  | Print the number of lines whose column count matches the number of elements in the header line.
-0             | Number column names starting at 0 instead of 1.
-d D           | Change column delimiter to D (default is tab character).
-s N           | Use line N as header row.
-S N           | Print contents of line N using first line as header.

## Examples

The file [test.csv](test.csv) contains the following data:

Name | Age |Salary
-----|-----|------
Alice|42|65000
Bob|37|58000
Charlie|45|67000

```
$ cols.py test.csv 
test.csv: 3 columns.

$ cols.py -c test.csv 
test.csv: 3 columns.
  1 = Name
  2 = Age
  3 = Salary

$ cols.py -0 -c test.csv 
test.csv: 3 columns.
  0 = Name
  1 = Age
  2 = Salary

$ cols.py -c -s 3 test.csv 
test.csv: 3 columns.
  1 = Bob
  2 = 37
  3 = 58000

$ ../cols.py -c -S 3 test.csv 
test.csv: 3 columns.
  Name = Charlie
  Age = 45
  Salary = 67000

$ cols.py -m test.csv 
test.csv: 3 columns, 3/3 matching.
```

## Credits
**csvtoxls.py** is (c) 2016, A. Riva, <A href='http://dibig.biotech.ufl.edu'>DiBiG</A>, <A href='http://biotech.ufl.edu/'>ICBR Bioinformatics</A>, University of Florida
