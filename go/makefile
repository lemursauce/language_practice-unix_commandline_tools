GO=go build
GODEVFLAGS=
GORELFLAGS=-ldflags "-s -w"

BUILDDIR=build
DEV=dev
REL=release

SRCS=wc.go
BINSDEV=$(SRCS:%.go=$(BUILDDIR)/$(DEV)/%.exe)
BINSREL=$(SRCS:%.go=$(BUILDDIR)/$(REL)/%.exe)
RUN_NAMES=$(SRCS:%.go=%)

all: clean $(BINSDEV)

$(BUILDDIR)/$(DEV)/%.exe: $(SRCS)
	$(GO) $(GODEVFLAGS) -o $(patsubst %.exe,%,$@) $^

$(BUILDDIR)/$(REL)/%.exe: $(SRCS)
	$(GO) $(GORELFLAGS) -o $(patsubst %.exe,%,$@) $^

.PHONY: build clean _clean clear release

build: clean $(BINSDEV)

release: clean $(BINSREL)

clean _clean clear:
	rm -rf $(BUILDDIR)
