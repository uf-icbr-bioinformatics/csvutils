#!/usr/bin/env python

#####
#
# csvtoxls.py - Convert tab-delimited files to Excel format.
#
####
__doc__       = "Convert tab-delimited files to Excel format."
__author__    = "Alberto Riva, UF ICBR Bioinformatics core, University of Florida"
__email__     = "ariva@ufl.edu"
__license__   = "GPL v3.0"
__copyright__ = "Copyright 2018-2023, University of Florida Research Foundation"
__version__   = "2.0"

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

# Utils

def version():
    sys.stdout.write("csvtoxls.py v{}\n".format(__version__))
    sys.exit(0)

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

def decodeDelimiter(d):
    if d == 'tab':
        return '\t'
    elif d in ['space', 'sp']:
        return ' '
    else:
        return d[0]

def setup(args):
    if len(args) == 1:
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





# Csv class, representing an input csv file with its options.
class CSV():
    csvfile = None
    params = {}

    def __init__(self, filename, params):
        self.csvfile = filename
        self.params = params

    def dump(self):
        sys.stdout.write("CSV {} {}\n".format(self.csvfile, self.params))

    def setQuick(self, parent):
        """Set sheet name to basename of filename, if not specified, and firstrowhdr."""
        if self.params['quick']:
          if "name" not in self.params:
            fname = os.path.split(self.csvfile)[1]
            self.params["name"] = parent.validateSheetName(os.path.splitext(fname)[0])
          self.params['rowhdr'] = 0

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

    def to_worksheet(self, parent, ws):
        """Copy the contents of tab-delimited file `csvfile' to worksheet `ws', starting at row `firstrow' and column `firstcol'.
If `firstrowhdr' is True, the cells in the first row will be set to bold. If `firstcolhdr' is True, che cells in the
first column will be set to bold."""
        maxrow = 0
        maxcol = 0
        r = 0
        c = 0
        with open(self.csvfile, 'r') as f:
          if self.params['header']:
            hc = 0
            for ch in self.params['header']:
              ws.write(self.params['firstrow'], hc + self.params['firstcol'], ch, parent.formats['bold'])
              hc += 1
            r += 1
          reader = csv.reader(f, delimiter=self.params['delim'])
          for row in reader:
            c = 0
            if r > maxrow:
              maxrow = r
            for col in row:
              if c > maxcol:
                maxcol = c
              if col.startswith("="):
                ws.write_formula(r + self.params['firstrow'], c + self.params['firstcol'], col)
              elif (r <= self.params['rowhdr']) or (c <= self.params['colhdr']):
                ws.write(r + self.params['firstrow'], c + self.params['firstcol'], col, parent.formats['bold'])
              else:
                ws.write(r + self.params['firstrow'], c + self.params['firstcol'], col)
              c += 1
            r += 1
        return (maxrow + 1, maxcol + 1)

OPTIONS = {'-n':        'name',
           '-name':     'name', 
           '-w':        'Dwidth',
           '-width':    'Dwidth',
           '-d':        'delim', 
           '-delim':    'delim', 
           '-fr':       'Ifirstrow', 
           '-firstrow': 'Ifirstrow',
           '-fc':       'Ifirstcol',
           '-firstcol': 'Ifirstcol',
           '-r':        'Irowhdr',
           '-rowhdr':   'Irowhdr',
           '-c':        'Icolhdr',
           '-colhdr':   'Icolhdr',
           "-t":        'titles',
           "-titles":   'titles'}

PROPERTIES = ['title', 'subject', 'author', 'manager', 'company',
              'category', 'keywords', 'comments', 'status', 'hyperlink_base']

class CSVtoXLSX(object):
  xlsxfile = None
  csvs = []
  sheetnames = []
  formats = {}
  properties = {'comments': 'Created with csvtoxls.py, https://github.com/uf-icbr-bioinformatics/csvutils'}
  params = {'quick': False, 'header': False, 'delim': '\t', 'width': 18, 'firstrow': 0, 'firstcol': 0, 'rowhdr': -1, 'colhdr': -1}
  _current = None

  def setPar(self, key, value):
    """Set parameter `key' to `value'. Sets the global value if _current is None, otherwise sets
it in the sheet being parsed."""
    if key[0] == "I":
      key = key[1:]
      value = int(value) - 1
    elif key[0] == "D":
      key = key[1:]
      value = int(value)
    elif key == 'delim':
      value = decodeDelimiter(value)
    elif key == 'name':
      value = self.validateSheetName(value)

    if self._current:
      self._current.params[key] = value
    else:
      if key != 'name':         # don't set name in the global params
        self.params[key] = value

  def usage(self):
    prog = os.path.split(sys.argv[0])[1]
    sys.stdout.write("""{} - Convert one or more tab-delimited files to .xlsx format

Usage:

  {} [global-options] outfile.xlsx file1.csv [file1-options] [file2.csv [file2-options]] ...

Each .csv file listed on the command line is written to outfile.xlsx as a separate sheet. 
The csv file name may be followed by one or more options, that apply only to that file. 

In the following list, W indicates options that apply to the whole worksheet; G indicates
global options, that can be specified before the first csv file and apply to all csv files;
F indicates options that can only be specified after a csv file and apply to that file only.

 Type | Short | Long          | Description 
------|-------|---------------|-----------------------------------------------------------
  W   | -p P  | --property P  | set a worksheet property (see below).
  L   | -n S  | --name S      | set the sheet name to S.
  GL  | -q    | --quick       | quick mode: sets sheet name to filename, adds -firstrowhdr.
  GL  | -d D  | --delim D     | file uses delimiter D. Possible values are: 'tab', 'space', or a single character (default: tab).
  GL  | -w N  | --width N     | set the width of all columns to N.
  GL  | -fr N | --firstrow N  | place the first row of the csv file in row N of the sheet (default: 1).
  GL  | -fc N | --firstcol N  | place the first column of the csv file in column N of the sheet (default: 1).
  GL  | -r N  | --rowhdr N    | format row N of the csv file as header (bold). This option may appear multiple times.
  GL  | -c N  | --colhdr N    | format column N of the csv file as header (bold). This option may appear multiple times.
  GL  | -R    | --firstrowhdr | equivalent to --rowhdr 1 (first row will be bold).
  GL  | -C    | --firstcolhdr | equivalent to --colhdr 1 (first column will be bold).
  GL  | -t T  | --titles T    | Set column titles to T (comma delimited).


Properties should be specified as `name=value'. The following property names can be used:

  {}

Full documentation and source code are available on GitHub:

  https://github.com/uf-icbr-bioinformatics/csvutils

(c) 2014-2023, A. Riva, DiBiG, ICBR Bioinformatics, University of Florida

""".format(prog, prog, ", ".join(PROPERTIES)))
    return False

  def parseArgs(self, args):
    if not args or "-h" in args or "--help" in args:
      return self.usage()
    if "-v" in args or "--version" in args:
      self.version()
      return True

    prev = ""
    current = None
    for a in args:
      if len(a) > 1 and a[:2] == '--':
        a = a[1:]
      if prev == "-p":
        self.setProperty(a)
        prev = ""
      elif prev:
        self.setPar(prev, a)
        prev = ""
      elif a in ["-p", "-property"]:
        prev = "-p"
      elif a in ["-q", "-quick"]:
        self.setPar('quick', True)
      elif a in ["-R", "-firstrowhdr"]:
        self.setPar('firstrowhdr', True)
      elif a in ["-C", "-firstcolhdr"]:
        self.setPar('firstcolhdr', True)
      elif a in OPTIONS:
        prev = OPTIONS[a]
      elif a[0] == '-':
        sys.stderr.write("Warning: unrecognized option `{}'.\n".format(a))
      elif self.xlsxfile is None:
        self.xlsxfile = a
      else:
        if os.path.isfile(a):
          C = CSV(a, self.params.copy()) # Create CSV object inheriting global params
          self.csvs.append(C)
          self._current = C
        else:
          sys.stderr.write("Error: file {} does not exist.\n".format(a))
    return True

  def setProperty(self, prop):
    if "=" in prop:
      cp = prop.find("=")
      key = prop[:cp]
      value = prop[cp+1:]
      if key in PROPERTIES: 
        self.properties[key] = value
      else:
        sys.stderr.write("Warning: property `{}' is not a standard Excel property.\n".format(key))
    else:
      sys.stderr.write("Warning: property specifications should have the form `key=value'.\n")

  def findSheetName(self, name):
    for n in self.sheetnames:
      if name.casefold() == n.casefold():
        return n
    return False

  def validateSheetName(self, name):
    name = name[:30] # excel sheet names can't be longer than 31 characters...
    if self.findSheetName(name):
      idx = 1
      prefix = name[:27]
      while True:
        name = "{}_{}".format(prefix, idx)
        if not self.findSheetName(name):
          break
        idx += 1
    self.sheetnames.append(name)
    return name

  def run(self):
    sys.stderr.write("Writing XLSX file {}\n".format(self.xlsxfile))
    workbook = xlsxwriter.Workbook(self.xlsxfile, {'strings_to_numbers': True})
    workbook.set_properties(self.properties)
    self.formats['bold'] = workbook.add_format({'bold': 1})

    # Loop through all defined Csv objects:
    for c in self.csvs:
      c.setQuick(self)
      #c.dump()
      worksheet = workbook.add_worksheet(c.params['name'] if 'name' in c.params else None)
      if PYTHON_VERSION == 2:
        (nrows, ncols) = c.to_worksheet_py2(self, worksheet)
      else:
        (nrows, ncols) = c.to_worksheet(self, worksheet)
      if nrows > 0 and ncols > 0:
        sys.stderr.write("+ File {} added to workbook: {} rows, {} columns.\n".format(c.csvfile, nrows, ncols))
        if 'width' in c.params:
          worksheet.set_column(0, ncols, c.params['width'])

    workbook.close()
    sys.stderr.write("XLSX file written.\n")



# def setupFromCmdline(args):
#     global CSVS
#     quick = False
#     c = None
#     xlsxfile = None
#     header = False
#     prev = ""

#     if '-h' in args:
#         usage()

#     if "-v" in args:
#         version()

#     for a in args[1:]:
#         if a in ['-q', "-quick"]:
#             quick = True
#         elif a in ["-R", "-firstrowhdr"]:
#             setPar(c, 'rowhdr', 0, True)
#         elif a == ["-C", "-firstcolhdr"]:
#             setPar(c, 'colhdr', 0, True)
#         elif a in OPTIONS:
#             prev = a
#         elif prev in ["-name", "-n"]:
#             a = validateSheetName(a)
#             setPar(c, 'name', a)
#             prev = ""
#         elif prev == ["-width", "-w"]:
#             setPar(c, 'width', int(a))
#             prev = ""
#         elif prev in ["-delim", "-d"]:
#             setPar(c, 'delim', decodeDelimiter(a))
#             prev = ""
#         elif prev in ["-fr", "-firstrow"]:
#             setPar(c, 'firstrow', int(a) - 1)
#             prev = ""
#         elif prev in ["-fc", "-firstcol"]:
#             setPar(c, 'firstcol', int(a) - 1)
#             prev = ""
#         elif prev in ["-r", "-rowhdr"]:
#             setPar(c, 'rowhdr', int(a) - 1, True)
#             prev = ""
#         elif prev in ["-c", "-colhdr"]:
#             setPar(c, 'colhdr', int(a) - 1, True)
#             prev = ""
#         elif prev in ["-l", "-header"]:
#             header = a.split(",")
#             prev = ""
#         elif a[0] == '-':
#             sys.stderr.write("Unrecognized option: {}\n".format(a))
#         elif xlsxfile:
#             c = Csv(a)
#             CSVS.append(c)
#         else:
#             xlsxfile = a
#     # for c in CSVS:
#     #     c.dump()
#     if quick:
#         for c in CSVS:
#             c.setQuick()
#     if header:
#         for c in CSVS:
#             c.header = header
#     return xlsxfile


# def main(xlsxfile):
#     global FORMATS

#     sys.stderr.write("Writing XLSX file {}\n".format(xlsxfile))
#     workbook = xlsxwriter.Workbook(xlsxfile, {'strings_to_numbers': True})
#     workbook.set_properties({'author': 'A. Riva, ariva@ufl.edu', 'company': 'DiBiG - ICBR Bioinformatics'}) # these should be read from conf or command-line
#     FORMATS['bold'] = workbook.add_format({'bold': 1})

#     # Loop through all defined Csv objects:
#     for c in CSVS:
#         worksheet = workbook.add_worksheet(c.name)
#         if PYTHON_VERSION == 2:
#           (nrows, ncols) = c.to_worksheet_py2(worksheet)
#         else:
#           (nrows, ncols) = c.to_worksheet(worksheet)
#         if nrows > 0 and ncols > 0:
#             sys.stderr.write("+ File {} added to workbook: {} rows, {} columns.\n".format(c.csvfile, nrows, ncols))
#             if c.width:
#                 worksheet.set_column(0, ncols, c.width)

#     workbook.close()
#     sys.stderr.write("XLSX file written.\n")

def csvtoxls_main():
  M = CSVtoXLSX()
  if M.parseArgs(sys.argv[1:]):
    M.run()

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
