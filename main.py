#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dashboard de Tarefas - Python
Sistema de Automação Windows + Linux Remoto

Ponto de entrada principal da aplicação.
"""

import sys
import os
import tkinter as tk
from tkinter import messagebox

# Adicionar o diretório atual ao path para importar módulos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from interface.dashboard import Dashboard
    from core.logs import LogManager
    from config.settings import Settings
except ImportError as e:
    print(f"Erro ao importar módulos: {e}")
    print("Verifique se todas as dependências estão instaladas:")
    print("pip install -r requirements.txt")
    sys.exit(1)


def main():
    """
    Função principal que inicia a aplicação.
    """
    try:
        # Inicializar configurações
        settings = Settings()
        
        # Inicializar sistema de logs
        log_manager = LogManager(settings)
        log_manager.registrar_log("INFO", "Iniciando Dashboard de Tarefas Python")
        
        # Criar janela principal
        root = tk.Tk()
        
        # Configurar janela principal
        root.title("Dashboard de Tarefas - Python")
        root.geometry("1200x800")
        root.minsize(800, 600)
        
        # Centralizar janela na tela
        root.update_idletasks()
        x = (root.winfo_screenwidth() // 2) - (1200 // 2)
        y = (root.winfo_screenheight() // 2) - (800 // 2)
        root.geometry(f"1200x800+{x}+{y}")
        
        # Criar dashboard
        dashboard = Dashboard(root, log_manager, settings)
        
        # Configurar protocolo de fechamento
        def on_closing():
            """Função chamada quando a janela é fechada."""
            try:
                log_manager.registrar_log("INFO", "Fechando Dashboard de Tarefas")
                dashboard.salvar_configuracoes()
                root.destroy()
            except Exception as e:
                log_manager.registrar_log("ERROR", f"Erro ao fechar aplicação: {e}")
                root.destroy()
        
        root.protocol("WM_DELETE_WINDOW", on_closing)
        
        # Iniciar loop principal
        log_manager.registrar_log("SUCCESS", "Dashboard iniciado com sucesso")
        root.mainloop()
        
    except Exception as e:
        # Em caso de erro crítico, mostrar mensagem
        error_msg = f"Erro crítico ao iniciar aplicação: {e}"
        print(error_msg)
        
        # Tentar mostrar mensagem de erro se possível
        try:
            root = tk.Tk()
            root.withdraw()  # Esconder janela principal
            messagebox.showerror("Erro Crítico", error_msg)
            root.destroy()
        except:
            pass
        
        sys.exit(1)


if __name__ == "__main__":
    main() 