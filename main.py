import sys
import re

#O sintático/parser está sempre olhando para o próximo token, e o léxico está sempre olhando para o token atual
#O tokenizer sempre começa no primeiro token, e o parser sempre começa no segundo token

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
            elif self.source[self.position].isdigit():
                i = self.position
                a = ''
                while i < len(self.source) and self.source[i].isdigit():
                    a += self.source[i]
                    i += 1
                self.position = i
                self.next = Token('INT', a)
            elif self.source[self.position] != ' ':
                raise Exception("Símbolo inválido")
        elif len(self.source) == 0:
            raise Exception("Entrada vazia")
        else:
            self.next = Token('EOF', '')

class Parser:
    @staticmethod
    def parseTerm(tokenizer):
        if tokenizer.next.type == "INT":
            n = int(tokenizer.next.value)
            tokenizer.selectNext()
            while tokenizer.next.type == "MULT" or tokenizer.next.type == "DIV":
                if tokenizer.next.type == "MULT":
                    tokenizer.selectNext()
                    if tokenizer.next.type == "INT":
                        n *= int(tokenizer.next.value)
                    else:
                        raise Exception("Símbolo inválido")
                elif tokenizer.next.type == "DIV":
                    tokenizer.selectNext()
                    if tokenizer.next.type == "INT":
                        n //= int(tokenizer.next.value)
                    else:
                        raise Exception("Símbolo inválido")
                tokenizer.selectNext()
            return n
        elif tokenizer.next.type != "PLUS" and tokenizer.next.type != "MINUS" and tokenizer.next.type != "EOF":
            raise Exception("Símbolo inválido")
        
    @staticmethod
    def parseExpression(tokenizer):
        a = Parser.parseTerm(tokenizer)
        while tokenizer.next.type == "PLUS" or tokenizer.next.type == "MINUS":
            if tokenizer.next.type == "PLUS":
                tokenizer.selectNext()
                b = Parser.parseTerm(tokenizer)
                a += b
            elif tokenizer.next.type == "MINUS":
                tokenizer.selectNext()
                b = Parser.parseTerm(tokenizer)
                a -= b
        return a

    @staticmethod
    def run(code):
        c = PrePro.filter(code)
        tokenizer = Tokenizer(c)
        tokenizer.selectNext()
        return Parser.parseExpression(tokenizer)

class PrePro:
    @staticmethod
    def filter(code):
        #c = re.sub(r'//.*\n', '', code,  flags=re.MULTILINE)
        c = re.sub(r'#.*$', '', code)
        return c

def main():
    code = sys.argv[1]
    print(Parser.run(code)," \n")

main()