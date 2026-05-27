class ErroLexico(Exception):
    def __init__(self, mensagem, linha, coluna):
        self.linha = linha
        self.coluna = coluna
        super().__init__(f"Erro Léxico (Linha {linha}, Col {coluna}): {mensagem}")


class ErroSintatico(Exception):
    def __init__(self, mensagem, linha=None, coluna=None):
        self.linha = linha
        self.coluna = coluna
        if linha is not None and coluna is not None:
            prefixo = f"Erro Sintático (Linha {linha}, Col {coluna}):"
        elif linha is not None:
            prefixo = f"Erro Sintático (Linha {linha}):"
        else:
            prefixo = "Erro Sintático:"
        super().__init__(f"{prefixo} {mensagem}")


class ErroSemantico(Exception):
    def __init__(self, mensagem, linha=None, coluna=None):
        self.linha = linha
        self.coluna = coluna
        if linha is not None and coluna is not None:
            prefixo = f"Erro Semântico (Linha {linha}, Col {coluna}):"
        elif linha is not None:
            prefixo = f"Erro Semântico (Linha {linha}):"
        else:
            prefixo = "Erro Semântico:"
        super().__init__(f"{prefixo} {mensagem}")
