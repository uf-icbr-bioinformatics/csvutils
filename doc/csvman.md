csvman
======

Command-line shell to manipulate delimited files.

## Introduction
**csvman** is a simple tool to manipulate delimited files. It allows you to load
delimited files in memory, filter rows based on their contents, select visible columns, and save table
data back to files.

## Installation
**csvman** is a self-contained Python script, and requires no installation. On Linux, you can make the script itself executable with the following command:

```bash
> chmod +x csvman.py
```

You will then be able to start the program by simply invoking it as **./csvman.py**, or **csvman.py** if you saved it in a directory in your PATH. csvman currently takes no arguments.

## Basic concepts
**csvman** operates on *tables*. Each table is a rectangular set of values loaded from a delimited file. Rows in the table are numbered starting at 1, while columns can be identified by their name (if the file contained a header line) or by their position, using the @N format: @1, @2, @3, etc.

The program can manage multiple tables at the same time.  Tables are numbered progressively based on the order in which they are loaded. At any time there is a *current* table, to which the operations performed apply. The current table is normally the last one loaded, but this can be changed using the **.** (dot) command. The current table is indicated by the number appearing in the prompt. For example, the prompt **3:>** indicates that the third loaded table is the current one.

Tables can be filtered by row and/or column. You can specify which columns of a table you want to be visible, and in which order. Rows are filtered based on their values, using numeric or string comparison operators. 

*Defaults* are variables that control certain aspects of the operation of the program. The defaults can be displayed or changed with the **defaults** command.

Online help can be otained using the **help** command, followed by the name of the command you want help on. The **?** command displays the list of available commands.

## Loading tables
Tables are loaded with the **load** command (also called **read**). You can provide the pathname of the file to be loaded, otherwise the program will pop up a window allowing you to select the file from your hard disk. Once the table is loaded, you will get a message showing that the table was loaded. The **list** command (also called **ls**) shows the list of currently loaded tables.

## Displaying tables
The **show** command (also called **desc**) displays the number of columns and rows (both total and visible) in the current table. For example:

```
1:> show
Table `test.csv', 1/2 columns, 311/1000 rows.
```

This table was loaded from file *test.csv*, and has two columns (of which only one is visible) and 1000 rows (of which 311 are visible). You can also specify an optional argument after the **show** command, to display a table other than the current one:

```
1:> show 2
```

displays the description of table 2 instead of the current one (1).

The **cols** command displays the list of columns in the current tables, in the original order. Currently filtered (i.e., invisible) columns are shown between square brackets ([ and ]).

The contents of a table can be displayed on the screen using the **print** command, which takes two optional arguments:

```python
1:> print         # Displays the whole contents of the table
1:> print 5       # Displays the first 5 rows of the table
1:> print 10 20   # Displays rows from 10 to 20 inclusive
1:> print 20 *    # Displays rows from 20 to the end of the table
```

## Column filtering
The **select** command allows you to choose which columns are visible, and in which order. Assuming you have a table with three columns called *First*, *Second*, and *Third*, the following command:

```
1:> select Third First
```

will hide column *Second*, and display only *Third* and *First*, in this order. **select** with no arguments will show you the current list of visible columns. Use **select all* or **select * ** to make all columns visible again, in the original order.

Please note that column names are case sensitive: in the previous example, using *third* instead of *Third* would have produced an error saying that the column does not exist. If the column name includes a space, use the double quotes: **select "First Name"**.

## Row filtering
Use the **filter** command (also called **!**) to select a subset of all rows. Its syntax is:

```
1:> filter column operator value
```

*Column* can be specified by name or by position, using @N where N is the column number. Assuming that *Name* is a column containing text and *Count* is a column containing numbers, the following table shows the currently available operators:

```python
1:> filter Name is abc      # string equality
1:> filter Name isnot abc   # string inequality
2:> filter Name sub abc     # substring match
1:> filter Count = 12       # Numeric equality
1:> filter Count != 12      # Numeric inequality
1:> filter Count > 12       # Numeric greater than
1:> filter Count < 12       # Numeric smaller than
1:> filter Count >= 12      # Numeric greater or equal to
1:> filter Count <= 12      # Numeric smaller or equal to
```

Filters are applied in *AND* mode: if you enter a second filter command, only the visible rows will be tested. Therefore, when using **filter** the number of visible rows will either remain the same or decrease. The **add** command, instead, works in *OR* mode: this command applies the same test performed by **filter**, with the difference that the test is applied to the hidden rows. Therefore, when using **add** the number of visible rows will either remain the same or increase. For example, to select all rows containing either *Alice* or *Bob* in the Name colum, you can execute: **filter Name is Alice** followed by **add Name is Bob**.

The **reset** command removes all filtering, making all rows visible again.

## Changing defaults
*Defaults* are internal variables that affect the way the program works. The following table lists the currently defined variables:

Variable | Initial Value | Description
---------|---------------|------------
delimiter| tab           | The delimiter used when reading and writing files. Possible values are the string 'tab' or a single character (e.g. **,**, **|**).
header   | True          | Whether the file has a header line containing column names. If changed to *False*, columns will not have names and should be indicated using @N syntax.
skip     | 0             | Number of lines to ignore at the beginning of a file when reading it. This is useful for cases in which the file has rows of meta-information before the start of the data.
maxunique| 100           | The maximum number of distinct values collected from a column for the **unique** command.

The **default** command (also called **def** or **defaults**) shows or modifies the current value of one or more defaults. It can be used in the following ways:

Command | Description
--------|------------
**def**                 | Displays the current list of defaults. For each one, prints its name, a short description, and the current value.
**def**&nbsp;*name*          | Ask the user for the new value for *name* (default is current value).
**def**&nbsp;*name*&nbsp;*value*  | Changes default *name* to *value*.
**def** *               | Ask the user for the new value of all defaults. The current value is the default, so if you keep pressing *Enter* you will go through all defaults without making any changes.

The following example shows how to modify defaults to allow the program to read a comma-delimited file with no header line:

```python
1:> def                 # Display current defaults
delimiter - Default delimiter ('tab' or a single character): tab
header - Files have header line with column names (True/False): True
maxunique - Maximum number of distinct values to return for the 'unique' command: 100
skip - Number of lines to skip at the beginning of a file: 0
1:> def delimiter ,     # Change default delimiter
delimiter set to ,.
1:> def header False    # Change header flag
header set to False.
1:> def                 # Display new defaults
delimiter - Default delimiter ('tab' or a single character): ,
header - Files have header line with column names (True/False): False
maxunique - Maximum number of distinct values to return for the 'unique' command: 100
skip - Number of lines to skip at the beginning of a file: 0
```

## Saving tables
The **save** command saves the current table to a file. The filename can be specified after the command, otherwise the program will open a popup window allowing you to choose the file to write the table to. When a table is saved only its visible rows and columns are written to the file.

## Miscellanous commands
The **unique** command (also called **uniq**) displays the unique values contained in the specified column, with the number of occurrences of each. If the number of distinct values is greater than the *maxunique* default, the command stops printing an error message.

## Reference
The following table shows the help message for each defined command.

**filter** (also: **!**)

Usage: filter column operator value

Filter the current table so that only the rows for which the datum in the specified 'column' matches 'value' according to 'operator' remain visible. The column can be specified either by name or by number, using @N (for example, @3 indicates the third column). Currently defined operators are =, !=, >, <, >=, <= (for numbers), 'is' (equality for strings), 'isnot' (inequality for strings), 'sub' (substring match).

Filters are applied in AND: if you enter a second filter command, only the visible rows will be tested. Therefore, when using 'filter' the number of visible rows will either remain the same or decrease. See the 'add' command for OR mode.

**.**

Usage: . id

Set the current table to the one with the specified id number. Use the 'list' command to display all loaded tables with their id numbers.

**?**

Use 'help <command> to get help on a command. '?' prints all available commands.

**add**

Usage: add column operator value

This command applies the same test performed by 'filter', with the difference that the test is applied to the hidden rows. Therefore, when using 'add' the number of visible rows will either remain the same or increase. For example, to select all rows containing either 'Alice' or 'Bob' in the Name colum, you can execute: 'filter Name is Alice' followed by 'add Name is Bob'.

**cols**

Usage: cols [id]

List the columns of the current table, or of table `id' if specified.

**def** (also: **default** or **defaults**)

Usage: default [*] [key] [value]

Show or set the default options used by the program. If called with no arguments, the command will display the current value of the defaults. For each one, it will print its name (in bold on ANSI terminals), a short description, and its current value.

If called with a single '*' as the argument, the command will print the description of each default as in the previous case, with its current value between square brackets, and will wait for the user to input a new value. The current value is the default, so if you keep pressing 'enter' you will go through all defaults without making any changes.

If called with a single argument that is the name of a default, the command will interactively ask for a new value for that default only. Finally, if a second argument is provided, the command will set the specified default to that value. For example, 'default delimiter ,' changes the default delimiter used when reading files to a comma.

**delete** (also: **del**)

Usage: delete [id]

Deletes the current table, or table 'id' if specified.

**desc** (also: **show**)

Usage: desc [id]

Describe the contents of the current table, or of table `id' if specified.

**help**

Use 'help <command> to get help on a command. '?' prints all available commands.

**list** (also: **ls**)

Usage: list

List the currently loaded tables. Each table is preceded by its ID number. To switch to a different table, use the '.' command followed by the ID of the table you want to switch to.

**load** (also: **read**)

Usage: load [filename]

Load the contents of the specified file into a new table. If filename is not specified, the program will open a popup window to select the desired file.

**print**

Usage: print [n] [m]

Prints the contents of the current table to the screen. If 'n' is specified, prints the first n lines. If 'm' is also specified, prints lines from n to m (inclusive, starting at 1). If m is '*', print lines from n to the end of the table.

**quit** (also: **q**)

Terminate the program.

**reset** (also: **res**)

Make all rows and columns in the current table visible again.

**save**

Usage: save [filename]

Save the current table to the specified file. If `filename' is not specified, the program will open a popup window allowing you to choose the file to save the table to.

**select**

Usage: select [all] [*] [name1 name2 ...]

With no arguments, prints the list of currently visible columns. If the first argument is 'all' or '*', makes all columns visible restoring their original order. Otherwise, the arguments should be valid column names or column numbers in the form @N. Only the specified columns will be visible when printing or saving the table, and they will appear in the order in which they are specified in the 'select' command. For example, if a table has three columns, 'select @3 @1' will make only the third and first columns visible, in this order.

**unique** (also: **uniq**)

Usage: unique column

Prints a table containing all distinct values found in the specified column, preceded by the number of occurrences for each value (similar to the 'uniq -c' Unix command).

If the column contains more than 100 distinct values, the command will stop and print an error message. This limit can be changed using the 'default' command.


## Future developments
The following are features being considered for inclusion in the next release:

* Full regular expressions in filtering for strings;
* Specify filenames to be loaded at startup on the command line;
* Provide values for defaults on command line;
* Specify commands to execute on command line (either directly or in a file), turning the program into an automated CSV file processor;
* The output of the **unique** command could become a new table;
* Commands to join two tables (based on common field) or to concatenate them (based on common columns)

## Feedback
Please send bug reports and feature requests to ariva@ufl.edu.

## Credits
**csvman.py** is (c) 2015, A. Riva, <A href='http://dibig.biotech.ufl.edu/'>DiBiG</A>, <A href='http://biotech.ufl.edu/'>ICBR Bioinformatics</A>, University of Florida
