# Compiling and running

This uses gcc/g++ and makefile to compile on UNIX systems, so ensure you have a working gcc/g++ compiler and are able to run the `make` command on your UNIX system.

To compile, simply run the `make` command within this `/cpp` folder and this will create executables for all the runnable commandline tools.

Compiled files can be easily cleaned by running `make clean`, which will remove all focused executables as well as any extra `*.o` files (if any remain for whatever reason).

## wc

When compiled, this commandline tool can be ran using `./wc` in the `/cpp` folder, or if running from a different location make sure to call the relative path instead.

When getting started, make sure to type `./wc --help` for a more detailed explanation on how the tool works, but notably you can run several flags:
* `-c` or `--bytes` - prints the byte counts of the files you wish to count
* `-m` or `--chars` - prints the character counts of the files you wish to count. Because of the way that c++ reads files, this is treated the same as the `-c` flag, which is NOT characteristic of the real UNIX `wc` tool.
* `-l` or `--lines` - prints the counts of newlines
* `-L` or `--max-line-length` - prints the maximum display widths, also known as the maximum lengths of all the lines.
* `-w` or `--words` - prints the counts of the words in each file.

Unlike the real `wc` tool, this `./wc` tool does not handle wildcard inputs, so you would have to enter the names of all the files manually (although, as an alternative, you can run something like `./wc $(find . -type f -name "*.txt")` as a sort of pseudo-wildcard).

Testing is not yet implemented, but may be in the future.