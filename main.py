import sys

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
        if self.source[self.position] == '+':
            self.next = Token('PLUS', self.source[self.position])
            self.position += 1
        elif self.source[self.position] == '-':
            self.next = Token('MINUS', self.source[self.position])
            self.position += 1
        elif self.source[self.position].isdigit():
            i = self.position
            a = ''
            while i < len(self.source) and self.source[i].isdigit():
                a += self.source[i]
                i += 1
            self.position = i
            self.next = Token('INT', a)

class Parser:
    @staticmethod
    def parseExpression(tokenizer):
        tokenizer.selectNext()
        if tokenizer.next.type == "INT":
            n = int(tokenizer.next.value)
            tokenizer.selectNext()
            while tokenizer.next.type == "PLUS" or tokenizer.next.type == "MINUS":
                if tokenizer.next.type == "PLUS":
                    tokenizer.selectNext()
                    if tokenizer.next.type == "INT":
                        n += int(tokenizer.next.value)
                    else:
                        raise Exception("Símbolo inválido")
                elif tokenizer.next.type == "MINUS":
                    tokenizer.selectNext()
                    if tokenizer.next.type == "INT":
                        n -= int(tokenizer.next.value)
                    else:
                        raise Exception("Símbolo inválido")
                if tokenizer.position < len(tokenizer.source):
                    tokenizer.selectNext()
            return n
        else:
            raise Exception("Símbolo inválido")

    @staticmethod
    def run(code):
        tokenizer = Tokenizer(code)
        return Parser.parseExpression(tokenizer)

def main():
    code = sys.argv[1]
    print(Parser.run(code)," \n")

main()