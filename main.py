import sys
import re

#O sintático/parser está sempre olhando para o próximo token, e o léxico está sempre olhando para o token atual
#O tokenizer sempre começa no primeiro token, e o parser sempre começa no segundo token

alpha = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_1234567890'
reserved = ['println', 'if', 'else', 'end', 'while', 'readline', 'break', 'continue', 'Int', 'String']

header = """; constantes
SYS_EXIT equ 1
SYS_READ equ 3
SYS_WRITE equ 4
STDIN equ 0
STDOUT equ 1
True equ 1
False equ 0

segment .data

segment .bss  ; variaveis
  res RESB 1

section .text
  global _start

print:  ; subrotina print

  PUSH EBP ; guarda o base pointer
  MOV EBP, ESP ; estabelece um novo base pointer

  MOV EAX, [EBP+8] ; 1 argumento antes do RET e EBP
  XOR ESI, ESI

print_dec: ; empilha todos os digitos
  MOV EDX, 0
  MOV EBX, 0x000A
  DIV EBX
  ADD EDX, '0'
  PUSH EDX
  INC ESI ; contador de digitos
  CMP EAX, 0
  JZ print_next ; quando acabar pula
  JMP print_dec

print_next:
  CMP ESI, 0
  JZ print_exit ; quando acabar de imprimir
  DEC ESI

  MOV EAX, SYS_WRITE
  MOV EBX, STDOUT

  POP ECX
  MOV [res], ECX
  MOV ECX, res

  MOV EDX, 1
  INT 0x80
  JMP print_next

print_exit:
  POP EBP
  RET

; subrotinas if/while
binop_je:
  JE binop_true
  JMP binop_false

binop_jg:
  JG binop_true
  JMP binop_false

binop_jl:
  JL binop_true
  JMP binop_false

binop_false:
  MOV EBX, False
  JMP binop_exit
binop_true:
  MOV EBX, True
binop_exit:
  RET

_start:

  PUSH EBP ; guarda o base pointer
  MOV EBP, ESP ; estabelece um novo base pointer

  ; codigo gerado pelo compilador
"""

footer = """  ; interrupcao de saida
  POP EBP
  MOV EAX, 1
  INT 0x80"""

class Token:
    def __init__(self, type, value):
        self.type = type
        self.value = value

class Tokenizer:
    def __init__(self, source):
        self.source = source
        self.position = 0
        self.next = None

    def selectNext(self):
        if self.position < len(self.source):
            while(self.position < len(self.source) and self.source[self.position] == ' ' and (self.position + 1 < len(self.source))):
                if self.source[self.position-1].isdigit() and self.source[self.position+1].isdigit():
                    raise Exception("Símbolo inválido")
                self.position += 1
            if self.source[self.position] == '+':
                self.next = Token('PLUS', self.source[self.position])
                self.position += 1
            elif self.source[self.position] == '-':
                self.next = Token('MINUS', self.source[self.position])
                self.position += 1
            elif self.source[self.position] == '*':
                self.next = Token('MULT', self.source[self.position])
                self.position += 1
            elif self.source[self.position] == '/':
                self.next = Token('DIV', self.source[self.position])
                self.position += 1
            elif self.source[self.position] == '(':
                self.next = Token('LPAREN', self.source[self.position])
                self.position += 1
            elif self.source[self.position] == ')':
                self.next = Token('RPAREN', self.source[self.position])
                self.position += 1
            elif self.source[self.position].isdigit():
                i = self.position
                a = ''
                while i < len(self.source) and self.source[i].isdigit():
                    a += self.source[i]
                    i += 1
                self.position = i
                self.next = Token('INT', a)
            elif self.source[self.position] == '=':
                if self.source[self.position+1] == '=':
                    self.next = Token('EQUALS_BOOL', self.source[self.position] + self.source[self.position+1])
                    self.position += 2
                else:
                    self.next = Token('EQUALS', self.source[self.position])
                    self.position += 1
            elif self.source[self.position] in alpha:
                i = self.position
                a = ''
                while i < len(self.source) and self.source[i] in alpha:
                    a += self.source[i]
                    i += 1
                self.position = i
                self.next = Token('WORD', a)
            elif self.source[self.position] == '\n':
                #i = self.position
                #while i < len(self.source) and self.source[i] == '\n' or self.source[i] == ' ':
                #    i += 1                
                #self.next = Token('NEWLINE', self.source[i-1])
                #self.position = i-1
                self.next = Token('NEWLINE', self.source[self.position])
                self.position += 1
            elif self.source[self.position] == '>':
                self.next = Token('GREATER', self.source[self.position])
                self.position += 1
            elif self.source[self.position] == '<':
                self.next = Token('LESS', self.source[self.position])
                self.position += 1
            elif self.source[self.position] == '!':
                self.next = Token('NOT', self.source[self.position])
                self.position += 1
            elif self.source[self.position] == '&':
                if self.source[self.position+1] == '&':
                    self.next = Token('AND', self.source[self.position] + self.source[self.position+1])
                    self.position += 2
                else:
                    raise Exception("Símbolo inválido")
            elif self.source[self.position] == '|':
                if self.source[self.position+1] == '|':
                    self.next = Token('OR', self.source[self.position] + self.source[self.position+1])
                    self.position += 2
                else:
                    raise Exception("Símbolo inválido")
            elif self.source[self.position] == ':':
                if self.source[self.position+1] == ':':
                    self.next = Token('DECLARE', self.source[self.position] + self.source[self.position+1])
                    self.position += 2
            elif self.source[self.position] == '"':
                self.next = Token('QUOTE', self.source[self.position])
                self.position += 1
            elif self.source[self.position] == '.':
                self.next = Token('CONCAT', self.source[self.position])
                self.position += 1
            elif self.source[self.position] != ' ':
                raise Exception("Símbolo inválido")
            elif self.source[self.position] == ' ':
                self.next = Token('EOF', '')
        elif len(self.source) == 0:
            raise Exception("Entrada vazia")
        else:
            self.next = Token('EOF', '')
        #print(self.next.type, self.next.value)

class Parser:
    @staticmethod
    def parseTerm(tokenizer):
        a = Parser.parseFactor(tokenizer)
        tokenizer.selectNext()
        while tokenizer.next.type == "MULT" or tokenizer.next.type == "DIV" or tokenizer.next.type == "AND":
            if tokenizer.next.type == "MULT":
                tokenizer.selectNext()
                b = Parser.parseFactor(tokenizer)
                a = BinOp("MULT", [a, b])
            elif tokenizer.next.type == "DIV":
                tokenizer.selectNext()
                b = Parser.parseFactor(tokenizer)
                a = BinOp("DIV", [a, b])
            elif tokenizer.next.type == "AND":
                tokenizer.selectNext()
                b = Parser.parseFactor(tokenizer)
                a = BinOp("AND", [a, b])
            tokenizer.selectNext()
        return a
        
    @staticmethod
    def parseExpression(tokenizer):
        a = Parser.parseTerm(tokenizer)
        while tokenizer.next.type == "PLUS" or tokenizer.next.type == "MINUS" or tokenizer.next.type == "OR" or tokenizer.next.type == "CONCAT":
            if tokenizer.next.type == "PLUS":
                tokenizer.selectNext()
                b = Parser.parseTerm(tokenizer)
                a = BinOp("PLUS", [a, b])
            elif tokenizer.next.type == "MINUS":
                tokenizer.selectNext()
                b = Parser.parseTerm(tokenizer)
                a = BinOp("MINUS", [a, b])
            elif tokenizer.next.type == "OR":
                tokenizer.selectNext()
                b = Parser.parseTerm(tokenizer)
                a = BinOp("OR", [a, b])
            elif tokenizer.next.type == "CONCAT":
                tokenizer.selectNext()
                b = Parser.parseTerm(tokenizer)
                a = BinOp("CONCAT", [a, b])
        return a
    
    @staticmethod
    def parseRelExpression(tokenizer):
        a = Parser.parseExpression(tokenizer)
        while tokenizer.next.type == "EQUALS_BOOL" or tokenizer.next.type == "GREATER" or tokenizer.next.type == "LESS":
            if tokenizer.next.type == "EQUALS_BOOL":
                tokenizer.selectNext()
                b = Parser.parseExpression(tokenizer)
                a = BinOp("EQUALS_BOOL", [a, b])
            elif tokenizer.next.type == "GREATER":
                tokenizer.selectNext()
                b = Parser.parseExpression(tokenizer)
                a = BinOp("GREATER", [a, b])
            elif tokenizer.next.type == "LESS":
                tokenizer.selectNext()
                b = Parser.parseExpression(tokenizer)
                a = BinOp("LESS", [a, b])
        return a
    
    @staticmethod
    def parseFactor(tokenizer):
        if tokenizer.next.type == "INT":
            n = IntVal(tokenizer.next.value)
            return n
        elif tokenizer.next.type == "PLUS" or tokenizer.next.type == "MINUS" or tokenizer.next.type == "NOT":
            if tokenizer.next.type == "PLUS":
                tokenizer.selectNext()
                n = Parser.parseFactor(tokenizer)
                a = UnOp("PLUS", [n])
                return a
            elif tokenizer.next.type == "MINUS":
                tokenizer.selectNext()
                n = Parser.parseFactor(tokenizer)
                a = UnOp("MINUS", [n])
                return a
            elif tokenizer.next.type == "NOT":
                tokenizer.selectNext()
                n = Parser.parseFactor(tokenizer)
                a = UnOp("NOT", [n])
                return a
        elif tokenizer.next.type == "LPAREN":
            tokenizer.selectNext()
            n = Parser.parseRelExpression(tokenizer)
            if tokenizer.next.type == "RPAREN":
                return n
            else:
                raise Exception("Símbolo inválido")
        elif tokenizer.next.type == "WORD":
            if tokenizer.next.value in reserved:
                if tokenizer.next.value != "readline":
                    raise Exception("Símbolo inválido")
                else:
                    tokenizer.selectNext()
                    if tokenizer.next.type == "LPAREN":
                        tokenizer.selectNext()
                        if tokenizer.next.type == "RPAREN":
                            return ReadLineOp()
                        else:
                            raise Exception("Símbolo inválido")
                    else:
                        raise Exception("Símbolo inválido")
            n = IdentifierOp(tokenizer.next.value)
            return n
        elif tokenizer.next.type == "QUOTE":
            tokenizer.selectNext()
            n = StrVal(tokenizer.next.value)
            tokenizer.selectNext()
            if tokenizer.next.type == "QUOTE":
                return n
            else:
                raise Exception("Símbolo inválido")
        else:
            raise Exception("Símbolo inválido")
        
    @staticmethod
    def parseBlock(tokenizer):
        children = []
        while tokenizer.next.type != "EOF":
            if tokenizer.next.value == "end" or tokenizer.next.value == "else":
                break
            children.append(Parser.parseStatement(tokenizer))
            tokenizer.selectNext()
        return BlockOp(children)

    @staticmethod
    def parseStatement(tokenizer):
        if tokenizer.next.type == "WORD":
            if tokenizer.next.value in reserved:
                if tokenizer.next.value == "println":
                    tokenizer.selectNext()
                    if tokenizer.next.type == "LPAREN":
                        tokenizer.selectNext()
                        a = Parser.parseRelExpression(tokenizer)
                        if tokenizer.next.type == "RPAREN":
                            tokenizer.selectNext()
                            if tokenizer.next.type == "NEWLINE":
                                return PrintOp(a)
                            else:
                                raise Exception("Símbolo inválido")
                        else:
                            raise Exception("Símbolo inválido")
                    else:
                        raise Exception("Símbolo inválido")
                elif tokenizer.next.value == "while":
                    tokenizer.selectNext()
                    a = Parser.parseRelExpression(tokenizer)
                    if tokenizer.next.type == "NEWLINE":
                        tokenizer.selectNext()
                        b = Parser.parseBlock(tokenizer)
                        if tokenizer.next.type == "WORD":
                            if tokenizer.next.value == "end":
                                return WhileOp([a, b])
                            else:
                                raise Exception("Símbolo inválido")
                        else:
                            raise Exception("Símbolo inválido")
                elif tokenizer.next.value == "if":
                    tokenizer.selectNext()
                    a = Parser.parseRelExpression(tokenizer)
                    if tokenizer.next.type == "NEWLINE":
                        tokenizer.selectNext()
                        b = Parser.parseBlock(tokenizer)
                        if tokenizer.next.type == "WORD":
                            if tokenizer.next.value == "end":
                                return IfOp([a, b])
                            elif tokenizer.next.value == "else":
                                tokenizer.selectNext()
                                c = Parser.parseBlock(tokenizer)
                                if tokenizer.next.type == "WORD":
                                    if tokenizer.next.value == "end":
                                        return IfOp([a, b, c])
                                    else:
                                        raise Exception("Símbolo inválido")
                                else:
                                    raise Exception("Símbolo inválido")
                            else:
                                raise Exception("Símbolo inválido")
                        else:
                            raise Exception("Símbolo inválido")
            else:
                i = IdentifierOp(tokenizer.next.value)
                #i = tokenizer.next.value
                tokenizer.selectNext()
                if tokenizer.next.type == "EQUALS":
                    tokenizer.selectNext()
                    a = Parser.parseRelExpression(tokenizer)
                    return AssignOp([i, a])
                elif tokenizer.next.type == "DECLARE":
                    tokenizer.selectNext()
                    if tokenizer.next.value == "Int":
                        tokenizer.selectNext()
                        if tokenizer.next.type == "EQUALS":
                            tokenizer.selectNext()
                            a = Parser.parseRelExpression(tokenizer)
                            return VarDeclOp("Int",[i, a])
                        return VarDeclOp("Int",[i])
                    elif tokenizer.next.value == "String":
                        tokenizer.selectNext()
                        if tokenizer.next.type == "EQUALS":
                            tokenizer.selectNext()
                            a = Parser.parseRelExpression(tokenizer)
                            return VarDeclOp("String",[i, a])
                        return VarDeclOp("String",[i])
                else: 
                    raise Exception("Símbolo inválido")
        elif tokenizer.next.type == "NEWLINE":
            return NoOp()
        else:
            raise Exception("Símbolo inválido")

    @staticmethod
    def run(code):
        c = PrePro.filter(code)
        tokenizer = Tokenizer(c)
        tokenizer.selectNext()
        a = Parser.parseBlock(tokenizer)
        if tokenizer.next.type == "EOF":
            return a
        else:
            raise Exception("Fim de arquivo inválido")

class PrePro:
    @staticmethod
    def filter(code):
        c = re.sub(r'#.*\n', '', code).replace("\s", "")
        #c = re.sub(r'#.*$', '', code).replace("\n", "").replace("\s", "")
        return c
    
class Node:
    id = 0
    def __init__(self, value, children):
        self.value = value
        self.children = children
        self.id = Node.new_id()
    
    def evaluate(self, code):
        pass

    @staticmethod
    def new_id():
        Node.id += 1
        return Node.id

class BinOp(Node):
    def __init__(self, value, children):
        self.value = value
        self.children = children
        self.id = Node.new_id()
    
    def evaluate(self, code):
        l = self.children[0].evaluate(code)
        code.add(f"PUSH EBX")
        r = self.children[1].evaluate(code)
        code.add(f"POP EAX")
        if self.value == "PLUS":
            if l[0] == r[0] and l[0] == "Int":
                code.add(f"ADD EAX, EBX")
                code.add(f"MOV EBX, EAX")
                return ("Int", l[1] + r[1])
            else:
                raise Exception("Tipo Inválido")
        elif self.value == "MINUS":
            if l[0] == r[0] and l[0] == "Int":
                code.add(f"SUB EAX, EBX")
                code.add(f"MOV EBX, EAX")
                return ("Int", l[1] - r[1])
            else:
                raise Exception("Tipo Inválido")
        elif self.value == "MULT":
            if l[0] == r[0] and l[0] == "Int":
                code.add(f"IMUL EAX, EBX")
                code.add(f"MOV EBX, EAX")
                return ("Int", l[1] * r[1])
            else:
                raise Exception("Tipo Inválido")
        elif self.value == "DIV":
            if l[0] == r[0] and l[0] == "Int":
                code.add(f"IDIV EAX, EBX")
                code.add(f"MOV EBX, EAX")
                return ("Int", l[1] // r[1])
            else:
                raise Exception("Tipo Inválido")
        elif self.value == "EQUALS_BOOL":
            code.add(f"CMP EAX, EBX")
            code.add(f"CALL binop_je")
            if l[1] == r[1]:
                return ("Int", 1)
            else:
                return ("Int", 0)
        elif self.value == "GREATER":
            code.add(f"CMP EAX, EBX")
            code.add(f"CALL binop_jg")
            if l[0] == r[0] and l[0] == "Int":
                if l[1] > r[1]:
                    return ("Int", 1)
                else:
                    return ("Int", 0)
            elif l[0] == r[0] and l[0] == "String":
                if l[1] > r[1]:
                    return ("String", 1)
                else:
                    return ("String", 0)
            else:
                raise Exception("Tipo Inválido")
        elif self.value == "LESS":
            code.add(f"CMP EAX, EBX")
            code.add(f"CALL binop_jl")
            if l[0] == r[0] and l[0] == "Int":
                if l[1] < r[1]:
                    return ("Int", 1)
                else:
                    return ("Int", 0)
            elif l[0] == r[0] and l[0] == "String":
                if l[1] < r[1]:
                    return ("String", 1)
                else:
                    return ("String", 0)
            else:
                raise Exception("Tipo Inválido")
        elif self.value == "AND":
            code.add(f"AND EAX, EBX")
            code.add(f"MOV EBX, EAX")
            if l[0] == r[0] and l[0] == "Int":
                return ("Int", l and r)
            elif l[0] == r[0] and l[0] == "String":
                return ("String", l and r)
            else:
                raise Exception("Tipo Inválido")
        elif self.value == "OR":
            code.add(f"OR EAX, EBX")
            code.add(f"MOV EBX, EAX")
            if l[0] == r[0] and l[0] == "Int":
                if l[1] or r[1]:
                    return ("Int", 1)
                else:
                    return ("Int", 0)
            elif l[0] == r[0] and l[0] == "String":
                if l[1] or r[1]:
                    return ("String", 1)
                else:
                    return ("String", 0)
            else:
                raise Exception("Tipo Inválido")
        elif self.value == "CONCAT":
            return ("String", str(l[1]) + str(r[1]))

class UnOp(Node):
    def __init__(self, value, children):
        self.value = value
        self.children = children
        self.id = Node.new_id()
    
    def evaluate(self, code):
        if self.value == "PLUS":
            if self.children[0].evaluate()[0] == "Int":
                return ["Int", self.children[0].evaluate()[1]]
            else:
                raise Exception("Tipo Inválido")
        elif self.value == "MINUS":
            if self.children[0].evaluate()[0] == "Int":
                return ["Int", -self.children[0].evaluate()[1]]
            else:
                raise Exception("Tipo Inválido")
        elif self.value == "NOT":
            if self.children[0].evaluate()[0] == "Int":
                if self.children[0].evaluate()[1] == 0:
                    return ["Int", 1]
                else:
                    return ["Int", 0]
            else:
                raise Exception("Tipo Inválido")
        
class IntVal(Node):
    def __init__(self, value):
        self.value = value
        self.id = Node.new_id()
    
    def evaluate(self, code):
        code.add(f"MOV EBX, {self.value}")
        return ["Int", int(self.value)]
    
class StrVal(Node):
    def __init__(self, value):
        self.value = value
        self.id = Node.new_id()
    
    def evaluate(self, code):
        return ["String", str(self.value)]
    
class NoOp(Node):
    def __init__(self):
        self.id = Node.new_id()
        pass
    
    def evaluate(self, code):
        pass

class PrintOp(Node):
    def __init__(self, children):
        self.children = children
        self.id = Node.new_id()
    
    def evaluate(self, code):
        p = self.children.evaluate(code)[1]
        code.add(f"PUSH EBX")
        code.add(f"CALL print")
        code.add(f"POP EBX")
        print(p)

class AssignOp(Node):
    def __init__(self, children):
        self.children = children
        self.id = Node.new_id()
    
    def evaluate(self, code):
        eval = self.children[1].evaluate(code)
        code.add(f"MOV [EBP - {SymbolTable.getter(self.children[0].value)[2]}], EBX")
        SymbolTable.setter(self.children[0].value, eval)

class BlockOp(Node):
    def __init__(self, children):
        self.children = children
        self.id = Node.new_id()
    
    def evaluate(self, code):
        for child in self.children:
            child.evaluate(code)

class IdentifierOp(Node):
    def __init__(self, value):
        self.value = value
        self.id = Node.new_id()
    
    def evaluate(self, code):
        code.add(f"MOV EBX, [EBP - {SymbolTable.getter(self.value)[2]}]")
        return SymbolTable.getter(self.value)

class ReadLineOp(Node):
    def __init__(self):
        self.id = Node.new_id()
        pass
    
    def evaluate(self, code):
        return ["Int", int(input())]

class WhileOp(Node):
    def __init__(self, children):
        self.children = children
        self.id = Node.new_id()
    
    def evaluate(self, code):
        code.add(f"LOOP_{self.id}:")
        self.children[0].evaluate(code)
        code.add(f"CMP EBX, False")
        code.add(f"JE EXIT_{self.id}")
        self.children[1].evaluate(code)
        code.add(f"JMP LOOP_{self.id}")
        code.add(f"EXIT_{self.id}:")

        """ while self.children[0].evaluate()[1] != 0:
            self.children[1].evaluate() """

class IfOp(Node):
    def __init__(self, children):
        self.children = children
        self.id = Node.new_id()
    
    def evaluate(self, code):
        code.add(f"IF_{self.id}:")
        self.children[0].evaluate(code)
        code.add(f"CMP EBX, False")
        code.add(f"JE ELSE_{self.id}")
        self.children[1].evaluate(code)
        code.add(f"JMP END_IF_{self.id}")
        code.add(f"ELSE_{self.id}:")

        if len(self.children) == 3:
            self.children[2].evaluate(code)
        """ if self.children[0].evaluate()[1]:
            self.children[1].evaluate()
        else:
            if len(self.children) == 3:
                self.children[2].evaluate() """

class VarDeclOp(Node):
    def __init__(self, value, children):
        self.children = children
        self.value = value
        self.id = Node.new_id()
    
    def evaluate(self, code):
        if len(self.children) == 1:
            if self.value == "Int":
                code.add("PUSH DWORD 0")
                SymbolTable.create(self.children[0].value, [self.value, 0])
            elif self.value == "String":
                code.add("PUSH DWORD 0")
                SymbolTable.create(self.children[0].value, [self.value, ""])
            else:
                raise Exception("Tipo inválido")
        else:
            if self.value == "Int" and self.children[1].evaluate()[0] == "Int":
                code.add("PUSH DWORD 0")
                SymbolTable.create(self.children[0].value, [self.value, self.children[1].evaluate()[1]])
            elif self.value == "String" and self.children[1].evaluate()[0] == "String":
                code.add("PUSH DWORD 0")
                SymbolTable.create(self.children[0].value, [self.value, self.children[1].evaluate()[1]])
            else:
                raise Exception("Tipo inválido")

class SymbolTable:
    table = {}
    address = 0
    
    def setter(name, value):
        if SymbolTable.table[name][0] == value[0]:
            SymbolTable.table[name][1] = value[1]
        else:
            raise Exception("Tipo inválido")
    
    def getter(name):
        return SymbolTable.table[name]
    
    def create(name, value):
        if name in SymbolTable.table:
            raise Exception("Variável já declarada")
        SymbolTable.address += 4
        SymbolTable.table[name] = [value[0], value[1], SymbolTable.address]

class Asm:
    def __init__(self, filename):
        self.code = ""
        self.filename = filename[:-3] + ".asm"
    
    def add(self, code):
        self.code += code + "\n"

    def save(self):
        with open(self.filename, 'w') as f:
            f.write(header + self.code + footer)

def read_file(filename):
    with open(filename, 'r') as f:
        return f.read()

def main():
    name = sys.argv[1]
    code = read_file(sys.argv[1])
    #code = read_file("test.jl")
    #name = "test.jl"
    asm_code = Asm(name)
    Parser.run(code).evaluate(asm_code)
    asm_code.save()

main()