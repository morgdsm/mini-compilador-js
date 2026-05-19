# Mini-Compilador JavaScript

Compilador didático para um subconjunto da linguagem JavaScript, desenvolvido em Python puro para fins acadêmicos.

---

## Objetivo

Demonstrar as três fases clássicas de análise de um compilador — léxica, sintática e semântica — aplicadas a uma versão simplificada do JavaScript chamada **Mini-JavaScript**.

O compilador **não gera código executável**. Sua saída é a listagem de tokens e o diagnóstico de erros encontrados nas três fases.

---

## Estrutura do Projeto

```
mini_compilador/
├── main.py          # Orquestrador das fases
├── lexer.py         # Analisador léxico
├── parser.py        # Analisador sintático
├── semantic.py      # Analisador semântico
├── tokens.py        # Definição de tokens e palavras-chave
├── errors.py        # Classes de erro por fase
├── examples/
│   ├── valido.js        # Programa correto
│   ├── erro_lexico.js   # Erro na fase léxica
│   ├── erro_sintatico.js# Erro na fase sintática
│   └── erro_semantico.js# Erros na fase semântica
└── tests/
    ├── test_lexer.py
    ├── test_parser.py
    └── test_semantic.py

main.py              # Ponto de entrada
```

---

## Linguagem Mini-JavaScript

### Declarações

| Construção | Válida? |
|---|---|
| `let x = 10` | Sim |
| `const PI = 3.14` | Sim |
| `var x = 1` | **Erro sintático** |
| `let x` | **Erro sintático** (sem valor inicial) |

### Tipos suportados

- **Inteiro**: `42`, `0`, `100`
- **Decimal**: `3.14`, `0.5`
- **String**: `"hello"`, `'world'`
- **Booleano**: `true`, `false`

### Operadores

| Categoria | Símbolos |
|---|---|
| Aritméticos | `+` `-` `*` `/` `()` |
| Relacionais | `>` `<` `==` `!=` |
| Lógicos | `&&` `\|\|` `!` |
| Atribuição | `=` |

### Estruturas de controle

```js
if (condicao) {
    // ...
} else {
    // ...
}

while (condicao) {
    // ...
}
```

### Funções

```js
function nome(param1, param2) {
    return param1 + param2
}
```

### Ponto e vírgula opcional

O compilador emite automaticamente o token `FIM_INSTRUCAO` ao encontrar `;` ou uma **quebra de linha válida** (após identificadores, literais, `)` ou `}`).

---

## Arquitetura

### Fase 1 — Analisador Léxico (`lexer.py`)

Converte o código-fonte em uma sequência de tokens. Percorre o texto caractere a caractere e reconhece:

- Palavras-chave (`let`, `const`, `if`, `while`, `function`, `return`, ...)
- Identificadores e literais (inteiros, decimais, strings)
- Operadores simples e compostos (`==`, `!=`, `&&`, `||`)
- Comentários de linha (`//`) e de bloco (`/* */`)
- `FIM_INSTRUCAO` por `;` ou quebra de linha válida

Erros léxicos são lançados como `ErroLexico` com linha e coluna.

### Fase 2 — Analisador Sintático (`parser.py`)

Implementa um **parser recursivo descendente** que valida a gramática da Mini-JavaScript. Reconhece:

- Declarações de variáveis (`let`, `const`)
- Declarações de funções com parâmetros
- Blocos `{ ... }`
- Estruturas `if/else` e `while`
- Expressões com precedência correta (lógico → relacional → aditivo → multiplicativo → unário → primário)
- Chamadas de função

Rejeita `var` com mensagem clara. Erros sintáticos são lançados como `ErroSintatico`.

### Fase 3 — Analisador Semântico (`semantic.py`)

Percorre os tokens novamente com uma **tabela de símbolos aninhada** (escopos). Verifica:

| Regra | Exemplo de violação |
|---|---|
| Variável já declarada no escopo | `let x = 1` e `let x = 2` no mesmo escopo |
| Reatribuição de `const` | `const PI = 3.14` seguido de `PI = 3.0` |
| Variável não declarada | `let r = z + 1` sem declarar `z` |
| Aridade de função | `soma(1, 2, 3)` para `function soma(a, b)` |
| Operações inválidas com strings | `"texto" - 1` |
| Escopo léxico correto | variável local não vaza para o escopo externo |

Erros semânticos são coletados e exibidos todos de uma vez.

---

## Execução

```bash
python main.py <arquivo.js>
```

Em sistemas Windows, defina a variável de ambiente para UTF-8:

```powershell
$env:PYTHONIOENCODING="utf-8"; python main.py mini_compilador/examples/valido.js
```

---

## Exemplos

### Programa válido

```bash
python main.py mini_compilador/examples/valido.js
```

```
FASE 1 — ANÁLISE LÉXICA
...tokens...

FASE 2 — ANÁLISE SINTÁTICA
[OK]
Sintaxe válida.

FASE 3 — ANÁLISE SEMÂNTICA
[OK]
Nenhum erro encontrado.

RESULTADO FINAL
Programa ACEITO.
```

### Erro léxico

```bash
python main.py mini_compilador/examples/erro_lexico.js
```

```
FASE 1 — ANÁLISE LÉXICA
[ERRO] [Léxico] Linha 4, Col 11: caractere inesperado: '@'

RESULTADO FINAL
Programa REJEITADO.
```

### Erro sintático

```bash
python main.py mini_compilador/examples/erro_sintatico.js
```

```
FASE 2 — ANÁLISE SINTÁTICA
[ERRO] [Sintático] Linha 3, Col 1: 'var' não é permitido; use 'let' ou 'const'

RESULTADO FINAL
Programa REJEITADO.
```

### Erros semânticos

```bash
python main.py mini_compilador/examples/erro_semantico.js
```

```
FASE 3 — ANÁLISE SEMÂNTICA
[ERRO] [Semântico] Linha 4, Col 5: variável 'x' já declarada neste escopo
[ERRO] [Semântico] Linha 7, Col 1: não é possível reatribuir constante 'PI'
[ERRO] [Semântico] Linha 9, Col 19: operação '-' inválida com strings
[ERRO] [Semântico] Linha 15, Col 1: função 'soma' espera 2 argumento(s), recebeu 3
[ERRO] [Semântico] Linha 17, Col 13: variável 'z' não declarada

RESULTADO FINAL
Programa REJEITADO.
```

---

## Testes Automatizados

```bash
python -m unittest discover mini_compilador/tests/ -v
```

Os testes cobrem:
- Reconhecimento correto de todos os tipos de token
- Inserção automática de `FIM_INSTRUCAO`
- Rejeição de `var` e declarações sem valor
- Funções, blocos, `if/else`, `while`
- Escopos aninhados e vazamento de variáveis
- Verificação de aridade de funções
- Operações inválidas por tipo

---

## Requisitos

- Python 3.8 ou superior
- Sem dependências externas
