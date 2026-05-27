import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from mini_compilador.lexer import Lexer
from mini_compilador.parser import Parser
from mini_compilador.semantic import AnalisadorSemantico


def erros_semanticos(codigo):
    tokens = Lexer(codigo).tokenizar()
    if Parser(tokens).analisar():
        return []
    tokens2 = Lexer(codigo).tokenizar()
    return AnalisadorSemantico(tokens2).analisar()


def sem_erros(codigo):
    return len(erros_semanticos(codigo)) == 0


def com_erro(codigo, fragmento):
    erros = erros_semanticos(codigo)
    msgs = [str(e) for e in erros]
    return any(fragmento in m for m in msgs)


class TestDeclaracoes(unittest.TestCase):
    def test_variavel_valida(self):
        self.assertTrue(sem_erros("let x = 10"))

    def test_const_valida(self):
        self.assertTrue(sem_erros("const PI = 3.14"))

    def test_redeclaracao(self):
        self.assertTrue(com_erro("let x = 1\nlet x = 2", "já declarada"))

    def test_reatribuicao_const(self):
        codigo = "const PI = 3.14\nPI = 3.0"
        self.assertTrue(com_erro(codigo, "constante"))

    def test_variavel_nao_declarada(self):
        self.assertTrue(com_erro("let y = z + 1", "não declarada"))


class TestEscopos(unittest.TestCase):
    def test_variavel_local_nao_vaza(self):
        codigo = """
function f() {
    let local = 10
}
let r = local + 1
"""
        self.assertTrue(com_erro(codigo, "não declarada"))

    def test_variavel_externa_acessivel(self):
        codigo = """
let x = 10
function f() {
    let r = x + 1
    return r
}
"""
        self.assertTrue(sem_erros(codigo))

    def test_parametro_acessivel_no_corpo(self):
        codigo = "function f(a, b) { return a + b }"
        self.assertTrue(sem_erros(codigo))


class TestFuncoes(unittest.TestCase):
    def test_funcao_redeclarada(self):
        codigo = "function f() {}\nfunction f() {}"
        self.assertTrue(com_erro(codigo, "já declarada"))

    def test_argumentos_corretos(self):
        codigo = "function soma(a, b) { return a + b }\nlet r = soma(1, 2)"
        self.assertTrue(sem_erros(codigo))

    def test_argumentos_incorretos(self):
        codigo = "function soma(a, b) { return a + b }\nlet r = soma(1, 2, 3)"
        self.assertTrue(com_erro(codigo, "argumento"))


class TestTipos(unittest.TestCase):
    def test_subtracao_string(self):
        codigo = 'let x = "a" - "b"'
        self.assertTrue(com_erro(codigo, "strings"))

    def test_multiplicacao_string(self):
        codigo = 'let x = "a" * 2'
        self.assertTrue(com_erro(codigo, "strings"))

    def test_adicao_string_valida(self):
        codigo = 'let x = "hello" + " world"'
        self.assertTrue(sem_erros(codigo))

    def test_operacao_numerica_valida(self):
        self.assertTrue(sem_erros("let r = 1 + 2 * 3 - 4 / 2"))


class TestProgramaCompleto(unittest.TestCase):
    def test_programa_valido(self):
        codigo = """
let x = 10
const y = 3.14
function soma(a, b) {
    return a + b
}
let r = soma(x, 5)
if (r > 10) {
    let dobro = r * 2
}
let i = 0
while (i < 5) {
    i = i + 1
}
"""
        self.assertTrue(sem_erros(codigo))


if __name__ == "__main__":
    unittest.main()
