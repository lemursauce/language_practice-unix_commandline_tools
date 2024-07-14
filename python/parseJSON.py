from typing import List, Tuple
from enum import Enum

##### only useful for passing all the tests in step 5 of the codingchallenges.fyi source #####

MAX_DEPTH = 19
curr_depth = 0

##### useful info for tokenization process #####

extra_tokens = False

class Token(Enum):
    WS = 0      # white space, shouldn't really be included in final tokens unless extra_tokens=True
    BRACE = 1   # '{}'
    BRACKET = 2 # '[]'
    NAME = 3    # same qualities as STRING, just in the context of a key rather than a value
    COLON = 4   # shouldn't really be included in final tokens unless extra_tokens=True
    STRING = 5
    NUMBER = 6
    BOOL = 7
    NULL = 8
    UNKNOWN = 999

braceMatch = {
    '{':'}',
    '}':'{',
    '[':']',
    ']':'['
}

tokens = []

##### tokenize start #####

def tokenize(s : str) -> List[Tuple[Token,any]]:
    global tokens
    global curr_depth
    tokens = []
    curr_depth = 0
    i = tokenizeWhitespace(s, 0, tokens)
    if (s[i] == '{'):
        curr_depth += 1
        i = tokenizeObject(s, i, tokens)
    elif (s[i] == '['):
        curr_depth += 1
        i = tokenizeArray(s, i, tokens)
    else:
        raise Exception(f"A JSON payload should be an object or array")
    i = tokenizeWhitespace(s, i, tokens)
    if i < len(s):
        raise Exception(f"There is extra content outside of the main object/array")
    return tokens

##### tokenize functions #####

def tokenizeValue(s : str, i : int, tokens : List[Tuple[Token,any]]) -> int:
    global curr_depth
    i = tokenizeWhitespace(s, i, tokens)
    if (s[i] == '{'):
        curr_depth += 1
        if MAX_DEPTH != None and curr_depth > MAX_DEPTH:
            raise Exception("JSON MAX_DEPTH has been exceeded")
        i = tokenizeObject(s, i, tokens)
    elif (s[i] == '['):
        curr_depth += 1
        if MAX_DEPTH != None and curr_depth > MAX_DEPTH:
            raise Exception("JSON MAX_DEPTH has been exceeded")
        i = tokenizeArray(s, i, tokens)
    elif (s[i] == '\"'):
        i = tokenizeString(s, i, tokens)
    elif (s[i] == 'n'):
        i = tokenizeNull(s, i, tokens)
    elif (s[i] in 'tf'):
        i = tokenizeBool(s, i, tokens)
    elif (s[i] == '-' or s[i].isnumeric()):
        i = tokenizeNumber(s, i, tokens)
    else:
        raise Exception(f"Value type must be a string, number, boolean, object, or array, instead read \"{s[i]}\"")
    return i

def tokenizeObject(s : str, i : int, tokens : List[Tuple[Token,any]]) -> int:
    global curr_depth
    tokens.append((Token.BRACE, '{'))
    i += 1
    
    # check if object is empty
    i = tokenizeWhitespace(s, i, tokens)
    if s[i] == braceMatch['{']:
        curr_depth -= 1
        tokens.append((Token.BRACE, braceMatch['{']))
        return i+1
    
    while (i < len(s)):
        
        # name
        i = tokenizeString(s, i, tokens, Token.NAME)
        # colon
        i = tokenizeWhitespace(s, i, tokens)
        if s[i] == ':':
            if extra_tokens: tokens.append((Token.COLON, ':'))
            i += 1
        else:
            raise Exception(f"expected ':' after key name, instead received \"{s[i]}\"")
        # value
        i = tokenizeValue(s, i, tokens)
        
        
        # check if end of object
        i = tokenizeWhitespace(s, i, tokens)
        if s[i] == braceMatch['{']:
            curr_depth -= 1
            tokens.append((Token.BRACE, braceMatch['{']))
            return i+1
        elif s[i] != ',':
            break
        i += 1
    raise Exception(f"expected end bracket {braceMatch['{']} to Object")

def tokenizeArray(s : str, i : int, tokens : List[Tuple[Token,any]]) -> int:
    global curr_depth
    tokens.append((Token.BRACKET, '['))
    i += 1
    
    # check if array is empty
    i = tokenizeWhitespace(s, i, tokens)
    if i < len(s) and s[i] == braceMatch['[']:
        curr_depth -= 1
        tokens.append((Token.BRACKET, braceMatch['[']))
        return i+1
    
    while (i < len(s)):
        
        # value
        i = tokenizeValue(s, i, tokens)
        
        # check if end of object
        i = tokenizeWhitespace(s, i, tokens)
        if i >= len(s): break
        if s[i] == braceMatch['[']:
            curr_depth -= 1
            tokens.append((Token.BRACKET, braceMatch['[']))
            return i+1
        elif s[i] != ',':
            break
        i += 1
    raise Exception(f"expected end bracket {braceMatch['[']} to Array")



def tokenizeString(s : str, i : int, tokens : List[Tuple[Token,any]], type : Token = Token.STRING) -> int:
    i = tokenizeWhitespace(s, i, tokens)
    if s[i] != '\"':
        raise Exception("tried parsing string that does not exist")
    i += 1
    temp = ""
    while i < len(s) and s[i] != '\"':
        if s[i] in '\n\r\b\f\t': raise Exception("invalid characters encountered when parsing string")
        if s[i] == '\\':
            i += 1
            if (i >= len(s)): raise Exception("escape character is left incomplete")
            u = False
            
            # handle escape characters
            if   s[i] == '\"': temp += '\"'
            elif s[i] == '\\': temp += '\\'
            elif s[i] == '/': temp += '/'
            elif s[i] == 'b': temp += '\b'
            elif s[i] == 'f': temp += '\f'
            elif s[i] == 'n': temp += '\n'
            elif s[i] == 'r': temp += '\r'
            elif s[i] == 't': temp += '\t'
            elif s[i] == 'u': u = True
            else:
                raise Exception("invalid escape character")
            i += 1
            
            # handle unicode
            if u:
                j = i+4
                if (j >= len(s)): raise Exception("escape character is left incomplete")
                for c in s[i:j]:
                    if c.lower() not in '0123456789abcdef':
                        raise Exception("unicode escape character must comprise of 4 hexadecimal characters")
                temp += chr(int(s[i:j],16))
                i = j
            
        else:
            temp += s[i]
            i += 1
    if i >= len(s):
        raise Exception("expected end quote")
    if s[i] == '\"': i += 1
    tokens.append((type, temp))
    return i

def tokenizeNumber(s : str, i : int, tokens : List[Tuple[Token,any]]) -> int:
    val = 0
    neg = False
    firstZero = False
    if s[i] == '-':
        neg = True
        i += 1
    elif s[i] == '0':
        firstZero = True
        i += 1
    
    frac = False
    frac_val = 0.1
    expo = False
    while (i < len(s)):
        if s[i].isnumeric():
            if firstZero and not frac:
                raise Exception("cannot lead numeric value with extra zeros")
            if frac:
                val += frac_val * int(s[i])
                frac_val /= 10
            else:
                val *= 10
                val += int(s[i])
            i += 1
        elif s[i] == '.':
            if frac:
                raise Exception("cannot have a numeric value with multiple decimal points")
            frac = True
            i += 1
        elif s[i].lower() == 'e':
            i += 1
            val *= 1.0
            expo = True
            break
        else:
            break
    if neg: val *= -1
    
    if expo:
        expo_val = 0
        expo_neg = False
        if not s[i].isnumeric():
            if s[i] not in '+-':
                raise Exception("invalid character within number exponent")
            if s[i] == '-':
                expo_neg = True
            i += 1
        expo_valid = False
        while (i < len(s)):
            if s[i].isnumeric():
                expo_valid = True
                expo_val *= 10
                expo_val += int(s[i])
            else:
                break
            i += 1
            pass
        if not expo_valid:
            raise Exception("invalid exponent: no integer value found where exponent should be")
        if expo_neg : expo_val *= -1
        val *= 10**expo_val
    tokens.append((Token.NUMBER, val))
    return i

def tokenizeBool(s : str, i : int, tokens : List[Tuple[Token,any]]) -> int:
    if s[i:i+4].lower() == "true":
        tokens.append((Token.BOOL, True))
        i += 4
    elif s[i:i+5].lower() == "false":
        tokens.append((Token.BOOL, False))
        i += 5
    else:
        raise Exception("Value type must be a string, number, boolean, object, or array")
    return i

def tokenizeNull(s : str, i : int, tokens : List[Tuple[Token,any]]) -> int:
    if s[i:i+4].lower() == "null":
        tokens.append((Token.BOOL, True))
        i += 4
    else:
        raise Exception("Value type must be a string, number, boolean, object, or array")
    return i

def tokenizeWhitespace(s : str, i : int, tokens : List[Tuple[Token,any]]) -> int:
    wsCount = 0
    while i < len(s) and s[i].isspace():
        i += 1
        wsCount += 4 if (s[i] == '\t') else 1
    if extra_tokens and wsCount > 0: tokens.append((Token.WS, wsCount))
    return i

##### validation function #####

def validateJSON(fileName : str, err : bool = False, prnt : bool = False) -> bool:
    if err or prnt: print(fileName)
    with open(fileName) as f:
        allChars = f.read().strip()
        
        try:
            tokenize(allChars)
            if (prnt):
                for token in tokens:
                    print('(', token[0].name, ", ", repr(token[1]), ')', sep='')
        except Exception as ex:
            if err or prnt: print(ex)
            return False
    return True

##### main calls #####

import argparse

def parse_args() -> argparse.Namespace:
    arg_parser = argparse.ArgumentParser(
        prog="parseJSON",
        description="A toy JSON parser/validator",
        epilog="")
    arg_parser.add_argument("filenames", nargs='*', default=None, help="Input files")
    arg_parser.add_argument("-e", "--error", action="store_true", help="print error/exception info")
    arg_parser.add_argument("-p", "--print", action="store_true", help="print all info (including final tokens when valid)")
    return arg_parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    if args.filenames == None or len(args.filenames) == 0:
        exit(0)
    for fileName in args.filenames:
        valid = validateJSON(fileName, args.error, args.print)
        if not args.error and not args.print:
            print(fileName, ": ", "valid" if valid else "not valid", sep = '')
        
