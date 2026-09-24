"""Ponto de entrada da interface grafica.

Uso:
    python main.py

Requer Tkinter instalado (no Ubuntu/Debian: sudo apt install python3-tk).
"""

from gui.janela import JanelaPrincipal


def main() -> None:
    JanelaPrincipal().mainloop()


if __name__ == "__main__":
    main()
