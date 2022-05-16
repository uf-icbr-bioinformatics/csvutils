#!/usr/bin/env python

#####
#
# csvtoxls.py - Convert tab-delimited files to Excel format.
#
####
__doc__ = "Convert tab-delimited files to Excel format."
__author__ = "Alberto Riva, UF ICBR Bioinformatics core, University of Florida"
__email__ = "ariva@ufl.edu"
__license__ = "GPL v3.0"
__copyright__ = "Copyright 2018, University of Florida Research Foundation"

import sys
import csv
import codecs
import os.path
import importlib
import xlsxwriter

PYTHON_VERSION = sys.version_info[0]

try:
  import xlrd
  HAS_XLRD = True
except:
  HAS_XLRD = False

from sys import platform as _platform
IS_WIN = (_platform[0:3] == 'win') or (_platform == 'darwin') # Are we on Windows or Mac?
if IS_WIN:
    importlib.import_module("Tkinter")
    importlib.import_module("tkFileDialog")

# Dictionary of defined formats
FORMATS = {}

# List of Csv objects (each one represents a csv file, converted to a separate sheet)
CSVS = []

# List of sheet names seen so far (to avoid duplicates)
SHEET_NAMES = []

def validateSheetName(name):
  global SHEET_NAMES
  name = name[:min(len(name), 30)] # excel sheet names can't be longer than 31 characters...
  if name in SHEET_NAMES:
    idx = 1
    prefix = name[:min(len(name), 27)]
    while True:
      name = "{}_{}".format(prefix, idx)
      if not name in SHEET_NAMES:
        break
      idx += 1
  SHEET_NAMES.append(name)
  return name

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
        sys.stdout.write("Csv {} name={} delim={} width={} firstrow={} firstcol={} rowhdr={} colhdr={}\n".format(self.csvfile, self.name, self.delim, self.width, 
                                                                                                               self.firstrow, self.firstcol, self.rowhdr, self.colhdr))

    def setQuick(self):
        """Set sheet name to basename of filename, if not specified, and firstrowhdr."""
        if self.name == None:
            fname = os.path.split(self.csvfile)[1]
            self.name = validateSheetName(os.path.splitext(fname)[0])
        if not 0 in self.rowhdr:
            self.rowhdr.append(0)

    def to_worksheet_py2(self, ws):
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
                        if col.startswith("="):
                            ws.write_formula(r + self.firstrow, c + self.firstcol, col)
                        elif (r in self.rowhdr) or (c in self.colhdr):
                            ws.write(r + self.firstrow, c + self.firstcol, col, FORMATS['bold'])
                        else:
                            ws.write(r + self.firstrow, c + self.firstcol, col)
            finally:
                f.close()
                return (maxrow + 1, maxcol + 1)
        else:
            sys.stderr.write("Warning: file {} does not exist or is not readable.\n".format(self.csvfile))
            return (0, 0)

    def to_worksheet(self, ws):
        """Copy the contents of tab-delimited file `csvfile' to worksheet `ws', starting at row `firstrow' and column `firstcol'.
If `firstrowhdr' is True, the cells in the first row will be set to bold. If `firstcolhdr' is True, che cells in the
first column will be set to bold."""
        global FORMATS

        maxrow = 0
        maxcol = 0
        r = 0
        c = 0
        #with open(self.csvfile, 'rb') as f:
        if os.path.isfile(self.csvfile):
            with open(self.csvfile, 'r') as f:
                reader = csv.reader(f, delimiter=self.delim)
                for row in reader:
                    r += 1
                    c = 0
                    if r > maxrow:
                        maxrow = r
                    for col in row:
                        c += 1
                        if c > maxcol:
                            maxcol = c
                        if col.startswith("="):
                            ws.write_formula(r + self.firstrow, c + self.firstcol, col)
                        elif (r in self.rowhdr) or (c in self.colhdr):
                            ws.write(r + self.firstrow, c + self.firstcol, col, FORMATS['bold'])
                        else:
                            ws.write(r + self.firstrow, c + self.firstcol, col)
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
    prev = ""

    if '-h' in args:
        usage()

    if "-v" in args:
        version()

    for a in args[1:]:
        if a in ['-q', "-quick"]:
            quick = True
        elif a in ["-R", "-firstrowhdr"]:
            setPar(c, 'rowhdr', 0, True)
        elif a == ["-C", "-firstcolhdr"]:
            setPar(c, 'colhdr', 0, True)
        elif a in OPTIONS:
            prev = a
        elif prev in ["-name", "-n"]:
            a = validateSheetName(a)
            setPar(c, 'name', a)
            prev = ""
        elif prev == ["-width", "-w"]:
            setPar(c, 'width', int(a))
            prev = ""
        elif prev in ["-delim", "-d"]:
            setPar(c, 'delim', decodeDelimiter(a))
            prev = ""
        elif prev in ["-fr", "-firstrow"]:
            setPar(c, 'firstrow', int(a) - 1)
            prev = ""
        elif prev in ["-fc", "-firstcol"]:
            setPar(c, 'firstcol', int(a) - 1)
            prev = ""
        elif prev in ["-r", "-rowhdr"]:
            setPar(c, 'rowhdr', int(a) - 1, True)
            prev = ""
        elif prev in ["-c", "-colhdr"]:
            setPar(c, 'colhdr', int(a) - 1, True)
            prev = ""
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
    sys.stdout.write("""{} - Convert one or more tab-delimited files to .xlsx format

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

  http://github.com/albertoriva/csvtoxls/

(c) 2014-2020, A. Riva, DiBiG, ICBR Bioinformatics, University of Florida

""".format(prog, prog))
    sys.exit(-1)

def version():
    sys.stdout.write("csvtoxls.py v1.0\n")
    sys.exit(0)

def main(xlsxfile):
    global FORMATS

    sys.stderr.write("Writing XLSX file {}\n".format(xlsxfile))
    workbook = xlsxwriter.Workbook(xlsxfile, {'strings_to_numbers': True})
    workbook.set_properties({'author': 'A. Riva, ariva@ufl.edu', 'company': 'DiBiG - ICBR Bioinformatics'}) # these should be read from conf or command-line
    FORMATS['bold'] = workbook.add_format({'bold': 1})

    # Loop through all defined Csv objects:
    for c in CSVS:
        worksheet = workbook.add_worksheet(c.name)
        if PYTHON_VERSION == 2:
          (nrows, ncols) = c.to_worksheet_py2(worksheet)
        else:
          (nrows, ncols) = c.to_worksheet(worksheet)
        if nrows > 0 and ncols > 0:
            sys.stderr.write("+ File {} added to workbook: {} rows, {} columns.\n".format(c.csvfile, nrows, ncols))
            if c.width:
                worksheet.set_column(0, ncols, c.width)

    workbook.close()
    sys.stderr.write("XLSX file written.\n")

def csvtoxls_main():
    xlsxfile = setup(sys.argv)
    if xlsxfile:
        main(xlsxfile)

### Reverse conversion: Excel to csv

class XLStoCSV():
    delimiter = '\t'
    quoted = False              # If True, put double-quotes around each field.

    def main(self):
        for x in sys.argv[1:]:
            self.writeAllSheets(x)
    
    def sheetToFile(self, filename, sheet):
        """Write the contents of `sheet' to `filename' using the 
    supplied `delimiter'."""
        with open(filename, "w") as out:
            for rown in range(sheet.nrows):
                newr = []
                for x in sheet.row_values(rown):
                    try:
                        if not type(x).__name__ == 'unicode':
                            x = str(x)
                        newr.append(x.encode('utf-8'))
                    except:
                        sys.stderr.write("Error storing value `{}' of type `{}'.\n".format(x, type(x).__name__))
                        return
                if self.quoted:
                    out.write('"' + newr[0] + '"')
                else:
                    out.write(newr[0])
                for r in newr[1:]:
                    out.write(self.delimiter)
                    if self.quoted:
                        out.write('"' + r + '"')
                    else:
                        out.write(r)
                out.write("\n")

    def writeAllSheets(self, xlsfile):
        """Write all sheets in the supplied `xlsfile' to corresponding delimited files."""
        if not HAS_XLRD:
            sys.stderr.write("This feature requires the xlrd module.\n")
            return
        basename = os.path.splitext(xlsfile)[0]
        book = xlrd.open_workbook(xlsfile)
        sheetnames = book.sheet_names()
        sys.stderr.write("{} sheets:\n".format(book.nsheets))
        for i in range(book.nsheets):
            outfile = "{}-{}.csv".format(basename, sheetnames[i])
            sys.stderr.write("Writing sheet {} to `{}'\n".format(i+1, outfile))
            self.sheetToFile(outfile, book.sheet_by_index(i))

if __name__ == "__main__":
    progname = os.path.split(sys.argv[0])[1]
    if progname == 'csvtoxls.py':
        csvtoxls_main()
    elif progname == 'xlstocsv.py':
        X = XLStoCSV()
        X.main()
