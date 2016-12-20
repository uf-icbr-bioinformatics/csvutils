#!/usr/bin/env python

###################################################
#
# (c) 2016, Alberto Riva, ariva@ufl.edu
# DiBiG, ICBR Bioinformatics, University of Florida
#
# See the LICENSE file for license information.
###################################################

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
        elif a == '-h':
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
        if ZERO:
            idx = 0
        else:
            idx = 1
        if RAW:
            for p in range(ncols):
                print hdr[p]
        elif FIRSTHDR:
            for p in range(ncols):
                print "  {} = {}".format(hdr[p], row[p])
        else:
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
    sys.stderr.write("""Usage: cols.py [-h] [-c] [-0] [-m] [-d D] [-s N] [-R] files...

Examine one or more delimited files and report one of the following:

number of columns in the first line (default)
numbered list of entries in the first line (-c, --colnames)
number of lines matching the number of columns in the first line (-m, --matches)
 
Delimiter is tab by default, can be changed with -d option. Numbering starts
at 1, unless -0 is specified, in which case it is zero-based.

The program examines the first row by default, or the line specified with the
-s option. If -S is used instead of -s, the program prints the contents of the
specified line using the contents of the first line as column names instead of
progressive numbers.

If -R is specified, assume the header is in R style (ie, the header for the first
column is missing).
""")

if __name__ == "__main__":
    parseOptions(sys.argv[1:])
    if len(INFILES) == 0:
        processFromStream("stdin", sys.stdin)
    else:
        for f in INFILES:
            processOneFile(f)
