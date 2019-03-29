# assoc.py
Read key-value mappings from a tab-delimited file and use them to translate input strings.


## Introduction
This program reads a tab-delimited file `filename' and builds a table mapping the 
strings from the input column (by default, the first one) to the corresponding ones
in the output column (by default the one after the input column, unless a different
one is specified with the `col' argument). A different input column can be specified
with the -i argument or by appending :N to the filename, where N is the column number. 

After creating the mapping, the program will read identifiers from standard input and
write the corresponding identifiers to standard output. If an identifier does not 
appear in the translation table, the program prints the missing value tag (set with
-m) unless -p is specified, in which case the original identifier is printed unchanged..

## Usage

```
  assoc.py [options] filename
```

The following command-line options are supported:


Option | Description
-------|------------
  -i I | Set input column to I (1-based). Default: 1.
  -o O | Set output column to O (1-based). Default: 2.
  -m M | Set the missing value tag to M. Default: '???'.
  -d D | Set delimiter to D. Use 'sp' for space and 'nl' for newline. Default: tab. 
  -p   | Preserve mode: if an input string has no translation, print the string itself instead of the missing tag.
  -r   | Interactive mode.


## Examples

Assume you have a tab-delimited file called TABLE with three columns:

```
  john   lennon	    guitar
  paul	 mccartney  bass
  george harrison   guitar
  ringo  starr      drums
```

A file called NAMES containing:

```
  ringo
  john
  mick
```

And a file called INSTRUMENTS containing:
```
  bass
  drums
```

Then:

```
# By default, map first column to second
$ cat NAMES | assoc.py TABLE
starr
lennon
???

# Map first column to third
$ cat NAMES | assoc.py -o 3 TABLE
drums
guitar
???

# Use a different value for missing identifiers
$ cat NAMES | assoc.py -m unknown TABLE
starr
lennon
unknown

# Map third column to second:
$ cat INSTRUMENTS | assoc.py -o 2 TABLE:3
starr
mccartney

# Previous example could also be written as:
$ cat INSTRUMENTS | assoc.py -i 3 -o 2 TABLE
starr
mccartney
````