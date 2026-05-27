import os
import sys

from mini_compilador.main import compilar


PASTA_EXEMPLOS = os.path.join("mini_compilador", "examples")
EXTENSOES_SUPORTADAS = (".js", ".txt")


def listar_arquivos():
    if not os.path.isdir(PASTA_EXEMPLOS):
        return []
    return sorted(
        f for f in os.listdir(PASTA_EXEMPLOS) if f.endswith(EXTENSOES_SUPORTADAS)
    )


def imprimir_boas_vindas():
    print()
    print("=" * 60)
    print("  Ola, seja bem-vindo ao Mini-Compilador JavaScript!")
    print("=" * 60)
    print()
    print("Este compilador analisa arquivos .txt ou .js em tres fases:")
    print("  1. Lexica    - converte o codigo em tokens")
    print("  2. Sintatica - valida a estrutura gramatical")
    print("  3. Semantica - verifica escopos, tipos e declaracoes")
    print()
    print("Ao final, o programa e classificado como ACEITO ou REJEITADO.")
    print()
    print("Para que o compilador leia seus codigos, e necessario colocar")
    print(f"os arquivos .txt ou .js na pasta: {PASTA_EXEMPLOS}/")
    print()


def perguntar_prosseguir():
    while True:
        resposta = input("Deseja prosseguir? (s/n): ").strip().lower()
        if resposta in ("s", "sim", "y", "yes"):
            return True
        if resposta in ("n", "nao", "não", "no"):
            return False
        print("Resposta invalida. Use 's' para sim ou 'n' para nao.")


def imprimir_dica():
    print()
    print("DICA: use nomes curtos e objetivos para seus arquivos (.js/.txt), \n assim fica facil identifica-los na lista abaixo.")
    print()


def imprimir_arquivos(arquivos):
    print("Arquivos disponiveis:")
    for i, nome in enumerate(arquivos, 1):
        print(f"  {i}. {nome}")
    print()


def escolher_arquivos(arquivos):
    while True:
        imprimir_arquivos(arquivos)
        print("Escolha um numero para iniciar a leitura,")
        print("ou digite 'all' para ler todos de uma vez.")
        print("Para sair, digite 'sair'.")
        print()

        escolha = input("Opcao: ").strip().lower()

        if escolha == "sair":
            return None
        if escolha == "all":
            return list(arquivos)
        if escolha.isdigit():
            n = int(escolha)
            if 1 <= n <= len(arquivos):
                return [arquivos[n - 1]]

        print()
        print(f"Comando invalido: {escolha!r}")
        print("")
        print()


def executar(nomes):
    for nome in nomes:
        caminho = os.path.join(PASTA_EXEMPLOS, nome)
        print()
        print("#" * 60)
        print(f"#  ARQUIVO: {nome}")
        print("#" * 60)
        try:
            compilar(caminho)
        except SystemExit:
            # compilar() chama sys.exit(1) em erro; capturamos para
            # nao interromper a leitura dos demais arquivos no modo 'all'
            pass


def modo_interativo():
    imprimir_boas_vindas()

    if not perguntar_prosseguir():
        print("\nObrigado por utilizar o nosso projeto!")
        return

    imprimir_dica()

    while True:
        arquivos = listar_arquivos()
        if not arquivos:
            print(f"Nenhum arquivo .txt ou .js encontrado em {PASTA_EXEMPLOS}/")
            print("    Adicione arquivos e rode o programa novamente.")
            return

        escolhidos = escolher_arquivos(arquivos)
        if escolhidos is None:
            print("\nObrigado por utilizar o nosso projeto!")
            return

        executar(escolhidos)

        print()
        print("=" * 60)
        print("  Voltando ao menu principal...")
        print("=" * 60)
        print()


def main():
    if len(sys.argv) >= 2:
        compilar(sys.argv[1])
    else:
        modo_interativo()


if __name__ == "__main__":
    main()
