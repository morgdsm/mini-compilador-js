from .tokens import TipoToken
from .errors import ErroSintatico


_DESC_TOKEN = {
    TipoToken.ABRE_CHAVE: "'{'",
    TipoToken.FECHA_CHAVE: "'}'",
    TipoToken.ABRE_PAREN: "'('",
    TipoToken.FECHA_PAREN: "')'",
    TipoToken.IGUAL: "'='",
    TipoToken.VIRGULA: "','",
    TipoToken.FIM_INSTRUCAO: "fim de instrução",
    TipoToken.IDENTIFICADOR: "identificador",
    TipoToken.EOF: "fim de arquivo",
}


class _EscopoDeclaracoes:
    def __init__(self, pai=None):
        self.declarados = set()
        self.pai = pai

    def declarar(self, nome):
        self.declarados.add(nome)

    def contem(self, nome):
        if nome in self.declarados:
            return True
        return self.pai.contem(nome) if self.pai else False


class Parser:
    _SYNC_DECL = frozenset({
        TipoToken.FIM_INSTRUCAO,
        TipoToken.FECHA_CHAVE,
        TipoToken.LET,
        TipoToken.CONST,
        TipoToken.VAR,
        TipoToken.FUNCTION,
        TipoToken.IF,
        TipoToken.WHILE,
        TipoToken.RETURN,
        TipoToken.ELSE,
        TipoToken.EOF,
    })

    _SYNC_EXPR = _SYNC_DECL | frozenset({
        TipoToken.FECHA_PAREN,
        TipoToken.VIRGULA,
    })

    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.erros = []
        self._escopo = _EscopoDeclaracoes()

    def _atual(self):
        return self.tokens[self.pos]

    def _descricao(self, tipo):
        return _DESC_TOKEN.get(tipo, tipo.name.lower())

    def _descricao_atual(self):
        token = self._atual()
        if token.tipo == TipoToken.EOF:
            return "fim de arquivo"
        if token.tipo == TipoToken.IDENTIFICADOR:
            return f"'{token.valor}'"
        return self._descricao(token.tipo)

    def _erro(self, mensagem, linha, coluna):
        self.erros.append(ErroSintatico(mensagem, linha, coluna))

    def _consumir(self, tipo, contexto=None):
        token = self._atual()
        if token.tipo == tipo:
            self.pos += 1
            return token

        esperado = self._descricao(tipo)
        if contexto:
            msg = f"Esperado {esperado} {contexto}, encontrado {self._descricao_atual()}"
        else:
            msg = f"Esperado {esperado}, encontrado {self._descricao_atual()}"
        self._erro(msg, token.linha, token.coluna)
        return None

    def _verificar(self, *tipos):
        return self._atual().tipo in tipos

    def _pular_fim_instrucao(self):
        while self._verificar(TipoToken.FIM_INSTRUCAO):
            self.pos += 1

    def _sincronizar(self, conjunto):
        while not self._verificar(TipoToken.EOF):
            if self._verificar(*conjunto):
                return
            self.pos += 1

    def _fim_instrucao(self):
        if self._verificar(TipoToken.FIM_INSTRUCAO):
            self.pos += 1
            return True
        token = self._atual()
        if token.tipo in (TipoToken.EOF, TipoToken.FECHA_CHAVE):
            return True
        self._erro(
            f"Esperado fim de instrução, encontrado {self._descricao_atual()}",
            token.linha,
            token.coluna,
        )
        self._sincronizar(self._SYNC_DECL)
        return False

    # ------------------------------------------------------------------ programa
    def analisar(self):
        self.erros = []
        self._escopo = _EscopoDeclaracoes()
        self._pular_fim_instrucao()
        while not self._verificar(TipoToken.EOF):
            self._declaracao()
            self._pular_fim_instrucao()
        return self.erros

    # ------------------------------------------------------------------ declarações
    def _declaracao(self):
        t = self._atual()

        if t.tipo == TipoToken.VAR:
            self._erro("'var' não é permitido; use 'let' ou 'const'", t.linha, t.coluna)
            self.pos += 1
            self._sincronizar_decl()
            return

        if t.tipo in (TipoToken.LET, TipoToken.CONST):
            self._decl_variavel()
            return

        if t.tipo == TipoToken.FUNCTION:
            self._decl_funcao()
            return

        if t.tipo == TipoToken.IF:
            self._stmt_if()
            return

        if t.tipo == TipoToken.WHILE:
            self._stmt_while()
            return

        if t.tipo == TipoToken.RETURN:
            self._stmt_return()
            return

        if (t.tipo == TipoToken.IDENTIFICADOR
                and self.pos + 1 < len(self.tokens)
                and self.tokens[self.pos + 1].tipo == TipoToken.IGUAL):
            self._stmt_atribuicao()
            return

        if not self._expressao():
            self._sincronizar_decl()
            return
        self._fim_instrucao()

    def _sincronizar_decl(self):
        self._sincronizar(self._SYNC_DECL)

    def _decl_variavel(self):
        self.pos += 1  # let | const
        token_nome = self._consumir(TipoToken.IDENTIFICADOR, "após palavra-chave de declaração")
        if token_nome is None:
            self._sincronizar_decl()
            return
        if self._consumir(TipoToken.IGUAL, "após nome de variável") is None:
            self._sincronizar_decl()
            return
        if not self._expressao():
            self._sincronizar_decl()
            return
        self._fim_instrucao()
        self._escopo.declarar(token_nome.valor)

    def _decl_funcao(self):
        self.pos += 1  # function
        token_nome = self._consumir(TipoToken.IDENTIFICADOR, "após 'function'")
        if token_nome is None:
            self._sincronizar_decl()
            return
        self._escopo.declarar(token_nome.valor)

        if self._consumir(TipoToken.ABRE_PAREN, "após nome de função") is None:
            self._sincronizar_decl()
            return

        escopo_anterior = self._escopo
        self._escopo = _EscopoDeclaracoes(pai=escopo_anterior)
        self._lista_parametros()

        if self._consumir(TipoToken.FECHA_PAREN, "após parâmetros") is None:
            self._escopo = escopo_anterior
            self._sincronizar_decl()
            return

        self._bloco()
        self._escopo = escopo_anterior

    def _lista_parametros(self):
        if self._verificar(TipoToken.FECHA_PAREN):
            return
        token = self._consumir(TipoToken.IDENTIFICADOR, "como parâmetro")
        if token:
            self._escopo.declarar(token.valor)
        while self._verificar(TipoToken.VIRGULA):
            self.pos += 1
            token = self._consumir(TipoToken.IDENTIFICADOR, "após ','")
            if token:
                self._escopo.declarar(token.valor)

    def _bloco(self):
        if self._consumir(TipoToken.ABRE_CHAVE) is None:
            self._sincronizar_decl()
            return

        self._pular_fim_instrucao()
        escopo_anterior = self._escopo
        self._escopo = _EscopoDeclaracoes(pai=escopo_anterior)

        while not self._verificar(TipoToken.FECHA_CHAVE, TipoToken.EOF):
            self._declaracao()
            self._pular_fim_instrucao()

        if self._consumir(TipoToken.FECHA_CHAVE) is None:
            token = self._atual()
            self._erro(
                f"Esperado '}}', encontrado {self._descricao_atual()}",
                token.linha,
                token.coluna,
            )
            self._sincronizar_decl()

        self._escopo = escopo_anterior

    def _stmt_if(self):
        self.pos += 1  # if
        if self._consumir(TipoToken.ABRE_PAREN, "após 'if'") is None:
            self._sincronizar_decl()
            return
        if not self._expressao():
            self._sincronizar(self._SYNC_EXPR)
        if self._consumir(TipoToken.FECHA_PAREN, "após condição") is None:
            self._sincronizar_decl()
            return
        self._bloco()
        if self._verificar(TipoToken.ELSE):
            self.pos += 1
            self._bloco()

    def _stmt_while(self):
        self.pos += 1  # while
        if self._consumir(TipoToken.ABRE_PAREN, "após 'while'") is None:
            self._sincronizar_decl()
            return
        if not self._expressao():
            self._sincronizar(self._SYNC_EXPR)
        if self._consumir(TipoToken.FECHA_PAREN, "após condição") is None:
            self._sincronizar_decl()
            return
        self._bloco()

    def _stmt_return(self):
        self.pos += 1  # return
        if not self._verificar(TipoToken.FIM_INSTRUCAO, TipoToken.EOF, TipoToken.FECHA_CHAVE):
            if not self._expressao():
                self._sincronizar_decl()
                return
        self._fim_instrucao()

    def _stmt_atribuicao(self):
        token_nome = self._atual()
        nome = token_nome.valor
        if not self._escopo.contem(nome):
            self._erro(
                f"declaração implícita de '{nome}' não permitida; use 'let' ou 'const'",
                token_nome.linha,
                token_nome.coluna,
            )
        self.pos += 1  # identificador
        if self._consumir(TipoToken.IGUAL) is None:
            self._sincronizar_decl()
            return
        if not self._expressao():
            self._sincronizar_decl()
            return
        self._fim_instrucao()

    # ------------------------------------------------------------------ expressões
    def _expressao(self):
        return self._expr_logico_ou()

    def _expr_logico_ou(self):
        if not self._expr_logico_e():
            return False
        while self._verificar(TipoToken.OU_LOGICO):
            self.pos += 1
            if not self._expr_logico_e():
                return False
        return True

    def _expr_logico_e(self):
        if not self._expr_relacional():
            return False
        while self._verificar(TipoToken.E_LOGICO):
            self.pos += 1
            if not self._expr_relacional():
                return False
        return True

    def _expr_relacional(self):
        if not self._expr_aditiva():
            return False
        if self._verificar(
            TipoToken.MAIOR, TipoToken.MENOR, TipoToken.IGUAL_IGUAL, TipoToken.DIFERENTE
        ):
            self.pos += 1
            return self._expr_aditiva()
        return True

    def _expr_aditiva(self):
        if not self._expr_multiplicativa():
            return False
        while self._verificar(TipoToken.MAIS, TipoToken.MENOS):
            self.pos += 1
            if not self._expr_multiplicativa():
                return False
        return True

    def _expr_multiplicativa(self):
        if not self._expr_unaria():
            return False
        while self._verificar(TipoToken.ASTERISCO, TipoToken.BARRA):
            self.pos += 1
            if not self._expr_unaria():
                return False
        return True

    def _expr_unaria(self):
        if self._verificar(TipoToken.NAO, TipoToken.MENOS):
            self.pos += 1
            return self._expr_unaria()
        return self._expr_primaria()

    def _expr_primaria(self):
        t = self._atual()

        if t.tipo in (TipoToken.INTEIRO, TipoToken.DECIMAL, TipoToken.STRING,
                      TipoToken.TRUE, TipoToken.FALSE):
            self.pos += 1
            return True

        if t.tipo == TipoToken.IDENTIFICADOR:
            self.pos += 1
            if self._verificar(TipoToken.ABRE_PAREN):
                self.pos += 1
                self._lista_argumentos()
                if self._consumir(TipoToken.FECHA_PAREN, "após argumentos") is None:
                    self._sincronizar(self._SYNC_EXPR)
                    return False
            return True

        if t.tipo == TipoToken.ABRE_PAREN:
            self.pos += 1
            if not self._expressao():
                self._sincronizar(self._SYNC_EXPR)
                return False
            if self._consumir(TipoToken.FECHA_PAREN, "após expressão") is None:
                self._sincronizar(self._SYNC_EXPR)
                return False
            return True

        self._erro(
            f"token inesperado na expressão: {self._descricao_atual()}",
            t.linha,
            t.coluna,
        )
        self.pos += 1
        return False

    def _lista_argumentos(self):
        if self._verificar(TipoToken.FECHA_PAREN):
            return
        if not self._expressao():
            self._sincronizar(self._SYNC_EXPR)
            return
        while self._verificar(TipoToken.VIRGULA):
            self.pos += 1
            if not self._expressao():
                self._sincronizar(self._SYNC_EXPR)
                return
