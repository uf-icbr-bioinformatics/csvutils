csvtoxls
========

Convert csv files to xlsx

## Introduction
**csvtoxls** is a command-line tool to convert one or more tab-delimited files to
an Excel workbook in .xlsx format. It can convert multiple files to different sheets
of the same workbook, and apply simple formatting (currently, bold face only) to 
specified rows and columns.

## Prerequisites
This program relies on the excellent **XlsxWriter** package, available at 
http://xlsxwriter.readthedocs.org/en/latest/index.html. Please follow the 
installation instructions on that site if it is not already available in your
Python environment.

## Installation
No installation necessary; simply call the script from the shell prompt:

```bash
> python csvtoxls.py
```

For simplicity, you can make the csvtoxls script directly executable:

```bash
> chmod +x csvtoxls.py
> ./csvtoxls.py
```

## Usage
To convert a csv file **file1.csv** to a workbook **out.xlsx**:

```bash
> csvtoxls.py out.xlsx file1.csv
```

You can put multiple input files on the command line. Each one will be 
converted to a different sheet in the output file, in the order in which
they appear on the command line:

```bash
> csvtoxls.py out.xlsx file1.csv file2.csv file3.csv
```

By default, the contents of each csv file are stored in the sheet starting
from the A1 cell, with default formatting. Numbers are converted to numeric 
cells, all other cells are kept as text.

## Sheet options

The following options can be specified after each input file name, to control
some details of the conversion:

Option       | Description
-------------|------------
-name S      | set the sheet name to S
-delim D     | set the delimiter to D. Possible values are: 'tab', 'space', or a single character (default: tab).
-width N     | set the width of all columns to N
-firstrow N  | place the first row of the csv file in row N of the sheet (default: 1)
-firstcol N  | place the first column of the csv file in column N of the sheet (default: 1)
-rowhdr N    | format row N of the csv file as header (bold). This option may appear multiple times.
-colhdr N    | format column N of the csv file as header (bold). This option may appear multiple times.
-firstrowhdr | equivalent to -rowhdr 1 (first row will be bold)
-firstcolhdr | equivalent to -colhdr 1 (first column will be bold)

## Examples

```bash
> csvtoxls.py out.xlsx \
              file1.csv -name Sales -firstrow 3 -firstrowhdr \
              file2.csv -name Totals -delim , -colhdr 1 -colhdr 2
```

This creates a file **out.xlsx** containing two sheets. The first sheet, called Sales, shows the contents of 
tab-delimited file **file1.csv**, starting at row 3. The first row of the data will be in bold face. The 
second sheet, called Totals, will show the contents of comma-delimited file **file2.csv**. The first two columns of the data will be in bold face.

## Credits
**csvtoxls.py** is (c) 2014-2015, A. Riva, <A href='http://dibig.biotech.ufl.edu'>DiBiG</A>, <A href='http://biotech.ufl.edu/'>ICBR Bioinformatics</A>, University of Florida
