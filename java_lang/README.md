# Compiling and running

This uses javac and makefile to compile on UNIX systems, so ensure you have a working javac compiler and are able to run the `make` command on your UNIX system.

To compile, simply run the `make` command within this `/java_lang` folder and this will create executables for all the runnable commandline tools.

The compiled files to run can be found by typing `make ls`, which will highlight which files to run under the java command to activate the desired tool. (e.g. to run the java `wc` program, you would call `java java_lang/WC`).

## wc

This commandline tool can be ran using `java java_lang/WC` in the `/java_lang` folder, or if running from a different location make sure to call the relative path instead.

When getting started, make sure to type `java java_lang/WC --help` for a more detailed explanation on how the tool works, but notably you can run several flags:
* `-c` or `--bytes` - prints the byte counts of the files you wish to count
* `-m` or `--chars` - prints the character counts of the files you wish to count
* `-l` or `--lines` - prints the counts of newlines
* `-L` or `--max-line-length` - prints the maximum display widths, also known as the maximum lengths of all the lines
* `-w` or `--words` - prints the counts of the words in each file

On pure binary files, the behavior may behave wildly different from the real `wc` tool.

Unlike the real `wc` tool, this `java java_lang/WC` tool does not handle wildcard inputs, so you would have to enter the names of all the files manually (although, as an alternative, you can run something like `java java_lang/WC $(find . -type f -name "*.txt")` as a sort of pseudo-wildcard).

Testing is not yet implemented, but may be in the future.