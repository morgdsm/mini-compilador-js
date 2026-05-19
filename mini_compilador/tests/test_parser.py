import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from mini_compilador.lexer import Lexer
from mini_compilador.parser import Parser
from mini_compilador.errors import ErroSintatico


def analisar(codigo):
    tokens = Lexer(codigo).tokenizar()
    Parser(tokens).analisar()


def deve_falhar(codigo):
    with unittest.TestCase().assertRaises(ErroSintatico):
        analisar(codigo)


class TestDeclaracoes(unittest.TestCase):
    def test_let_simples(self):
        analisar("let x = 10")

    def test_const_simples(self):
        analisar("const PI = 3.14")

    def test_let_string(self):
        analisar('let nome = "joao"')

    def test_var_proibido(self):
        with self.assertRaises(ErroSintatico):
            analisar("var x = 1")

    def test_declaracao_sem_valor(self):
        with self.assertRaises(ErroSintatico):
            analisar("let x")


class TestFuncoes(unittest.TestCase):
    def test_funcao_sem_parametros(self):
        analisar("function f() { return 1 }")

    def test_funcao_com_parametros(self):
        analisar("function soma(a, b) { return a + b }")

    def test_funcao_vazia(self):
        analisar("function vazia() {}")

    def test_funcao_com_corpo(self):
        analisar("""
        function fatorial(n) {
            let r = 1
            while (n > 1) {
                r = r * n
                n = n - 1
            }
            return r
        }
        """)


class TestControle(unittest.TestCase):
    def test_if_simples(self):
        analisar("if (x > 0) { let y = 1 }")

    def test_if_else(self):
        analisar("if (x > 0) { let y = 1 } else { let y = 0 }")

    def test_while(self):
        analisar("while (i < 10) { i = i + 1 }")

    def test_if_sem_parentes(self):
        with self.assertRaises(ErroSintatico):
            analisar("if x > 0 { }")


class TestExpressoes(unittest.TestCase):
    def test_aritmetica(self):
        analisar("let r = 1 + 2 * 3 - 4 / 2")

    def test_parenteses(self):
        analisar("let r = (1 + 2) * 3")

    def test_relacionais(self):
        analisar("let b = x > 0")
        analisar("let b = x == y")
        analisar("let b = x != y")

    def test_logicos(self):
        analisar("let b = x > 0 && y < 10")
        analisar("let b = a || b")
        analisar("let b = !ok")

    def test_chamada_funcao(self):
        analisar("let r = f(1, 2, 3)")

    def test_expressao_sem_operando(self):
        with self.assertRaises(ErroSintatico):
            analisar("let r = +")


class TestPontoVirgula(unittest.TestCase):
    def test_com_ponto_virgula(self):
        analisar("let x = 1; let y = 2;")

    def test_sem_ponto_virgula(self):
        analisar("let x = 1\nlet y = 2")

    def test_misto(self):
        analisar("let x = 1;\nlet y = 2")


if __name__ == "__main__":
    unittest.main()
