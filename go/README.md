# Compiling and running

This uses go and makefile to compile on UNIX systems, so ensure you have a working go compiler/builder and are able to run the `make` command on your UNIX system.

To compile, simply run the `make` command within this `/go` folder and this will create executables for all the runnable commandline tools. These will be found in the relative `/build/dev` directory.

Additionally, you can specify `make release` to build smaller (and potentially quicker) executables into the `/build/release` directory.

Compiled files can be easily cleaned/removed by running `make clean`, which will remove all the `/build` directory.

## wc

When compiled, this commandline tool can be ran using `./build/<build_mode>/wc` in the `/go` folder, or if running from a different location make sure to call the relative path instead.

When getting started, make sure to type `./build/<build_mode>/wc --help` for a more detailed explanation on how the tool works, but notably you can run several flags:
* `-c` or `--bytes` - prints the byte counts of the files you wish to count
* `-m` or `--chars` - prints the character counts of the files you wish to count
* `-l` or `--lines` - prints the counts of newlines
* `-L` or `--max-line-length` - prints the maximum display widths, also known as the maximum lengths of all the lines
* `-w` or `--words` - prints the counts of the words in each file

On pure binary files, the behavior may behave wildly different from the real `wc` tool.

Unlike the real `wc` tool, this tool does not handle wildcard inputs, so you would have to enter the names of all the files manually (although, as an alternative, you can run something like `./build/<build_mode>/wc $(find . -type f -name "*.txt")` as a sort of pseudo-wildcard).

Testing is not yet implemented, but may be in the future.