class ErroLexico(Exception):
    def __init__(self, mensagem, linha, coluna):
        self.linha = linha
        self.coluna = coluna
        super().__init__(f"[Léxico] Linha {linha}, Col {coluna}: {mensagem}")


class ErroSintatico(Exception):
    def __init__(self, mensagem, linha=None, coluna=None):
        self.linha = linha
        self.coluna = coluna
        pos = f" Linha {linha}, Col {coluna}:" if linha else ""
        super().__init__(f"[Sintático]{pos} {mensagem}")


class ErroSemantico(Exception):
    def __init__(self, mensagem, linha=None, coluna=None):
        self.linha = linha
        self.coluna = coluna
        pos = f" Linha {linha}, Col {coluna}:" if linha else ""
        super().__init__(f"[Semântico]{pos} {mensagem}")
