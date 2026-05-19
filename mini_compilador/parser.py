from .tokens import TipoToken
from .errors import ErroSintatico


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def _atual(self):
        return self.tokens[self.pos]

    def _consumir(self, tipo, mensagem=None):
        token = self._atual()
        if token.tipo != tipo:
            msg = mensagem or f"esperado {tipo.name}, encontrado {token.valor!r}"
            raise ErroSintatico(msg, token.linha, token.coluna)
        self.pos += 1
        return token

    def _verificar(self, *tipos):
        return self._atual().tipo in tipos

    def _pular_fim_instrucao(self):
        while self._verificar(TipoToken.FIM_INSTRUCAO):
            self.pos += 1

    def _fim_instrucao(self):
        if self._verificar(TipoToken.FIM_INSTRUCAO):
            self.pos += 1
            return
        token = self._atual()
        if token.tipo in (TipoToken.EOF, TipoToken.FECHA_CHAVE):
            return
        raise ErroSintatico(
            f"esperado fim de instrução, encontrado {token.valor!r}",
            token.linha,
            token.coluna,
        )

    # ------------------------------------------------------------------ programa
    def analisar(self):
        self._pular_fim_instrucao()
        while not self._verificar(TipoToken.EOF):
            self._declaracao()
            self._pular_fim_instrucao()

    # ------------------------------------------------------------------ declarações
    def _declaracao(self):
        t = self._atual()

        if t.tipo == TipoToken.VAR:
            raise ErroSintatico(
                "'var' não é permitido; use 'let' ou 'const'", t.linha, t.coluna
            )

        if t.tipo in (TipoToken.LET, TipoToken.CONST):
            return self._decl_variavel()

        if t.tipo == TipoToken.FUNCTION:
            return self._decl_funcao()

        if t.tipo == TipoToken.IF:
            return self._stmt_if()

        if t.tipo == TipoToken.WHILE:
            return self._stmt_while()

        if t.tipo == TipoToken.RETURN:
            return self._stmt_return()

        if t.tipo == TipoToken.IDENTIFICADOR and self.tokens[self.pos + 1].tipo == TipoToken.IGUAL:
            return self._stmt_atribuicao()

        # expressão solta (chamada de função, etc.)
        self._expressao()
        self._fim_instrucao()

    def _decl_variavel(self):
        self.pos += 1  # let | const
        token_nome = self._consumir(TipoToken.IDENTIFICADOR, "esperado nome de variável")
        self._consumir(TipoToken.IGUAL, "esperado '=' após nome de variável")
        self._expressao()
        self._fim_instrucao()
        return ("decl_var", token_nome.valor)

    def _decl_funcao(self):
        self.pos += 1  # function
        token_nome = self._consumir(TipoToken.IDENTIFICADOR, "esperado nome de função")
        self._consumir(TipoToken.ABRE_PAREN, "esperado '(' após nome de função")
        self._lista_parametros()
        self._consumir(TipoToken.FECHA_PAREN, "esperado ')' após parâmetros")
        self._bloco()
        return ("decl_func", token_nome.valor)

    def _lista_parametros(self):
        if self._verificar(TipoToken.FECHA_PAREN):
            return
        self._consumir(TipoToken.IDENTIFICADOR, "esperado nome de parâmetro")
        while self._verificar(TipoToken.VIRGULA):
            self.pos += 1
            self._consumir(TipoToken.IDENTIFICADOR, "esperado nome de parâmetro")

    def _bloco(self):
        self._consumir(TipoToken.ABRE_CHAVE, "esperado '{'")
        self._pular_fim_instrucao()
        while not self._verificar(TipoToken.FECHA_CHAVE, TipoToken.EOF):
            self._declaracao()
            self._pular_fim_instrucao()
        self._consumir(TipoToken.FECHA_CHAVE, "esperado '}'")

    def _stmt_if(self):
        self.pos += 1  # if
        self._consumir(TipoToken.ABRE_PAREN, "esperado '(' após 'if'")
        self._expressao()
        self._consumir(TipoToken.FECHA_PAREN, "esperado ')' após condição")
        self._bloco()
        if self._verificar(TipoToken.ELSE):
            self.pos += 1
            self._bloco()

    def _stmt_while(self):
        self.pos += 1  # while
        self._consumir(TipoToken.ABRE_PAREN, "esperado '(' após 'while'")
        self._expressao()
        self._consumir(TipoToken.FECHA_PAREN, "esperado ')' após condição")
        self._bloco()

    def _stmt_return(self):
        self.pos += 1  # return
        if not self._verificar(TipoToken.FIM_INSTRUCAO, TipoToken.EOF, TipoToken.FECHA_CHAVE):
            self._expressao()
        self._fim_instrucao()

    def _stmt_atribuicao(self):
        self.pos += 1  # identificador
        self.pos += 1  # =
        self._expressao()
        self._fim_instrucao()

    # ------------------------------------------------------------------ expressões
    def _expressao(self):
        return self._expr_logico_ou()

    def _expr_logico_ou(self):
        self._expr_logico_e()
        while self._verificar(TipoToken.OU_LOGICO):
            self.pos += 1
            self._expr_logico_e()

    def _expr_logico_e(self):
        self._expr_relacional()
        while self._verificar(TipoToken.E_LOGICO):
            self.pos += 1
            self._expr_relacional()

    def _expr_relacional(self):
        self._expr_aditiva()
        if self._verificar(
            TipoToken.MAIOR, TipoToken.MENOR, TipoToken.IGUAL_IGUAL, TipoToken.DIFERENTE
        ):
            self.pos += 1
            self._expr_aditiva()

    def _expr_aditiva(self):
        self._expr_multiplicativa()
        while self._verificar(TipoToken.MAIS, TipoToken.MENOS):
            self.pos += 1
            self._expr_multiplicativa()

    def _expr_multiplicativa(self):
        self._expr_unaria()
        while self._verificar(TipoToken.ASTERISCO, TipoToken.BARRA):
            self.pos += 1
            self._expr_unaria()

    def _expr_unaria(self):
        if self._verificar(TipoToken.NAO, TipoToken.MENOS):
            self.pos += 1
            self._expr_unaria()
            return
        self._expr_primaria()

    def _expr_primaria(self):
        t = self._atual()

        if t.tipo in (TipoToken.INTEIRO, TipoToken.DECIMAL, TipoToken.STRING,
                      TipoToken.TRUE, TipoToken.FALSE):
            self.pos += 1
            return

        if t.tipo == TipoToken.IDENTIFICADOR:
            self.pos += 1
            if self._verificar(TipoToken.ABRE_PAREN):
                self.pos += 1
                self._lista_argumentos()
                self._consumir(TipoToken.FECHA_PAREN, "esperado ')' após argumentos")
            return

        if t.tipo == TipoToken.ABRE_PAREN:
            self.pos += 1
            self._expressao()
            self._consumir(TipoToken.FECHA_PAREN, "esperado ')' após expressão")
            return

        raise ErroSintatico(
            f"token inesperado na expressão: {t.valor!r}", t.linha, t.coluna
        )

    def _lista_argumentos(self):
        if self._verificar(TipoToken.FECHA_PAREN):
            return
        self._expressao()
        while self._verificar(TipoToken.VIRGULA):
            self.pos += 1
            self._expressao()
