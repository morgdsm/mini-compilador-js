import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from mini_compilador.lexer import Lexer
from mini_compilador.tokens import TipoToken
from mini_compilador.errors import ErroLexico


def tokenizar(codigo):
    return Lexer(codigo).tokenizar()


def tipos(codigo):
    return [t.tipo for t in tokenizar(codigo)]


class TestTokensBasicos(unittest.TestCase):
    def test_inteiro(self):
        ts = tokenizar("42")
        self.assertEqual(ts[0].tipo, TipoToken.INTEIRO)
        self.assertEqual(ts[0].valor, "42")

    def test_decimal(self):
        ts = tokenizar("3.14")
        self.assertEqual(ts[0].tipo, TipoToken.DECIMAL)

    def test_string_dupla(self):
        ts = tokenizar('"hello"')
        self.assertEqual(ts[0].tipo, TipoToken.STRING)
        self.assertEqual(ts[0].valor, "hello")

    def test_string_simples(self):
        ts = tokenizar("'world'")
        self.assertEqual(ts[0].tipo, TipoToken.STRING)

    def test_palavras_chave(self):
        for palavra, tipo in [
            ("let", TipoToken.LET),
            ("const", TipoToken.CONST),
            ("var", TipoToken.VAR),
            ("if", TipoToken.IF),
            ("else", TipoToken.ELSE),
            ("while", TipoToken.WHILE),
            ("function", TipoToken.FUNCTION),
            ("return", TipoToken.RETURN),
        ]:
            with self.subTest(palavra=palavra):
                ts = tokenizar(palavra)
                self.assertEqual(ts[0].tipo, tipo)

    def test_identificador(self):
        ts = tokenizar("minhaVar")
        self.assertEqual(ts[0].tipo, TipoToken.IDENTIFICADOR)

    def test_operadores_aritmeticos(self):
        ts = tokenizar("+ - * /")
        self.assertEqual(ts[0].tipo, TipoToken.MAIS)
        self.assertEqual(ts[1].tipo, TipoToken.MENOS)
        self.assertEqual(ts[2].tipo, TipoToken.ASTERISCO)
        self.assertEqual(ts[3].tipo, TipoToken.BARRA)

    def test_operadores_relacionais(self):
        ts = tokenizar("> < == !=")
        self.assertEqual(ts[0].tipo, TipoToken.MAIOR)
        self.assertEqual(ts[1].tipo, TipoToken.MENOR)
        self.assertEqual(ts[2].tipo, TipoToken.IGUAL_IGUAL)
        self.assertEqual(ts[3].tipo, TipoToken.DIFERENTE)

    def test_operadores_logicos(self):
        ts = tokenizar("&& || !")
        self.assertEqual(ts[0].tipo, TipoToken.E_LOGICO)
        self.assertEqual(ts[1].tipo, TipoToken.OU_LOGICO)
        self.assertEqual(ts[2].tipo, TipoToken.NAO)


class TestFimInstrucao(unittest.TestCase):
    def test_ponto_virgula_gera_fim_instrucao(self):
        ts = tokenizar("let x = 1;")
        tipos_lista = [t.tipo for t in ts]
        self.assertIn(TipoToken.FIM_INSTRUCAO, tipos_lista)

    def test_quebra_linha_apos_expressao_gera_fim_instrucao(self):
        ts = tokenizar("let x = 1\nlet y = 2")
        tipos_lista = [t.tipo for t in ts]
        self.assertIn(TipoToken.FIM_INSTRUCAO, tipos_lista)

    def test_quebra_linha_apos_abre_chave_nao_gera_fim(self):
        codigo = "function f() {\nlet x = 1\n}"
        ts = tokenizar(codigo)
        tipos_lista = [t.tipo for t in ts]
        idx_chave = tipos_lista.index(TipoToken.ABRE_CHAVE)
        self.assertNotEqual(tipos_lista[idx_chave + 1], TipoToken.FIM_INSTRUCAO)


class TestComentarios(unittest.TestCase):
    def test_comentario_linha(self):
        ts = tokenizar("// isso é um comentário\nlet x = 1")
        self.assertEqual(ts[0].tipo, TipoToken.LET)

    def test_comentario_bloco(self):
        ts = tokenizar("/* bloco */\nlet x = 1")
        self.assertEqual(ts[0].tipo, TipoToken.LET)

    def test_comentario_bloco_nao_fechado(self):
        with self.assertRaises(ErroLexico):
            tokenizar("/* sem fechamento")


class TestErrosLexicos(unittest.TestCase):
    def test_caractere_invalido(self):
        with self.assertRaises(ErroLexico):
            tokenizar("let x = @")

    def test_string_nao_fechada(self):
        with self.assertRaises(ErroLexico):
            tokenizar('"sem fechamento')

    def test_numero_dois_pontos(self):
        with self.assertRaises(ErroLexico):
            tokenizar("3.14.15")


class TestPosicao(unittest.TestCase):
    def test_linha_e_coluna(self):
        ts = tokenizar("let x = 1")
        self.assertEqual(ts[0].linha, 1)
        self.assertEqual(ts[0].coluna, 1)
        self.assertEqual(ts[1].coluna, 5)

    def test_linha_segunda_linha(self):
        ts = tokenizar("let x = 1\nlet y = 2")
        let_y = next(t for t in ts if t.valor == "y")
        self.assertEqual(let_y.linha, 2)


if __name__ == "__main__":
    unittest.main()
