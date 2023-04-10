import sys
import re

#O sintático/parser está sempre olhando para o próximo token, e o léxico está sempre olhando para o token atual
#O tokenizer sempre começa no primeiro token, e o parser sempre começa no segundo token

alpha = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_1234567890'
reserved = ['println', 'if', 'else', 'while', 'read', 'break', 'continue']

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
        while tokenizer.next.type == "PLUS" or tokenizer.next.type == "MINUS" or tokenizer.next.type == "OR":
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
                if tokenizer.next.value != "read":
                    raise Exception("Símbolo inválido")
                else:
                    tokenizer.selectNext()
                    if tokenizer.next.type == "LPAREN":
                        tokenizer.selectNext()
                        if tokenizer.next.type == "RPAREN":
                            return ReadOp()
                        else:
                            raise Exception("Símbolo inválido")
                    else:
                        raise Exception("Símbolo inválido")
            n = IdentifierOp(tokenizer.next.value)
            return n
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
                            return PrintOp(a)
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
                    a = Parser.parseExpression(tokenizer)
                    return AssignOp([i, a])
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
        c = re.sub(r'#.*\n', '', code,  flags=re.MULTILINE).replace("\s", "")
        #c = re.sub(r'#.*$', '', code).replace("\n", "").replace("\s", "")
        return c
    
class Node:
    def __init__(self, value, children):
        self.value = value
        self.children = children
    
    def evaluate(self):
        pass

class BinOp(Node):
    def __init__(self, value, children):
        self.value = value
        self.children = children
    
    def evaluate(self):
        if self.value == "PLUS":
            return self.children[0].evaluate() + self.children[1].evaluate()
        elif self.value == "MINUS":
            return self.children[0].evaluate() - self.children[1].evaluate()
        elif self.value == "MULT":
            return self.children[0].evaluate() * self.children[1].evaluate()
        elif self.value == "DIV":
            return self.children[0].evaluate() // self.children[1].evaluate()
        elif self.value == "EQUALS_BOOL":
            return self.children[0].evaluate() == self.children[1].evaluate()
        elif self.value == "GREATER":
            return self.children[0].evaluate() > self.children[1].evaluate()
        elif self.value == "LESS":
            return self.children[0].evaluate() < self.children[1].evaluate()
        elif self.value == "AND":
            return self.children[0].evaluate() and self.children[1].evaluate()
        elif self.value == "OR":
            return self.children[0].evaluate() or self.children[1].evaluate()

class UnOp(Node):
    def __init__(self, value, children):
        self.value = value
        self.children = children
    
    def evaluate(self):
        if self.value == "PLUS":
            return self.children[0].evaluate()
        elif self.value == "MINUS":
            return -self.children[0].evaluate()
        elif self.value == "NOT":
            return not self.children[0].evaluate()
        
class IntVal(Node):
    def __init__(self, value):
        self.value = value
    
    def evaluate(self):
        return int(self.value)
    
class NoOp(Node):
    def __init__(self):
        pass
    
    def evaluate(self):
        pass

class PrintOp(Node):
    def __init__(self, children):
        self.children = children
    
    def evaluate(self):
        print(self.children.evaluate())

class AssignOp(Node):
    def __init__(self, children):
        self.children = children
    
    def evaluate(self):
        SymbolTable.setter(self.children[0].value, self.children[1].evaluate())

class BlockOp(Node):
    def __init__(self, children):
        self.children = children
    
    def evaluate(self):
        for child in self.children:
            child.evaluate()

class IdentifierOp(Node):
    def __init__(self, value):
        self.value = value
    
    def evaluate(self):
        return SymbolTable.getter(self.value)

class ReadOp(Node):
    def __init__(self):
        pass
    
    def evaluate(self):
        return int(input())

class WhileOp(Node):
    def __init__(self, children):
        self.children = children
    
    def evaluate(self):
        while self.children[0].evaluate():
            self.children[1].evaluate()

class IfOp(Node):
    def __init__(self, children):
        self.children = children
    
    def evaluate(self):
        if self.children[0].evaluate():
            self.children[1].evaluate()
        else:
            if len(self.children) == 3:
                self.children[2].evaluate()

class SymbolTable:
    table = {}
    
    def setter(name, value):
        SymbolTable.table[name] = value
    
    def getter(name):
        return SymbolTable.table[name]

def read_file(filename):
    with open(filename, 'r') as f:
        return f.read()

def main():
    #code = read_file(sys.argv[1])
    code = read_file("test.txt")
    Parser.run(code).evaluate()

main()