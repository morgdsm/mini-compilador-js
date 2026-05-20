import re
import bisect
from .tokens import Token, TipoToken, PALAVRAS_CHAVE
from .errors import ErroLexico


_TOKEN_RE = re.compile(r'''
    (?P<COM_BLOCO>      /\*[\s\S]*?\*/                                )
  | (?P<COM_BLOCO_A>    /\*[\s\S]*                                    )
  | (?P<COM_LINHA>      //[^\n]*                                      )
  | (?P<DECIMAL>        \d+\.\d+                                      )
  | (?P<INTEIRO>        \d+                                           )
  | (?P<STRING>         "(?:[^"\\\n]|\\.)*"|'(?:[^'\\\n]|\\.)*'      )
  | (?P<STR_ABERTA>     ["'][^\n]*                                    )
  | (?P<IDENT>          [A-Za-z_]\w*                                  )
  | (?P<IGUAL_IGUAL>    ==                                            )
  | (?P<DIFERENTE>      !=                                            )
  | (?P<E_LOGICO>       &&                                            )
  | (?P<OU_LOGICO>      \|\|                                          )
  | (?P<MAIS>           \+                                            )
  | (?P<MENOS>          -                                             )
  | (?P<ASTERISCO>      \*                                            )
  | (?P<BARRA>          /                                             )
  | (?P<IGUAL>          =                                             )
  | (?P<MAIOR>          >                                             )
  | (?P<MENOR>          <                                             )
  | (?P<NAO>            !                                             )
  | (?P<ABRE_PAREN>     \(                                            )
  | (?P<FECHA_PAREN>    \)                                            )
  | (?P<ABRE_CHAVE>     \{                                            )
  | (?P<FECHA_CHAVE>    \}                                            )
  | (?P<VIRGULA>        ,                                             )
  | (?P<PONTO_VIRGULA>  ;                                             )
  | (?P<NEWLINE>        \n                                            )
  | (?P<ESPACOS>        [ \t\r]+                                      )
  | (?P<ERRO>           .                                             )
''', re.VERBOSE)

# Tipos de token após os quais uma quebra de linha insere FIM_INSTRUCAO (ASI)
_PERMITE_ASI = frozenset({
    TipoToken.IDENTIFICADOR,
    TipoToken.INTEIRO,
    TipoToken.DECIMAL,
    TipoToken.STRING,
    TipoToken.TRUE,
    TipoToken.FALSE,
    TipoToken.FECHA_PAREN,
    TipoToken.FECHA_CHAVE,
    TipoToken.RETURN,
})

# Mapeamento direto: nome do grupo regex → TipoToken
_MAPA_TIPO = {
    "IGUAL_IGUAL":   TipoToken.IGUAL_IGUAL,
    "DIFERENTE":     TipoToken.DIFERENTE,
    "E_LOGICO":      TipoToken.E_LOGICO,
    "OU_LOGICO":     TipoToken.OU_LOGICO,
    "MAIS":          TipoToken.MAIS,
    "MENOS":         TipoToken.MENOS,
    "ASTERISCO":     TipoToken.ASTERISCO,
    "BARRA":         TipoToken.BARRA,
    "IGUAL":         TipoToken.IGUAL,
    "MAIOR":         TipoToken.MAIOR,
    "MENOR":         TipoToken.MENOR,
    "NAO":           TipoToken.NAO,
    "ABRE_PAREN":    TipoToken.ABRE_PAREN,
    "FECHA_PAREN":   TipoToken.FECHA_PAREN,
    "ABRE_CHAVE":    TipoToken.ABRE_CHAVE,
    "FECHA_CHAVE":   TipoToken.FECHA_CHAVE,
    "VIRGULA":       TipoToken.VIRGULA,
    "PONTO_VIRGULA": TipoToken.FIM_INSTRUCAO,
}


def _decode_string(raw):
    """Traduz sequências de escape no conteúdo de uma string (sem as aspas)."""
    out = []
    i = 0
    while i < len(raw):
        if raw[i] == "\\" and i + 1 < len(raw) and raw[i + 1] in ('"', "'", "\\", "n", "t"):
            out.append({"n": "\n", "t": "\t"}.get(raw[i + 1], raw[i + 1]))
            i += 2
        else:
            out.append(raw[i])
            i += 1
    return "".join(out)


class Lexer:
    def __init__(self, codigo):
        self.codigo = codigo
        self._line_starts = self._calc_line_starts(codigo)
        self.tokens = []

    @staticmethod
    def _calc_line_starts(codigo):
        """Retorna lista com o offset de início de cada linha (índice 0 = linha 1)."""
        starts = [0]
        for i, ch in enumerate(codigo):
            if ch == "\n":
                starts.append(i + 1)
        return starts

    def _lc(self, pos):
        """Converte offset de byte em (linha, coluna) base-1."""
        linha = bisect.bisect_right(self._line_starts, pos)
        coluna = pos - self._line_starts[linha - 1] + 1
        return linha, coluna

    def _ultimo_permite_asi(self):
        return bool(self.tokens) and self.tokens[-1].tipo in _PERMITE_ASI

    def tokenizar(self):
        codigo = self.codigo

        for m in _TOKEN_RE.finditer(codigo):
            grupo = m.lastgroup
            texto = m.group()
            linha, coluna = self._lc(m.start())

            # ── ignorados ────────────────────────────────────────────────────
            if grupo in ("COM_LINHA", "COM_BLOCO", "ESPACOS"):
                continue

            # ── erros léxicos ────────────────────────────────────────────────
            if grupo == "COM_BLOCO_A":
                raise ErroLexico("comentário de bloco não fechado", linha, coluna)

            if grupo == "STR_ABERTA":
                fim = m.end()
                if fim >= len(codigo) or codigo[fim] != "\n":
                    raise ErroLexico("string não fechada antes do fim do arquivo", linha, coluna)
                raise ErroLexico("string não fechada antes do fim da linha", linha, coluna)

            if grupo == "ERRO":
                raise ErroLexico(f"caractere inesperado: {texto!r}", linha, coluna)

            # ── quebra de linha → ASI ────────────────────────────────────────
            if grupo == "NEWLINE":
                if self._ultimo_permite_asi():
                    self.tokens.append(Token(TipoToken.FIM_INSTRUCAO, "\\n", linha, coluna))
                continue

            # ── literais ─────────────────────────────────────────────────────
            if grupo == "INTEIRO":
                self.tokens.append(Token(TipoToken.INTEIRO, texto, linha, coluna))
                continue

            if grupo == "DECIMAL":
                self.tokens.append(Token(TipoToken.DECIMAL, texto, linha, coluna))
                continue

            if grupo == "STRING":
                valor = _decode_string(texto[1:-1])
                self.tokens.append(Token(TipoToken.STRING, valor, linha, coluna))
                continue

            # ── identificador ou palavra-chave ───────────────────────────────
            if grupo == "IDENT":
                tipo = PALAVRAS_CHAVE.get(texto, TipoToken.IDENTIFICADOR)
                self.tokens.append(Token(tipo, texto, linha, coluna))
                continue

            # ── operadores e delimitadores ───────────────────────────────────
            self.tokens.append(Token(_MAPA_TIPO[grupo], texto, linha, coluna))

        self.tokens.append(Token(TipoToken.EOF, "", *self._lc(len(codigo))))
        return self.tokens
