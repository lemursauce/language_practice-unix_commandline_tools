#include <memory.h>
#include <unistd.h>
#include <string.h>
#include <stdio.h>
#include <stdlib.h>
#include "common.h"

// simple functions

bool isWhiteSpace(char c) {
    return (c == ' ' || c == '\n' || c == '\r' || c == '\t');
}

int intStrLen(size_t val) {
    int len = 0;
    while (val) {
        ++len;
        val /= 10;
    }
    return len;
}

// custom arg parsing

int flagMatch(const char * flag, const char * base) {
    if (!flag || !flag[0]) return 0;
    if (!base || !base[0]) return 0;
    if (flag[0] == '-' && flag[1] != '-') {
        return (base[0] == '-' && base[1] == flag[1]) ? 2 : 0;
    }
    
    int i = 0;
    for (; flag[i] && base[i] && base[i] != '='; ++i) {
        if (flag[i] != base[i]) return 0;
    }
    if (flag[i] == 0 && (base[i] == 0 || base[i] == '=')) return i;

    return 0;
}

int optParse::getOpt(int * option_index) {
    if (!(arguments || argv)) return -1;
    if (argi >= argc) return -1;

    const char * arg = argv[argi];
    if (arg[0] != '-') {
        ++argi;
        if (option_index) *option_index = -1;
        optarg = arg;
        return '?';
    }

    int i = 0;
    int val = 0;

    while (arguments[i].argName) {
        if (flagMatch(arguments[i].argName, arg)) {
            if (option_index) *option_index = i;
            ++argi;

            // get argument if asked or required
            optarg = 0;
            if (arguments[i].has_arg && argi < argc && argv[argi][0] != '-') {
                optarg = argv[argi];
                ++argi;
            } else if (arguments[i].has_arg & opt_required_argument) {
                fprintf(stderr, "Error: Option \"%s\" requires an argument\n", arguments[i].argName);
                exit(EXIT_FAILURE);
                return -1;
            }

            if (arguments[i].flag) {
                *arguments[i].flag = arguments[i].val;
            } else {
                val = arguments[i].val;
            }

            return val;
        }
        ++i;
    }
    fprintf(stderr, "Error:\"%s\" is an invalid option\n", arg);
    exit(EXIT_FAILURE);
    return -1;
}