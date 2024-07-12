#ifndef COMMON_H
#define COMMON_H

#include <sys/types.h>
#include <utility>

// simple functions

bool isWhiteSpace(char c);
int intStrLen(size_t val);

template <typename T>
void rewriteMax(T& base, T& newValue) {
    if (base < newValue) base = newValue;
}
template <typename T>
void rewriteMax(T& base, T&& newValue) {
    if (base < newValue) base = std::move(newValue);
}

// custom arg parsing

#define opt_no_argument       0
#define opt_required_argument 1
#define opt_optional_argument 2
#define opt_argument_inline   4
#define opt_zero_terminate    8

struct opt_t {
    const char* argName;
    int has_arg;
    int *flag;
    int val;

    opt_t(const char * argName, int has_arg, int * flag, int val) : argName(argName), has_arg(has_arg), flag(flag), val(val) {}
};

/**
 * @brief Custom option/argument parser for a command. Takes `argc` and `argv` from `main` and parses based on given option rules.
 * 
 * @note The last `arg_t.argName` within `<this>.arguments` must be an empty string, otherwise `getOpt()` will not terminate.
 */
struct optParse {
    const char ** argv; //char *argv[]
    const opt_t * arguments;
    const char * optarg;
    int argc = 0;
    int argi = 1;

    optParse(int __argc, const char** __argv, opt_t * __arguments) : argv(__argv), arguments(__arguments), optarg(0), argc(__argc) {}

    int getOpt(int * option_index = nullptr);
};

#endif