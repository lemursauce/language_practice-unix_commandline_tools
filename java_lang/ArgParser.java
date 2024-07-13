package java_lang;

import java.util.concurrent.atomic.AtomicInteger;

public class ArgParser {

    public String[] args;
    public Option[] options;
    public String optarg = null;
    private int argc = 0;
    private int argi = 0;

    ArgParser(String[] args, Option[] options) {
        this.args = args;
        this.argc = args.length;
        this.options = options;
    }

    private int flagmatch(String flag, String base) {
        if (flag == null || base == null) return 0;
        if (flag.length() < 1 || base.length() < 1) return 0;
        if (flag.charAt(0) == '-' && flag.charAt(1) != '-') {
            return (base.charAt(0) == '-' && base.charAt(1) == flag.charAt(1)) ? 2 : 0;
        }

        int i = 0;
        for (; i < flag.length() && i < base.length() && base.charAt(i) != '='; ++i) {
            if (flag.charAt(i) != base.charAt(i)) return 0;
        }
        if (i == flag.length() && (i == base.length() || base.charAt(i) == '=')) return i;
        return 0;
    }

    public int getArg() {
        return getArg(null);
    }
    public int getArg(AtomicInteger option_index) {
        if (this.argi >= this.argc) return -1;

        String arg = this.args[this.argi];
        if (arg.charAt(0) != '-' || arg.length() == 1) {
            ++argi;
            if (option_index != null) option_index.set(-1);
            this.optarg = arg;
            return 63; // same value as char '?'
        }

        int val = 0;
        for (int i = 0; i < this.options.length; ++i) {
            if (flagmatch(this.options[i].optionName, arg) > 0) {
                if (option_index != null) option_index.set(i);
                ++this.argi;

                this.optarg = null;
                if (this.options[i].has_arg != OptionRequirement.no_argument && this.argi < this.argc
                    && this.args[this.argi].length() > 0 && this.args[this.argi].charAt(0) != '-') {
                    this.optarg = this.args[this.argi];
                    ++this.argi;
                } else if (this.options[i].has_arg == OptionRequirement.required_argument) {
                    System.err.println("Option \"" + this.options[i].optionName + "\" requires an argument");
                    System.exit(1);
                }

                if (this.options[i].flag == null) {
                    val = this.options[i].val;
                } else {
                    this.options[i].flag.set(this.options[i].val);
                }

                return val;
            }
        }

        System.err.println("Error: \"" + arg + "\" is an invalid option");
        System.exit(1);
        return -1;
    }
}
