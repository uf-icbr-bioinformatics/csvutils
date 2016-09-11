#!/usr/bin/env python

###################################################
#
# (c) 2015, Alberto Riva, ariva@ufl.edu
# DiBiG, ICBR Bioinformatics, University of Florida
#
# See the LICENSE file for license information.
###################################################

###################################################
#
# TODO:
# 1. implement defaults. Delimiter, header (y/n), nunique - DONE
# 2. option to skip initial lines - DONE
# 3. what to do for lines that don't have the same number
#    of fields as the header?
# 4. command to find unique values in a column - DONE
# 4b. output of unique becomes new table
# 5. finish regex support
###################################################

import os
import re
import sys
import time
import shlex
import Tkinter, tkFileDialog

try:
    import readline
    HAS_READLINE=True
except ImportError:             # Windows doesn't have readline :(
    HAS_READLINE=False

HAS_ANSI = True
from sys import platform as _platform
if _platform[0:3] == 'win':
    HAS_ANSI = False            # Windows doesn't have ANSI :(

### Utilities

def readDelimited(stream, delimiter):
    line = stream.readline().rstrip("\n\r")
    return line.split(delimiter)

def parseDelimited(line, delimiter):
    return line.rstrip("\n\r").split(delimiter)

def parseCommandLine(line):
    p = shlex.split(line)       # To respect quotes
    return p

def toInt(s, warn=False):
    try:
        return int(s)
    except ValueError:
        if warn:
            print "Value '{}' should be a number.".format(s)
        return None

def toFloat(s, warn=False):
    try:
        return float(s)
    except ValueError:
        if warn:
            print "Value '{}' should be a number.".format(s)
        return None

def startAnsi(s, base, color):
    """Write the ANSI code for color `color' to stream `s'."""
    if HAS_ANSI:
        s.write("\033[{};{}m".format(base, color))

def startBold(s):
    """Write the ANSI code for bold to stream `s'."""
    if HAS_ANSI:
        s.write("\033[1;1m")

def endAnsi(s):
    """Write the ANSI code for normal font to stream `s'."""
    if HAS_ANSI:
        s.write("\033[0;0m")

def promptFor(prompt, default=None, convert=None):
    if default == None:
        s = "{}: ".format(prompt)
    else:
        s = "{} [{}]: ".format(prompt, default)
    try:
        w = raw_input(s)
    except EOFError:
        w = ''
    if w == '':
        if default == None:
            w = None
        else:
            w = default
    if convert:
        return convert(w)
    else:
        return w

def convertDelimiter(d):
    if d == 'tab':
        return '\t'
    elif d == 'comma':
        return ','
    elif d == 'pipe':
        return '|'
    elif len(d) == 1:
        return d
    else:
        print "The delimiter should be one of tab, comma, pipe, or a single character."
        return '\t'

def unconvertDelimiter(d):
    # print "Unconverting '{}'".format(d)
    if d == '\t':
        return 'tab'
    else:
        return d

def convertBoolean(d):
    return (d == 'True' or d == 'true' or d == 'T')

def convertInt(d):
    try:
        return int(d)
    except ValueError:
        print "The value {} should be a number.".format(d)
        return None

### Defaults management

def getDefault(key):
    return defaults[key][0]

def setDefault(key, value):
    dfl = defaults[key]
    convert = dfl[1]
    dfl[0] = convert(value)

def askDefault(key, prompt):
    dfl = defaults[key]
    # print "Asking for {}.".format(key)
    v = promptFor(prompt, default=unconvertDelimiter(dfl[0]), convert=dfl[1])
    # print "Received '{}'".format(v)
    if v != None:
        dfl[0] = v
        return v

def showDefaults():
    for k in sorted(defaults):
        dfl = defaults[k]
        startBold(sys.stdout)
        print k,
        endAnsi(sys.stdout)
        print " - {}: {}".format(dfl[2], unconvertDelimiter(dfl[0]))

def askAllDefaults():
    for k in sorted(defaults):
        dfl = defaults[k]
        askDefault(k, dfl[2])

def askSomeDefaults(keys):
    for k in keys:
        dfl = defaults[k]
        askDefault(k, dfl[2])

### Testing functions

def testEqual(x, v):
    return x == v

def testNotEqual(x, v):
    return x != v

def testGreater(x, v):
    return x > v

def testSmaller(x, v):
    return x < v

def testGreaterEq(x, v):
    return x >= v

def testSmallerEq(x, v):
    return x <= v

def testSubstring(x, v):
    #print "x={}, v={}".format(x,v)
    return re.search(v, x)

### Class representing a table (read from a file)

class Table():
    idx = 0
    filename = ""
    columns = []                # List of columns in original order
    vcols = []                  # List containing visible columns in the desired order
    data = []
    nrow = 0
    vrow = 0
    ncol = 0

    def __init__(self, filename):
        self.filename = filename

    def readFile(self):
        n = 0
        delimiter = getDefault('delimiter')
        filename = os.path.expanduser(self.filename)
        if not os.path.isfile(filename):
            print "File `{}' does not exist.".format(filename)
            return None

        with open(filename, "r") as f:
            # Skip extra lines before header if necessary
            for n in range(getDefault('skip')):
                f.readline()
            
            # Read header
            self.colnames = readDelimited(f, delimiter)
            nc = 0
            for c in self.colnames:
                ce = [nc, c, True]
                self.columns.append(ce)
                self.vcols.append(ce)
                nc += 1
            self.ncol = nc
            
            while True:
                line = f.readline()
                if not line:
                    break
                row = parseDelimited(line, delimiter)
                self.data.append([True, row]) # all rows are initially visible
                n += 1
        self.nrow = n
        self.vrow = n
        return (self.ncol, self.nrow)

    def describe(self):
        print "Table `{}', {}/{} columns, {}/{} rows.".format(self.filename, len(self.vcols), self.ncol, self.vrow, self.nrow)

    def showColumns(self):
        """Print the names of the columns in this table."""
        for c in self.columns:
            if c[2]:
                print "{:2}. {}".format(c[0] + 1, c[1])
            else:
                print "{:2}, [{}]".format(c[0] + 1, c[1])
                
    def showVisibleColumns(self):
        """Print the names of the columns in this table."""
        i = 1
        for c in self.vcols:
            if c[2]:
                print "{:2}. {}".format(i, c[1])
                i += 1

    def getColumnDesc(self, name):
        """Returns the descriptor for column named `name'."""
        for ce in self.columns:
            if ce[1] == name:
                return ce
        else:
            return None

    def getColumnDescByIdx(self, idx):
        """Returns the descriptor for column with index `idx'."""
        for ce in self.columns:
            if ce[0] == idx:
                return ce
        else:
            return None

    def getColumnIdx(self, name):
        """Returns the position of the column named `name'."""
        d = self.getColumnDesc(name)
        if d:
            return d[0]
        else:
            return None

    def resolveColumn(self, nameOrId):
        """Returns the descriptor for the column indicated by `nameOrId'. If
`nameOrId' starts with an @, the remaining part is interpreted as a column
number (1-based), otherwise as a column name. Returns None if the column
cannot be found."""
        if nameOrId[0] == '@':
            idx = toInt(nameOrId[1:], warn=True)
            if idx == None:
                return None
            idx = idx -1
            if idx > self.ncol:
                print "The current table only has {} columns, but column {} was addressed.".format(self.ncol, idx + 1)
                return None
            return self.getColumnDescByIdx(idx)
        else:
            return self.getColumnDesc(nameOrId)

    def resolveColumns(self, namesOrIds):
        result = []
        for n in namesOrIds:
            desc = self.resolveColumn(n)
            if desc != None:
                result.append(desc)
        return result

    def selectAllColumns(self):
        """Make all columns in this table visible."""
        for ce in self.columns:
            ce[2] = True
        self.vcols = [ce for ce in self.columns]
    
    def selectColumns(self, names):
        for ce in self.columns:
            ce[2] = False
        self.vcols = self.resolveColumns(names)
        for ce in self.vcols:
            ce[2] = True

    def reset(self):
        """Return all rows and columns to visible status."""
        for row in self.data:
            row[0] = True
        self.vrow = self.nrow

    def hideAllRows(self):
        """Make all rows invisible."""
        for row in self.data:
            row[0] = False
        self.vrow = 0

    def filterRows(self, colidx, test, value, numeric=False):
        """Apply `test' to the value in column `colidx' and `value'. Set as invisible 
all the rows for which the test returns False."""
        nv = 0
        if numeric:
            value = toFloat(value)
        for row in self.data:
            if row[0]:          # only consider visible rows
                x = row[1][colidx]
                if numeric:
                    x = toFloat(x)
                    if x == None:
                        break   # skip to next row
                # print "Testing {} and {}".format(x, value)
                if test(x, value):
                    nv += 1
                else:
                    row[0] = False
        self.vrow = nv
        return nv

    def addRows(self, colidx, test, value, numeric=False):
        """Apply `test' to the value in column `colidx' and `value' in all currently invisible
rows. Set as visible all the rows for which the test returns True."""
        if numeric:
            value = toFloat(value)
        for row in self.data:
            if not row[0]:      # only consider invisible rows
                x = row[1][colidx]
                if numeric:
                    x = toFloat(x)
                    if x == None:
                        break   # skip to next row
                if test(x, value):
                    row[0] = True
                    self.vrow += 1

    def uniqueValues(self, colidx, maxunique=100):
        """Returns a dictionary containing the number of occurrences of each distinct value
in column `idx'. If there are more than `maxunique' distinct values, the function returns
None."""
        result = {}
        n = 0
        for row in self.data:
            if row[0]:
                v = row[1][colidx]
                if v in result:
                    result[v] += 1
                else:
                    result[v] = 1
                    n += 1
                    if n > maxunique:
                        return None
        return result

    def writeToStream(self, s, low, high, ansi=False):
        """Write this table to stream `s'."""
        r = 1                   # number of row being printed
        delimiter = getDefault('delimiter')
        first = True
        if ansi:
            startBold(s)
        for ce in self.vcols:
            if first:
                first = False
            else:
                s.write(delimiter)
            s.write(ce[1])
        if ansi:
            endAnsi(s)
        s.write("\n")

        for row in self.data:
            first = True
            if row[0]:          # only visible rows
                if high > 0 and r > high:
                    break       # we're done
                elif r >= low:
                    for ce in self.vcols:
                        if first:
                            first = False
                        else:
                            s.write(delimiter)
                        s.write(row[1][ce[0]])
                    s.write("\n")
                r += 1

    def save(self, filename, low=1, high=-1):
        """Save the current contents of this table to `filename'. `low' and `high' indicate the first and last 
 row to print, respectively."""
        with open(filename, "w") as f:
            self.writeToStream(f, low, high)

    def printRange(self, low=1, high=-1):
        """Print the contents of the current table to standard output."""
        #print "range: {}-{}".format(low, high)
        self.writeToStream(sys.stdout, low, high, ansi=True)

### Class representing command line

class Cmdline():
    cmd = None
    words = []
    aptr = 0

    def __init__(self, words):
        self.cmd = words[0]
        self.words = words[1:]
        self.aptr = 0

    def getCmd(self):
        return self.cmd

    def getRequired(self, num=False, warn=True):
        if self.aptr < len(self.words):
            w = self.words[self.aptr]
            self.aptr += 1
            if num:
                n = toInt(w, warn=warn)
                if n == None:
                    return w
                else:
                    return n
            return w
        else:
            self.aptr += 1
            if warn:
                print "Error: missing argument for command `{}' at position {}.".format(self.cmd, self.aptr)
            return None

    def getOptional(self, default, num=False):
        w = self.getRequired(num=num, warn=False)
        if w:
            return w
        else:
            return default

### Class representing the table manager

class TableManager():
    tables = []
    current = None
    prompt = "> "
    nextTableIdx = 1
    cont = True                 # continue looping?

    def __init__(self):
        tables = []
    
    def setCurrent(self, table):
        self.current = table
        self.prompt = "{}:> ".format(table.idx)

    def findNewCurrent(self, idx):
        """Return the index of the table immediately before `idx', if there is one,
or immediately after, if there is one, or None."""
        before = None
        for t in self.tables:
            if t.idx < idx:
                before = t.idx
            elif t.idx > idx:
                return t.idx
        return before

    def getTable(self, idx):
        """Returns the table whose index is `idx'."""
        for t in self.tables:
            if t.idx == idx:
                return t

    def wantedOrCurrent(self, cmdline):
        table = None
        idx = cmdline.getOptional(None, num=True)
        if idx:
            table = self.getTable(idx)
        if not table:
            table = self.current        
        return table

    ### Commands

    def commandQuit(self, cmdline):
        """Terminate the program."""
        self.cont = False

    def commandLoad(self, cmdLine):
        """Load the contents of the specified file into a new table. 

Usage: load [filename]

If filename is not specified, the program will open a popup window to select the desired file."""
        filename = cmdLine.getOptional(None)
        if filename == None:
            filename = tkFileDialog.askopenfilename(title='Select file to load')

        table = Table(filename)
        now = time.clock()
        success = table.readFile()
        now = time.clock() - now
        if success:
            print "`{}' loaded in {} secs.".format(filename, now)
            table.idx = self.nextTableIdx
            self.nextTableIdx += 1
            self.tables.append(table)
            self.setCurrent(table)
            table.describe()

    def commandShow(self, cmdline):
        """Describe current table.

Usage: show [id]

Describe the contents of the current table, or of table `id' if specified."""
        table = self.wantedOrCurrent(cmdline)
        table.describe()

    def commandCols(self, cmdline):
        """Usage: cols [id]

List the columns of the current table, or of table `id' if specified."""
        table = self.wantedOrCurrent(cmdline)
        table.showColumns()

    def commandList(self, cmdline):
        """Usage: list

List the currently loaded tables. Each table is preceded by its ID number. To switch to a different table, use the '.' command followed by the ID of the table you want to switch to."""
        for t in self.tables:
            print "{:2}:".format(t.idx),
            t.describe()

    def commandSetCurr(self, cmdline):
        """Usage: . id

Set the current table to the one with the specified id number. Use the 'list' command to display all loaded tables with their id numbers."""
        table = self.wantedOrCurrent(cmdline)
        self.setCurrent(table)
        table.describe()

    def commandSave(self, cmdline):
        """Usage: save [filename]

Save the current table to the specified file. If `filename' is not specified, the program will open a popup window allowing you to choose the file to save the table to."""
        filename = cmdline.getOptional(None)
        if filename == None:
            filename = tkFileDialog.asksaveasfilename()
        if filename != None and filename != '':
            self.current.save(filename)
            print "Current table saved to `{}'.".format(filename)

    def commandSelect(self, cmdline):
        """Usage: select [all] [*] [name1 name2 ...]

With no arguments, prints the list of currently visible columns. If the first argument is 'all' or '*', makes all columns visible restoring their original order. Otherwise, the arguments should be valid column names or column numbers in the form @N. Only the specified columns will be visible when printing or saving the table, and they will appear in the order in which they are specified in the 'select' command. For example, if a table has three columns, 'select @3 @1' will make only the third and first columns visible, in this order."""
        table = self.current
        firstarg = cmdline.getOptional(None)
        if firstarg == None:
            print "Visible columns:"
            table.showVisibleColumns()
        elif firstarg == 'all' or firstarg == '*':
            table.vcols = [ce for ce in table.columns]
        else:
            wanted = [firstarg]
            while True:
                w = cmdline.getOptional(None)
                if w == None:
                    break
                wanted.append(w)
            table.selectColumns(wanted)
        print "{} columns visible.".format(len(table.vcols))

    def commandDelete(self, cmdline):
        """Usage: delete [id]

Deletes the current table, or table 'id' if specified."""
        table = self.wantedOrCurrent(cmdline)
        self.tables.remove(table)
        if table == self.current:   # need to choose another current
            newcurr = self.findNewCurrent(table.idx)
            if newcurr == None: # no more tables
                self.current = None
                self.prompt = "> "
            else:
                self.setCurrent(self.getTable(newcurr))
            
    def commandPrint(self, cmdline):
        """Usage: print [n] [m]

Prints the contents of the current table to the screen. If 'n' is specified, prints the first n lines. If 'm' is also specified, prints lines from n to m (inclusive, starting at 1). If m is '*', print lines from n to the end of the table."""
        low = 1
        high = -1
        a = cmdline.getOptional(None, num=True)
        b = cmdline.getOptional(None, num=True)
        if b == '*':
            low = a
        elif b:
            low = a
            high = b
        elif a:
            high = a
        self.current.printRange(low, high)

    def commandFilter(self, cmdline):
        """Usage: filter column operator value

Filter the current table so that only the rows for which the datum in the specified 'column' matches 'value' according to 'operator' remain visible. The column can be specified either by name or by number, using @N (for example, @3 indicates the third column). Currently defined operators are =, !=, >, <, >=, <= (for numbers), 'is' (equality for strings), 'isnot' (inequality for strings), 'sub' (substring match).

Filters are applied in AND: if you enter a second filter command, only the visible rows will be tested. Therefore, when using 'filter' the number of visible rows will either remain the same or decrease. See the 'add' command for OR mode."""

        colname = cmdline.getRequired()
        operator = cmdline.getRequired()
        value = cmdline.getRequired()

        if colname == None or operator == None or value == None:
            return

        table = self.current

        column = table.resolveColumn(colname)
        if column == None:
            return
        colidx = column[0]

        if operator in operatorsTable:
            op = operatorsTable[operator]
        else:
            print "Unknown operator '{}'.".format(operator)
            return
        table.filterRows(colidx, op[0], value, numeric=op[1])
        table.describe()

    def commandAdd(self, cmdline):
        """Usage: add column operator value

This command applies the same test performed by 'filter', with the difference that the test is applied to the hidden rows. Therefore, when using 'add' the number of visible rows will either remain the same or increase. For example, to select all rows containing either 'Alice' or 'Bob' in the Name colum, you can execute: 'filter Name is Alice' followed by 'add Name is Bob'."""
        colname = cmdline.getRequired()
        operator = cmdline.getRequired()
        value = cmdline.getRequired()
        table = self.current

        if colname == None or operator == None or value == None:
            return

        column = table.resolveColumn(colname)
        if column == None:
            return
        colidx = column[0]

        if operator in operatorsTable:
            op = operatorsTable[operator]
        else:
            print "Unknown operator '{}'.".format(operator)
            return
        table.addRows(colidx, op[0], value, numeric=op[1])
        table.describe()

    def commandUnique(self, cmdline):
        """Usage: unique column

Prints a table containing all distinct values found in the specified column, preceded by the number of occurrences for each value (similar to the 'uniq -c' Unix command).

If the column contains more than 100 distinct values, the command will stop and print an error message. This limit can be changed using the 'default' command."""
        table = self.current
        colname = cmdline.getRequired()
        if colname == None:
            return

        column = table.resolveColumn(colname)
        if column == None:
            return
        colidx = column[0]

        result = table.uniqueValues(colidx, getDefault('maxunique'))
        if result == None:
            print "The current column has more than {} unique values. Please select a different column or increase the 'maxunique' default value.".format(100)
        for k in sorted(result):
            print "{:8} {}".format(result[k], k)

    def helpOnCommand(self, what):
        cmd = commandTable[what]
        startBold(sys.stdout)
        print what
        endAnsi(sys.stdout)
        startAnsi(sys.stdout, 0, 31)
        print cmd.__doc__
        endAnsi(sys.stdout)        
        print

    def commandHelp(self, cmdline):
        """Display available commands, or help on a single command.

Use 'help <command> to get help on a command. '?' prints all available commands."""
        if cmdline.getCmd() == '?':
            print "Available commands:",
            for c in sorted(commandTable):
                print c,
            print
        elif cmdline.getCmd() == '??':
            print "Available commands:"
            for c in sorted(commandTable):
                cmd = commandTable[c]
                doc = cmd.__doc__
                docl = doc.split("\n", 1)[0]
                startBold(sys.stdout)
                print c + ": ",
                endAnsi(sys.stdout)
                print docl
                #print "  {}: {}".format(c, docl)
        else:
            what = cmdline.getOptional(None)
            if what == None:
                print "Use 'help <command> to get help on a command. '?' prints all available commands."
            elif what == '*':
                for c in sorted(commandTable):
                    self.helpOnCommand(c)
            elif what in commandTable:
                self.helpOnCommand(what)
            else:
                print "Command `{}' not recognized.".format(what)


    def commandReset(self, cmdline):
        """Make all rows and columns in the current table visible again."""
        self.current.reset()
        self.current.describe()

    def commandDefaults(self, cmdline):
        """Show or set the default options used by the program. 

Usage: default [*] [key] [value]

If called with no arguments, the command will display the current value of the defaults. For each one, it will print its name (in bold on ANSI terminals), a short description, and its current value.

If called with a single '*' as the argument, the command will print the description of each default as in the previous case, with its current value between square brackets, and will wait for the user to input a new value. The current value is the default, so if you keep pressing 'enter' you will go through all defaults without making any changes.

If called with a single argument that is the name of a default, the command will interactively ask for a new value for that default only. Finally, if a second argument is provided, the command will set the specified default to that value. For example, 'default delimiter ,' changes the default delimiter used when reading files to a comma."""
        what = cmdline.getOptional(None)
        if what == None:
            showDefaults()
        elif what == '*':
            askAllDefaults()
        elif what in defaults:
            val = cmdline.getOptional(None)
            if val == None:
                askSomeDefaults([what])
            else:
                setDefault(what, val)
                print "{} set to {}.".format(what, val)
        else:
            print "The first argument should be either '*' or the name of a default. Please use 'default' with no arguments to see the list of valid defaults."

    def REPL(self):
        while self.cont:
            try:
                line = raw_input(self.prompt)
                parsed = parseCommandLine(line)
                if len(parsed) > 0:
                    command = parsed[0]
                    if command in commandTable:
                        cmd = commandTable[command]
                        cmd(Cmdline(parsed))
                    else:
                        print "Command `{}' not recognized.".format(command)
            except EOFError:
                print
                self.cont = False

def initTk():
    # The following two lines are to hide the main Tk window
    root = Tkinter.Tk()
    root.withdraw()

if __name__=="__main__":

    # Initialization
    initTk()
    if HAS_READLINE:
        readline.parse_and_bind("tab: complete")

    mgr = TableManager()
    commandTable = {'quit': mgr.commandQuit,
                    'q'   : mgr.commandQuit,
                    '.'   : mgr.commandSetCurr,
                    '?'   : mgr.commandHelp,
                    '??'  : mgr.commandHelp,
                    'list': mgr.commandList,
                    'ls'  : mgr.commandList,
                    'help': mgr.commandHelp,
                    'load': mgr.commandLoad,
                    'read': mgr.commandLoad,
                    'show': mgr.commandShow,
                    'desc': mgr.commandShow,
                    'cols': mgr.commandCols,
                    'save': mgr.commandSave,
                    'print': mgr.commandPrint,
                    'res'   : mgr.commandReset,
                    'reset' : mgr.commandReset,
                    'filter': mgr.commandFilter,
                    'add'   : mgr.commandAdd,
                    '!'     : mgr.commandFilter,
                    'del'   : mgr.commandDelete,
                    'delete': mgr.commandDelete,
                    'select': mgr.commandSelect,
                    'uniq'  : mgr.commandUnique,
                    'unique': mgr.commandUnique,
                    'def'   : mgr.commandDefaults,
                    'default': mgr.commandDefaults,
                    'defaults': mgr.commandDefaults}
    operatorsTable = {'='  : (testEqual, True),
                      '!=' : (testNotEqual, True),
                      '>'  : (testGreater, True),
                      '<'  : (testSmaller, True),
                      '>=' : (testGreaterEq, True),
                      '<=' : (testSmallerEq, True),
                      'is' : (testEqual, False),
                      'isnot' : (testNotEqual, False),
                      'sub'   : (testSubstring, False)}
    defaults = {'delimiter': ['\t', convertDelimiter, "Default delimiter ('tab' or a single character)"],
                'header'   : [True, convertBoolean, "Files have header line with column names (True/False)"],
                'skip'     : [0, convertInt, "Number of lines to skip at the beginning of a file"],
                'maxunique': [100, convertInt, "Maximum number of distinct values to return for the 'unique' command"]}

    startAnsi(sys.stdout, 1, 34)
    print "CSVmanager, v1.0"
    print "(c) 2015, A. Riva (ariva@ufl.edu)"
    print "Use 'help <command> to get help on a command. '?' prints all available commands."
    endAnsi(sys.stdout)
    mgr.REPL()

