import sys

n = sys.argv[1]
t = ''
r = []
s = []

for i in range(len(n)):
    if n[i].isdigit():
        t = t + n[i]
    elif n[i] == '+':
        r.append(int(t))
        t = ''
        s.append(1)
    elif n[i] == '-':
        r.append(int(t))
        t = ''
        s.append(2)
    
    if i == len(n)-1:
        r.append(int(t))

a = r[0]

for i in range(1, len(r)):
    if s[i-1] == 1:
        a = a + r[i]
    elif s[i-1] == 2:
        a = a - r[i]

print(a)