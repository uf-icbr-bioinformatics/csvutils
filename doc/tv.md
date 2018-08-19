# tv.py
Full-screen interactive viewer for delimited files.

## Introduction
This program displays a tab-delimited file in full screen, lining up columns
correctly. It supports horizontal and vertical scrolling, jumping to an arbitrary row/column,
switching between multiple files.

## Usage

```
  tv.py [options] filenames...
```

The following command-line options are supported:

Option | Description
---------------|------------
  -d D | Use character D as delimiter (use 'tab' for tab). Default: autodetect.
  -m M | Read the first M lines from each input file (default: 1000).
  -b   | Enable header mode (first line bold and always visible).
  -h   | Display usage message (all other options are ignored).
  
While displaying a file, the following keys can be used:

Key | Description
----|------------
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
