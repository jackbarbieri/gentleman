from typing import Dict, Callable
from state import InterpretState, CompileState
import math

Primitives: Dict[str, Dict[str, Callable]] = {}

def primitive(func) -> None:
    docstring = func.__doc__
    specialCompile: bool = docstring.find(' | (COMPTIME)') != -1
    noCompile: bool = docstring.find("| (NOCOMP)") != -1
    lexeme = docstring[docstring.find("lex: ") + 5:].split()[0].strip()
    funcs = Primitives.get(lexeme, {"compile": None, "execute": None})
    if specialCompile:
        funcs['compile'] = func
    else:
        defaultCompile: Callable[[CompileState], None] = lambda state: state.codes.append(lexeme)
        if noCompile:
            funcs['compile'] = lambda state: None
        else:
            funcs["compile"] = defaultCompile
        funcs['execute'] = func
    Primitives[lexeme] = funcs

def compileTime(func) -> Callable:
    func.__doc__ = func.__doc__ + " | (COMPTIME)"
    return func

def noComp(func) -> Callable:
    func.__doc__ = func.__doc__ + " | (NOCOMP)"
    return func

@primitive
def plus(state: InterpretState) -> None:
    """lex: +"""
    a, b = state.dataStack.pop(), state.dataStack.pop()
    state.dataStack.append(a + b)
    state.pos += 1

@primitive
def minus(state: InterpretState) -> None:
    """lex: -"""
    a, b = state.dataStack.pop(), state.dataStack.pop()
    state.dataStack.append(b - a)
    state.pos += 1

@primitive
def star(state: InterpretState) -> None:
    """lex: *"""
    a, b = state.dataStack.pop(), state.dataStack.pop()
    state.dataStack.append(a * b)
    state.pos += 1

@primitive
def slash(state: InterpretState) -> None:
    """lex: /"""
    a, b = state.dataStack.pop(), state.dataStack.pop()
    state.dataStack.append(int(b // a))
    state.pos += 1

@primitive
def fslash(state: InterpretState) -> None:
    """lex: f/"""
    a, b = state.dataStack.pop(), state.dataStack.pop()
    state.dataStack.append(float(b) / a)
    state.pos += 1
    
@primitive
def carat(state: InterpretState) -> None:
    """lex: ^"""
    a, b = state.dataStack.pop(), state.dataStack.pop()
    state.dataStack.append(b ** a)
    state.pos += 1

@primitive
def equals(state: InterpretState) -> None:
    """lex: ="""
    a, b = state.dataStack.pop(), state.dataStack.pop()
    if a == b:
        state.dataStack.append(-1)
    else:
        state.dataStack.append(0)
    state.pos += 1

@primitive
def tilde(state: InterpretState) -> None:
    """lex: ~"""
    a = state.dataStack.pop()
    if a == 0:
        state.dataStack.append(-1)
    else:
        state.dataStack.append(0)
    state.pos += 1

@primitive
def lessthan(state: InterpretState) -> None:
    """lex: <"""
    a, b = state.dataStack.pop(), state.dataStack.pop()
    if b < a:
        state.dataStack.append(-1)
    else:
        state.dataStack.append(0)
    state.pos += 1

@primitive
def greaterthan(state: InterpretState) -> None:
    """lex: >"""
    a, b = state.dataStack.pop(), state.dataStack.pop()
    if b > a:
        state.dataStack.append(-1)
    else:
        state.dataStack.append(0)
    state.pos += 1

@primitive
def percent(state: InterpretState) -> None:
    """lex: %"""
    a, b = state.dataStack.pop(), state.dataStack.pop()
    state.dataStack.append(b % a)
    state.pos += 1

@primitive
def ampersand(state: InterpretState) -> None:
    """lex: &"""
    a, b = state.dataStack.pop(), state.dataStack.pop()
    if a == 0 or b == 0:
        state.dataStack.append(0)
    else:
        state.dataStack.append(-1)
    state.pos += 1

@primitive
@noComp
def push(state: InterpretState) -> None:
    """lex: push"""
    value = state.codes[state.pos+1]
    state.dataStack.append(value)
    state.pos += 2

@primitive
@noComp
def end(state: CompileState) -> None:
    """lex: end"""
    state.end = True

@primitive
@noComp
def call(state: InterpretState) -> None:
    """lex: call"""
    state.branchStack.append(state.pos + 2)
    state.pos = state.codes[state.pos+1]

@primitive
def dot(state: InterpretState) -> None:
    """lex: ."""
    state.stdout += f' {state.dataStack.pop()}'
    state.pos += 1

@primitive
def dots(state: InterpretState) -> None:
    """lex: .s"""
    state.stdout += f' <{len(state.dataStack)}> {" ".join([str(i) for i in state.dataStack])}'
    state.pos += 1

@primitive
def dup(state: InterpretState) -> None:
    """lex: dup"""
    a = state.dataStack.pop()
    state.dataStack.extend((a, a))
    state.pos += 1

@primitive
def drop(state: InterpretState) -> None:
    """lex: drop"""
    state.dataStack.pop()
    state.pos += 1

@primitive
def swap(state: InterpretState) -> None:
    """lex: swap"""
    state.dataStack[-1], state.dataStack[-2] = state.dataStack[-2], state.dataStack[-1]
    state.pos += 1

@primitive
def over(state: InterpretState) -> None:
    """lex: over"""
    state.dataStack.append(state.dataStack[-2])
    state.pos += 1

@primitive
@compileTime
def colon(state: CompileState) -> None:
    """lex: :"""
    word = state.tokens[state.pos + 1]
    state.words[word] = len(state.codes)
    state.pos += 1

@primitive
def semicolon(state: InterpretState) -> None:
    """lex: ;"""
    state.pos = state.branchStack.pop()

@primitive
@compileTime
def semicolon(state: CompileState) -> None:
    """lex: ;"""
    state.codes.append(';')
    state.last_return = len(state.codes)

@primitive
def prim_if(state: InterpretState) -> None:
    """lex: if"""
    if state.dataStack.pop() == 0:
        state.pos = state.codes[state.pos+1]
    else:
        state.pos += 2

@primitive
@compileTime
def prim_if(state: CompileState) -> None:
    """lex: if"""
    state.branchStack.append(len(state.codes) + 1)
    state.codes.extend(("if", None))

@primitive
def prim_then(state: InterpretState) -> None:
    """lex: then"""
    ifPos = state.branchStack.pop()
    state.codes[ifPos] = len(state.codes) + 2
    state.branchStack.append(len(state.codes) + 1)
    state.codes.extend(("else", None))

@primitive
@compileTime
def prim_then(state: CompileState) -> None:
    """lex: then"""
    elsePos = state.branchStack.pop()
    state.codes[elsePos] = len(state.codes)

@primitive
def prim_else(state:InterpretState) -> None:
    """lex: else"""
    state.pos = state.codes[state.pos+1]

@primitive
@compileTime
def prim_else(state:CompileState) -> None:
    """lex: else"""
    ifPos = state.branchStack.pop()
    state.codes[ifPos] = len(state.codes) + 2
    state.branchStack.append(len(state.codes) + 1)
    state.codes.extend(("else", None))

@primitive
def do(state: InterpretState) -> None:
    """lex: do"""
    a,b = state.dataStack.pop(), state.dataStack.pop()
    state.branchStack.extend((b, a))
    state.pos += 1

@primitive
@compileTime
def do(state: CompileState) -> None:
    """lex: do"""
    state.branchStack.append(len(state.codes) + 1)
    state.codes.append("do")

@primitive
def loop(state:InterpretState) -> None:
    """lex: loop"""
    a,b = state.branchStack.pop(), state.branchStack.pop()
    a += 1
    if a < b:
        state.branchStack.extend((b,a))
        state.pos = state.codes[state.pos+1]
    else:
        state.pos += 2

@primitive
@compileTime
def loop(state:CompileState) -> None:
    """lex: loop"""
    doPos = state.branchStack.pop()
    state.codes.extend(("loop", doPos))

@primitive
def i(state:InterpretState) -> None:
    """lex: i"""
    state.dataStack.append(state.branchStack[-1])
    state.pos += 1

@primitive
@compileTime
def var(state: CompileState) -> None:
    """lex: var"""
    varName = state.tokens[state.pos+1]
    if varName not in state.variables:
        state.variables[varName] = len(state.variables)
    state.pos += 1

@primitive
def bang(state: InterpretState) -> None:
    """lex: !"""
    a, b = state.dataStack.pop(), state.dataStack.pop()
    state.variables[a] = b
    state.pos += 1

@primitive
def at(state: InterpretState) -> None:
    """lex: @"""
    a = state.dataStack.pop()
    state.dataStack.append(state.variables[a])
    state.pos += 1

@primitive
def emit(state: InterpretState) -> None:
    """lex: emit"""
    state.stdout += chr(state.dataStack.pop())
    state.pos += 1

@primitive
@compileTime
def char(state: CompileState) -> None:
    """lex: char"""
    charCode = ord(state.tokens[state.pos+1])
    state.codes.extend(("push", charCode))
    state.pos += 1


@primitive
def dotquote(state: InterpretState) -> None:
    """lex: .\""""
    state.stdout += state.codes[state.pos + 1]
    state.pos += 2

@primitive
@compileTime
def dotquote(state: CompileState) -> None:
    """lex: .\""""
    state.pos += 1
    string = ''
    currentCode = state.tokens[state.pos]
    while currentCode[-1] != '"':
        string += currentCode + ' '
        state.pos += 1
        currentCode = state.tokens[state.pos]
    string += currentCode[:-1]
    state.codes.extend(('."', string))
