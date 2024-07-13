package java_lang;

import java.util.concurrent.atomic.AtomicInteger;

public class Option {
    public String optionName;
    public OptionRequirement has_arg;
    public AtomicInteger flag;
    public int val;

    Option(String optionName, OptionRequirement has_arg, AtomicInteger flag, int val) {
        this.optionName = optionName;
        this.has_arg = has_arg;
        this.flag = flag;
        this.val = val;
    }
}
