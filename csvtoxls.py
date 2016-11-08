#!/usr/bin/env python

###################################################
#
# (c) 2015, Alberto Riva, ariva@ufl.edu
# DiBiG, ICBR Bioinformatics, University of Florida
#
# See the LICENSE file for license information.
###################################################

import sys
import csv
import codecs
import os.path
import importlib
import xlsxwriter
# import Tkinter, tkFileDialog

from sys import platform as _platform
IS_WIN = (_platform[0:3] == 'win') or (_platform == 'darwin') # Are we on Windows or Mac?
if IS_WIN:
    importlib.import_module("Tkinter")
    importlib.import_module("tkFileDialog")

# Dictionary of defined formats
FORMATS = {}

# List of Csv objects (each one represents a csv file, converted to a separate sheet)
CSVS = []

# Generator to read UTF-8 data (from Python docs)

def unicode_csv_reader(unicode_csv_data, dialect=csv.excel, **kwargs):
    # csv.py doesn't do Unicode; encode temporarily as UTF-8:
    csv_reader = csv.reader(utf_8_encoder(unicode_csv_data), dialect=dialect, **kwargs)
    for row in csv_reader:
        # decode UTF-8 back to Unicode, cell by cell:
        yield [unicode(cell, 'utf-8') for cell in row]

def utf_8_encoder(unicode_csv_data):
    for line in unicode_csv_data:
        yield line.encode('utf-8')

# Csv class, representing an input csv file with its options.
class Csv():
    csvfile = None
    name = None
    delim = '\t'
    width = 18
    firstrow = 0
    firstcol = 0
    rowhdr = []
    colhdr = []

    def __init__(self, file):
        self.csvfile = file
        self.rowhdr = []
        self.colhdr = []

    def dump(self):
        print "Csv {} name={} delim={} width={} firstrow={} firstcol={} rowhdr={} colhdr={}".format(self.csvfile, self.name, self.delim, self.width, 
                                                                                                    self.firstrow, self.firstcol, self.rowhdr, self.colhdr)

    def setQuick(self):
        """Set sheet name to basename of filename, if not specified, and firstrowhdr."""
        if self.name == None:
            self.name = os.path.splitext(self.csvfile)[0][:30] # limit to the first 30 chars
        if not 0 in self.rowhdr:
            self.rowhdr.append(0)

    def to_worksheet(self, ws):
        """Copy the contents of tab-delimited file `csvfile' to worksheet `ws', starting at row `firstrow' and column `firstcol'.
If `firstrowhdr' is True, the cells in the first row will be set to bold. If `firstcolhdr' is True, che cells in the
first column will be set to bold."""
        global FORMATS

        maxrow = 0
        maxcol = 0
        #with open(self.csvfile, 'rb') as f:
        try:
            f = codecs.open(self.csvfile, 'r', 'utf-8')
            #reader = csv.reader(f, delimiter=self.delim)
            reader = unicode_csv_reader(f, delimiter=self.delim)
            for r, row in enumerate(reader):
                if r > maxrow:
                    maxrow = r
                for c, col in enumerate(row):
                    if c > maxcol:
                        maxcol = c
                    if (r in self.rowhdr) or (c in self.colhdr):
                        ws.write(r + self.firstrow, c + self.firstcol, col, FORMATS['bold'])
                    else:
                        ws.write(r + self.firstrow, c + self.firstcol, col)
        finally:
            f.close()
        return (maxrow + 1, maxcol + 1)

def decodeDelimiter(d):
    if d == 'tab':
        return '\t'
    elif d == 'space':
        return ' '
    else:
        return d[0]

def setup(args):
    n = len(args)

    if n == 1:
        if IS_WIN:
            return setupWin()
        else:
            usage()
            return None
    else:
        return setupFromCmdline(args, n)

def setupWin():
    c = None

    # The following two lines are to hide the main Tk window
    root = Tkinter.Tk()
    root.withdraw()

    xlsxfile = tkFileDialog.asksaveasfilename(title="Enter output file (.xlsx)")
    if xlsxfile == None:
        return None

    infiles = tkFileDialog.askopenfilename(title="Select input file(s) (.csv)", multiple=True)
    for f in infiles:
        c = Csv(f)
        c.rowhdr.append(0)
        CSVS.append(c)
    return xlsxfile

def setupFromCmdline(args, n):
    i = 2
    c = None
    quick = False

    xlsxfile = args[1]

    while True:
        if i >= n:
            if quick:
                for c in CSVS:
                    c.setQuick()
            return xlsxfile
        
        w = args[i]
        if w[0] == '-':
            if w == '-q':
                print "Quick mode enabled"
                quick = True
            elif c:
                if w == "-name":
                    i = i + 1
                    c.name = args[i]
                elif w == "-width":
                    i = i + 1
                    c.width = int(args[i])
                elif w == "-delim":
                    i = i + 1
                    c.delim = decodeDelimiter(args[i])
                elif w == "-firstrow":
                    i = i + 1
                    c.firstrow = int(args[i] - 1)
                elif w == "-firstcol":
                    i = i + 1
                    c.firstcol = int(args[i] - 1)
                elif w == "-rowhdr":
                    i = i + 1
                    c.rowhdr.append(int(args[i]) - 1)
                elif w == "-colhdr":
                    i = i + 1
                    c.colhdr.append(int(args[i]) - 1)
                elif w == "-firstrowhdr":
                    c.rowhdr.append(0)
                elif w == "-firstcolhdr":
                    c.colhdr.append(0)
            else:
                print "Error: sheet options specified before csv file name."
                return None

        else:
            c = Csv(args[i])
            CSVS.append(c)

        i = i + 1

def usage():
    prog = sys.argv[0]
    print """{} - Convert a tab-delimited file to .xlsx format

Usage:

  {} outfile.xlsx file1.csv [file1 options...] [file2.csv [file2 options...]] ...

Each .csv file appearing on the command line is written to outfile.xlsx as a separate
sheet. The csv file name may be followed by one or more options, that apply only to that
file. Valid options are:

  -q           - quick mode: sets sheet name to filename, adds -firstrowhdr
  -name S      - set the sheet name to S.
  -delim D     - file uses delimiter D. Possible values are: 'tab', 'space', or a single character (default: tab).
  -width N     - set the width of all columns to N.
  -firstrow N  - place the first row of the csv file in row N of the sheet (default: 1).
  -firstcol N  - place the first column of the csv file in column N of the sheet (default: 1).
  -rowhdr N    - format row N of the csv file as header (bold). This option may appear multiple times.
  -colhdr N    - format column N of the csv file as header (bold). This option may appear multiple times.
  -firstrowhdr - equivalent to -rowhdr 1 (first row will be bold).
  -firstcolhdr - equivalent to -colhdr 1 (first column will be bold).

Full documentation and source code are available on GitHub:

  http://github.com/albertoriva/cvstoxls/

(c) 2014, A. Riva, DiBiG, ICBR Bioinformatics, University of Florida
""".format(prog, prog)

def main(xlsxfile):
    global FORMATS

    workbook = xlsxwriter.Workbook(xlsxfile, {'strings_to_numbers': True})
    workbook.set_properties({'author': 'A. Riva, ariva@ufl.edu', 'company': 'DiBiG - ICBR Bioinformatics'}) # these should be read from conf or command-line
    FORMATS['bold'] = workbook.add_format({'bold': 1})

    # Loop through all defined Csv objects:
    for c in CSVS:
        worksheet = workbook.add_worksheet(c.name)
        (nrows, ncols) = c.to_worksheet(worksheet)
        print "File {} added to workbook: {} rows, {} columns.".format(c.csvfile, nrows, ncols)
        if c.width:
            worksheet.set_column(0, ncols, c.width)

    workbook.close()

if __name__ == "__main__":
    xlsxfile = setup(sys.argv)
    if xlsxfile:
        main(xlsxfile)

