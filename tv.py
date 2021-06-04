#!/usr/bin/env python

#####
#
# tv.py - Interactive, full-screen viewer for delimited files.
#
####
__doc__ = "Interactive, full-screen viewer for delimited files."
__author__ = "Alberto Riva, UF ICBR Bioinformatics core, University of Florida"
__email__ = "ariva@ufl.edu"
__license__ = "GPL v3.0"
__copyright__ = "Copyright 2018, University of Florida Research Foundation"

import sys
import csv
import time
import curses

PY3 = (sys.version_info.major == 3)

if PY3:
    from curses import wrapper
else:
    from curses.wrapper import wrapper

def writeDelimiter(d):
    x = "t" if ord(d) == 9 else d
    return x

class TDFile():
    filename = None
    label = ""
    delim = None
    delimname = ""
    quotechar = None
    rmode = False
    data = []
    nrows = 0
    ncols = 0
    colsizes = None
    row = 0
    col = 0
    gap = 1
    maxrows = 1000
    header = False
    
    def __init__(self, filename):
        self.filename = filename
        if self.delim is None:
            self.delim = self.detectDelimiter()
            self.delimname = writeDelimiter(self.delim)
            # sys.stderr.write("Delimiter: {} {}\n".format(self.delim, self.delimname))
            # raw_input()
        rows_read = 0
        self.data = []
        first = True
        with open(self.filename, "r") as f:
            c = self.openReader(f)
            for parsed in c:
                if first and self.rmode:
                    parsed = ['\t'] + parsed
                    first = False
                ll = len(parsed)
                self.nrows += 1
                if self.colsizes:
                    for i in range(self.ncols):
                        if i < ll:
                            self.colsizes[i] = max(self.colsizes[i], len(parsed[i]))
                else:
                    self.ncols = len(parsed)
                    self.colsizes = [len(w) for w in parsed]
                self.data.append(parsed)
                rows_read += 1
                if rows_read >= self.maxrows:
                    break
        self.row = 0
        self.col = 0

    def openReader(self, f):
        if self.delim == ',':
            return csv.reader(f, delimiter=self.delim, quotechar='"')
        else:
            return csv.reader(f, delimiter=self.delim)
        
    def detectDelimiter(self):
        hits = {'\t': 0, ',': 0, ';': 0, ':': 0}
        with open(self.filename, "r") as f:
            for i in range(5):
                line = f.readline()
                for ch in line:
                    if ch in hits:
                        hits[ch] += 1
        best = ''
        bestc = 0

        for ch in hits.keys():
            count = hits[ch]
            if count > bestc:
                best = ch
                bestc = count
        #sys.stderr.write("Delimiter detected as: {}\n".format("tab" if best == "\t" else best))
        #time.sleep(1)
        return best

    def writeLine(self, win, ypos, w, rdata, attr):
        xpos = 0
        l = len(rdata)
        c = self.col
        while True:
            if c >= l:
                break
            toDisplay = rdata[c]
            if xpos + self.colsizes[c] >= w:
                av = w - xpos - 2
                if len(toDisplay) > av:
                    toDisplay = toDisplay[:av] + " >"
            win.addstr(toDisplay, attr)
            xpos += self.colsizes[c] + self.gap
            if xpos >= w:
                break
            win.move(ypos, xpos)
            c += 1
            if c >= self.ncols:
                break

    def display(self, win):
        """Display the current view of the file in window `win'."""
        (h, w) = win.getmaxyx()
        ypos = 0
        r = self.row
        win.move(0, 0)
        win.erase()
        if self.header:
            self.writeLine(win, 0, w, self.data[0], curses.A_BOLD)
            ypos = 1
            win.move(1, 0)
            if r == 0:
                r = 1
        maxrow = h - 1
        while True:
            rdata = self.data[r]
            self.writeLine(win, ypos, w, rdata, curses.A_NORMAL)
            r += 1
            ypos += 1
            xpos = 0
            if ypos == maxrow or r == self.nrows:
                break
            win.move(ypos, xpos)
        win.move(maxrow, 0)
        win.addstr("[{}] Row: {}/{} Col: {}/{}".format(self.delimname, self.row + 1, self.nrows, self.col + 1, self.ncols), curses.A_BOLD)
        win.move(maxrow, w - len(self.label) - 1)
        win.addstr(self.label, curses.A_BOLD)
        win.refresh()

    def left(self):
        if self.col > 0:
            self.col += -1

    def right(self):
        self.col += 1
        if self.col == self.ncols:
            self.col += -1

    def up(self):
        if self.row > 0:
            self.row += -1

    def down(self):
        self.row += 1
        if self.row == self.nrows:
            self.row += -1

    def top(self):
        self.row = 0

    def bottom(self):
        self.row = self.nrows - 1

    def pageup(self, win):
        (h, w) = win.getmaxyx()
        if self.row >= h:
            self.row -= h

    def pagedown(self, win):
        (h, w) = win.getmaxyx()
        if self.row + h < self.nrows:
            self.row += h

    def askRow(self, win):
        (h, w) = win.getmaxyx()
        win.move(h-1, 0)
        win.clrtoeol()
        win.addstr("Enter row number: ", curses.A_BOLD)
        try:
            curses.echo()
            r = win.getstr()
        finally:
            curses.noecho()
        try:
            r = int(r)
            if r <= 0 or r > self.nrows:
                return
            self.row = r - 1
        except ValueError:
            pass

    def askColumn(self, win):
        (h, w) = win.getmaxyx()
        win.move(h-1, 0)
        win.clrtoeol()
        win.addstr("Enter column number: ", curses.A_BOLD)
        try:
            curses.echo()
            c = win.getstr()
        finally:
            curses.noecho()
        try:
            c = int(c)
            if c <= 0 or c > self.ncols:
                return
            self.col = c - 1
        except ValueError:
            pass

def decodeDelimiter(a):
    if a == 'tab':
        return '\t'
    else:
        return a

def usage():
    sys.stdout.write("""tv.py - viewer for delimited files

Usage: tv.py [options] filenames...

Options:
  -d D | Use character D as delimiter (use 'tab' for tab). Default: autodetect.
  -m M | Read the first M lines from each input file (default: {}).
  -b   | Enable header mode (first line bold and always visible).

While displaying a file, the following keys can be used:

  arrow keys  | move up, down, left, right
  Enter       | move down
  Home, End   | go to top or bottom of file respectively
  PgUp        | move up one page
  PgDn, Space | move down one page
  keypad '5'  | go to first line, first column
  r           | prompt for row number, jump to it
  c           | prompt for column number, jump to it
  h           | toggle header mode
  n           | jump to next file
  p           | jump to previous file
  +/-         | increase, decrease gap between columns
  q, Q        | quit

(c) 2018, A. Riva, ICBR Bioinformatics Core, University of Florida

""".format(TDFile.maxrows))

class Driver():
    files = []
    nfiles = 0
    current = 0
    quitting = False

    def __init__(self, args):
        self.parseArgs(args)

    def parseArgs(self, args):
        if "-h" in args:
            return
        prev = ""
        for a in args:
            if prev == "-m":
                TDFile.maxrows = int(a)
                prev = ""
            elif prev == "-d":
                TDFile.delim = decodeDelimiter(a)
                #print "decoded: <{}>".format(TDFile.delimiter)
                prev = ""
            elif a in ["-m", "-d"]:
                prev = a
            elif a == '-b':
                TDFile.header = True
            elif a == '-R':
                TDFile.rmode = True
            else:
                self.files.append([a, None])
        self.nfiles = len(self.files)

    def displayAll(self, win):
        while True:
            pfile = self.files[self.current]
            filename = pfile[0]
            if not pfile[1]:
                pfile[1] = TDFile(filename)
            tdf = pfile[1]
            if self.nfiles == 1:
                tdf.label = filename
            else:
                tdf.label = "{} [{}/{}]".format(filename, self.current + 1, self.nfiles)
            self.run(win, tdf)
            if self.quitting:
                return

    def run(self, win, tdf):
        curses.curs_set(0)
        while True:
            tdf.display(win)
            a = win.getch()
            if a in [113, 81]:      # Quit (q, Q)
                self.quitting = True
                break
            elif a == ord('n'):
                self.current += 1
                if self.current == self.nfiles:
                    self.current -= 1
                else:
                    break
            elif a == ord('p'):
                if self.current > 0:
                    self.current -= 1
                    break
            elif a == curses.KEY_RIGHT:
                tdf.right()
            elif a == curses.KEY_LEFT:
                tdf.left()
            elif a == curses.KEY_UP:
                tdf.up()
            elif a in [curses.KEY_DOWN, ord('\n')]:
                tdf.down()
            elif a == curses.KEY_HOME:
                tdf.top()
            elif a == curses.KEY_END:
                tdf.bottom()
            elif a == curses.KEY_PPAGE:
                tdf.pageup(win)
            elif a in [curses.KEY_NPAGE, 32]:
                tdf.pagedown(win)
            elif a == ord('r'):
                tdf.askRow(win)
            elif a == ord('c'):
                tdf.askColumn(win)
            elif a == ord('+'):
                tdf.gap += 1
            elif a == ord('-'):
                if tdf.gap > 0:
                    tdf.gap -= 1
            elif a == ord('h'):
                tdf.header = not tdf.header
            elif a == 350:       # Keypad 5
                tdf.col = 0
                tdf.top()

if __name__ == "__main__":
    D = Driver(sys.argv[1:])
    if D.nfiles > 0:
        _wrapper(D.displayAll)
    else:
       usage()     
