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
        print("Iniciando Dashboard...")
        
        # Inicializar configurações
        try:
            settings = Settings()
            print("Configurações carregadas com sucesso")
        except Exception as e:
            print(f"Erro ao carregar configurações: {e}")
            # Tentar criar configurações básicas
            settings = None
        
        # Inicializar sistema de logs
        try:
            log_manager = LogManager(settings)
            if settings:
                log_manager.registrar_log("INFO", "Iniciando Dashboard de Tarefas Python")
            print("Sistema de logs inicializado")
        except Exception as e:
            print(f"Erro ao inicializar logs: {e}")
            log_manager = None
        
        # Criar janela principal
        root = tk.Tk()
        
        # Configurar janela principal
        root.title("Dashboard de Tarefas - Python")
        root.geometry("1400x900")
        root.minsize(1000, 700)
        
        # Centralizar janela na tela
        root.update_idletasks()
        x = (root.winfo_screenwidth() // 2) - (1400 // 2)
        y = (root.winfo_screenheight() // 2) - (900 // 2)
        root.geometry(f"1400x900+{x}+{y}")
        
        # Configurar ícone da janela (se disponível)
        try:
            root.iconbitmap("assets/icon.ico")
        except:
            pass  # Ignorar se não houver ícone
        
        # Criar dashboard
        try:
            dashboard = Dashboard(root, log_manager, settings)
            print("Dashboard criado com sucesso")
        except Exception as e:
            print(f"Erro ao criar dashboard: {e}")
            # Mostrar mensagem de erro na interface
            error_label = tk.Label(root, text=f"Erro ao inicializar dashboard:\n{e}", 
                                 fg="red", font=("Arial", 12))
            error_label.pack(expand=True, fill="both", padx=20, pady=20)
            
            # Botão para sair
            exit_button = tk.Button(root, text="Sair", command=root.destroy)
            exit_button.pack(pady=10)
            
            root.mainloop()
            return
        
        # Configurar protocolo de fechamento
        def on_closing():
            """Função chamada quando a janela é fechada."""
            try:
                if log_manager:
                    log_manager.registrar_log("INFO", "Fechando Dashboard de Tarefas")
                if hasattr(dashboard, 'salvar_configuracoes'):
                    dashboard.salvar_configuracoes()
                root.destroy()
            except Exception as e:
                if log_manager:
                    log_manager.registrar_log("ERROR", f"Erro ao fechar aplicação: {e}")
                root.destroy()
        
        root.protocol("WM_DELETE_WINDOW", on_closing)
        
        # Iniciar loop principal
        if log_manager:
            log_manager.registrar_log("SUCCESS", "Dashboard iniciado com sucesso")
        print("Dashboard iniciado com sucesso!")
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