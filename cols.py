#!/usr/bin/env python

#####
#
# cols.py - Display and check number of columns in delimited files.
#
####
__doc__ = "Display and check number of columns in delimited files."
__author__ = "Alberto Riva, UF ICBR Bioinformatics core, University of Florida"
__email__ = "ariva@ufl.edu"
__license__ = "GPL v3.0"
__copyright__ = "Copyright 2018, University of Florida Research Foundation"


import sys
import csv
import os.path

DELIMITER = '\t'
MODE = 'default'
RSTYLE = False
ZERO = False
FIRSTHDR = False                # First row is header regardless of ROWNUM
ROWNUM = 1
SKIP = None
RAW = False
INFILES = []
ITEMSFILE = None
ITEMS = []

def parseOptions(args):
    global MODE
    global RSTYLE
    global ZERO
    global DELIMITER
    global ROWNUM
    global FIRSTHDR
    global SKIP
    global RAW

    next = ""
    for a in args:
        if next == "-d":
            DELIMITER = a
            next = ""
        elif next == "-s":
            try:
                ROWNUM = int(a)
            except ValueError:
                SKIP = a
            next = ""
        elif next == "-S":
            ROWNUM = int(a)
            FIRSTHDR = True
            next = ""
        elif a == '-h' or a == '--help':
            usage()
            sys.exit(1)
        elif a in ['-d', '-s', '-S']:
            next = a
        elif a in ['-c', '--colnames']:
            MODE = 'names'
        elif a in ['-m', '--matches']:
            MODE = 'matches'
        elif a in ['-r', '--raw']:
            MODE = 'names'
            RAW = True
        elif a in ['-i', '--index']:
            MODE = 'index'
        elif a == '-0':
            ZERO = True
        elif a == '-R':
            RSTYLE = True
        else:
            INFILES.append(a)

def processFromStream(filename, f):
    # print "skipping to row {}".format(ROWNUM)
    hdr = []
    row = []
    reader = csv.reader(f, delimiter=DELIMITER, quotechar='"')
    # print (MODE, ROWNUM, DELIMITER, SKIP, FIRSTHDR, RAW)

    if FIRSTHDR:
        #hdr = f.readline().rstrip("\n").split(DELIMITER)
        hdr = reader.next()

    if RSTYLE:
        hdr = ["<<RowNum>>"] + hdr

    for i in range(1, ROWNUM):
        #f.readline()
        reader.next()

    while True:
        #row = f.readline().rstrip("\n").split(DELIMITER)
        row = reader.next()
        if SKIP == None or hdr[0][0] != SKIP:
            break

    ncols = len(row)
    if MODE == 'default':
        sys.stderr.write("{}: {} columns.\n".format(filename, ncols))
    elif MODE == 'names':
        sys.stderr.write("{}: {} columns.\n".format(filename, ncols))

        if RAW:
            for p in range(ncols):
                print row[p]
        elif FIRSTHDR:
            for p in range(ncols):
                print "  {} = {}".format(hdr[p], row[p])
        else:
            idx = 0 if ZERO else 1
            for h in row:
                print "  {} = {}".format(idx, h)
                idx += 1

    elif MODE == 'matches':
        total = 0
        matching = 0
        for line in f:
            total += 1
            if line.count(DELIMITER) + 1 == ncols:
                matching += 1
        sys.stderr.write("{}: {} columns, {}/{} matching.\n".format(filename, ncols, matching, total))
    
def processOneFile(filename):
    ncols = 0
    if os.path.exists(filename):
        with open(filename, "r") as f:
            processFromStream(filename, f)
    else:
        sys.stderr.write("{}: File not found.\n".format(filename))

def usage():
    sys.stderr.write("""cols.py - analyze columns in a delimited file.

Usage: cols.py [-h] [-c] [-0] [-m] [-d D] [-s N] [-R] [-i I] files...

With no options, print the number of columns in each of the supplied 
files (computed as the number of fields in header, by default the 
first row of the file). If no files are supplied, read standard input.

Options:

  -h, --help     | Print this help message.
  -c, --colnames | Print entries in the first line as numbered list.
  -m, --matches  | Print the number of lines matching the number of
                   fields in the header line.
  -i, --items I  | Print to standard output the columns of each input
                   file matching the items in file I.
  -r, --raw      | Print the contents of the header line, one item
                   per line.
  -s N           | Use line N as the header (default: 1)
  -S N           | Print the contents of line N using the first line
                   as field names, in the format "field = value".
  -0             | Number columns starting at 0 instead of 1.
  -d D           | Use D as the delimiter (default: tab).
  -R             | Assume R-style header (number of fields in header
                   line is one less than the number of fields in the
                   rest of the file.

""")

if __name__ == "__main__":
    parseOptions(sys.argv[1:])
    if len(INFILES) == 0:
        processFromStream("stdin", sys.stdin)
    else:
        for f in INFILES:
            processOneFile(f)
