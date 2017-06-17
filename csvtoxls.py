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
            fname = os.path.split(self.csvfile)[1]
            self.name = os.path.splitext(fname)[0][:30] # limit to the first 30 chars
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
        if os.path.isfile(self.csvfile):
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
        else:
            sys.stderr.write("Warning: file {} does not exist or is not readable.\n".format(self.csvfile))
            return (0, 0)

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
        return setupFromCmdline(args)

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

def setPar(c, attr, value, append=False):
    if c:
        if append:
            getattr(c, attr).append(value)
        else:
            setattr(c, attr, value)
    else:
        sys.stderr.write("Error: sheet options specified before csv file name.\n")
        sys.exit(-1)

def setupFromCmdline(args):
    global CSVS
    OPTIONS = ['-n', '-name', '-w', '-width', '-d', '-delim', '-fr', '-firstrow', '-fc', '-firstcol', '-r', '-rowhdr', '-c', '-colhdr', 
               '-R', '-firstrowhdr', '-C', '-firstcolhdr']
    quick = False
    c = None
    xlsxfile = None
    next = ""

    if '-h' in args:
        usage()

    for a in args[1:]:
        if a in ['-q', "-quick"]:
            sys.stderr.write("Quick mode enabled.\n")
            quick = True
        elif a in ["-R", "-firstrowhdr"]:
            setPar(c, 'rowhdr', 0, True)
        elif a == ["-C", "-firstcolhdr"]:
            setPar(c, 'colhdr', 0, True)
        elif a in OPTIONS:
            next = a
        elif next in ["-name", "-n"]:
            a = a[:min(len(a), 30)] # excel sheet names can't be longer than 31 characters...
            setPar(c, 'name', a)
            next = ""
        elif next == ["-width", "-w"]:
            setPar(c, 'width', int(a))
            next = ""
        elif next in ["-delim", "-d"]:
            setPar(c, 'delim', decodeDelimiter(a))
            next = ""
        elif next in ["-fr", "-firstrow"]:
            setPar(c, 'firstrow', int(a) - 1)
            next = ""
        elif next in ["-fc", "-firstcol"]:
            setPar(c, 'firstcol', int(a) - 1)
            next = ""
        elif next in ["-r", "-rowhdr"]:
            setPar(c, 'rowhdr', int(a) - 1, True)
            next = ""
        elif next in ["-c", "-colhdr"]:
            setPar(c, 'colhdr', int(a) - 1, True)
            next = ""
        elif a[0] == '-':
            sys.stderr.write("Unrecognized option: {}\n".format(a))
        elif xlsxfile:
            c = Csv(a)
            CSVS.append(c)
        else:
            xlsxfile = a
    # for c in CSVS:
    #     c.dump()
    if quick:
        for c in CSVS:
            c.setQuick()
    return xlsxfile


def usage():
    prog = os.path.split(sys.argv[0])[1]
    print """{} - Convert one or more tab-delimited files to .xlsx format

Usage:

  {} outfile.xlsx file1.csv [file1-options...] [file2.csv [file2-options...]] ...

Each .csv file appearing on the command line is written to outfile.xlsx as a separate
sheet. The csv file name may be followed by one or more options, that apply only to that
file. Valid options are:

  -q    | -quick       - quick mode: sets sheet name to filename, adds -firstrowhdr
  -n S  | -name S      - set the sheet name to S.
  -d D  | -delim D     - file uses delimiter D. Possible values are: 'tab', 'space', or a single character (default: tab).
  -w N  | -width N     - set the width of all columns to N.
  -fr N | -firstrow N  - place the first row of the csv file in row N of the sheet (default: 1).
  -fc N | -firstcol N  - place the first column of the csv file in column N of the sheet (default: 1).
  -r N  | -rowhdr N    - format row N of the csv file as header (bold). This option may appear multiple times.
  -c N  | -colhdr N    - format column N of the csv file as header (bold). This option may appear multiple times.
  -R    | -firstrowhdr - equivalent to -rowhdr 1 (first row will be bold).
  -C    | -firstcolhdr - equivalent to -colhdr 1 (first column will be bold).

Full documentation and source code are available on GitHub:

  http://github.com/albertoriva/cvstoxls/

(c) 2014-2017, A. Riva, DiBiG, ICBR Bioinformatics, University of Florida
""".format(prog, prog)
    sys.exit(-1)

def main(xlsxfile):
    global FORMATS

    print "Writing XLSX file {}".format(xlsxfile)
    workbook = xlsxwriter.Workbook(xlsxfile, {'strings_to_numbers': True})
    workbook.set_properties({'author': 'A. Riva, ariva@ufl.edu', 'company': 'DiBiG - ICBR Bioinformatics'}) # these should be read from conf or command-line
    FORMATS['bold'] = workbook.add_format({'bold': 1})

    # Loop through all defined Csv objects:
    for c in CSVS:
        worksheet = workbook.add_worksheet(c.name)
        (nrows, ncols) = c.to_worksheet(worksheet)
        if nrows > 0 and ncols > 0:
            sys.stderr.write("File {} added to workbook: {} rows, {} columns.\n".format(c.csvfile, nrows, ncols))
            if c.width:
                worksheet.set_column(0, ncols, c.width)

    workbook.close()

if __name__ == "__main__":
    xlsxfile = setup(sys.argv)
    if xlsxfile:
        main(xlsxfile)

