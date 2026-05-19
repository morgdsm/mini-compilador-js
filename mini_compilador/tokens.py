from enum import Enum, auto


class TipoToken(Enum):
    # Literais
    INTEIRO = auto()
    DECIMAL = auto()
    STRING = auto()
    IDENTIFICADOR = auto()

    # Palavras-chave
    LET = auto()
    CONST = auto()
    VAR = auto()
    IF = auto()
    ELSE = auto()
    WHILE = auto()
    FUNCTION = auto()
    RETURN = auto()
    TRUE = auto()
    FALSE = auto()

    # Operadores aritméticos
    MAIS = auto()
    MENOS = auto()
    ASTERISCO = auto()
    BARRA = auto()

    # Operadores relacionais
    MAIOR = auto()
    MENOR = auto()
    IGUAL_IGUAL = auto()
    DIFERENTE = auto()

    # Operadores lógicos
    E_LOGICO = auto()
    OU_LOGICO = auto()
    NAO = auto()

    # Atribuição
    IGUAL = auto()

    # Delimitadores
    ABRE_PAREN = auto()
    FECHA_PAREN = auto()
    ABRE_CHAVE = auto()
    FECHA_CHAVE = auto()
    VIRGULA = auto()
    PONTO_VIRGULA = auto()
    FIM_INSTRUCAO = auto()

    # Fim de arquivo
    EOF = auto()


PALAVRAS_CHAVE = {
    "let": TipoToken.LET,
    "const": TipoToken.CONST,
    "var": TipoToken.VAR,
    "if": TipoToken.IF,
    "else": TipoToken.ELSE,
    "while": TipoToken.WHILE,
    "function": TipoToken.FUNCTION,
    "return": TipoToken.RETURN,
    "true": TipoToken.TRUE,
    "false": TipoToken.FALSE,
}


class Token:
    def __init__(self, tipo, valor, linha, coluna):
        self.tipo = tipo
        self.valor = valor
        self.linha = linha
        self.coluna = coluna

    def __repr__(self):
        return f"Token({self.tipo.name}, {self.valor!r}, {self.linha}:{self.coluna})"
