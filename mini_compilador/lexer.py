from .tokens import Token, TipoToken, PALAVRAS_CHAVE
from .errors import ErroLexico


class Lexer:
    def __init__(self, codigo):
        self.codigo = codigo
        self.pos = 0
        self.linha = 1
        self.coluna = 1
        self.tokens = []

    def _atual(self):
        if self.pos < len(self.codigo):
            return self.codigo[self.pos]
        return None

    def _proximo(self):
        if self.pos + 1 < len(self.codigo):
            return self.codigo[self.pos + 1]
        return None

    def _avancar(self):
        ch = self.codigo[self.pos]
        self.pos += 1
        if ch == "\n":
            self.linha += 1
            self.coluna = 1
        else:
            self.coluna += 1
        return ch

    def _pular_espacos(self):
        while self._atual() in (" ", "\t", "\r"):
            self._avancar()

    def _ler_numero(self):
        linha, coluna = self.linha, self.coluna
        num = ""
        is_decimal = False
        while self._atual() and (self._atual().isdigit() or self._atual() == "."):
            if self._atual() == ".":
                if is_decimal:
                    raise ErroLexico("número com mais de um ponto decimal", linha, coluna)
                is_decimal = True
            num += self._avancar()
        tipo = TipoToken.DECIMAL if is_decimal else TipoToken.INTEIRO
        return Token(tipo, num, linha, coluna)

    def _ler_string(self):
        linha, coluna = self.linha, self.coluna
        delimitador = self._avancar()
        texto = ""
        while self._atual() and self._atual() != delimitador:
            if self._atual() == "\n":
                raise ErroLexico("string não fechada antes do fim da linha", linha, coluna)
            if self._atual() == "\\" and self._proximo() in ('"', "'", "\\", "n", "t"):
                self._avancar()
                esc = self._avancar()
                texto += {"n": "\n", "t": "\t"}.get(esc, esc)
            else:
                texto += self._avancar()
        if self._atual() is None:
            raise ErroLexico("string não fechada antes do fim do arquivo", linha, coluna)
        self._avancar()
        return Token(TipoToken.STRING, texto, linha, coluna)

    def _ler_identificador(self):
        linha, coluna = self.linha, self.coluna
        nome = ""
        while self._atual() and (self._atual().isalnum() or self._atual() == "_"):
            nome += self._avancar()
        tipo = PALAVRAS_CHAVE.get(nome, TipoToken.IDENTIFICADOR)
        return Token(tipo, nome, linha, coluna)

    def _ultimo_token_permite_fim_instrucao(self):
        if not self.tokens:
            return False
        ultimo = self.tokens[-1].tipo
        return ultimo in (
            TipoToken.IDENTIFICADOR,
            TipoToken.INTEIRO,
            TipoToken.DECIMAL,
            TipoToken.STRING,
            TipoToken.TRUE,
            TipoToken.FALSE,
            TipoToken.FECHA_PAREN,
            TipoToken.FECHA_CHAVE,
            TipoToken.RETURN,
        )

    def tokenizar(self):
        while self.pos < len(self.codigo):
            ch = self._atual()

            if ch in (" ", "\t", "\r"):
                self._pular_espacos()
                continue

            if ch == "\n":
                linha, coluna = self.linha, self.coluna
                self._avancar()
                if self._ultimo_token_permite_fim_instrucao():
                    self.tokens.append(Token(TipoToken.FIM_INSTRUCAO, "\\n", linha, coluna))
                continue

            if ch == "/" and self._proximo() == "/":
                while self._atual() and self._atual() != "\n":
                    self._avancar()
                continue

            if ch == "/" and self._proximo() == "*":
                linha, coluna = self.linha, self.coluna
                self._avancar()
                self._avancar()
                while self._atual():
                    if self._atual() == "*" and self._proximo() == "/":
                        self._avancar()
                        self._avancar()
                        break
                    self._avancar()
                else:
                    raise ErroLexico("comentário de bloco não fechado", linha, coluna)
                continue

            if ch.isdigit():
                self.tokens.append(self._ler_numero())
                continue

            if ch in ('"', "'"):
                self.tokens.append(self._ler_string())
                continue

            if ch.isalpha() or ch == "_":
                self.tokens.append(self._ler_identificador())
                continue

            linha, coluna = self.linha, self.coluna

            if ch == ";":
                self._avancar()
                self.tokens.append(Token(TipoToken.FIM_INSTRUCAO, ";", linha, coluna))
                continue

            simples = {
                "+": TipoToken.MAIS,
                "-": TipoToken.MENOS,
                "*": TipoToken.ASTERISCO,
                "(": TipoToken.ABRE_PAREN,
                ")": TipoToken.FECHA_PAREN,
                "{": TipoToken.ABRE_CHAVE,
                "}": TipoToken.FECHA_CHAVE,
                ",": TipoToken.VIRGULA,
            }

            if ch in simples:
                self.tokens.append(Token(simples[ch], ch, linha, coluna))
                self._avancar()
                continue

            if ch == "/" :
                self.tokens.append(Token(TipoToken.BARRA, ch, linha, coluna))
                self._avancar()
                continue

            if ch == "=" and self._proximo() == "=":
                self._avancar()
                self._avancar()
                self.tokens.append(Token(TipoToken.IGUAL_IGUAL, "==", linha, coluna))
                continue

            if ch == "!" and self._proximo() == "=":
                self._avancar()
                self._avancar()
                self.tokens.append(Token(TipoToken.DIFERENTE, "!=", linha, coluna))
                continue

            if ch == "=":
                self._avancar()
                self.tokens.append(Token(TipoToken.IGUAL, "=", linha, coluna))
                continue

            if ch == ">" :
                self._avancar()
                self.tokens.append(Token(TipoToken.MAIOR, ">", linha, coluna))
                continue

            if ch == "<":
                self._avancar()
                self.tokens.append(Token(TipoToken.MENOR, "<", linha, coluna))
                continue

            if ch == "&" and self._proximo() == "&":
                self._avancar()
                self._avancar()
                self.tokens.append(Token(TipoToken.E_LOGICO, "&&", linha, coluna))
                continue

            if ch == "|" and self._proximo() == "|":
                self._avancar()
                self._avancar()
                self.tokens.append(Token(TipoToken.OU_LOGICO, "||", linha, coluna))
                continue

            if ch == "!":
                self._avancar()
                self.tokens.append(Token(TipoToken.NAO, "!", linha, coluna))
                continue

            raise ErroLexico(f"caractere inesperado: {ch!r}", linha, coluna)

        self.tokens.append(Token(TipoToken.EOF, "", self.linha, self.coluna))
        return self.tokens
