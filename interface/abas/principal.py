# -*- coding: utf-8 -*-
"""
Aba Principal - Controle do Planka.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import subprocess
import os
from pathlib import Path

# Importar o PlankaManager
import sys
sys.path.append(str(Path(__file__).parent.parent.parent))
from core.planka import PlankaManager


class AbaPrincipal(ttk.Frame):
    """
    Aba principal com controle do Planka.
    """
    
    def __init__(self, parent, log_manager, settings, **kwargs):
        """
        Inicializa a aba principal.
        
        Args:
            parent: Widget pai (notebook)
            log_manager: Gerenciador de logs
            settings: Configurações do sistema
            **kwargs: Argumentos adicionais para ttk.Frame
        """
        super().__init__(parent, **kwargs)
        
        self.parent = parent
        self.log_manager = log_manager
        self.settings = settings
        
        # Status do Planka
        self.status_planka = "Desconhecido"
        self.modo_desenvolvimento = False
        
        # Thread para operações longas
        self.thread_operacao = None
        
        # Inicializar PlankaManager
        self.planka_manager = PlankaManager(settings)
        
        self._criar_interface()
        self._verificar_status_inicial()
        
        self.log_manager.log_sistema("SUCCESS", "Aba principal inicializada")
    
    def _criar_interface(self):
        """Cria a interface da aba principal."""
        # Frame principal
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Título
        titulo_frame = ttk.Frame(main_frame)
        titulo_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(titulo_frame, text="🏠 Dashboard Principal", 
                 font=("Arial", 16, "bold")).pack(side=tk.LEFT)
        
        # Status do Planka
        self.lbl_status_planka = ttk.Label(titulo_frame, text="Status: Verificando...",
                                          font=("Arial", 10))
        self.lbl_status_planka.pack(side=tk.RIGHT)
        
        # Frame de controles do Planka
        planka_frame = ttk.LabelFrame(main_frame, text="Controle do Planka", padding=20)
        planka_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Grid para botões
        botoes_frame = ttk.Frame(planka_frame)
        botoes_frame.pack(fill=tk.X)
        
        # Primeira linha de botões
        linha1 = ttk.Frame(botoes_frame)
        linha1.pack(fill=tk.X, pady=(0, 10))
        
        # Botão Iniciar Planka
        self.btn_iniciar = ttk.Button(linha1, text="🚀 Iniciar Planka", 
                                     command=self._iniciar_planka, style="Accent.TButton")
        self.btn_iniciar.pack(side=tk.LEFT, padx=(0, 10))
        
        # Botão Parar Planka
        self.btn_parar = ttk.Button(linha1, text="⏹️ Parar Planka", 
                                   command=self._parar_planka)
        self.btn_parar.pack(side=tk.LEFT, padx=(0, 10))
        
        # Botão Reiniciar Planka
        self.btn_reiniciar = ttk.Button(linha1, text="🔄 Reiniciar Planka", 
                                       command=self._reiniciar_planka)
        self.btn_reiniciar.pack(side=tk.LEFT, padx=(0, 10))
        
        # Botão Abrir no Browser
        self.btn_abrir = ttk.Button(linha1, text="🌐 Abrir no Browser", 
                                   command=self._abrir_browser)
        self.btn_abrir.pack(side=tk.LEFT, padx=(0, 10))
        
        # Segunda linha de botões
        linha2 = ttk.Frame(botoes_frame)
        linha2.pack(fill=tk.X, pady=(0, 10))
        
        # Botão Modo Desenvolvimento
        self.btn_desenvolvimento = ttk.Button(linha2, text="🔧 Modo Desenvolvimento", 
                                             command=self._modo_desenvolvimento)
        self.btn_desenvolvimento.pack(side=tk.LEFT, padx=(0, 10))
        
        # Botão Descarregar Planka
        self.btn_descarregar = ttk.Button(linha2, text="📥 Descarregar Planka", 
                                         command=self._descarregar_planka)
        self.btn_descarregar.pack(side=tk.LEFT, padx=(0, 10))
        
        # Botão Verificar Dependências
        self.btn_verificar = ttk.Button(linha2, text="🔍 Verificar Dependências", 
                                       command=self._verificar_dependencias)
        self.btn_verificar.pack(side=tk.LEFT, padx=(0, 10))
        
        # Frame de informações
        info_frame = ttk.LabelFrame(main_frame, text="Informações do Sistema", padding=20)
        info_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Grid de informações
        info_grid = ttk.Frame(info_frame)
        info_grid.pack(fill=tk.X)
        
        # Informações do Planka
        ttk.Label(info_grid, text="Diretório do Planka:").grid(row=0, column=0, sticky="w", pady=2)
        self.lbl_dir_planka = ttk.Label(info_grid, text="Verificando...", foreground="blue")
        self.lbl_dir_planka.grid(row=0, column=1, sticky="w", padx=(10, 0), pady=2)
        
        ttk.Label(info_grid, text="URL do Planka:").grid(row=1, column=0, sticky="w", pady=2)
        self.lbl_url_planka = ttk.Label(info_grid, text="http://localhost:3000", foreground="blue")
        self.lbl_url_planka.grid(row=1, column=1, sticky="w", padx=(10, 0), pady=2)
        
        ttk.Label(info_grid, text="Porta:").grid(row=2, column=0, sticky="w", pady=2)
        self.lbl_porta = ttk.Label(info_grid, text="3000", foreground="blue")
        self.lbl_porta.grid(row=2, column=1, sticky="w", padx=(10, 0), pady=2)
        
        # Frame de logs do Planka
        logs_frame = ttk.LabelFrame(main_frame, text="Logs do Planka", padding=10)
        logs_frame.pack(fill=tk.BOTH, expand=True)
        
        # Área de logs
        self.text_logs = tk.Text(logs_frame, height=10, font=("Consolas", 9),
                                bg="black", fg="white", wrap=tk.WORD)
        scrollbar = ttk.Scrollbar(logs_frame, orient="vertical", command=self.text_logs.yview)
        self.text_logs.configure(yscrollcommand=scrollbar.set)
        
        self.text_logs.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Configurar tags para cores
        self.text_logs.tag_configure("info", foreground="lightblue")
        self.text_logs.tag_configure("warning", foreground="yellow")
        self.text_logs.tag_configure("error", foreground="red")
        self.text_logs.tag_configure("success", foreground="lightgreen")
        
        # Frame de controles dos logs
        logs_controls = ttk.Frame(logs_frame)
        logs_controls.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(logs_controls, text="Limpar Logs", 
                  command=self._limpar_logs).pack(side=tk.LEFT)
        
        ttk.Button(logs_controls, text="Obter Logs", 
                  command=self._obter_logs_planka).pack(side=tk.LEFT, padx=(10, 0))
        
        ttk.Button(logs_controls, text="Atualizar", 
                  command=self._verificar_status_inicial).pack(side=tk.LEFT, padx=(10, 0))
        
        # Configurar estado inicial dos botões
        self._atualizar_estado_botoes()
    
    def _verificar_status_inicial(self):
        """Verifica o status inicial do Planka."""
        try:
            # Verificar se o diretório existe
            dir_planka = self.settings.obter_diretorio_planka()
            if dir_planka.exists():
                self.lbl_dir_planka.config(text=str(dir_planka))
                self.log_manager.log_sistema("INFO", f"Diretório do Planka encontrado: {dir_planka}")
            else:
                self.lbl_dir_planka.config(text="Não encontrado", foreground="red")
                self.log_manager.log_sistema("WARNING", f"Diretório do Planka não encontrado: {dir_planka}")
            
            # Verificar se o Planka está rodando
            self._verificar_status_planka()
            
        except Exception as e:
            self.log_manager.log_sistema("ERROR", f"Erro ao verificar status inicial: {e}")
    
    def _verificar_status_planka(self):
        """Verifica se o Planka está rodando."""
        try:
            # Usar o PlankaManager para verificar status
            status = self.planka_manager.verificar_status()
            
            if status == "online":
                self.status_planka = "Rodando"
                self.lbl_status_planka.config(text="Status: 🟢 Rodando", foreground="green")
                self.log_manager.log_sistema("SUCCESS", "Planka está rodando")
            elif status == "offline":
                self.status_planka = "Parado"
                self.lbl_status_planka.config(text="Status: 🔴 Parado", foreground="red")
                self.log_manager.log_sistema("INFO", "Planka não está rodando")
            else:
                self.status_planka = "Erro"
                self.lbl_status_planka.config(text="Status: ⚠️ Erro", foreground="orange")
                self.log_manager.log_sistema("ERROR", "Erro ao verificar status do Planka")
            
            self._atualizar_estado_botoes()
            
        except Exception as e:
            self.log_manager.log_sistema("ERROR", f"Erro ao verificar status do Planka: {e}")
            self.status_planka = "Erro"
            self.lbl_status_planka.config(text="Status: ⚠️ Erro", foreground="orange")
    
    def _atualizar_estado_botoes(self):
        """Atualiza o estado dos botões baseado no status do Planka."""
        if self.status_planka == "Rodando":
            self.btn_iniciar.config(state="disabled")
            self.btn_parar.config(state="normal")
            self.btn_reiniciar.config(state="normal")
            self.btn_abrir.config(state="normal")
        else:
            self.btn_iniciar.config(state="normal")
            self.btn_parar.config(state="disabled")
            self.btn_reiniciar.config(state="disabled")
            self.btn_abrir.config(state="disabled")
    
    def _iniciar_planka(self):
        """Inicia o Planka."""
        if self.thread_operacao and self.thread_operacao.is_alive():
            messagebox.showwarning("Aviso", "Operação em andamento. Aguarde...")
            return
        
        self.thread_operacao = threading.Thread(target=self._executar_iniciar_planka)
        self.thread_operacao.daemon = True
        self.thread_operacao.start()
    
    def _executar_iniciar_planka(self):
        """Executa a inicialização do Planka em thread separada."""
        try:
            self.log_manager.log_planka("INFO", "Iniciando Planka...")
            self._adicionar_log("Iniciando Planka...", "info")
            
            # Usar o PlankaManager para iniciar
            sucesso, mensagem = self.planka_manager.iniciar_planka()
            
            if sucesso:
                self.log_manager.log_planka("SUCCESS", mensagem)
                self._adicionar_log(mensagem, "success")
                
                # Atualizar status
                self._verificar_status_planka()
            else:
                self.log_manager.log_planka("ERROR", mensagem)
                self._adicionar_log(f"Erro: {mensagem}", "error")
                
        except Exception as e:
            self.log_manager.log_planka("ERROR", f"Erro inesperado: {e}")
            self._adicionar_log(f"Erro inesperado: {e}", "error")
            
            # Verificar status após inicialização
            self.after(2000, self._verificar_status_planka)
            
        except subprocess.TimeoutExpired:
            self.log_manager.log_planka("ERROR", "Timeout ao iniciar Planka")
            self._adicionar_log("Timeout ao iniciar Planka", "error")
        except Exception as e:
            self.log_manager.log_planka("ERROR", f"Erro ao iniciar Planka: {e}")
            self._adicionar_log(f"Erro ao iniciar Planka: {e}", "error")
    
    def _parar_planka(self):
        """Para o Planka."""
        if self.thread_operacao and self.thread_operacao.is_alive():
            messagebox.showwarning("Aviso", "Operação em andamento. Aguarde...")
            return
        
        self.thread_operacao = threading.Thread(target=self._executar_parar_planka)
        self.thread_operacao.daemon = True
        self.thread_operacao.start()
    
    def _executar_parar_planka(self):
        """Executa a parada do Planka em thread separada."""
        try:
            self.log_manager.log_planka("INFO", "Parando Planka...")
            self._adicionar_log("Parando Planka...", "info")
            
            # Usar o PlankaManager para parar
            sucesso, mensagem = self.planka_manager.parar_planka()
            
            if sucesso:
                self.log_manager.log_planka("SUCCESS", mensagem)
                self._adicionar_log(mensagem, "success")
                
                # Atualizar status
                self._verificar_status_planka()
            else:
                self.log_manager.log_planka("ERROR", mensagem)
                self._adicionar_log(f"Erro: {mensagem}", "error")
            
            # Verificar status após parada
            self.after(2000, self._verificar_status_planka)
            
        except Exception as e:
            self.log_manager.log_planka("ERROR", f"Erro inesperado: {e}")
            self._adicionar_log(f"Erro inesperado: {e}", "error")
    
    def _reiniciar_planka(self):
        """Reinicia o Planka."""
        if self.thread_operacao and self.thread_operacao.is_alive():
            messagebox.showwarning("Aviso", "Operação em andamento. Aguarde...")
            return
        
        self.thread_operacao = threading.Thread(target=self._executar_reiniciar_planka)
        self.thread_operacao.daemon = True
        self.thread_operacao.start()
    
    def _executar_reiniciar_planka(self):
        """Executa o reinício do Planka em thread separada."""
        try:
            self.log_manager.log_planka("INFO", "Reiniciando Planka...")
            self._adicionar_log("Reiniciando Planka...", "info")
            
            # Usar o PlankaManager para reiniciar
            sucesso, mensagem = self.planka_manager.reiniciar_planka()
            
            if sucesso:
                self.log_manager.log_planka("SUCCESS", mensagem)
                self._adicionar_log(mensagem, "success")
                
                # Atualizar status
                self._verificar_status_planka()
            else:
                self.log_manager.log_planka("ERROR", mensagem)
                self._adicionar_log(f"Erro: {mensagem}", "error")
            
        except Exception as e:
            self.log_manager.log_planka("ERROR", f"Erro inesperado: {e}")
            self._adicionar_log(f"Erro inesperado: {e}", "error")
    
    def _abrir_browser(self):
        """Abre o Planka no navegador."""
        try:
            import webbrowser
            url = self.settings.obter("planka", "url", "http://localhost:3000")
            webbrowser.open(url)
            self.log_manager.log_planka("INFO", f"Planka aberto no navegador: {url}")
            self._adicionar_log(f"Planka aberto no navegador: {url}", "info")
        except Exception as e:
            self.log_manager.log_planka("ERROR", f"Erro ao abrir navegador: {e}")
            self._adicionar_log(f"Erro ao abrir navegador: {e}", "error")
    
    def _modo_desenvolvimento(self):
        """Inicia o modo desenvolvimento."""
        # TODO: Implementar modo desenvolvimento na Fase 2
        messagebox.showinfo("Modo Desenvolvimento", 
                           "Modo desenvolvimento será implementado na Fase 2")
    
    def _descarregar_planka(self):
        """Descarrega o repositório do Planka."""
        # TODO: Implementar download do repositório na Fase 2
        messagebox.showinfo("Descarregar Planka", 
                           "Download do repositório será implementado na Fase 2")
    
    def _verificar_dependencias(self):
        """Verifica as dependências do sistema."""
        try:
            dependencias = self.planka_manager.verificar_dependencias()
            
            # Criar mensagem com status das dependências
            mensagem = "Status das Dependências:\n\n"
            for dep, status in dependencias.items():
                icone = "✅" if status else "❌"
                mensagem += f"{icone} {dep.upper()}: {'Disponível' if status else 'Não encontrado'}\n"
            
            # Verificar se todas estão disponíveis
            todas_disponiveis = all(dependencias.values())
            if todas_disponiveis:
                mensagem += "\n🎉 Todas as dependências estão disponíveis!"
                messagebox.showinfo("Dependências", mensagem)
            else:
                mensagem += "\n⚠️ Algumas dependências estão faltando."
                messagebox.showwarning("Dependências", mensagem)
                
            self.log_manager.log_planka("INFO", "Verificação de dependências realizada")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao verificar dependências: {e}")
            self.log_manager.log_planka("ERROR", f"Erro ao verificar dependências: {e}")
    
    def _limpar_logs(self):
        """Limpa os logs do Planka."""
        self.text_logs.delete(1.0, tk.END)
        self.log_manager.log_planka("INFO", "Logs do Planka limpos")
    
    def _obter_logs_planka(self):
        """Obtém logs do Planka."""
        try:
            self.log_manager.log_planka("INFO", "Obtendo logs do Planka...")
            self._adicionar_log("Obtendo logs do Planka...", "info")
            
            # Usar o PlankaManager para obter logs
            logs = self.planka_manager.obter_logs(linhas=100)
            
            # Limpar área de logs
            self.text_logs.delete(1.0, tk.END)
            
            # Adicionar logs
            self.text_logs.insert(tk.END, logs)
            
            # Rolar para o final
            self.text_logs.see(tk.END)
            
            self.log_manager.log_planka("SUCCESS", "Logs do Planka obtidos com sucesso")
            self._adicionar_log("Logs do Planka obtidos com sucesso!", "success")
            
        except Exception as e:
            self.log_manager.log_planka("ERROR", f"Erro ao obter logs: {e}")
            self._adicionar_log(f"Erro ao obter logs: {e}", "error")
    
    def _adicionar_log(self, mensagem: str, nivel: str = "info"):
        """Adiciona um log à área de texto."""
        try:
            import datetime
            timestamp = datetime.datetime.now().strftime("%H:%M:%S")
            log_entry = f"[{timestamp}] {mensagem}\n"
            
            self.text_logs.insert(tk.END, log_entry, nivel)
            self.text_logs.see(tk.END)
            
        except Exception as e:
            self.log_manager.log_sistema("ERROR", f"Erro ao adicionar log: {e}")
    
    def atualizar(self):
        """Atualiza a aba principal."""
        self._verificar_status_inicial() 