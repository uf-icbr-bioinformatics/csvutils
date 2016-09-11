# colx.py
Perform intersection (or other set operations) on columns from one or more delimited files.

## Introduction
*colx.py* counts and optionally prints the intersection (or union, or difference) of the elements 
in specified columns of two or more files. Usage:

```
Usage: colx.py [-wqsmiduh] [-o outfile] filespecs...
```

Filespecs have the form **filename:col** where **filename** points to an existing file and **col** is column number. If col is omitted it 
defaults to 1 (the first column). The number of entries in each input column and in
the final output are printed to standard error.

## Syntax

Option | Description
-------|------------
  -h         | Print this usage message. Ignore all other options.
  -o outfile | Print the resulting list to file 'outfile' (can be combined with -w).
  -w         | Print the resulting elements to standard output.
  -q         | Do not print counts to standard error.
  -s[r][an]  | Sort resulting list. By default, sort is alphabetical. Add an 'n' to sort numerically instead. Add an 'r' to reverse sort order.
  -c char    | Use 'char' as delimiter. Use 's' for space, 't' for tab (default).
  -g char    | Lines starting with 'char' will be ignored (default: #).
  -m         | Enable 'multi' mode. Will compute all pairwise intersections between all input columns. Disables -i, -d, -u.
  -i         | Intersection mode. Result will consist of the intersection of all input columns. This is the default mode.
  -u         | Union mode. Result list includes all elements of all input columns.
  -d         | Difference mode. Result list includes elements in first list but not in successive lists.

## Usage
Filespecs are processed in left-to-right order, and the mode can be changed
any number of times while processing the files. For example, the following:

```
  colx.py -u f:1 f:2 -d f:3
```

computes the union of the elements in columns 1 and 2 of file f, and then removes the
elements in column 3. This also applies to other options. For example, if file f1 is
tab-delimited and file f2 is comma-delimited, you can do:

```
  colx.py -c t f1:1 -c , f2:1
```
to use the appropriate delimiter for each file.

## Credits
**csvtoxls.py** is (c) 2016, A. Riva, <A href='http://dibig.biotech.ufl.edu'>DiBiG</A>, <A href='http://biotech.ufl.edu/'>ICBR Bioinformatics</A>, University of Florida

