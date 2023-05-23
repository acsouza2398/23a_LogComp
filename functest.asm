; constantes
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

soma:
PUSH EBP ; guarda o base pointer
MOV EBP, ESP ; estabelece um novo base pointer
PUSH DWORD 0 ;VarDeclOp de x
PUSH DWORD 0 ;VarDeclOp de y
MOV EBX, [EBP + 12]
MOV [EBP - 4], EBX ;AssignOp de x
MOV EBX, [EBP + 8]
MOV [EBP - 8], EBX ;AssignOp de y
POP EAX
POP EAX
MOV EBX, [EBP - 4] ;IdentifierOp de x
PUSH EBX ; 1
MOV EBX, [EBP - 8] ;IdentifierOp de y
POP EAX
ADD EAX, EBX ;Soma de 1 e 2
MOV EBX, EAX ;EBX = 1 + 2
POP EBP ; restaura o base pointer	
RET


subtract:
PUSH EBP ; guarda o base pointer
MOV EBP, ESP ; estabelece um novo base pointer
PUSH DWORD 0 ;VarDeclOp de x
PUSH DWORD 0 ;VarDeclOp de y
MOV EBX, [EBP + 12]
MOV [EBP - 4], EBX ;AssignOp de x
MOV EBX, [EBP + 8]
MOV [EBP - 8], EBX ;AssignOp de y
POP EAX
POP EAX
MOV EBX, [EBP - 4] ;IdentifierOp de x
PUSH EBX ; 4
MOV EBX, [EBP - 8] ;IdentifierOp de y
POP EAX
SUB EAX, EBX
MOV EBX, EAX
POP EBP ; restaura o base pointer	
RET



_start:

  PUSH EBP ; guarda o base pointer
  MOV EBP, ESP ; estabelece um novo base pointer

  ; codigo gerado pelo compilador
  PUSH DWORD 0 ;VarDeclOp de x_1
MOV EBX, 2 ;IntVal 2
MOV [EBP - 4], EBX ;AssignOp de x_1
MOV EBX, 1 ;IntVal 1
PUSH 1 ;Empilhando valor de  x
MOV EBX, [EBP - 4] ;IdentifierOp de x_1
PUSH 2 ;Empilhando valor de  y
CALL soma
POP EAX
POP EAX
MOV [EBP - 4], EBX ;AssignOp de x_1
MOV EBX, 1 ;IntVal 1
PUSH 1 ;Empilhando valor de  x
MOV EBX, [EBP - 4] ;IdentifierOp de x_1
PUSH 3 ;Empilhando valor de  y
CALL soma
POP EAX
POP EAX
MOV [EBP - 4], EBX ;AssignOp de x_1
MOV EBX, [EBP - 4] ;IdentifierOp de x_1
PUSH 4 ;Empilhando valor de  x
MOV EBX, 1 ;IntVal 1
PUSH 1 ;Empilhando valor de  y
CALL subtract
POP EAX
POP EAX
MOV [EBP - 4], EBX ;AssignOp de x_1
MOV EBX, [EBP - 4] ;IdentifierOp de x_1
PUSH EBX
CALL print
POP EBX
  ; interrupcao de saida
  POP EBP
  MOV EAX, 1
  INT 0x80