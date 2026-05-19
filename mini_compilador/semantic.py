from .tokens import TipoToken, Token
from .errors import ErroSemantico


class TabelaSimbolos:
    def __init__(self, pai=None):
        self.simbolos = {}
        self.pai = pai

    def declarar(self, nome, tipo_decl, linha, coluna):
        if nome in self.simbolos:
            raise ErroSemantico(f"variável '{nome}' já declarada neste escopo", linha, coluna)
        self.simbolos[nome] = {"tipo_decl": tipo_decl, "tipo_valor": None}

    def buscar(self, nome):
        if nome in self.simbolos:
            return self.simbolos[nome]
        if self.pai:
            return self.pai.buscar(nome)
        return None

    def atualizar_tipo(self, nome, tipo_valor):
        if nome in self.simbolos:
            self.simbolos[nome]["tipo_valor"] = tipo_valor
            return True
        if self.pai:
            return self.pai.atualizar_tipo(nome, tipo_valor)
        return False


class AnalisadorSemantico:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.escopo_atual = TabelaSimbolos()
        self.erros = []
        self.funcoes = {}

    def _atual(self):
        return self.tokens[self.pos]

    def _consumir(self, tipo):
        token = self.tokens[self.pos]
        if token.tipo == tipo:
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
        # tolerante: sem erro se ausente

    def analisar(self):
        self._pular_fim_instrucao()
        while not self._verificar(TipoToken.EOF):
            self._declaracao()
            self._pular_fim_instrucao()
        return self.erros

    def _declaracao(self):
        t = self._atual()

        if t.tipo in (TipoToken.LET, TipoToken.CONST):
            self._decl_variavel()
        elif t.tipo == TipoToken.FUNCTION:
            self._decl_funcao()
        elif t.tipo == TipoToken.IF:
            self._stmt_if()
        elif t.tipo == TipoToken.WHILE:
            self._stmt_while()
        elif t.tipo == TipoToken.RETURN:
            self._stmt_return()
        elif (t.tipo == TipoToken.IDENTIFICADOR
              and self.pos + 1 < len(self.tokens)
              and self.tokens[self.pos + 1].tipo == TipoToken.IGUAL):
            self._stmt_atribuicao()
        else:
            self._expressao()
            self._fim_instrucao()

    def _decl_variavel(self):
        tipo_decl = self._atual().tipo
        self.pos += 1
        token_nome = self._consumir(TipoToken.IDENTIFICADOR)
        nome = token_nome.valor
        self._consumir(TipoToken.IGUAL)

        tipo_valor = self._expressao()
        self._fim_instrucao()

        try:
            self.escopo_atual.declarar(nome, tipo_decl, token_nome.linha, token_nome.coluna)
            self.escopo_atual.atualizar_tipo(nome, tipo_valor)
        except ErroSemantico as e:
            self.erros.append(e)

    def _decl_funcao(self):
        self.pos += 1  # function
        token_nome = self._consumir(TipoToken.IDENTIFICADOR)
        nome = token_nome.valor

        if nome in self.funcoes:
            self.erros.append(
                ErroSemantico(f"função '{nome}' já declarada", token_nome.linha, token_nome.coluna)
            )

        self._consumir(TipoToken.ABRE_PAREN)
        params = self._lista_parametros()
        self._consumir(TipoToken.FECHA_PAREN)

        self.funcoes[nome] = len(params)

        escopo_anterior = self.escopo_atual
        self.escopo_atual = TabelaSimbolos(pai=escopo_anterior)
        for p in params:
            try:
                self.escopo_atual.declarar(p.valor, TipoToken.LET, p.linha, p.coluna)
            except ErroSemantico as e:
                self.erros.append(e)

        self._bloco()
        self.escopo_atual = escopo_anterior

    def _lista_parametros(self):
        params = []
        if self._verificar(TipoToken.FECHA_PAREN):
            return params
        params.append(self._consumir(TipoToken.IDENTIFICADOR))
        while self._verificar(TipoToken.VIRGULA):
            self.pos += 1
            params.append(self._consumir(TipoToken.IDENTIFICADOR))
        return params

    def _bloco(self):
        self._consumir(TipoToken.ABRE_CHAVE)
        self._pular_fim_instrucao()
        escopo_anterior = self.escopo_atual
        self.escopo_atual = TabelaSimbolos(pai=escopo_anterior)
        while not self._verificar(TipoToken.FECHA_CHAVE, TipoToken.EOF):
            self._declaracao()
            self._pular_fim_instrucao()
        self._consumir(TipoToken.FECHA_CHAVE)
        self.escopo_atual = escopo_anterior

    def _stmt_if(self):
        self.pos += 1
        self._consumir(TipoToken.ABRE_PAREN)
        self._expressao()
        self._consumir(TipoToken.FECHA_PAREN)
        self._bloco()
        if self._verificar(TipoToken.ELSE):
            self.pos += 1
            self._bloco()

    def _stmt_while(self):
        self.pos += 1
        self._consumir(TipoToken.ABRE_PAREN)
        self._expressao()
        self._consumir(TipoToken.FECHA_PAREN)
        self._bloco()

    def _stmt_return(self):
        self.pos += 1
        if not self._verificar(TipoToken.FIM_INSTRUCAO, TipoToken.EOF, TipoToken.FECHA_CHAVE):
            self._expressao()
        self._fim_instrucao()

    def _stmt_atribuicao(self):
        token_nome = self._consumir(TipoToken.IDENTIFICADOR)
        self.pos += 1  # =
        nome = token_nome.valor
        info = self.escopo_atual.buscar(nome)
        if info is None:
            self.erros.append(
                ErroSemantico(f"variável '{nome}' não declarada", token_nome.linha, token_nome.coluna)
            )
        elif info["tipo_decl"] == TipoToken.CONST:
            self.erros.append(
                ErroSemantico(f"não é possível reatribuir constante '{nome}'",
                              token_nome.linha, token_nome.coluna)
            )
        tipo_valor = self._expressao()
        if info:
            self.escopo_atual.atualizar_tipo(nome, tipo_valor)
        self._fim_instrucao()

    # ------------------------------------------------------------------ expressões
    def _expressao(self):
        return self._expr_logico_ou()

    def _expr_logico_ou(self):
        t = self._expr_logico_e()
        while self._verificar(TipoToken.OU_LOGICO):
            self.pos += 1
            self._expr_logico_e()
            t = "bool"
        return t

    def _expr_logico_e(self):
        t = self._expr_relacional()
        while self._verificar(TipoToken.E_LOGICO):
            self.pos += 1
            self._expr_relacional()
            t = "bool"
        return t

    def _expr_relacional(self):
        t = self._expr_aditiva()
        if self._verificar(
            TipoToken.MAIOR, TipoToken.MENOR, TipoToken.IGUAL_IGUAL, TipoToken.DIFERENTE
        ):
            self.pos += 1
            self._expr_aditiva()
            return "bool"
        return t

    def _expr_aditiva(self):
        t = self._expr_multiplicativa()
        while self._verificar(TipoToken.MAIS, TipoToken.MENOS):
            op = self._atual()
            self.pos += 1
            t2 = self._expr_multiplicativa()
            if op.tipo == TipoToken.MAIS:
                if t in ("inteiro", "decimal") and t2 in ("inteiro", "decimal"):
                    t = "decimal" if "decimal" in (t, t2) else "inteiro"
                elif t == "string" or t2 == "string":
                    t = "string"
                else:
                    t = t or t2
            else:
                if t == "string" or t2 == "string":
                    self.erros.append(
                        ErroSemantico("operação '-' inválida com strings", op.linha, op.coluna)
                    )
                t = "decimal" if "decimal" in (t, t2) else "inteiro"
        return t

    def _expr_multiplicativa(self):
        t = self._expr_unaria()
        while self._verificar(TipoToken.ASTERISCO, TipoToken.BARRA):
            op = self._atual()
            self.pos += 1
            t2 = self._expr_unaria()
            if t == "string" or t2 == "string":
                self.erros.append(
                    ErroSemantico("operação aritmética inválida com strings", op.linha, op.coluna)
                )
            t = "decimal" if "decimal" in (t, t2) else "inteiro"
        return t

    def _expr_unaria(self):
        if self._verificar(TipoToken.NAO):
            self.pos += 1
            self._expr_unaria()
            return "bool"
        if self._verificar(TipoToken.MENOS):
            self.pos += 1
            t = self._expr_unaria()
            if t == "string":
                token = self.tokens[self.pos - 1]
                self.erros.append(
                    ErroSemantico("operador unário '-' inválido para string", token.linha, token.coluna)
                )
            return t
        return self._expr_primaria()

    def _expr_primaria(self):
        t = self._atual()

        if t.tipo == TipoToken.INTEIRO:
            self.pos += 1
            return "inteiro"

        if t.tipo == TipoToken.DECIMAL:
            self.pos += 1
            return "decimal"

        if t.tipo == TipoToken.STRING:
            self.pos += 1
            return "string"

        if t.tipo in (TipoToken.TRUE, TipoToken.FALSE):
            self.pos += 1
            return "bool"

        if t.tipo == TipoToken.IDENTIFICADOR:
            self.pos += 1
            if self._verificar(TipoToken.ABRE_PAREN):
                return self._chamada_funcao(t)
            info = self.escopo_atual.buscar(t.valor)
            if info is None:
                self.erros.append(
                    ErroSemantico(f"variável '{t.valor}' não declarada", t.linha, t.coluna)
                )
                return None
            return info["tipo_valor"]

        if t.tipo == TipoToken.ABRE_PAREN:
            self.pos += 1
            tp = self._expressao()
            self._consumir(TipoToken.FECHA_PAREN)
            return tp

        # token inesperado: avança para não travar
        self.pos += 1
        return None

    def _chamada_funcao(self, token_nome):
        self.pos += 1  # (
        args = self._lista_argumentos()
        self._consumir(TipoToken.FECHA_PAREN)

        nome = token_nome.valor
        if nome in self.funcoes:
            esperado = self.funcoes[nome]
            if len(args) != esperado:
                self.erros.append(
                    ErroSemantico(
                        f"função '{nome}' espera {esperado} argumento(s), recebeu {len(args)}",
                        token_nome.linha,
                        token_nome.coluna,
                    )
                )
        return None

    def _lista_argumentos(self):
        args = []
        if self._verificar(TipoToken.FECHA_PAREN):
            return args
        args.append(self._expressao())
        while self._verificar(TipoToken.VIRGULA):
            self.pos += 1
            args.append(self._expressao())
        return args
