from state import InterpretState, CompileState
from primitives import Primitives
from helpers import isInt, isFloat

class Interpreter:
    def __init__(self):
        self.compileState = CompileState()
        self.interpretState = InterpretState()
    def run(self, tokens) -> str: 
        self.interpretState.stdout = ''
        self.compile(self.compileState, tokens)
        return self.interpretState.stdout
    def compile(self, state: CompileState, tokens):
        state.tokens.extend(tokens)
        if state.codes:
            state.codes.pop()
        state.end = False
        while not state.end:
            if state.pos == len(state.tokens):
                state.codes.append('end')
                state.end = True
                break
            token = state.tokens[state.pos]
            if isInt(token):
                state.codes.extend(('push', int(token)))
            elif isFloat(token):
                state.codes.extend(('push', float(token)))
            elif token in Primitives:
                Primitives[token]['compile'](state)
            elif token in state.variables:
                state.codes.extend(('push', state.variables[token]))
            elif token in state.words:
                state.codes.extend(('call', state.words[token]))
            else:
                self.interpretState.stdout += '\nError: Unknown word: ' + token + '\n'
            state.pos += 1
        self.interpret(self.interpretState, state.codes, len(state.variables), state.last_return)
    def interpret(self, state: InterpretState, codes, var_count, start):
        state.codes = codes
        state.variables.extend([0] * (var_count - len(state.variables)))
        state.pos = max(start, state.pos)
        state.end = False

        while not state.end:
            code = state.codes[state.pos]
            try:
                Primitives[code]['execute'](state)
            except IndexError:
                state.stdout += '\nError: Pop on empty stack\n'
                state.pos += 1
