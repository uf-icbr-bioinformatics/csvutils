#!/usr/bin/env python

###################################################
#
# (c) 2016, Alberto Riva, ariva@ufl.edu
# DiBiG, ICBR Bioinformatics, University of Florida
#
# See the LICENSE file for license information.
###################################################

import sys
import gzip
import os.path

class Colx():
    current = None
    newlist = None
    multidc = {}
    mode = 'i'                  # 'd' for difference, '-u' for union
    isFirst = True
    ignchar = '#'
    delchar = '\t'
    outfile = None
    write = False
    quiet = False
    sort = False                # Value is a string, if it contains 'n', sort numerically, if it contains 'r', reverse.
    multi = False
    
    def __init__(self):
        self.current = set()
        self.newlist = set()
        self.multi = {}
        self.isFirst = True

    def addColumn(self, filename, col):
        # print "entering: {}".format(self.current)
        n = 0
        fn_open = gzip.open if filename.endswith('.gz') else open
        with fn_open(filename, "r") as f:
            for line in f:
                if not line.startswith(self.ignchar):
                    parsed = line.rstrip("\r\n").split(self.delchar)
                    e = parsed[col]
                    if e != '':
                        n += 1
                        if self.isFirst:
                            self.current.add(e)
                        elif self.mode in ['i', 'd']:
                            self.newlist.add(e)
                        else:
                            self.current.add(e)
        if not self.isFirst:
            if self.mode == 'i':
                self.current = self.current & self.newlist
                self.newlist = set()
            elif self.mode == 'd':
                self.current = self.current - self.newlist
                self.newlist = set()
        # print "exiting: {}".format(self.current)
        return n

    def addColumnOld(self, filename, col):
        n = 0
        if self.mode == 'i' and not self.isFirst and self.current == []:
            return False            # we already know what's going to happen...
        if self.mode == 'u' and not self.isFirst: # If computing union, every time start from previous list
            self.newlist = self.current
        fn_open = gzip.open if filename.endswith('.gz') else open
        with fn_open(filename, "r") as f:
            for line in f:
                if not line.startswith(self.ignchar):
                    parsed = line.rstrip("\r\n").split(self.delchar)
                    e = parsed[col]
                    if e != '':
                        n += 1
                        if self.isFirst: # first time around, simply build the initial list
                            self.current.append(e)
                        elif self.mode == 'i':
                            if e in self.current:
                                self.newlist.append(e)
                        elif self.mode == 'u' or self.mode == 'd':
                            self.newlist.append(e)
        if self.mode == 'd':
            old = self.current
            self.current = []
            for e in old:
                if not e in self.newlist:
                    self.current.append(e)
            self.newlist = []
        elif not self.isFirst:
            self.current = self.newlist
            self.newlist = []
        return n

    def addColumnMulti(self, filename, col, idx):
        m = self.multidc
        n = 0
        fn_open = gzip.open if filename.endswith('.gz') else open
        with fn_open(filename, "r") as f:
            for line in f:
                if not line.startswith(self.ignchar):
                    parsed = line.rstrip("\r\n").split(self.delchar)
                    e = parsed[col]
                    if e != '':
                        n += 1
                        if e in m:
                            m[e] = m[e] | idx
                        else:
                            m[e] = idx
        return n

    def reportMulti(self, multimap, idx):
        # print self.multidc
        for i in range(3, idx): # we don't care about 1 and 2
            if not i in multimap:
                n = 0
                for (item, count) in self.multidc.iteritems():
                    if (count & i) == i:
                        n += 1
                files = decodeBitmask(multimap, i)
                sys.stdout.write("{}: {}\n".format(files, n))
    
    def sortCurrent(self):
        """Sort the contents of the 'current' set according to the flags in the 'sort' attribute. Returns sorted values as list."""
        if self.sort:
            reverse = ('r' in self.sort)
            if 'n' in self.sort:
                data = [ (float(x), x) for x in self.current ]
                sdata = sorted(data, reverse=reverse)
                return [ x[1] for x in sdata]
            else:
                return sorted(self.current, reverse=reverse)
        else:
            return list(self.current)
        
def writeList(stream, data):
    for c in data:
        stream.write(c + "\n")

def decodeBitmask(map, value, sep='|'):
    result = []
    x = 1
    while x <= value:
        if value & x > 0:
            result.append(map[x])
        x = x * 2
    return sep.join(result)
            
def parseFilespec(fs):
    """Parse a filespec of the form 'filename' or 'filename:c', where filename is an existing file
and c is a column number (defaulting to 1). Returns a tuple (filename, c-1) if successful, False 
otherwise."""
    c = 1
    p = fs.find(":")
    if p > -1:
        s = fs[p+1:]
        if s != '':
            c = int(s)
        fs = fs[:p]
    if os.path.isfile(fs):
        return (fs, c-1)
    else:
        return False
    
def main(C, args):
    next = ""
    multimap = {}
    idx = 1
    for a in args:
        if next == '-o':
            C.outfile = a
            next = ""
        elif next == '-c':
            if a == 's':
                C.delchar = " "
            elif a == 't':
                C.delchar = "\t"
            else:
                C.delchar = a[0]
            next = ""
        elif next == '-g':
            C.ignchar = a[0]
            next = ""
        elif a in ['-o', '-c', '-g']:
            next = a
        elif a == '-w':
            C.write = True
        elif a == '-q':
            C.quiet = True
        elif a.startswith('-s'):
            C.sort = a[1:]
        elif a == '-m':
            C.multi = True
        elif a in ['-i', '-d', '-u']:
            C.mode = a[1:]
        else:
            fs = parseFilespec(a)
            if fs:
                if C.multi:
                    multimap[idx] = "{}:{}".format(fs[0], fs[1]+1)
                    n = C.addColumnMulti(fs[0], fs[1], idx)
                    idx = idx * 2
                else:
                    n = C.addColumn(fs[0], fs[1])
                C.isFirst = False
                if n and not C.quiet:
                    sys.stderr.write("{}:{}: {} elements\n".format(fs[0], fs[1]+1, n))

    if C.multi:
        C.reportMulti(multimap, idx)
    else:
        data = C.sortCurrent()
        if not C.quiet:
            if C.mode == 'd':
                label = 'Difference'
            elif C.mode == 'u':
                label = 'Union'
            else:
                label = 'Intersection'

            sys.stderr.write("{}: {} elements\n".format(label, len(data)))
        if C.outfile:
            with open(C.outfile, "w") as out:
                writeList(out, data)
        if C.write:
            writeList(sys.stdout, data)

def usage():
    sys.stderr.write("""Usage: colx.py [-wqsmiduh] [-o outfile] filespecs...

Count and optionally print the intersection (or union, or difference) of the elements 
in specified columns of two or more files. Filespecs have the form filename:col where
filename points to an existing file and col is column number. If col is omitted it 
defaults to 1 (the first column). The number of entries in each input column and in
the final output are printed to standard error.

  -h         | Print this usage message. Ignore all other options.
  -o outfile | Print the resulting list to file 'outfile' (can be combined with -w).
  -w         | Print the resulting elements to standard output.
  -q         | Do not print counts to standard error.
  -s[r][an]  | Sort resulting list. By default, sort is alphabetical. Add an 'n' to
               sort numerically instead. Add an 'r' to reverse sort order.
  -c char    | Use 'char' as delimiter. Use 's' for space, 't' for tab (default).
  -g char    | Lines starting with 'char' will be ignored (default: #).
  -m         | Enable 'multi' mode. Will compute all pairwise intersections between
               all input columns. Disables -i, -d, -u.
  -i         | Intersection mode. Result will consist of the intersection of all
               input columns. This is the default mode.
  -u         | Union mode. Result list includes all elements of all input columns.
  -d         | Difference mode. Result list includes elements in first list but
               not in successive lists.

Note that filespecs are processed in left-to-right order, and the mode can be changed
any number of times while processing the files. For example, the following:

  colx.py -u f:1 f:2 -d f:3

computes the union of the elements in columns 1 and 2 of file f, and then removes the
elements in column 3. This also applies to other options. For example, if file f1 is
tab-delimited and file f2 is comma-delimited, you can do:

  colx.py -c t f1:1 -c , f2:1

to use the appropriate delimiter for each file.

Full documentation and source code are available on GitHub:

  http://github.com/albertoriva/colx/

(c) 2016, A. Riva, DiBiG, ICBR Bioinformatics, University of Florida

""")

            
if __name__ == "__main__":
    args = sys.argv[1:]
    if '-h' in args or '--help' in args:
        usage()
    else:
        main(Colx(), args)
        
