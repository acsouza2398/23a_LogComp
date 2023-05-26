# Status dos testes

![git status](http://3.129.230.99/svg/acsouza2398/23a_LogComp)

<br>

# Mudanças feitas entre versão 2.4 e versão 3.1
1.	Baseado na versão 2.4, retomar as mudanças da versão 3.0 de geração de código.
2.	Criar uma classe `Func_Asm()` espelhada da classe `Asm()` para guardar as funções criadas e não conflitar com o código da `main()`. A sua função `save()` recebe o nome de um arquivo em Assembly temporário e escreve em modo append a função gerada em `FuncCallOp()`.
3.	Criar uma classe `Rep_Asm()` espelhada da `Func_Asm()` para guardar funções repetidas e já declaradas. O seu método `save()` deve ser apenas pass.
4.	Separar a função `save()` da classe `Asm()` e deixa-la independente. A função recebe o código principal e o nome do arquivo final pra a escrita e cria um arquivo em Assembly na ordem: header + funções + start + código final + footer. Como as funções precisam estar antes do começo da função principal, é preciso separar o header original em dois pedaços para comportar a declaração das funções.
5.	Adaptar a classe `FuncTable()` para ter uma variável estática de endereço relativo iniciando com 4 e criar uma lista estática para guardar o nome de todas as funções declaradas.
6.	Adaptar a classe `FuncCallOp()` para:
    1.	Criar uma instância da `Func_Asm()` para salvar a função a ser declarada apenas se essa função ainda não estiver na lista de funções da `FuncTable()`. Adicionar a essa instância o label com o nome da função e estabelecer o novo stack pointer.
    2.	Caso a função ainda não tenha sido declarado, fazer o `Evaluate()` dos argumentos da funçao e salvar isso na instância da `Func_Asm()` criada. Caso contrário, criar uma instância da `Rep_Asm()` e passar esta ao `Evaluate()` para não haver uma repetição de declarações da mesma função.
    3.	Fazer o `Evaluate()` dos filhos passados ao `FuncCallOp()` e adicionar os seus valores ao stack do código principal. Fazer o assign desses valores as variáveis dentro da função considerando o seu endereço positivo relativo da stack, onde a primeira variável da função está em +4, a segunda está em +8, e assim por diante. Usar a variável de endereço relativo da `FuncTable()` para fazer esse referenciamento.
    4.	No código principal, fazer a chamada da função e após tirar os argumentos empilhados antes da chamada da stack.
    5.	Fazer o evaluate do return e, caso a função ainda não esteja na lista de funções declaradas, fazer o append do seu nome nessa lista. Retornar o return da função.
7.	Adaptar o `ReturnOp()` para fazer o `Evaluate()` do seu filho, restaurar o ponteiro, adicionar RET e salvar a função usando o método `save()` do `Func_Asm()` antes de retornar o valor do `Evaluate()`.

## Exemplo de código:
    function soma(x::Int, y::Int)::Int
        return x + y
    end
    function subtract(x::Int, y::Int)::Int
        return x - y
    end
    
    x_1::Int
    x_1 = 2
    x_1 = soma(1, x_1)
    x_1 = soma(1, x_1)
    x_1 = subtract(x_1, 1)
    println(x_1)

## Mesmo exemplo em Assembly NASM (gerado pelo compilador):
    ; CONSTANTES
    SYS_EXIT EQU 1
    SYS_READ EQU 3
    SYS_WRITE EQU 4
    STDIN EQU 0
    STDOUT EQU 1
    TRUE EQU 1
    FALSE EQU 0

    SEGMENT .DATA

    SEGMENT .BSS  ; VARIAVEIS
    RES RESB 1

    SECTION .TEXT
    GLOBAL _START

    PRINT:  ; SUBROTINA PRINT

    PUSH EBP ; GUARDA O BASE POINTER
    MOV EBP, ESP ; ESTABELECE UM NOVO BASE POINTER

    MOV EAX, [EBP+8] ; 1 ARGUMENTO ANTES DO RET E EBP
    XOR ESI, ESI

    PRINT_DEC: ; EMPILHA TODOS OS DIGITOS
    MOV EDX, 0
    MOV EBX, 0X000A
    DIV EBX
    ADD EDX, '0'
    PUSH EDX
    INC ESI ; CONTADOR DE DIGITOS
    CMP EAX, 0
    JZ PRINT_NEXT ; QUANDO ACABAR PULA
    JMP PRINT_DEC

    PRINT_NEXT:
    CMP ESI, 0
    JZ PRINT_EXIT ; QUANDO ACABAR DE IMPRIMIR
    DEC ESI

    MOV EAX, SYS_WRITE
    MOV EBX, STDOUT

    POP ECX
    MOV [RES], ECX
    MOV ECX, RES

    MOV EDX, 1
    INT 0X80
    JMP PRINT_NEXT

    PRINT_EXIT:
    POP EBP
    RET

    ; SUBROTINAS IF/WHILE
    BINOP_JE:
    JE BINOP_TRUE
    JMP BINOP_FALSE

    BINOP_JG:
    JG BINOP_TRUE
    JMP BINOP_FALSE

    BINOP_JL:
    JL BINOP_TRUE
    JMP BINOP_FALSE

    BINOP_FALSE:
    MOV EBX, FALSE
    JMP BINOP_EXIT
    BINOP_TRUE:
    MOV EBX, TRUE
    BINOP_EXIT:
    RET

    SOMA:
    PUSH EBP
    MOV EBP, ESP
    PUSH DWORD 0 
    PUSH DWORD 0 
    MOV EBX, [EBP + 12]
    MOV [EBP - 4], EBX 
    MOV EBX, [EBP + 8]
    MOV [EBP - 8], EBX
    POP EAX
    POP EAX
    MOV EBX, [EBP - 4] 
    PUSH EBX
    MOV EBX, [EBP - 8]
    POP EAX
    ADD EAX, EBX
    MOV EBX, EAX
    POP EBP	
    RET

    SUBTRACT:
    PUSH EBP 
    MOV EBP, ESP 
    PUSH DWORD 0 
    PUSH DWORD 0 
    MOV EBX, [EBP + 12]
    MOV [EBP - 4], EBX 
    MOV EBX, [EBP + 8]
    MOV [EBP - 8], EBX 
    POP EAX
    POP EAX
    MOV EBX, [EBP - 4] 
    PUSH EBX 
    MOV EBX, [EBP - 8] 
    POP EAX
    SUB EAX, EBX
    MOV EBX, EAX
    POP EBP	
    RET

    _START:

    PUSH EBP ; GUARDA O BASE POINTER
    MOV EBP, ESP ; ESTABELECE UM NOVO BASE POINTER

    ; CODIGO GERADO PELO COMPILADOR
    PUSH DWORD 0 
    MOV EBX, 2 
    MOV [EBP - 4], EBX 
    MOV EBX, 1 
    PUSH 1 
    MOV EBX, [EBP - 4] 
    PUSH 2 
    CALL SOMA
    POP EAX
    POP EAX
    MOV [EBP - 4], EBX ;ASSIGNOP DE X_1
    MOV EBX, 1 ;INTVAL 1
    PUSH 1 ;EMPILHANDO VALOR DE  X
    MOV EBX, [EBP - 4] ;IDENTIFIEROP DE X_1
    PUSH 3 ;EMPILHANDO VALOR DE  Y
    CALL SOMA
    POP EAX
    POP EAX
    MOV [EBP - 4], EBX ;ASSIGNOP DE X_1
    MOV EBX, [EBP - 4] ;IDENTIFIEROP DE X_1
    PUSH 4 ;EMPILHANDO VALOR DE  X
    MOV EBX, 1 ;INTVAL 1
    PUSH 1 ;EMPILHANDO VALOR DE  Y
    CALL SUBTRACT
    POP EAX
    POP EAX
    MOV [EBP - 4], EBX ;ASSIGNOP DE X_1
    MOV EBX, [EBP - 4] ;IDENTIFIEROP DE X_1
    PUSH EBX
    CALL PRINT
    POP EBX
    ; INTERRUPCAO DE SAIDA
    POP EBP
    MOV EAX, 1
    INT 0X80


