#!/usr/bin/env python

import sys
import csv
from numpy import histogram
from collections import defaultdict

class Histo(object):
    filename = "/dev/stdin"
    outfile = "/dev/stdout"
    column = 0
    mode = "cat"                # or "quant" for quantitative
    order = "alpha"             # or "asc" or "desc" for numerical
    nbins = 0                   # for quant mode
    _values = None

    def __init__(self):
        self._values = defaultdict(int)

    def parseArgs(self, args):
        if "-h" in args or "--help" in args:
            self.usage()
            return False
        prev = ""
        for a in args:
            if prev == "-o":
                self.outfile = a
                prev = ""
            elif prev == "-c":
                self.column = int(a) - 1
                prev = ""
            elif prev == "-b":
                self.nbins = int(a)
                self.mode = "quant"
                prev = ""
            elif a in ["-o", "-c", "-b"]:
                prev = a
            elif a == "-n":
                self.order = "desc"
            elif a == "-N":
                self.order = "asc"
            else:
                self.filename = a
        return True

    def usage(self):
        sys.stdout.write("""histogram.py - generate histograms of numerical or categorical data.

Usage: histogram.py [options] [filename]

Where options are:

  -o O | Write output to file O.
  -c C | Read values from column C of input (default: {}).
  -b B | Use B bins (enables numerical mode).
  -n   | Sort categorical histogram by number of occurrences (descending).
  -N   | Sort categorical histogram by number of occurrences (ascending).

Input is read from specified filename, or from standard input.

In categorical mode (the default) output consists of two columns:

  value occurrences

In numerical mode (enabled with -b) output consists of three columns:

  min max occurrences

where min and max are the edges of each bin (see numpy.histogram() for details).

""".format(self.column + 1))

    def run(self):
        if self.mode == "cat":
            self.runCategorical()
            self.reportCategorical()
        else:
            self.runNumerical()

    def runCategorical(self):
        with open(self.filename, "r") as f:
            c = csv.reader(f, delimiter='\t')
            for line in c:
                w = line[self.column]
                self._values[w] += 1

    def reportCategorical(self):
        counts = []
        for k in self._values.keys():
            counts.append( [ k, self._values[k] ])
        if self.order == "alpha":
            counts.sort(key=lambda r: r[0])
        elif self.order == "asc":
            counts.sort(key=lambda r: r[1])
        elif self.order == "desc":
            counts.sort(key=lambda r: r[1], reverse=True)
        with open(self.outfile, "w") as out:
            for cnt in counts:
                out.write("{}\t{}\n".format(cnt[0], cnt[1]))

    def runNumerical(self):
        data = []
        with open(self.filename, "r") as f:
            c = csv.reader(f, delimiter='\t')
            for line in c:
                try:
                    data.append(float(line[self.column]))
                except ValueError:
                    pass
        hist, edges = histogram(data, bins=self.nbins)
        with open(self.outfile, "w") as out:
            for i in range(len(hist)):
                out.write("{:f}\t{:f}\t{}\n".format(edges[i], edges[i+1], hist[i]))

if __name__ == "__main__":
    args = sys.argv[1:]
    H = Histo()
    if H.parseArgs(args):
        H.run()
