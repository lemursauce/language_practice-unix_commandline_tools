#include <stdio.h>
#include <string.h>

#include "linkedlist.h"
#include "common.h"

const char * help_str = 
"Usage: ./wc [OPTION]... [FILE]...\n\n"
"Print newline, word, and byte counts for each FILE, and a total line if\n"
"more than one FILE is specified. A word is a non-zero-length sequence of\n"
"characters delimited by white space.\n\n"
"With no FILE, or when FILE is -, read standard input.\n\n"
"The options below may be used to select which counts are printed, always in\n"
"the following order: newline, word, character, byte, maximum line length.\n"
"  -c, --bytes            print the byte counts\n"
"  -m, --chars            print the character counts\n"
"  -l, --lines            print the newline counts\n"
"  -L, --max-line-length  print the maximum display width\n"
"  -w, --words            print the word counts\n"
"      --help     display this help and exit\n\n"
"(Thank you for using/testing this coding challenges word count tool!)";

// as an aside, the print order is: -l, -w, -m, -c, -L

struct wc_flag_t {
    int l = 0, w = 0, m = 0, c = 0, L = 0;
};

struct wc_stats_t {
    size_t l = 0, w = 0, m = 0, c = 0, L = 0;
};

// helper function to make the later code easier to read
void printStats(wc_stats_t & stats, wc_flag_t & flags, int fmtLen, char * name = 0) {
    int flagPrinted = 0;
    if (flags.l) {
        printf("%*lu", fmtLen, stats.l);
        flagPrinted = 1;
    }
    if (flags.w) {
        if (flagPrinted) putchar(' ');
        printf("%*lu", fmtLen, stats.w);
        flagPrinted = 1;
    }
    if (flags.m) {
        if (flagPrinted) putchar(' ');
        printf("%*lu", fmtLen, stats.m);
        flagPrinted = 1;
    }
    if (flags.c) {
        if (flagPrinted) putchar(' ');
        printf("%*lu", fmtLen, stats.c);
        flagPrinted = 1;
    }
    if (flags.L) {
        if (flagPrinted) putchar(' ');
        printf("%*lu", fmtLen, stats.L);
        flagPrinted = 1;
    }
    if (flagPrinted && name) printf(" %s", name);
    putchar('\n');
}

int wc(List<char*> &fileNames, wc_flag_t &flags) {
    wc_stats_t tot_stats;
    List<wc_stats_t> indv_stats;
    int totfmtlen = 0;
    int use_stdin = 0;
    int printTot = 0;

    int flagcount = flags.l + flags.w + flags.m + flags.c + flags.L;
    if (!flagcount) return 0;   // if none of the flags are chosen for some reason, then wc should not print anything

    if (fileNames.empty()) {
        fileNames.push_back(0);
        if (flagcount > 1) totfmtlen = 7;
        use_stdin = 1;
    }

    if (fileNames.size() > 1) {
        printTot = 1;
    }

    // gather stats
    for (auto it = fileNames.begin(); it != fileNames.end(); ++it) {
        // get input file
        FILE *file = stdin;
        int isFile = 0;
        if (*it && strcmp(*it, "-") != 0) {
            file = fopen(*it, "rb");
            if (file == NULL) {
                fprintf(stderr, "Invalid file was read\n");
                return 1;
            }
            isFile = 1;
        }

        wc_stats_t curr_stats;

        // iterate by one character at a time until end of file
        char c = fgetc(file);
        int spaceMode = 1;
        size_t currLine = 0;
        while (!feof(file)) {   // didn't use EOF since that caused some issues on some files when testing
            curr_stats.c++;
            curr_stats.m++;

            int nextSpaceMode = isWhiteSpace(c);
            if (!nextSpaceMode && spaceMode ^ nextSpaceMode) {
                curr_stats.w++;
            }
            spaceMode = nextSpaceMode;

            if (c == '\n' || c == '\r') {
                curr_stats.l++;
                currLine = 0;
            } else {
                ++currLine;
                if (currLine > curr_stats.L) curr_stats.L = currLine;
            }
            c = fgetc(file);
        }

        // update running stats
        tot_stats.l += curr_stats.l;
        tot_stats.w += curr_stats.w;
        tot_stats.m += curr_stats.m;
        tot_stats.c += curr_stats.c;
        rewriteMax<size_t>(tot_stats.L, curr_stats.L);
        indv_stats.push_back(curr_stats);

        // update format for printing all stats
        if (flags.l) rewriteMax<int>(totfmtlen, intStrLen(tot_stats.l));
        if (flags.w) rewriteMax<int>(totfmtlen, intStrLen(tot_stats.w));
        if (flags.m) rewriteMax<int>(totfmtlen, intStrLen(tot_stats.m));
        if (flags.c) rewriteMax<int>(totfmtlen, intStrLen(tot_stats.c));
        if (flags.L) rewriteMax<int>(totfmtlen, intStrLen(tot_stats.L));

        // close file if read
        if (isFile) fclose(file);
    }
    
    // print stats for all listed files (including stdin)
    auto nameit = fileNames.begin();
    for (auto it = indv_stats.begin(); it != indv_stats.end(); ++it, ++nameit) {
        printStats(*it, flags, totfmtlen, *nameit);
    }

    // cleanup if wc had read only from stdin
    if (use_stdin) fileNames.pop_back();
    // print total if more than one entry
    if (printTot) printStats(tot_stats, flags, totfmtlen, (char*) "total");

    return 0;
}

int main(int argc, char *argv[]) {
    wc_flag_t wc_flags;
    int help = 0;

    opt_t long_options[] = {
        {"-",  opt_no_argument, 0, '?'},
        {"-l", opt_no_argument, &wc_flags.l, 1},
        {"-w", opt_no_argument, &wc_flags.w, 1},
        {"-m", opt_no_argument, &wc_flags.m, 1},
        {"-c", opt_no_argument, &wc_flags.c, 1},
        {"-L", opt_no_argument, &wc_flags.L, 1},
        {"--lines",             opt_no_argument, &wc_flags.l, 1},
        {"--words",             opt_no_argument, &wc_flags.w, 1},
        {"--characters",        opt_no_argument, &wc_flags.m, 1},
        {"--bytes",             opt_no_argument, &wc_flags.c, 1},
        {"--max-line-length",   opt_no_argument, &wc_flags.L, 1},
        {"--help",              opt_no_argument, &help, 1},
        {0,0,0,0}
    };

    // get arguments
    int opt = -1;
    int flag_set = 0;
    
    // iterate and build flag and file information
    optParse op(argc, (const char**) argv, long_options);
    List<char*> fileNames;
    while ((opt = op.getOpt()) != -1) {
        if (opt == '?') {
            // non-flag inputs should be file names
            fileNames.push_back((char*) op.optarg);
        } else {
            flag_set = 1;
        }
    }

    // if the help flag is set, just run that and nothing else
    if (help) {
        printf("%s", help_str);
        return 0;
    }

    // set default flags if none chosen
    if (!flag_set) {
        wc_flags.l = wc_flags.w = wc_flags.c = 1;
    }

    // run actual wc call with necessary flags
    return wc(fileNames, wc_flags);
}