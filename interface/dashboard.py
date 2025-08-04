# -*- coding: utf-8 -*-
"""
Interface principal do Dashboard de Tarefas.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time

from .componentes.tooltip import criar_tooltip
from .abas.principal import AbaPrincipal
from .abas.base_dados import AbaBaseDados
from .abas.servidores import AbaServidores
from .abas.build_planka import AbaBuildPlanka


class Dashboard(ttk.Frame):
    """
    Interface principal do Dashboard de Tarefas.
    """
    
    def __init__(self, parent, log_manager, settings, **kwargs):
        """
        Inicializa o dashboard principal.
        
        Args:
            parent: Widget pai (root)
            log_manager: Gerenciador de logs
            settings: Configurações do sistema
            **kwargs: Argumentos adicionais para ttk.Frame
        """
        super().__init__(parent, **kwargs)
        
        self.parent = parent
        self.log_manager = log_manager
        self.settings = settings
        
        # Criar diretórios necessários
        if self.settings:
            try:
                self.settings.criar_diretorios_necessarios()
            except Exception as e:
                print(f"Aviso: Erro ao criar diretórios necessários: {e}")
        
        # Abas do dashboard
        self.abas = {}
        self.aba_atual = None
        
        # Status do sistema
        self.status_sistema = {
            "planka": "Desconhecido",
            "base_dados": "Desconhecido", 
            "conexoes": 0
        }
        
        self._criar_interface()
        self._configurar_menu()
        self._inicializar_abas()
        
        # Registrar log de inicialização
        if self.log_manager:
            try:
                self.log_manager.log_sistema("SUCCESS", "Interface do dashboard inicializada")
            except Exception as e:
                print(f"Aviso: Erro ao registrar log: {e}")
    
    def _criar_interface(self):
        """Cria a interface principal do dashboard."""
        # Configurar peso das linhas e colunas
        self.parent.grid_rowconfigure(0, weight=1)
        self.parent.grid_columnconfigure(0, weight=1)
        self.grid(row=0, column=0, sticky="nsew")
        
        # Configurar peso das linhas e colunas do frame principal
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Frame principal
        main_frame = ttk.Frame(self)
        main_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)
        
        # Notebook (sistema de abas)
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.grid(row=0, column=0, sticky="nsew", pady=(0, 5))
        self.notebook.grid_rowconfigure(0, weight=1)
        self.notebook.grid_columnconfigure(0, weight=1)
        
        # Configurar tamanho mínimo para o notebook
        self.notebook.configure(width=800, height=600)
        
        # Barra de status
        self.status_bar = ttk.Frame(main_frame)
        self.status_bar.grid(row=1, column=0, sticky="ew", pady=(5, 0))
        self.status_bar.grid_columnconfigure(0, weight=1)
        self.status_bar.grid_columnconfigure(1, weight=1)
        self.status_bar.grid_columnconfigure(2, weight=1)
        self.status_bar.grid_columnconfigure(3, weight=1)
        
        # Status do sistema
        self.lbl_status = ttk.Label(self.status_bar, text="Sistema: Pronto")
        self.lbl_status.grid(row=0, column=0, sticky="w", padx=(0, 10))
        
        # Status do Planka
        self.lbl_status_planka = ttk.Label(self.status_bar, text="Planka: Desconhecido")
        self.lbl_status_planka.grid(row=0, column=1, sticky="w", padx=(0, 10))
        
        # Status de conexão
        self.lbl_status_conexao = ttk.Label(self.status_bar, text="Conexões: 0")
        self.lbl_status_conexao.grid(row=0, column=2, sticky="w", padx=(0, 10))
        
        # Status da base de dados
        self.lbl_status_db = ttk.Label(self.status_bar, text="Base de Dados: Desconhecido")
        self.lbl_status_db.grid(row=0, column=3, sticky="w")
        
        # Configurar evento de mudança de aba
        self.notebook.bind("<<NotebookTabChanged>>", self._on_aba_mudou)
        
        # Adicionar tooltips
        self._adicionar_tooltips()
    
    def _adicionar_tooltips(self):
        """Adiciona tooltips aos elementos da interface."""
        try:
            # Tooltips para abas
            criar_tooltip(self.notebook, "Navegue entre as diferentes seções do dashboard")
            
            # Tooltips para status
            criar_tooltip(self.lbl_status, "Status geral do sistema")
            criar_tooltip(self.lbl_status_planka, "Status atual do Planka")
            criar_tooltip(self.lbl_status_conexao, "Número de conexões SSH ativas")
            criar_tooltip(self.lbl_status_db, "Status da base de dados do Planka")
            
            self.log_manager.log_sistema("INFO", "Tooltips adicionados à interface")
        except Exception as e:
            self.log_manager.log_sistema("ERROR", f"Erro ao adicionar tooltips: {e}")
    
    def _configurar_menu(self):
        """Configura o menu principal."""
        # Menu principal
        menubar = tk.Menu(self.parent)
        self.parent.config(menu=menubar)
        
        # Menu Arquivo
        menu_arquivo = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Arquivo", menu=menu_arquivo)
        menu_arquivo.add_command(label="Limpar Logs Antigos", command=self._limpar_logs_antigos)
        menu_arquivo.add_separator()
        menu_arquivo.add_command(label="Sair", command=self._sair)
        
        # Menu Ajuda
        menu_ajuda = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Ajuda", menu=menu_ajuda)
        menu_ajuda.add_command(label="Sobre", command=self._sobre)
    
    def _inicializar_abas(self):
        """Inicializa todas as abas do dashboard."""
        try:
            # Inicializar apenas a aba principal primeiro
            self.abas["principal"] = AbaPrincipal(self.notebook, self.log_manager, self.settings)
            self.notebook.add(self.abas["principal"], text="🏠 Principal")
            
            # Definir aba atual
            self.aba_atual = "principal"
            
            # Inicializar outras abas imediatamente (sem thread para debug)
            self._inicializar_abas_background()
            
            if self.log_manager:
                self.log_manager.log_sistema("SUCCESS", "Aba principal inicializada")
            
        except Exception as e:
            print(f"❌ Erro ao inicializar abas: {e}")
            if self.log_manager:
                self.log_manager.log_sistema("ERROR", f"Erro ao inicializar abas: {e}")
            messagebox.showerror("Erro", f"Erro ao inicializar abas: {e}")
    
    def _inicializar_abas_background(self):
        """Inicializa as outras abas em background."""
        def init_background():
            try:
                # Aguardar um pouco para não interferir na inicialização da UI
                time.sleep(0.5)
                
                # Aba Base de Dados
                try:
                    print("Inicializando aba Base de Dados...")
                    self.abas["base_dados"] = AbaBaseDados(self.notebook, self.log_manager, self.settings)
                    self.notebook.add(self.abas["base_dados"], text="🗄️ Base de Dados")
                    print("✅ Aba Base de Dados inicializada")
                except Exception as e:
                    print(f"❌ Erro ao inicializar aba Base de Dados: {e}")
                    if self.log_manager:
                        self.log_manager.log_sistema("ERROR", f"Erro ao inicializar aba Base de Dados: {e}")
                
                time.sleep(0.2)
                
                # Aba Servidores
                try:
                    print("Inicializando aba Servidores...")
                    self.abas["servidores"] = AbaServidores(self.notebook, self.log_manager, self.settings)
                    self.notebook.add(self.abas["servidores"], text="🖥️ Servidores")
                    print("✅ Aba Servidores inicializada")
                except Exception as e:
                    print(f"❌ Erro ao inicializar aba Servidores: {e}")
                    if self.log_manager:
                        self.log_manager.log_sistema("ERROR", f"Erro ao inicializar aba Servidores: {e}")
                
                time.sleep(0.2)
                
                # Aba Build Planka
                try:
                    print("Inicializando aba Build Planka...")
                    self.abas["build_planka"] = AbaBuildPlanka(self.notebook, self.log_manager, self.settings)
                    self.notebook.add(self.abas["build_planka"], text="🔨 Build Planka")
                    print("✅ Aba Build Planka inicializada")
                except Exception as e:
                    print(f"❌ Erro ao inicializar aba Build Planka: {e}")
                    if self.log_manager:
                        self.log_manager.log_sistema("ERROR", f"Erro ao inicializar aba Build Planka: {e}")
                
                if self.log_manager:
                    self.log_manager.log_sistema("SUCCESS", "Todas as abas inicializadas")
                print("🎉 Todas as abas foram inicializadas com sucesso!")
                
            except Exception as e:
                print(f"❌ Erro geral ao inicializar abas em background: {e}")
                if self.log_manager:
                    self.log_manager.log_sistema("ERROR", f"Erro ao inicializar abas em background: {e}")
        
        # Executar imediatamente (sem thread para debug)
        init_background()
    
    def _on_aba_mudou(self, event):
        """Chamado quando a aba ativa muda."""
        try:
            # Obter índice da aba ativa
            indice_ativo = self.notebook.index(self.notebook.select())
            
            # Mapear índice para nome da aba
            nomes_abas = ["principal", "base_dados", "servidores", "build_planka"]
            if 0 <= indice_ativo < len(nomes_abas):
                self.aba_atual = nomes_abas[indice_ativo]
                if self.log_manager:
                    self.log_manager.log_sistema("INFO", f"Aba ativa: {self.aba_atual}")
                
        except Exception as e:
            if self.log_manager:
                self.log_manager.log_sistema("ERROR", f"Erro ao mudar aba: {e}")
    
    def atualizar_status(self, tipo: str, valor: str):
        """Atualiza o status na barra de status."""
        try:
            if tipo == "planka":
                self.lbl_status_planka.config(text=f"Planka: {valor}")
            elif tipo == "conexoes":
                self.lbl_status_conexao.config(text=f"Conexões: {valor}")
            elif tipo == "base_dados":
                self.lbl_status_db.config(text=f"Base de Dados: {valor}")
            elif tipo == "sistema":
                self.lbl_status.config(text=f"Sistema: {valor}")
        except Exception as e:
            if self.log_manager:
                self.log_manager.log_sistema("ERROR", f"Erro ao atualizar status {tipo}: {e}")
    
    def _limpar_logs_antigos(self):
        """Limpa logs antigos do sistema."""
        try:
            if not self.log_manager:
                messagebox.showwarning("Aviso", "Sistema de logs não disponível")
                return
                
            # Limpar logs com mais de 30 dias
            dias_limite = 30
            arquivos_removidos = self.log_manager.limpar_logs_antigos(dias_limite)
            
            if arquivos_removidos > 0:
                messagebox.showinfo("Sucesso", f"Removidos {arquivos_removidos} arquivos de log antigos")
            else:
                messagebox.showinfo("Info", "Nenhum arquivo de log antigo encontrado")
                
        except Exception as e:
            if self.log_manager:
                self.log_manager.log_sistema("ERROR", f"Erro ao limpar logs antigos: {e}")
            messagebox.showerror("Erro", f"Erro ao limpar logs antigos: {e}")
    
    def _sair(self):
        """Sai da aplicação."""
        if messagebox.askokcancel("Sair", "Deseja realmente sair?"):
            if self.log_manager:
                self.log_manager.log_sistema("INFO", "Aplicação encerrada pelo usuário")
            self.parent.quit()
    
    def _sobre(self):
        """Mostra informações sobre a aplicação."""
        messagebox.showinfo("Sobre", 
                           "Dashboard de Tarefas - Python\n\n"
                           "Versão: 2.0.0\n"
                           "Desenvolvido com Python + Tkinter\n\n"
                           "Funcionalidades:\n"
                           "• Controle do Planka\n"
                           "• Gestão da Base de Dados\n"
                           "• Conexões SSH\n"
                           "• Sistema de Logs\n\n"
                           "© 2025 - Sistema de Automação")
    
    def salvar_configuracoes(self):
        """Salva as configurações do sistema."""
        try:
            if self.settings:
                self.settings.salvar()
                if self.log_manager:
                    self.log_manager.log_sistema("SUCCESS", "Configurações salvas")
        except Exception as e:
            print(f"Erro ao salvar configurações: {e}")
            if self.log_manager:
                try:
                    self.log_manager.log_sistema("ERROR", f"Erro ao salvar configurações: {e}")
                except:
                    pass
    
    def obter_aba_atual(self) -> str:
        """Retorna o nome da aba atualmente ativa."""
        return self.aba_atual
    
    def obter_aba(self, nome: str):
        """Retorna uma aba específica pelo nome."""
        return self.abas.get(nome)
    
    def atualizar_aba(self, nome: str):
        """Atualiza uma aba específica."""
        if nome in self.abas:
            self.abas[nome].atualizar() 