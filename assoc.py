#!/usr/bin/env python

"""assoc.py - build association table from tab-delimited file, and decode lines from stdin."""

import sys
import csv
import json

def parseFilename(s):
    p = s.rfind(":")
    if p > 0:
        return (s[:p], int(s[p+1:]) - 1)
    else:
        return (s, 0)

def decodeDelimiter(d):
    if d == 'tab':
        return '\t'
    elif d == 'sp':
        return ' '
    elif d == 'nl':
        return '\n'
    else:
        return d

class Assoc(object):
    filename = ""
    words = []
    mode = "normal"
    incol = 0
    outcol = None
    delimiter = '\t'
    _missing = '???'
    _preserve = False
    _interactive = False
    _whole = False
    _data = {}

    def __init__(self, args):
        self.words = []
        self._data = {}
        self.parseArgs(args)

    def parseArgs(self, args):
        prev = ""
        for a in args:
            if prev == "-i":
                self.incol = int(a) - 1
                prev = ""
            elif prev == "-o":
                self.outcol = int(a) - 1
                prev = ""
            elif prev == "-m":
                self._missing = a
                prev = ""
            elif prev == "-d":
                self.delimiter = decodeDelimiter(a)
                prev = ""
            elif a in ["-i", "-o", "-m", "-d"]:
                prev = a
            elif a in ["-j", "-J"]:
                self.mode = a
            elif a == "-p":
                self._preserve = True
            elif a == "-w":
                self._whole = True
            elif a == "-r":
                self._interactive = True
            elif self.filename:
                self.words.append(a)
            else:
                if self.mode == "normal":
                    (f, c) = parseFilename(a)
                    self.filename = f
                    self.incol = c
                else:
                    self.filename = a

        if not self.outcol:
            self.outcol = self.incol + 1

    def readTable(self):
        src = self.filename
        if self.mode == "-j":
            self.readJSONfile()
        elif self.mode == "-J":
            self.readJSON()
            src = "JSON string"
        else:
            with open(self.filename, "r") as f:
                c = csv.reader(f, delimiter=self.delimiter)
                for line in c:
                    if len(line) > 1 and line[0][0] != "#":
                        if self._whole:
                            self._data[line[self.incol]] = "\t".join(line)
                        else:
                            self._data[line[self.incol]] = line[self.outcol]
        sys.stderr.write("[{} associations read from {}.]\n".format(len(self._data), src))

    def readJSONfile(self):
        with open(self.filename, "r") as f:
            self._data = json.load(f)

    def readJSON(self):
        self._data = json.loads(self.filename)

    def decode(self):
        try:
            for line in sys.stdin:
                line = line.strip()
                #print "/" + line + "/"
                if line in self._data:
                    w = str(self._data[line])
                elif self._preserve:
                    w = line
                else:
                    w = self._missing
                try:
                    sys.stdout.write(w + "\n")
                except IOError:
                    return
        except KeyboardInterrupt:
            return

    def decode_w(self):
        for v in self.words:
            if v in self._data:
                w = str(self._data[v])
            elif self._preserve:
                w = v
            else:
                w = self._missing
            sys.stdout.write(w + "\n")

    def decode_i(self):
        try:
            while True:
                line = input()
                if not line:
                    return
                line.strip()
                #print "/" + line + "/"
                if line in self._data:
                    w = str(self._data[line])
                elif self._preserve:
                    w = line
                else:
                    w = self._missing
                try:
                    sys.stdout.write(w + "\n")
                except IOError:
                    return
        except EOFError:
            return
        except KeyboardInterrupt:
            return
        

def usage():
    sys.stdout.write("""assoc.py - Create association table from tab-delimited or JSON file.

Usage: assoc.py [options] filename [words...]

This program reads a tab-delimited file `filename' and builds a table mapping the 
strings from the input column (by default, the first one) to the corresponding ones
in the output column (by default the one after the input column, unless a different
one is specified with the -o argument). A different input column can be specified
with the -i argument or by appending :N to the filename, where N is the column number. 

After creating the mapping, the program will read convert the words specified on the 
command line to the corresponding values in the mapping. If a word does not appear
in the translation table, the program prints the missing value tag (set with -m) 
unless -p is specified, in which case the original identifier is printed unchanged.
If no words are specified, the program reads them from standard input. 

if -j is specified, the mapping file is assumed to be in JSON format. It should contain
a single, flat dictionary mapping keys to values, e.g.: {{"a": 1, "b": 2}}. If -J is 
specified, the JSON dictionary is supplied on the command line in place of the filename 
argument, e.g.:

    assoc.py -J '{{"a": 1, "b": 2}}' other arguments...

Options:

  -i I | Set input column to I (1-based). Default: {}.
  -o O | Set output column to O (1-based). Default: {}.
  -m M | Set the missing value tag to M. Default: '{}'.
  -d D | Set delimiter to D. Use 'sp' for space and 'nl'
         for newline. Default: tab. 
  -p   | Preserve mode: if an input string has no translation, 
         print the string itself instead of the missing tag.
  -w   | Whole-line mode: output is the whole line associated with the identifier.
  -r   | Interactive mode.
  -j   | Input file is in JSON format.
  -J   | First argument is a JSON string.

Examples:

  assoc.py -o 3 file

will map the contents of column 1 to the contents of column 3, while

  assoc.py file:2 

will map the contents of column 2 to the contents of column 3.

""".format(Assoc.incol, Assoc.outcol, Assoc._missing))
    sys.exit(0)

if __name__ == "__main__":
    args = sys.argv[1:]
    if len(args) == 0 or "-h" in args or "--help" in args:
        usage()
    A = Assoc(args)
    A.readTable()
    if A._interactive:
        A.decode_i()
    elif A.words:
        A.decode_w()
    else:
        A.decode()
