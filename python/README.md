# Compiling and running

This specifically relies on python3, using the `os`, `sys`, and `argparse` libraries (mainly). This also includes the `typing` library just to make variable types more clear to the any readers.

To run, simply use the `python3` before the the python tool you wish to run.

## wc

This commandline tool can be ran using `python3 wc.py` in the `/python` folder, or if running from a different location make sure to call the relative path instead.

When getting started, make sure to type `python3 wc.py --help` for a more detailed explanation on how the tool works, but notably you can run several flags:
* `-c` or `--bytes` - prints the byte counts of the files you wish to count.
* `-m` or `--chars` - prints the character counts of the files you wish to count.
* `-l` or `--lines` - prints the counts of newlines.
* `-L` or `--max-line-length` - prints the maximum display widths, also known as the maximum lengths of all the lines.
* `-w` or `--words` - prints the counts of the words in each file.

On pure binary files, the behavior may behave wildly different from the real `wc` tool as this was designed entirely around how python handles reading file bytes.

Because of the nature of `argparse`, this tool can handle wildcard inputs!

Testing is not yet implemented, but may be in the future.

## JSON Validator

This commandline tool can be ran using `python3 validateJSON.py` in the `/python` folder, or if running from a different location make sure to call the relative path instead.

When getting started, make sure to type `python3 validateJSON.py --help` for a more detailed explanation on how the tool works, but notably you can run with a few flags:
* `-p` or `--print` - prints all trace information / the informaton that occurs in the background when this tool is ran.
* `-t` or `--tokens` - prints the tokens that are generated during the process, whether successful or not.

Because of the nature of `argparse`, this tool can handle wildcard inputs. Additionally, this can be ran on non-json files, but it is expected to be ran on files to test if they follow the json format, so binary files are out of the question.

Automatic testing is not yet implemented, but this has been tested on the files provided in [step 5](https://codingchallenges.fyi/challenges/challenge-json-parser#step-5).