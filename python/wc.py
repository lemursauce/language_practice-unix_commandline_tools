import argparse
import os
import sys
from typing import List

def parse_args() -> argparse.Namespace:
    arg_parser = argparse.ArgumentParser(
        prog="wc",
        description="A WC Clone",
        epilog="(Thank you for using/testing this coding challenges word count tool!)")
    arg_parser.add_argument("filenames", nargs='*', default=None, help="Input files")
    arg_parser.add_argument("-c", "--bytes", action="store_true", help="print the byte counts")
    arg_parser.add_argument("-m", "--chars", action="store_true", help="print the character counts")
    arg_parser.add_argument("-l", "--lines", action="store_true", help="print the newline counts")
    arg_parser.add_argument("-L", "--max-line-length", action="store_true", help="print the maximum display width")
    arg_parser.add_argument("-w", "--words", action="store_true", help="print the word counts")
    return arg_parser.parse_args() 

# for iteration purposes
flagNames : str = ["lines", "words", "chars", "bytes", "max_line_length"]

def countAllInFile(fileName:(str|None) = None) -> List[int]:
    content : bytes
    bCount : int = 0
    if (fileName == None or fileName == "" or fileName == "-"):
        content = sys.stdin.buffer.read()
        bCount = len(content)
    else:
        bCount = os.path.getsize(fileName)
        with open(fileName, 'rb') as f:
            content = f.read()
    
    nline : bool = False
    lCount : int = 0
    
    wCount : int= 0
    maxLine : int = 0
    mCount : int = 0
    for line in content.splitlines():
        maxLine = max(maxLine,len(line))
        
        if nline:
            lCount += 1
        else:
            nline = True
        wordList = line.split()
        wCount += len(wordList)
        mCount += len(line)
    mCount += lCount
    
    return [lCount, wCount, mCount, bCount, maxLine]

def printStats(flags:argparse.Namespace, stats:List[int], fmtLen:int, fileName:str|None = None) -> None:
    flagPrinted = False
    
    for i in range(5):
        if getattr(flags, flagNames[i]):
            if flagPrinted: print('',end=' ')
            print(f"{stats[i]:{fmtLen}d}",end='')
            flagPrinted = True
    
    if fileName and len(fileName) > 0:
        if flagPrinted: print('',end=' ')
        print(fileName, end='')
    print()

def countByFlags(flags:argparse.Namespace) -> List[int]:
    empty : bool = False
    total = [0]*5
    prntTot = False
    fmtLen = 0
    fileStats = []
    
    if len(flags.filenames) == 0:
        flags.filenames.append('')
        empty = True
        fmtLen = 7
    if len(flags.filenames) > 1:
        prntTot = True
    
    for fileName in flags.filenames:
        temp = countAllInFile(fileName)
        fileStats.append(temp)
        for i in range(4):
            if getattr(flags, flagNames[i]):
                total[i] += temp[i]
                fmtLen = max(fmtLen, len(str(temp[i])))
        if flags.max_line_length:
            total[4] = max(total[4], temp[4])
            fmtLen = max(fmtLen, len(str(temp[4])))
    
    for i in range(len(flags.filenames)):
        printStats(flags, fileStats[i], fmtLen, flags.filenames[i])
    if (prntTot): printStats(flags, total, fmtLen, "total")
    if (empty): flags.filenames.pop()
    
    return total

if __name__ == "__main__":
    flags = parse_args()
    flagSet : bool = flags.bytes or flags.chars or flags.lines or flags.max_line_length or flags.words
    if not flagSet:
        flags.lines = True
        flags.words = True
        flags.bytes = True
    
    countByFlags(flags)