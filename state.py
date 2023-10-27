from dataclasses import dataclass, field

@dataclass
class CompileState:
    tokens: list = field(default_factory=list)
    codes: list = field(default_factory=list)
    branchStack: list = field(default_factory=list)
    variables: dict = field(default_factory=dict)
    words: dict = field(default_factory=dict)
    pos: int = 0 
    last_return: int = 0
    end: bool = False

@dataclass
class InterpretState:
    codes: list = field(default_factory=list)
    dataStack: list = field(default_factory=list)
    branchStack: list   = field(default_factory=list)
    variables: list = field(default_factory=list)
    pos: int = 0
    end: bool = False
    stdout: str = field(default_factory=str)
