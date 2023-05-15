import sys
import re

#O sintático/parser está sempre olhando para o próximo token, e o léxico está sempre olhando para o token atual
#O tokenizer sempre começa no primeiro token, e o parser sempre começa no segundo token

alpha = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_1234567890'
reserved = ['println', 'if', 'else', 'end', 'while', 'readline', 'break', 'continue', 'Int', 'String', 'return', 'function']

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
            elif self.source[self.position] == ',':
                self.next = Token('COMMA', self.source[self.position])
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
        #tokenizer.selectNext()
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
            else:
                f = tokenizer.next.value
                c = []
                tokenizer.selectNext()	
                if tokenizer.next.type == "LPAREN":
                    tokenizer.selectNext()
                    if tokenizer.next.type != "RPAREN":
                        n = Parser.parseRelExpression(tokenizer)
                        c.append(n)
                        while tokenizer.next.type == "COMMA":
                            tokenizer.selectNext()
                            n = Parser.parseRelExpression(tokenizer)
                            c.append(n)
                            tokenizer.selectNext()
                        if tokenizer.next.type == "RPAREN":
                            tokenizer.selectNext()
                            return FuncCallOp(f, c)
                        else:
                            raise Exception("Símbolo inválido")
                    elif tokenizer.next.type == "RPAREN":
                        return FuncCallOp(f, c)
                    else:
                        raise Exception("Símbolo inválido")
            n = IdentifierOp(f)
            return n
        elif tokenizer.next.type == "QUOTE":
            tokenizer.selectNext()
            n = StrVal(tokenizer.next.value)
            tokenizer.selectNext()
            if tokenizer.next.type == "QUOTE":
                return n
            else:
                raise Exception("Símbolo inválido")
        elif tokenizer.next.type == "WORD":
            pass
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
                elif tokenizer.next.value == "function":
                    c = []
                    tokenizer.selectNext()
                    if tokenizer.next.type == "WORD":
                        if tokenizer.next.value in reserved:
                            raise Exception("Símbolo inválido")
                        else:
                            i = IdentifierOp(tokenizer.next.value)
                            tokenizer.selectNext()
                            if tokenizer.next.type == "LPAREN":
                                tokenizer.selectNext()
                                if tokenizer.next.type != "RPAREN":
                                    a = IdentifierOp(tokenizer.next.value)
                                    tokenizer.selectNext()
                                    if tokenizer.next.type == "DECLARE":
                                        tokenizer.selectNext()
                                        if tokenizer.next.value == "Int":
                                            c.append(VarDeclOp("Int",[a]))
                                        elif tokenizer.next.value == "String":
                                            c.append(VarDeclOp("String",[a]))
                                        tokenizer.selectNext()
                                        while tokenizer.next.type == "COMMA":
                                            tokenizer.selectNext()
                                            a = IdentifierOp(tokenizer.next.value)
                                            tokenizer.selectNext()
                                            if tokenizer.next.type == "DECLARE":
                                                tokenizer.selectNext()
                                                if tokenizer.next.value == "Int":
                                                    c.append(VarDeclOp("Int",[a]))
                                                elif tokenizer.next.value == "String":
                                                    c.append(VarDeclOp("String",[a]))
                                                else:
                                                    raise Exception("Símbolo inválido")
                                            tokenizer.selectNext()
                                        if tokenizer.next.type == "RPAREN":
                                            tokenizer.selectNext()
                                            if tokenizer.next.type == "DECLARE":
                                                tokenizer.selectNext()
                                                if tokenizer.next.value == "Int":
                                                    b = Parser.parseBlock(tokenizer)
                                                    return FuncDecOp("Int",[i, c, b])
                                                elif tokenizer.next.value == "String":
                                                    b = Parser.parseBlock(tokenizer)
                                                    return FuncDecOp("String",[i, c, b])
                                                else:
                                                    raise Exception("Símbolo inválido")
                                            else:
                                                raise Exception("Símbolo inválido")
                                    else:
                                        raise Exception("Símbolo inválido")
                                elif tokenizer.next.type == "RPAREN":
                                    tokenizer.selectNext()
                                    if tokenizer.next.type == "DECLARE":
                                        tokenizer.selectNext()
                                        if tokenizer.next.value == "Int":
                                            return FuncDecOp("Int",[i, c])
                                        elif tokenizer.next.value == "String":
                                            return FuncDecOp("String",[i, c])
                                        else:
                                            raise Exception("Símbolo inválido")
                                    else:
                                        raise Exception("Símbolo inválido")
                elif tokenizer.next.value == "return":
                    tokenizer.selectNext()
                    a = Parser.parseRelExpression(tokenizer)
                    return ReturnOp(a)

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
    def __init__(self, value, children):
        self.value = value
        self.children = children
    
    def evaluate(self, symbol_table):
        pass

class BinOp(Node):
    def __init__(self, value, children):
        self.value = value
        self.children = children
    
    def evaluate(self, symbol_table):
        l = self.children[0].evaluate(symbol_table)
        r = self.children[1].evaluate(symbol_table)
        if self.value == "PLUS":
            if l[0] == r[0] and l[0] == "Int":
                return ("Int", l[1] + r[1])
            else:
                raise Exception("Tipo Inválido")
        elif self.value == "MINUS":
            if l[0] == r[0] and l[0] == "Int":
                return ("Int", l[1] - r[1])
            else:
                raise Exception("Tipo Inválido")
        elif self.value == "MULT":
            if l[0] == r[0] and l[0] == "Int":
                return ("Int", l[1] * r[1])
            else:
                raise Exception("Tipo Inválido")
        elif self.value == "DIV":
            if l[0] == r[0] and l[0] == "Int":
                return ("Int", l[1] // r[1])
            else:
                raise Exception("Tipo Inválido")
        elif self.value == "EQUALS_BOOL":
            if l[1] == r[1]:
                return ("Int", 1)
            else:
                return ("Int", 0)
        elif self.value == "GREATER":
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
            if l[0] == r[0] and l[0] == "Int":
                return ("Int", l and r)
            elif l[0] == r[0] and l[0] == "String":
                return ("String", l and r)
            else:
                raise Exception("Tipo Inválido")
        elif self.value == "OR":
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
    
    def evaluate(self, symbol_table):
        if self.value == "PLUS":
            if self.children[0].evaluate(symbol_table)[0] == "Int":
                return ["Int", self.children[0].evaluate(symbol_table)[1]]
            else:
                raise Exception("Tipo Inválido")
        elif self.value == "MINUS":
            if self.children[0].evaluate(symbol_table)[0] == "Int":
                return ["Int", -self.children[0].evaluate(symbol_table)[1]]
            else:
                raise Exception("Tipo Inválido")
        elif self.value == "NOT":
            if self.children[0].evaluate(symbol_table)[0] == "Int":
                if self.children[0].evaluate(symbol_table)[1] == 0:
                    return ["Int", 1]
                else:
                    return ["Int", 0]
            else:
                raise Exception("Tipo Inválido")
        
class IntVal(Node):
    def __init__(self, value):
        self.value = value
    
    def evaluate(self, symbol_table):
        return ["Int", int(self.value)]
    
class StrVal(Node):
    def __init__(self, value):
        self.value = value
    
    def evaluate(self, symbol_table):
        return ["String", str(self.value)]
    
class NoOp(Node):
    def __init__(self):
        self.value = None
        self.children = None
    
    def evaluate(self, symbol_table):
        pass

class PrintOp(Node):
    def __init__(self, children):
        self.value = None
        self.children = children
    
    def evaluate(self, symbol_table):
        print(self.children.evaluate(symbol_table)[1])

class AssignOp(Node):
    def __init__(self, children):
        self.value = None
        self.children = children
    
    def evaluate(self, symbol_table):
        symbol_table.setter(self.children[0].value, self.children[1].evaluate(symbol_table))

class BlockOp(Node):
    def __init__(self, children):
        self.children = children
    
    def evaluate(self, symbol_table):
        for child in self.children:
            #print(child.value)
            if child is not None:
                if child.value == "Return":
                    return child.evaluate(symbol_table)
                child.evaluate(symbol_table)

class IdentifierOp(Node):
    def __init__(self, value):
        self.value = value
    
    def evaluate(self, symbol_table):
        return symbol_table.getter(self.value)

class ReadLineOp(Node):
    def __init__(self):
        pass
    
    def evaluate(self, symbol_table):
        return ["Int", int(input())]

class WhileOp(Node):
    def __init__(self, children):
        self.children = children
    
    def evaluate(self, symbol_table):
        while self.children[0].evaluate(symbol_table)[1] != 0:
            self.children[1].evaluate(symbol_table)

class IfOp(Node):
    def __init__(self, children):
        self.children = children
    
    def evaluate(self, symbol_table):
        if self.children[0].evaluate(symbol_table):
            self.children[1].evaluate(symbol_table)
        else:
            if len(self.children) == 3:
                self.children[2].evaluate(symbol_table)

class VarDeclOp(Node):
    def __init__(self, value, children):
        self.children = children
        self.value = value
    
    def evaluate(self, symbol_table):
            if len(self.children) == 1:
                if self.value == "Int":
                    symbol_table.create(self.children[0].value, [self.value, 0])
                elif self.value == "String":
                    symbol_table.create(self.children[0].value, [self.value, ""])
                else:
                    raise Exception("Tipo inválido")
            else:
                if self.value == "Int" and self.children[1].evaluate(symbol_table)[0] == "Int":
                    symbol_table.create(self.children[0].value, [self.value, self.children[1].evaluate(symbol_table)[1]])
                elif self.value == "String" and self.children[1].evaluate(symbol_table)[0] == "String":
                    symbol_table.create(self.children[0].value, [self.value, self.children[1].evaluate(symbol_table)[1]])
                else:
                    raise Exception("Tipo inválido")
            
class FuncDecOp(Node):
    def __init__(self, value, children):
        self.children = children
        self.value = value
    
    def evaluate(self, symbol_table):
        FuncTable.create(self.children[0].value, self)

class FuncCallOp(Node):
    def __init__(self, value, children):
        self.children = children
        self.value = value
    
    def evaluate(self, symbol_table):
        args = []
        new_func = FuncTable.getter(self.value)
        new_table = SymbolTable()

        for i in range(len(self.children)):
            args.append(new_func.children[1][i].children[0].value)
            new_func.children[1][i].evaluate(new_table)

        for i in range(len(args)):
            new_table.setter(args[i], self.children[i].evaluate(symbol_table))

        return new_func.children[2].evaluate(new_table)
    
class ReturnOp(Node):
    def __init__(self, children):
        self.value = "Return"
        self.children = children
    
    def evaluate(self, symbol_table):
        return self.children.evaluate(symbol_table)

class SymbolTable:
    def __init__(self):
        self.table = {}
    
    def setter(self, name, value):
        if self.table[name][0] == value[0]:
            self.table[name][1] = value[1]
        else:
            raise Exception("Tipo inválido")
    
    def getter(self, name):
        return self.table[name]
    
    def create(self, name, value):
        if name in self.table:
            raise Exception("Variável já declarada")
        self.table[name] = value

class FuncTable:
    table = {}
    
    def getter(name):
        return FuncTable.table[name]
    
    def create(name, value):
        FuncTable.table[name] = value

def read_file(filename):
    with open(filename, 'r') as f:
        return f.read()

def main():
    code = read_file(sys.argv[1])
    #code = read_file("test.jl")
    symbol_table = SymbolTable()
    Parser.run(code).evaluate(symbol_table)

main()