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

Converte o código-fonte em uma sequência de tokens. **Esta versão utiliza expressões regulares (módulo `re` do Python)**: um único padrão mestre compilado (`_TOKEN_RE`) com grupos nomeados escaneia o código inteiro via `re.finditer`, sem percorrer caractere a caractere manualmente.

Reconhece:

- Palavras-chave (`let`, `const`, `if`, `while`, `function`, `return`, ...)
- Identificadores e literais (inteiros, decimais, strings)
- Operadores simples e compostos (`==`, `!=`, `&&`, `||`)
- Comentários de linha (`//`) e de bloco (`/* */`)
- `FIM_INSTRUCAO` por `;` ou quebra de linha válida (ASI)

A conversão de offset de byte em linha/coluna é feita com `bisect` sobre um índice pré-calculado dos inícios de linha, tornando o cálculo O(log n) em vez de linear.

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

### Modo interativo (recomendado)

Basta rodar **sem argumentos**:

```bash
python main.py
```

O compilador abre um terminal interativo: mostra uma mensagem de boas-vindas
com um resumo das três fases, lista os arquivos `.js` **ou** `.txt`
encontrados em `mini_compilador/examples/` e pede para você escolher:

- um **número** correspondente a um arquivo da lista, ou
- a opção `all` para analisar **todos** os arquivos em sequência, ou
- `sair` para encerrar.

Após cada análise, o programa **volta automaticamente ao menu principal**,
permitindo analisar outro arquivo sem reiniciar. A lista é relida do disco a
cada volta, então arquivos adicionados durante a sessão aparecem
automaticamente.

Se você digitar algo inválido, o programa avisa e mostra a lista novamente.

### Modo direto (passando o caminho)

Para analisar um arquivo específico sem passar pelo menu:

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

## Notas de Implementação

### Declaração implícita: erro semântico, não sintático

O requisito original especifica que a atribuição a uma variável não declarada
(ex.: `x = 10` sem `let` prévio) deve produzir **Erro Sintático**. No
compilador, o **comportamento** é atendido — esse programa é rejeitado — mas
o erro é classificado como **Erro Semântico** (`variável 'x' não declarada`),
em conformidade com a separação clássica das fases de compilação.

Justificativa: a distinção entre **reatribuição válida** (`contador = contador + 1`,
com `contador` previamente declarado, como em [valido.js](mini_compilador/examples/valido.js))
e **declaração implícita** (`x = 10`, com `x` nunca declarado) **exige consulta
à tabela de símbolos**. A tabela de símbolos é responsabilidade da fase
semântica; fazer o parser realizar essa checagem violaria o princípio de que o
analisador sintático opera apenas sobre a estrutura da linguagem, sem
conhecimento contextual.

Compiladores reais (TypeScript em modo estrito, Java, C#, Rust, etc.) seguem a
mesma abordagem: variáveis não declaradas são reportadas pelo verificador
semântico, não pelo parser. O programa final continua sendo rejeitado, apenas
com a etiqueta de fase tecnicamente correta.

---

## Requisitos

- Python 3.8 ou superior
- Sem dependências externas
