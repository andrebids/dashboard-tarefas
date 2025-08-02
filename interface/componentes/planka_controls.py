# -*- coding: utf-8 -*-
"""
Componente de Controles do Planka - Botões e ações do Planka.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import webbrowser
from typing import Dict, Callable, Optional


class PlankaControls:
    """
    Componente de controles do Planka.
    Responsável pelos botões e ações principais do Planka.
    """
    
    def __init__(self, parent, planka_manager, log_manager, settings, 
                 callback_atualizar_status: Optional[Callable] = None):
        """
        Inicializa o componente de controles.
        
        Args:
            parent: Widget pai
            planka_manager: Instância do PlankaManager
            log_manager: Gerenciador de logs
            settings: Configurações do sistema
            callback_atualizar_status: Callback para atualizar status
        """
        self.parent = parent
        self.planka_manager = planka_manager
        self.log_manager = log_manager
        self.settings = settings
        self.callback_atualizar_status = callback_atualizar_status
        
        # Thread para operações longas
        self.thread_operacao = None
        
        # Widgets
        self.btn_iniciar = None
        self.btn_parar = None
        self.btn_reiniciar = None
        self.btn_abrir = None
        
        self._criar_interface()
    
    def _criar_interface(self):
        """Cria a interface dos controles."""
        # Frame principal
        self.frame_controles = ttk.LabelFrame(self.parent, text="Controle do Planka", padding=20)
        self.frame_controles.pack(fill=tk.X, pady=(0, 20))
        
        # Grid para botões
        self.frame_botoes = ttk.Frame(self.frame_controles)
        self.frame_botoes.pack(fill=tk.X)
        
        # Linha única de botões (removida segunda linha)
        self.linha1 = ttk.Frame(self.frame_botoes)
        self.linha1.pack(fill=tk.X, pady=(0, 10))
        
        # Botão Iniciar Planka
        self.btn_iniciar = ttk.Button(self.linha1, text="🚀 Iniciar Planka", 
                                     command=self._iniciar_planka, style="Accent.TButton")
        self.btn_iniciar.pack(side=tk.LEFT, padx=(0, 10))
        
        # Botão Parar Planka
        self.btn_parar = ttk.Button(self.linha1, text="⏹️ Parar Planka", 
                                   command=self._parar_planka)
        self.btn_parar.pack(side=tk.LEFT, padx=(0, 10))
        
        # Botão Reiniciar Planka
        self.btn_reiniciar = ttk.Button(self.linha1, text="🔄 Reiniciar Planka", 
                                       command=self._reiniciar_planka)
        self.btn_reiniciar.pack(side=tk.LEFT, padx=(0, 10))
        
        # Botão Abrir no Browser
        self.btn_abrir = ttk.Button(self.linha1, text="🌐 Abrir no Browser", 
                                   command=self._abrir_browser)
        self.btn_abrir.pack(side=tk.LEFT, padx=(0, 10))
        
        # Nota sobre modo desenvolvimento
        nota_frame = ttk.Frame(self.frame_controles)
        nota_frame.pack(fill=tk.X, pady=(10, 0))
        
        nota_label = ttk.Label(nota_frame, text="💡 Para modo desenvolvimento, use a aba 'Build Planka'", 
                              font=("Arial", 9), foreground="gray")
        nota_label.pack(side=tk.LEFT)
    
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
            
            # Usar o PlankaManager para iniciar
            sucesso, mensagem = self.planka_manager.iniciar_planka()
            
            if sucesso:
                self.log_manager.log_planka("SUCCESS", mensagem)
                
                # Atualizar status
                if self.callback_atualizar_status:
                    self.callback_atualizar_status()
            else:
                self.log_manager.log_planka("ERROR", mensagem)
                
        except Exception as e:
            self.log_manager.log_planka("ERROR", f"Erro inesperado: {e}")
            
            # Verificar status após inicialização
            if self.callback_atualizar_status:
                self.parent.after(2000, self.callback_atualizar_status)
    
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
            
            # Usar o PlankaManager para parar
            sucesso, mensagem = self.planka_manager.parar_planka()
            
            if sucesso:
                self.log_manager.log_planka("SUCCESS", mensagem)
                
                # Atualizar status
                if self.callback_atualizar_status:
                    self.callback_atualizar_status()
            else:
                self.log_manager.log_planka("ERROR", mensagem)
            
            # Verificar status após parada
            if self.callback_atualizar_status:
                self.parent.after(2000, self.callback_atualizar_status)
            
        except Exception as e:
            self.log_manager.log_planka("ERROR", f"Erro inesperado: {e}")
    
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
            
            # Usar o PlankaManager para reiniciar
            sucesso, mensagem = self.planka_manager.reiniciar_planka()
            
            if sucesso:
                self.log_manager.log_planka("SUCCESS", mensagem)
                
                # Atualizar status
                if self.callback_atualizar_status:
                    self.callback_atualizar_status()
            else:
                self.log_manager.log_planka("ERROR", mensagem)
            
        except Exception as e:
            self.log_manager.log_planka("ERROR", f"Erro inesperado: {e}")
    
    def _abrir_browser(self):
        """Abre o Planka no navegador."""
        try:
            url = self.settings.obter("planka", "url", "http://localhost:3000")
            webbrowser.open(url)
            self.log_manager.log_planka("INFO", f"Planka aberto no navegador: {url}")
        except Exception as e:
            self.log_manager.log_planka("ERROR", f"Erro ao abrir navegador: {e}")
    
    def atualizar_estado_botoes(self, status_planka: str):
        """
        Atualiza o estado dos botões baseado no status do Planka.
        
        Args:
            status_planka: Status atual do Planka
        """
        if status_planka == "online":
            self.btn_iniciar.config(state="disabled")
            self.btn_parar.config(state="normal")
            self.btn_reiniciar.config(state="normal")
            self.btn_abrir.config(state="normal")
        else:
            self.btn_iniciar.config(state="normal")
            self.btn_parar.config(state="disabled")
            self.btn_reiniciar.config(state="disabled")
            self.btn_abrir.config(state="disabled")
    
    def definir_callback_atualizar_status(self, callback: Callable):
        """
        Define o callback para atualizar status.
        
        Args:
            callback: Função a ser chamada para atualizar status
        """
        self.callback_atualizar_status = callback
    
    def obter_widget(self) -> ttk.Frame:
        """
        Retorna o widget principal do componente.
        
        Returns:
            ttk.Frame principal
        """
        return self.frame_controles 