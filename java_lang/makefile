JC=javac
JCFLAGS=-d .

PCKG=java_lang

SRCS=WC.java
DEPS=OptionRequirement.java Option.java ArgParser.java

ALLJAVA=$(DEPS) $(SRCS)
BINS=$(ALLJAVA:%.java=$(PCKG)/%.class)
RUN_NAMES=$(SRCS:%.java=$(PCKG)/%)

all: clean $(BINS)

$(PCKG)/%.class: %.java
	$(JC) $(JCFLAGS) $<

.PHONY: build clean _clean clear ls

build: clean $(BINS)

clean _clean clear:
	rm -r -f $(PCKG)

ls:
	@ if [ -d "$(PCKG)" ]; then \
		echo "java: " $(RUN_NAMES); \
	else \
		echo "Files not yet compiled/built. Please run 'make' or 'make build'"; \
	fi