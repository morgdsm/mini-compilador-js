import sys
import io

if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf8"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

from .lexer import Lexer
from .parser import Parser
from .semantic import AnalisadorSemantico
from .errors import ErroLexico, ErroSemantico


def _cabecalho(fase):
    print(f"\n{'=' * 50}")
    print(f"  {fase}")
    print("=" * 50)


def compilar(caminho):
    try:
        with open(caminho, encoding="utf-8") as f:
            codigo = f.read()
    except FileNotFoundError:
        print(f"Arquivo não encontrado: {caminho}")
        sys.exit(1)

    # ── FASE 1: léxico ──────────────────────────────────────────────────────────
    _cabecalho("FASE 1 — ANÁLISE LÉXICA")

    try:
        lexer = Lexer(codigo)
        tokens = lexer.tokenizar()
    except ErroLexico as e:
        print(f"\n[ERRO] {e}")
        print("\nRESULTADO FINAL\nPrograma REJEITADO.")
        sys.exit(1)

    largura_tipo = max((len(t.tipo.name) for t in tokens), default=10)
    print(f"\n{'TIPO':<{largura_tipo}}  {'VALOR':<20}  L:C")
    print("-" * (largura_tipo + 30))
    for t in tokens:
        valor = repr(t.valor) if t.tipo.name in ("STRING",) else t.valor
        print(f"{t.tipo.name:<{largura_tipo}}  {str(valor):<20}  {t.linha}:{t.coluna}")

    # ── FASE 2: sintático ───────────────────────────────────────────────────────
    _cabecalho("FASE 2 — ANÁLISE SINTÁTICA")

    parser = Parser(tokens)
    erros_sintaticos = parser.analisar()

    if erros_sintaticos:
        for e in erros_sintaticos:
            print(f"\n[ERRO] {e}")
        print("\nRESULTADO FINAL\nPrograma REJEITADO.")
        sys.exit(1)

    print("\n[OK]\nSintaxe válida.")

    # ── FASE 3: semântico ───────────────────────────────────────────────────────
    _cabecalho("FASE 3 — ANÁLISE SEMÂNTICA")

    semantico = AnalisadorSemantico(tokens)
    erros = semantico.analisar()

    if erros:
        for e in erros:
            print(f"\n[ERRO] {e}")
        print("\nRESULTADO FINAL\nPrograma REJEITADO.")
        sys.exit(1)

    print("\n[OK]\nNenhum erro encontrado.")

    # ── RESULTADO ───────────────────────────────────────────────────────────────
    print("\n" + "=" * 50)
    print("  RESULTADO FINAL")
    print("=" * 50)
    print("\nPrograma ACEITO.")
