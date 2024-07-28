package main

import (
	"bufio"
	"bytes"
	"flag"
	"fmt"
	"os"
	"slices"
	"sync"
	"unicode/utf8"
)

const (
	helpStr = `Usage: ./wc [OPTION]... [FILE]...

Print newline, word, and byte counts for each FILE, and a total line if
more than one FILE is specified. A word is a non-zero-length sequence of
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
`
)

const BUFSIZE int64 = 4096

var (
	wg sync.WaitGroup
)

type WC_FLAGS struct {
	l bool
	w bool
	m bool
	c bool
	L bool
}

type WC_STATS struct {
	l           int64
	w           int64
	m           int64
	c           int64
	L           int64
	fmtLen      int64
	name        string
	newLineIdxs []int
}

type Chunk struct {
	wcstats WC_STATS
	bufSize int64
	offset  int64
}

func NewStats(name string) WC_STATS {
	var stat WC_STATS
	stat.l = 0
	stat.w = 0
	stat.m = 0
	stat.c = 0
	stat.L = 0
	stat.fmtLen = 0
	stat.name = name
	return stat
}

func NewChunk() Chunk {
	var ch Chunk
	return ch
}

func _printHelp(wcflag bool, wcstat int64, fmtLen int64, flagPrinted *bool) {
	if wcflag {
		if *flagPrinted {
			fmt.Print(" ")
		}
		fmt.Printf("%*d", fmtLen, wcstat)
		*flagPrinted = true
	}
}

func printStat(stats WC_STATS, wcflags WC_FLAGS, fmtLen int64, name string) {
	flagPrinted := false
	_printHelp(wcflags.l, stats.l, fmtLen, &flagPrinted)
	_printHelp(wcflags.w, stats.w, fmtLen, &flagPrinted)
	_printHelp(wcflags.m, stats.m, fmtLen, &flagPrinted)
	_printHelp(wcflags.c, stats.c, fmtLen, &flagPrinted)
	_printHelp(wcflags.L, stats.L, fmtLen, &flagPrinted)
	if flagPrinted && name != "" {
		fmt.Printf(" %s", name)
	}
	fmt.Println()
}

//////////

func processBuffer(byteArr []byte, wcflags WC_FLAGS, order int64) WC_STATS {
	stats := NewStats("")
	if wcflags.l {
		stats.l = int64(bytes.Count(byteArr, []byte{'\n'}))
	}
	if wcflags.w {
		stats.w = int64(len(bytes.Fields(byteArr)))
	}
	if wcflags.m || wcflags.L {
		stats.m = int64(utf8.RuneCount(byteArr))
	}
	// c doesn't matter

	if wcflags.L {
		placement := (order * BUFSIZE)
		for i, b := range byteArr {
			if b == '\n' {
				orderedIdx := i + int(placement)
				stats.newLineIdxs = append(stats.newLineIdxs, orderedIdx)
			}
		}
	}

	return stats
}

func (stats *WC_STATS) Add(other WC_STATS) {
	stats.l += other.l
	stats.w += other.w
	stats.m += other.m
	stats.c += other.c
	stats.L = max(stats.L, other.L)
}

func (stats *WC_STATS) Aggregate(other WC_STATS) {
	/// not first chunk word issues?
	///

	stats.l += other.l
	stats.w += other.w
	stats.m += other.m
	stats.c += other.c
	stats.newLineIdxs = append(stats.newLineIdxs, other.newLineIdxs...)
}

func (stats *WC_STATS) finalizeMaxLineLength() {
	stats.L = 0
	slices.Sort(stats.newLineIdxs)
	if len(stats.newLineIdxs) > 0 {
		for i, idx := range stats.newLineIdxs {
			if i == 0 {
				stats.L = int64(stats.newLineIdxs[i])
				continue
			}
			nextLine := int64(idx - stats.newLineIdxs[i-1] - 1)
			if nextLine > stats.L {
				stats.L = nextLine
			}
		}
		lastLine := stats.c - int64(stats.newLineIdxs[len(stats.newLineIdxs)-1]-1)
		if lastLine > stats.L {
			stats.L = lastLine
		}
	} else {
		stats.L = stats.m
	}

}

func (stats *WC_STATS) finalizeFmtLength() {
	stats.fmtLen = max(stats.fmtLen, int64(len(fmt.Sprintf("%d", stats.l))))
	stats.fmtLen = max(stats.fmtLen, int64(len(fmt.Sprintf("%d", stats.w))))
	stats.fmtLen = max(stats.fmtLen, int64(len(fmt.Sprintf("%d", stats.m))))
	stats.fmtLen = max(stats.fmtLen, int64(len(fmt.Sprintf("%d", stats.c))))
	stats.fmtLen = max(stats.fmtLen, int64(len(fmt.Sprintf("%d", stats.L))))
}

//////////

func _wc(fileName string, wcflags WC_FLAGS, statc chan<- WC_STATS) {
	defer wg.Done()
	stats := NewStats(fileName)

	var file *os.File
	var err error

	if fileName != "" && fileName != "-" {
		file, err = os.Open(fileName)
		if err != nil {
			fmt.Printf("Could not access file: %s\n", fileName)
			os.Exit(1)
		}
	} else {
		file = os.Stdin
	}
	defer file.Close()

	ostat, err := file.Stat()
	if err != nil {
		fmt.Printf("could not get stats from file: %s\n", fileName)
		os.Exit(1)
	}
	stats.c = ostat.Size()

	chunks := make(chan Chunk, 1)
	if file == os.Stdin {
		stats.fmtLen = 7
		go func() {
			defer close(chunks)
			scanner := bufio.NewScanner(os.Stdin)
			first := true
			c := NewChunk()
			var bytes []byte
			for scanner.Scan() {
				if first {
					first = false
				} else {
					bytes = append(bytes, byte('\n'))
				}

				bytes = append(bytes, []byte(scanner.Text())...)
				bytes := []byte(scanner.Text())

				stats.c += int64(len(bytes))
			}
			if scanner.Err() != nil {
				fmt.Printf("error reading stdin\n")
				os.Exit(1)
			}
			c.bufSize = stats.c
			c.wcstats = processBuffer(bytes, wcflags, 0)
			chunks <- c
		}()
	} else {
		go func() {
			numOfChunks := stats.c / BUFSIZE
			var wgc sync.WaitGroup
			for i := int64(0); i < numOfChunks; i++ {
				wgc.Add(1)
				go func(order int64) {
					defer wgc.Done()

					c := NewChunk()
					buf := make([]byte, BUFSIZE)
					_, err := file.ReadAt(buf, BUFSIZE*order)
					if err != nil {
						fmt.Printf("error reading file: %s\n", fileName)
						fmt.Printf("%s\n", err.Error())
						os.Exit(1)
					}

					c.bufSize = BUFSIZE
					c.offset = BUFSIZE * order
					c.wcstats = processBuffer(buf, wcflags, order)
					chunks <- c
				}(i)
			}

			remainder := stats.c % BUFSIZE
			if remainder > 0 {
				wgc.Add(1)
				go func() {
					defer wgc.Done()
					c := NewChunk()
					buf := make([]byte, remainder)
					_, err := file.ReadAt(buf, BUFSIZE*numOfChunks)
					if err != nil {
						fmt.Printf("error reading file: %s\n", fileName)
						fmt.Printf("%s\n", err.Error())
						os.Exit(1)
					}

					c.bufSize = remainder
					c.offset = BUFSIZE * numOfChunks
					c.wcstats = processBuffer(buf, wcflags, numOfChunks)
					chunks <- c
				}()
			}

			wgc.Wait()
			close(chunks)
		}()
	}

	for c := range chunks {
		stats.Aggregate(c.wcstats)
	}

	stats.finalizeMaxLineLength()
	stats.finalizeFmtLength()

	statc <- stats
}

func _wcbatch(fileNames []string, wcflags WC_FLAGS, statc chan<- WC_STATS) {
	for _, fileName := range fileNames {
		wg.Add(1)
		go _wc(fileName, wcflags, statc)
	}
	wg.Wait()
	close(statc)
}

func wc(fileNames []string, wcflags WC_FLAGS) {
	total := NewStats("total")
	statc := make(chan WC_STATS, 2)
	go _wcbatch(fileNames, wcflags, statc)

	var statf []WC_STATS
	var fmtLen int64 = 0

	for stat := range statc {
		total.Add(stat)
		fmtLen = max(fmtLen, stat.fmtLen)
		statf = append(statf, stat)
	}
	total.finalizeFmtLength()
	fmtLen = max(fmtLen, total.fmtLen)

	for _, stat := range statf {
		printStat(stat, wcflags, fmtLen, stat.name)
	}

	if len(fileNames) > 1 {
		printStat(total, wcflags, fmtLen, total.name)
	}
}

//////////

func main() {
	var wcflags WC_FLAGS

	flag.BoolVar(&wcflags.c, "c", false, "print the byte counts")
	flag.BoolVar(&wcflags.c, "bytes", false, "print the byte counts")
	flag.BoolVar(&wcflags.m, "m", false, "print the character counts")
	flag.BoolVar(&wcflags.m, "chars", false, "print the character counts")
	flag.BoolVar(&wcflags.l, "l", false, "print the newline counts")
	flag.BoolVar(&wcflags.l, "lines", false, "print the newline counts")
	flag.BoolVar(&wcflags.L, "L", false, "print the maximum display width")
	flag.BoolVar(&wcflags.L, "max-line-length", false, "print the maximum display width")
	flag.BoolVar(&wcflags.w, "w", false, "print the word counts")
	flag.BoolVar(&wcflags.w, "words", false, "print the word counts")

	flag.Usage = func() { fmt.Print(helpStr) }

	// just to ensure that, given any order of flags / file inputs that flags and args are properly processed
	slices.Sort(os.Args[1:])

	flag.Parse()
	vals := flag.Args()

	if !wcflags.l && !wcflags.w && !wcflags.m && !wcflags.c && !wcflags.L {
		wcflags.l = true
		wcflags.w = true
		wcflags.c = true
	}

	if len(vals) <= 0 {
		vals = append(vals, "")
	}

	wc(vals, wcflags)
}
