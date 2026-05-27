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
├── docs/
│   └── MODELAGEM.md # Fase 1: tabela de tokens e GLC
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
| `x = 10` (sem `let`/`const`) | **Erro sintático** (declaração implícita) |
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

## Modelagem Formal (Fase 1)

A documentação completa da linguagem — **tabela de tokens com regex** e **GLC não ambígua** — está em:

[`mini_compilador/docs/MODELAGEM.md`](mini_compilador/docs/MODELAGEM.md)

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

Rejeita `var` e declarações implícitas (`x = 10` sem `let`/`const`) com mensagem clara.  
Acumula **múltiplos erros sintáticos** e tenta recuperação via pontos de sincronização (`;`, `}`, palavras-chave de declaração).  
Mensagens no formato: `Erro Sintático (Linha X, Col Y): Esperado '}', encontrado ')'`.

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
[ERRO] Erro Léxico (Linha 4, Col 11): caractere inesperado: '@'

RESULTADO FINAL
Programa REJEITADO.
```

### Erro sintático

```bash
python main.py mini_compilador/examples/erro_sintatico.js
```

```
FASE 2 — ANÁLISE SINTÁTICA
[ERRO] Erro Sintático (Linha 3, Col 1): 'var' não é permitido; use 'let' ou 'const'

RESULTADO FINAL
Programa REJEITADO.
```

### Erros semânticos

```bash
python main.py mini_compilador/examples/erro_semantico.js
```

```
FASE 3 — ANÁLISE SEMÂNTICA
[ERRO] Erro Semântico (Linha 4, Col 5): variável 'x' já declarada neste escopo
[ERRO] Erro Semântico (Linha 7, Col 1): não é possível reatribuir constante 'PI'
[ERRO] Erro Semântico (Linha 9, Col 19): operação '-' inválida com strings
[ERRO] Erro Semântico (Linha 15, Col 1): função 'soma' espera 2 argumento(s), recebeu 3
[ERRO] Erro Semântico (Linha 17, Col 13): variável 'z' não declarada

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
- Rejeição de `var`, declaração implícita e declarações sem valor
- Recuperação de erros sintáticos (múltiplos diagnósticos)
- Funções, blocos, `if/else`, `while`
- Escopos aninhados e vazamento de variáveis
- Verificação de aridade de funções
- Operações inválidas por tipo

---

## Nota pedagógica

### Declaração implícita: sintático ou semântico?

O enunciado do projeto exige que `x = 10` sem `let` ou `const` prévio produza **Erro Sintático**. O compilador atende a essa regra: o parser mantém um rastro mínimo de declarações por escopo e rejeita atribuições a identificadores ainda não declarados, enquanto permite reatribuições válidas como `contador = contador + 1` após `let contador = 0` (como em [valido.js](mini_compilador/examples/valido.js)).

Do ponto de vista **clássico** da teoria de compiladores, essa distinção costuma ser tratada na **análise semântica**: saber se um identificador já foi declarado exige consulta à tabela de símbolos, que é responsabilidade dessa fase — o parser, operando sobre uma GLC, validaria apenas a *forma* das frases (`IDENT = Expr`), sem conhecimento de contexto. Compiladores reais (TypeScript em modo estrito, Java, C#, Rust, etc.) frequentemente reportam variáveis não declaradas no verificador semântico, não no sintático.

**Resumo:** a implementação atual prioriza o **critério do enunciado** (erro sintático); a visão semântica permanece válida como referência teórica e explica por que o parser precisa de um controle de escopo mínimo para distinguir declaração implícita de reatribuição legítima.

---

## Requisitos

- Python 3.8 ou superior
- Sem dependências externas
