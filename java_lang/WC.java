package java_lang;

import java.util.ArrayList;
import java.util.concurrent.atomic.AtomicInteger; // to send references to integers

import java.io.InputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.IOException;

import java.lang.Math; // for max

class WC {
    private static String helpText =
    """
    Usage: wc [OPTION]... [FILE]...
    Print newline, word, and byte counts for each FILE, and a total line if
    more than one FILE is specified.  A word is a non-zero-length sequence of
    characters delimited by white space.

    With no FILE, or when FILE is -, read standard input.

    The options below may be used to select which counts are printed, always in
    the following order: newline, word, character, byte, maximum line length.
    -c, --bytes            print the byte counts
    -m, --chars            print the character counts
    -l, --lines            print the newline counts
    -L, --max-line-length  print the maximum display width
    -w, --words            print the word counts
        --help     display this help and exit
    (Thank you for using/testing this coding challenges word count tool!)
    """;

    public static void main(String[] args) {
        flags_t flags = new flags_t();
        AtomicInteger helpFlag = new AtomicInteger(0);

        Option[] options = {
            new Option("-l", OptionRequirement.no_argument, flags.l, 1),
            new Option("-w", OptionRequirement.no_argument, flags.w, 1),
            new Option("-m", OptionRequirement.no_argument, flags.m, 1),
            new Option("-c", OptionRequirement.no_argument, flags.c, 1),
            new Option("-L", OptionRequirement.no_argument, flags.L, 1),
            new Option("--lines",           OptionRequirement.no_argument, flags.l, 1),
            new Option("--words",           OptionRequirement.no_argument, flags.w, 1),
            new Option("--characters",      OptionRequirement.no_argument, flags.m, 1),
            new Option("--bytes",           OptionRequirement.no_argument, flags.c, 1),
            new Option("--max-line-length", OptionRequirement.no_argument, flags.L, 1),
            new Option("--help",            OptionRequirement.no_argument, helpFlag, 1)
        };

        ArgParser op = new ArgParser(args, options);
        ArrayList<String> fileNames = new ArrayList<>();
        int opt = -1;
        Boolean flagSet = false;
        while ((opt = op.getArg()) != -1) {
            if (opt == 63) {
                fileNames.add(op.optarg);
            } else {
                flagSet = true;
            }
        }

        if (helpFlag.get() > 0) {
            System.out.print(helpText);
            System.exit(0);
        }

        if (!flagSet) {
            flags.l.set(1);
            flags.w.set(1);
            flags.c.set(1);
        }

        wc(flags, fileNames);
    }

    /// main logic

    static void wc(flags_t flags, ArrayList<String> fileNames) {
        stats_t total = new stats_t();
        ArrayList<stats_t> fileStats = new ArrayList<>();
        int fmtLen = 0;
        int flagCount = flags.l.get() + flags.w.get() + flags.m.get() + flags.c.get() + flags.L.get();

        if (fileNames.isEmpty()) {
            fileNames.add(null);
            if (flagCount > 1) fmtLen = 7;
        }

        Boolean printTot = false;
        if (fileNames.size() > 1) {
            printTot = true;
        }

        for (String fileName : fileNames) {
            stats_t temp = new stats_t();
            InputStream in = System.in;
            Boolean isFile = false;
            if (!(fileName == null || fileName.length() == 0 || fileName == "-")) {
                try {
                    in = new FileInputStream(fileName);
                    temp.c = new File(fileName).length();
                    isFile = true;
                } catch (IOException ex) {
                    ex.printStackTrace();
                    System.exit(1);
                }
            }

            int byteRead = -1;
            Boolean spaceMode = true;
            long currLine = 0;
            try {
                while ((byteRead = in.read()) != -1) {
                    if (!isFile) ++temp.c;
                    ++temp.m;

                    Boolean nextSpaceMode = Character.isWhitespace(byteRead);
                    if (!nextSpaceMode && spaceMode ^ nextSpaceMode) {
                        ++temp.w;
                    }
                    spaceMode = nextSpaceMode;

                    if ((char)byteRead == '\n' || (char)byteRead == '\r') {
                        ++temp.l;
                        currLine = 0;
                    } else {
                        ++currLine;
                        if (currLine > temp.L) temp.L = currLine;
                    }
                }
            } catch (IOException ex) {
                ex.printStackTrace();
                System.exit(1);
            }

            total.l += temp.l;
            total.w += temp.w;
            total.m += temp.m;
            total.c += temp.c;
            if (total.L < temp.L) total.L = temp.L;

            if (flags.l.get() > 0) fmtLen = Math.max(fmtLen, Long.toString(total.l).length());
            if (flags.w.get() > 0) fmtLen = Math.max(fmtLen, Long.toString(total.w).length());
            if (flags.m.get() > 0) fmtLen = Math.max(fmtLen, Long.toString(total.m).length());
            if (flags.c.get() > 0) fmtLen = Math.max(fmtLen, Long.toString(total.c).length());
            if (flags.L.get() > 0) fmtLen = Math.max(fmtLen, Long.toString(total.L).length());
            
            fileStats.add(temp);
        }

        for (int i = 0; i < fileStats.size(); ++i) {
            fileStats.get(i).print(flags, fmtLen, fileNames.get(i));
        }
        if (printTot) total.print(flags, fmtLen, "total");
    }

    /// helpful classes

    static class flags_t {
        public AtomicInteger l, w, m, c, L;
        flags_t() {
            l = new AtomicInteger(0);
            w = new AtomicInteger(0);
            m = new AtomicInteger(0);
            c = new AtomicInteger(0);
            L = new AtomicInteger(0);
        }
    }

    static class stats_t {
        public long l = 0, w = 0, m = 0, c = 0, L = 0;

        public void print(flags_t flags, int fmtLen, String name) {
            Boolean flagPrinted = false;
            if (flags.l.get() > 0) {
                System.out.printf("%"+fmtLen+"d", this.l);
                flagPrinted = true;
            }
            if (flags.w.get() > 0) {
                if (flagPrinted) System.out.print(' ');
                System.out.printf("%"+fmtLen+"d", this.w);
                flagPrinted = true;
            }
            if (flags.m.get() > 0) {
                if (flagPrinted) System.out.print(' ');
                System.out.printf("%"+fmtLen+"d", this.m);
                flagPrinted = true;
            }
            if (flags.c.get() > 0) {
                if (flagPrinted) System.out.print(' ');
                System.out.printf("%"+fmtLen+"d", this.c);
                flagPrinted = true;
            }
            if (flags.L.get() > 0) {
                if (flagPrinted) System.out.print(' ');
                System.out.printf("%"+fmtLen+"d", this.L);
                flagPrinted = true;
            }
            if (flagPrinted && name != null) {
                System.out.print(" " + name);
            }
            System.out.println();
        }
    }
}