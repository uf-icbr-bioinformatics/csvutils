# assoc.py

##Introduction
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


##Examples

```
  assoc.py -o 3 file
```
Maps the contents of column 1 to the contents of column 3.

```
  assoc.py file:2 
```
Maps the contents of column 2 to the contents of column 3.

