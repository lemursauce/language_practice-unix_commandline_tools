from typing import List, Tuple
from enum import Enum

##### only useful for passing all the tests in step 5 of the codingchallenges.fyi source #####

MAX_DEPTH = 19

##### useful info for tokenization process #####

extra_tokens = True

class JSONToken(Enum):
    WS = 0      # white space, shouldn't really be included in final tokens
    OBJECT_BEGIN    = 1
    OBJECT_END      = 2
    ARRAY_BEGIN     = 3
    ARRAY_END       = 4
    NAME            = 5    # same qualities as STRING, just in the context of a key rather than a value
    NAME_SEPARATOR  = 6    # shouldn't really be included in final tokens unless extra_tokens=True
    VALUE_SEPARATOR = 7    # shouldn't really be included in final tokens unless extra_tokens=True
    STRING          = 8
    NUMBER          = 9
    BOOL            = 10
    NULL            = 11
    UNKNOWN         = 999

##### Parser class #####

class ParseJSON:
    def __init__(self, file:str|None = None , *,  prnt:bool = False):
        self.prnt = prnt
        self.tokenizeNewFile(file)
    
    def tokenizeNewFile(self, file:str|None) -> bool:
        self.tokens = []
        self.i : int = 0
        self.depth = 0
        self.pos : List[int] = [1,1]
        self.stack : List[Tuple[int,List[int]]] = []
        self.error_i : int = -1
        self.lastError : Tuple[List[int], str] | None = None
        self.file = file
        self.buildStr = ""
        if file is not None:
            return self.tokenize()
        else: return False
    
    #####
    
    def printPosInfo(self) -> None:
        print(self.stack, "@", (self.i, self.pos))
    def printError(self) -> None:
        if self.lastError is not None:
            print(f"Error at line {self.lastError[0][0]}, col {self.lastError[0][1]}: {self.lastError[1]}")
        else:
            print(f"No errors were encountered!")
    
    def pushInstance(self) -> None:
        self.stack.append((self.i, self.pos.copy()))
        if (self.prnt): self.printPosInfo()
    def updateInstance(self) -> None:
        self.stack[-1] = (self.i, self.pos.copy())
        if (self.prnt): self.printPosInfo()
    def popInstance(self) -> None:
        self.i, self.pos = self.stack.pop()
        if (self.prnt): self.printPosInfo()
    def removeInstance(self) -> None:
        self.stack.pop()
        if (self.prnt): self.printPosInfo()
    def revertInstance(self) -> None:
        self.i, self.pos = self.stack[-1]
        if (self.prnt): self.printPosInfo()
        
    def appendToken(self, t:JSONToken, val:str) -> None:
        self.tokens.append((t,val))
        if (self.prnt): print("tokens:", self.tokens)
    def setError(self, err:str) -> None:
        if self.i > self.error_i:
            self.error_i = self.i
            self.lastError = (self.pos.copy(), err)
        
    def increment_i(self) -> None:
        if self.i < len(self.file) and self.file[self.i] == '\n':
            self.pos[0] += 1
            self.pos[1] = 1
        else:
            self.pos[1] += 1
        self.i += 1
    
    #####
    
    ''' <JSON_text> ::= <object> | <array> '''
    def tokenize(self) -> bool:
        if (self.prnt): print("tokenize")
        self.pushInstance()
        if self.parseObject() or self.parseArray():
            if self.EOF():
                self.stack.clear()
                self.lastError = None
                return True
            else:
                self.setError("Expected end of file after parsing main JSON object/array")
        self.setError("Expected instance of object or array at beginning of file")
        self.popInstance()
        return False
    
    #####
    
    ''' <object> ::= <begin_object> (<member> (<value_separator> <member>)* )? <end_object> '''
    def parseObject(self) -> bool:
        if (self.prnt): print("object")
        
        self.depth += 1
        if MAX_DEPTH != None and self.depth > MAX_DEPTH:
            self.setError("Exceeded maximum depth allowed")
            return False
        
        self.pushInstance()
        if self.parseBeginObject():
            if self.parseMember():
                while self.parseValueSeparator():
                    if not self.parseMember():
                        self.popInstance()
                        self.depth -= 1
                        self.setError("Expected instance of member after value separator ','")
                        return False
                
            if self.parseEndObject():
                self.removeInstance()
                self.depth -= 1
                return True
            else:
                self.setError("Expected end of object '}'")
        self.popInstance()
        self.depth -= 1
        return False
    
    ''' <member> ::= <string> <name_separator> <value> '''
    def parseMember(self) -> bool:
        if (self.prnt): print("member")
        self.pushInstance()
        if self.parseName() and self.parseNameSeparator() and self.parseValue():
            self.removeInstance()
            return True
        self.popInstance()
        return False
    
    def parseName(self) -> bool:
        if (self.prnt): print("name")
        if self.__parseString():
            # add token
            self.appendToken(JSONToken.NAME, self.buildStr)
            return True
        
        self.setError("expected member to begin with name")
        return False
    
    ''' <array>  ::= <begin_array> (<value> (<value_separator> <value>)* )? <end_array> '''
    def parseArray(self) -> bool:
        if (self.prnt): print("array")
        
        self.depth += 1
        if MAX_DEPTH != None and self.depth > MAX_DEPTH:
            self.setError("Exceeded maximum depth allowed")
            return False
        
        self.pushInstance()
        if self.parseBeginArray():
            if self.parseValue():
                while self.parseValueSeparator():
                    if not self.parseValue():
                        self.popInstance()
                        self.depth -= 1
                        self.setError("Expected value after value separator ','")
                        return False
            
            if self.parseEndArray():
                self.removeInstance()
                self.depth -= 1
                return True
            else:
                self.setError("Expected end of array ']'")
        self.popInstance()
        self.depth -= 1
        return False
    
    
    ''' <value> ::= <null> | <true> | <false> | <string> | <number> | <object> | <array> '''
    def parseValue(self) -> bool:
        if (self.prnt): print("value")
        self.pushInstance()
        if self.parseNull() \
            or self.parseTrue() \
                or self.parseFalse() \
                    or self.parseString() \
                        or self.parseNumber() \
                            or self.parseObject() \
                                or self.parseArray():
            # tokens are added in unique declarations
            self.removeInstance()
            return True
        
        self.setError("expected a value instance")
        self.popInstance()
        return False
    
    def parseString(self) -> bool:
        if self.__parseString():
            # add token
            self.appendToken(JSONToken.STRING, self.buildStr)
            return True
        return False
        
    def parseNumber(self) -> bool:
        if self.__parseNumber():
            # add token
            self.appendToken(JSONToken.NUMBER, self.buildStr)
            return True
        return False
    
    #####
    
    ''' <opt_whitespace> ::= \s* '''
    def __itWhitespace(self):
        while self.i < len(self.file) and self.file[self.i].isspace():
            self.increment_i()
    
    ''' <?> ::= ? '''
    def __parseLiteral(self, lit:str) -> bool:
        if (self.prnt): print(f"literal \"{lit}\"")
        self.pushInstance()
        for c in lit:
            if self.i >= len(self.file) or self.file[self.i] != c:
                self.popInstance()
                return False
            self.increment_i()
        self.removeInstance()
            
        return True
    
    ''' <?_separator> ::= <opt_whitespace> <?> <opt_whitespace> '''
    def __parseSeparator(self, sep:str) -> bool:
        if (self.prnt): print(f"separator {sep}")
        self.pushInstance()
        self.__itWhitespace()
        if not self.__parseLiteral(sep):
            self.popInstance()
            return False
        self.removeInstance()
        self.__itWhitespace()
        return True
    
    ''' <string> ::= <string> ::= <quotation_mark> (<char>)* <quotation_mark> '''
    def __parseString(self) -> bool:
        if (self.prnt): print("string")
        self.buildStr = ""
        
        self.pushInstance()
        if not self.__parseLiteral('\"'):
            self.popInstance()
            return False
        
        while self.i < len(self.file) and self.file[self.i] != '\"':
            if not self.__parseStrChar():
                self.popInstance()
                self.setError("String contains an invalid character")
                return False
        
        if not self.__parseLiteral('\"'):
            self.popInstance()
            self.setError("Expected end of string '\"'")
            return False
        
        self.removeInstance()
        return True
    
    ''' <char> ::= <non escape> | <escape> '''
    def __parseStrChar(self) -> bool:
        return self.__parseNonEscape() or self.__parseEscape()
    
    def __parseNonEscape(self) -> bool:
        if self.file[self.i] in '\\\n\r\b\f\t':
            return False
        self.buildStr += self.file[self.i]
        self.increment_i()
        return True
    
    def __parseEscape(self) -> bool:
        if self.file[self.i] != '\\': return False
        if (self.prnt): print("escape")
        self.increment_i()
        if self.i >= len(self.file): return False
        
        escape = "\"\\/\b\f\n\r\t"
        for i, c in enumerate("\"\\/bfnrt"):
            if self.file[self.i] == c:
                self.buildStr += escape[i]
                self.increment_i()
                return True
        if self.file[self.i] == 'u':
            self.increment_i()
            # parse 4 hex (<unicode>)
            if (self.prnt): print("hex * 4")
            for _ in range(4):
                if not self.__parseHex(): return False
            self.buildStr += chr(int(self.file[self.i-4:self.i],16))
            return True
        
        self.setError("String contains an invalid escape character")
        return False
    
    def __parseHex(self) -> bool:
        if self.i >= len(self.file): return False
        if self.file[self.i] not in "0123456789abcdefABCDEF":
            self.setError("Invalid Unicode character")
            return False
        self.increment_i()
        return True
    
    ''' <number> ::= (<minus>)? <int> (frac)? (exp)? '''
    def __parseNumber(self) -> bool:
        if (self.prnt): print("number")
        self.buildStr = ""
        
        self.pushInstance()
        if self.__parseLiteral('-'):
            self.buildStr += '-'
        
        if not self.__parseInt():
            self.popInstance()
            return False
        
        self.__parseFrac()
        self.__parseExp()
        
        self.removeInstance()
        return True
    
    ''' <int> ::= <zero> | (<digit1-9> (<digit>)*) '''
    def __parseInt(self) -> bool:
        self.pushInstance()
        if self.i >= len(self.file) or not self.file[self.i].isdigit():
            self.popInstance()
            return False
        
        self.buildStr += self.file[self.i]
        
        self.increment_i()
        if self.file[self.i-1] != '0':
            while self.i < len(self.file) and self.file[self.i].isdigit():
                self.buildStr += self.file[self.i]
                self.increment_i()
            # extra error catching to be more human readable/understandable
            if self.i < len(self.file) and self.file[self.i].isalnum() and self.file[self.i] not in 'eE':
                self.popInstance()
                self.setError("Integers cannot contain letters")
                return False
        # extra error catching to be more human readable/understandable   
        elif self.i < len(self.file):
            if self.file[self.i].isdigit():
                self.popInstance()
                self.setError("Integers that are not '0' cannot have a leading 0")
                return False
            elif self.file[self.i].isalpha() and self.file[self.i] not in 'eE':
                self.popInstance()
                self.setError("Integers cannot contain letters")
                return False
        
        
        self.removeInstance()
        return True
    
    ''' <frac> ::= <decimal_point> (<digit>)+ '''
    def __parseFrac(self) -> bool:
        self.pushInstance()
        if not self.__parseLiteral('.'):
            self.popInstance()
            return False
        self.buildStr += '.'
        
        if self.i >= len(self.file) or not self.file[self.i].isdigit():
            self.popInstance()
            return False
        self.buildStr += self.file[self.i]
        self.increment_i()
        
        while self.i < len(self.file) and self.file[self.i].isdigit():
            self.buildStr += self.file[self.i]
            self.increment_i()
        
        self.removeInstance()
        return True
    
    ''' <exp> ::= (<e> | <E>) (<minus> | <plus>)? (<digit>)+ '''
    def __parseExp(self) -> bool:
        self.pushInstance()
        if not (self.__parseLiteral('e') or self.__parseLiteral('E')):
            self.popInstance()
            return False
        self.buildStr += self.file[self.i-1]
        
        if self.__parseLiteral('+') or self.__parseLiteral('-'):
            self.buildStr += self.file[self.i-1]
        
        if self.i >= len(self.file) or not self.file[self.i].isdigit():
            self.popInstance()
            return False
        self.buildStr += self.file[self.i]
        self.increment_i()
        
        while self.i < len(self.file) and self.file[self.i].isdigit():
            self.buildStr += self.file[self.i]
            self.increment_i()
        
        self.removeInstance()
        return True
    
    #####
    
    def parseBeginObject(self) -> bool:
        if self.__parseSeparator('{'):
            # add token
            self.appendToken(JSONToken.OBJECT_BEGIN, '{')
            return True
        return False
    def parseBeginArray(self) -> bool:
        if self.__parseSeparator('['):
            # add token
            self.appendToken(JSONToken.OBJECT_BEGIN, '[')
            return True
        return False
    def parseEndObject(self) -> bool:
        if self.__parseSeparator('}'):
            # add token
            self.appendToken(JSONToken.OBJECT_BEGIN, '}')
            return True
        return False
    def parseEndArray(self) -> bool:
        if self.__parseSeparator(']'):
            # add token
            self.appendToken(JSONToken.OBJECT_BEGIN, ']')
            return True
        return False
    def parseNameSeparator(self) -> bool:
        if self.__parseSeparator(':'):
            # add token
            if extra_tokens: self.appendToken(JSONToken.NAME_SEPARATOR, ':')
            return True
        self.setError("Expected name separator ':'")
        return False
    def parseValueSeparator(self) -> bool:
        if self.__parseSeparator(','):
            # add token
            if extra_tokens: self.appendToken(JSONToken.VALUE_SEPARATOR, ',')
            return True
        return False
    
    def parseNull(self) -> bool:
        if self.__parseLiteral("null"):
            # add token
            self.appendToken(JSONToken.NULL, 'null')
            return True
        return False
    def parseTrue(self) -> bool:
        if self.__parseLiteral("true"):
            # add token
            self.appendToken(JSONToken.BOOL, 'true')
            return True
        return False
    def parseFalse(self) -> bool:
        if self.__parseLiteral("false"):
            # add token
            self.appendToken(JSONToken.BOOL, 'false')
            return True
        return False
    
    def EOF(self) -> bool:
        if self.i >= len(self.file):
            return True
        self.setError("Expected to have reached the end of the file. There must be extra content in the file that is not allowed.")
        return False
    

##### main calls #####

import argparse

def parse_args() -> argparse.Namespace:
    arg_parser = argparse.ArgumentParser(
        prog="parseJSON",
        description="A toy JSON parser/validator",
        epilog="")
    arg_parser.add_argument("filenames", nargs='*', default=None, help="Input files")
    arg_parser.add_argument("-t", "--tokens", action="store_true", help="print tokens generated from parsing/validation")
    arg_parser.add_argument("-p", "--print", action="store_true", help="print all info (including final tokens when valid)")
    return arg_parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    if args.filenames == None or len(args.filenames) == 0:
        exit(1)
    p = ParseJSON(prnt=args.print)
    for fileName in args.filenames:
        try:
            with open(fileName) as f:
                valid = p.tokenizeNewFile(f.read().strip())
                if valid:
                    print(fileName, ": VALID", sep = '')
                    if args.print:
                        for token in p.tokens:
                            print("\t",token)
                else:
                    print(fileName, ": NOT VALID", sep = '')
                    p.printError()
                if args.tokens:
                    for token in p.tokens:
                        print("\t",token)
                    
        except Exception as ex:
            print(ex)