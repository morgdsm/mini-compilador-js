import sys
from mini_compilador.main import compilar


def main():
    if len(sys.argv) < 2:
        print("Uso: python main.py <arquivo.js>")
        sys.exit(1)
    compilar(sys.argv[1])


if __name__ == "__main__":
    main()
