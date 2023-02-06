import sys

n = sys.argv[1]
t = ''
r = []
s = []
c = 0
b = 0

#c = 1 > number, c = 2 > sinal, c = 3 > space

for i in range(len(n)):

    if n[i].isdigit():
        if b == 1:
            raise Exception("Espaço entre números")
        t = t + n[i]
        c = 1
    elif n[i] == '+':
        if b == 1:
            b = 0
        r.append(int(t))
        t = ''
        s.append(1)
        c = 2
    elif n[i] == '-':
        if b == 1:
            b = 0
        r.append(int(t))
        t = ''
        s.append(2)
        c = 2
    elif n[i] == ' ':
        if c == 1:
            b = 1
        c = 3
    else:
        raise Exception("Símbolo inválido")

    if i == (len(n)):
        r.append(int(t))

a = r[0]

for i in range(1, len(r)):
    if s[i-1] == 1:
        a = a + r[i]
    elif s[i-1] == 2:
        a = a - r[i]

print(a)