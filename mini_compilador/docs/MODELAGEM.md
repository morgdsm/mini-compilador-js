# Fase 1 — Modelagem Formal da Mini-JavaScript

Documento de entrega do Grupo 3 (Mini-JavaScript).  
UC Teoria da Computação e Compiladores — Projeto A3.

---

## 1. Tabela de Tokens Léxicos

| Token | Lexema / Padrão (Regex) | Descrição |
|---|---|---|
| `INTEIRO` | `\d+` | Literal inteiro (ex.: `42`) |
| `DECIMAL` | `\d+\.\d+` | Literal decimal (ex.: `3.14`) |
| `STRING` | `"(?:[^"\\\n]\|\\.)*"` ou `'(?:[^'\\\n]\|\\.)*'` | Literal de texto |
| `IDENTIFICADOR` | `[A-Za-z_]\w*` | Nome de variável, função ou parâmetro |
| `LET` | `let` | Declaração mutável |
| `CONST` | `const` | Declaração imutável |
| `VAR` | `var` | Palavra proibida (erro sintático) |
| `IF` | `if` | Condicional |
| `ELSE` | `else` | Ramo alternativo |
| `WHILE` | `while` | Laço |
| `FUNCTION` | `function` | Declaração de função |
| `RETURN` | `return` | Retorno de função |
| `TRUE` | `true` | Literal booleano |
| `FALSE` | `false` | Literal booleano |
| `MAIS` | `+` | Adição / concatenação |
| `MENOS` | `-` | Subtração / unário |
| `ASTERISCO` | `*` | Multiplicação |
| `BARRA` | `/` | Divisão |
| `MAIOR` | `>` | Relacional |
| `MENOR` | `<` | Relacional |
| `IGUAL_IGUAL` | `==` | Igualdade |
| `DIFERENTE` | `!=` | Diferença |
| `E_LOGICO` | `&&` | E lógico |
| `OU_LOGICO` | `\|\|` | Ou lógico |
| `NAO` | `!` | Negação lógica |
| `IGUAL` | `=` | Atribuição |
| `ABRE_PAREN` | `(` | Abre parêntese |
| `FECHA_PAREN` | `)` | Fecha parêntese |
| `ABRE_CHAVE` | `{` | Abre bloco |
| `FECHA_CHAVE` | `}` | Fecha bloco |
| `VIRGULA` | `,` | Separador de argumentos/parâmetros |
| `FIM_INSTRUCAO` | `;` **ou** `\n` válida (ASI) | Fim de comando |
| `EOF` | *(fim do arquivo)* | Terminador da fita |

### Regras léxicas específicas da Mini-JavaScript

1. **Comentários descartados:** `// ...` (linha) e `/* ... */` (bloco).
2. **Espaços em branco descartados:** `[ \t\r]+`.
3. **Ponto e vírgula opcional:** `;` é mapeado diretamente para `FIM_INSTRUCAO`.
4. **Inserção automática (ASI):** após `\n`, se o token anterior estiver em  
   `{ IDENTIFICADOR, INTEIRO, DECIMAL, STRING, TRUE, FALSE, FECHA_PAREN, FECHA_CHAVE, RETURN }`,  
   o léxico emite `FIM_INSTRUCAO` com lexema `\n`.
5. **Erros léxicos:** caractere fora do alfabeto, string não fechada, comentário de bloco aberto.

Implementação: `mini_compilador/lexer.py` — padrão mestre `_TOKEN_RE`.

---

## 2. Gramática Livre de Contexto (GLC)

Símbolo inicial: **Programa**

A gramática é **não ambígua**: precedência aritmética e lógica é forçada por camadas  
(Expressão → … → Termo → Fator), no estilo clássico de compiladores.

### 2.1 Programa e declarações

```
Programa        → { FIM_INSTRUCAO } Decl { FIM_INSTRUCAO }

Decl            → DeclVar
                | DeclFunc
                | StmtIf
                | StmtWhile
                | StmtReturn
                | StmtAtrib
                | Expr FIM_INSTRUCAO

DeclVar         → ("let" | "const") IDENT "=" Expr FIM_INSTRUCAO

DeclFunc        → "function" IDENT "(" ParamList? ")" Bloco

ParamList       → IDENT { "," IDENT }

Bloco           → "{" { FIM_INSTRUCAO } Decl { FIM_INSTRUCAO } "}"

StmtIf          → "if" "(" Expr ")" Bloco [ "else" Bloco ]

StmtWhile       → "while" "(" Expr ")" Bloco

StmtReturn      → "return" [ Expr ] FIM_INSTRUCAO

StmtAtrib       → IDENT "=" Expr FIM_INSTRUCAO
                  (* IDENT deve estar declarado no escopo — senão erro sintático *)
```

### 2.2 Expressões (precedência crescente)

```
Expr            → ExprOr

ExprOr          → ExprAnd { "||" ExprAnd }

ExprAnd         → ExprRel { "&&" ExprRel }

ExprRel         → ExprAdd [ ("==" | "!=" | ">" | "<") ExprAdd ]

ExprAdd         → ExprMul { ("+" | "-") ExprMul }

ExprMul         → ExprUnary { ("*" | "/") ExprUnary }

ExprUnary       → ("!" | "-") ExprUnary
                | ExprPrimary

ExprPrimary     → INTEIRO | DECIMAL | STRING | "true" | "false"
                | IDENT [ "(" ArgList? ")" ]
                | "(" Expr ")"

ArgList         → Expr { "," Expr }
```

### 2.3 Restrições sintáticas adicionais (Mini-JavaScript)

| Construção | Resultado |
|---|---|
| `var x = 1` | Erro sintático |
| `let x` (sem `=`) | Erro sintático |
| `x = 10` sem `let`/`const` prévio | Erro sintático (declaração implícita) |
| `let x = 1` seguido de `x = 2` | Válido (reatribuição) |

Operadores lógicos permitidos: **somente** `&&`, `||` e `!`.

---

## 3. Sincronização para recuperação de erros

Pontos de sincronização do parser (descida recursiva):

- **Nível de declaração:** `FIM_INSTRUCAO`, `}`, `let`, `const`, `function`, `if`, `while`, `return`, `else`, `EOF`.
- **Nível de expressão:** tokens acima + `)`, `,`.

Após reportar um erro, o parser avança até o próximo ponto de sincronização e continua a análise, acumulando múltiplos diagnósticos.

---

## 4. Formato de mensagens

| Fase | Formato |
|---|---|
| Léxico | `Erro Léxico (Linha L, Col C): mensagem` |
| Sintático | `Erro Sintático (Linha L, Col C): Esperado 'X', encontrado 'Y'` |
| Semântico | `Erro Semântico (Linha L, Col C): mensagem` |
