# -*- coding: utf-8 -*-
"""
Interface principal do Dashboard de Tarefas.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional

from .componentes.console import Console
from .abas.principal import AbaPrincipal
from .abas.base_dados import AbaBaseDados
from .abas.servidores import AbaServidores
from .abas.logs import AbaLogs


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
        self.settings.criar_diretorios_necessarios()
        
        # Abas do dashboard
        self.abas = {}
        self.aba_atual = None
        
        # Console global
        self.console = None
        
        self._criar_interface()
        self._configurar_menu()
        self._inicializar_abas()
        
        # Registrar log de inicialização
        self.log_manager.log_sistema("SUCCESS", "Interface do dashboard inicializada")
    
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
        
        # Console global (fixa na parte inferior)
        self.console = Console(main_frame)
        self.console.grid(row=1, column=0, sticky="ew", pady=(5, 0))
        
        # Configurar callbacks da console
        self.console.definir_callback_limpar(self._limpar_console)
        self.console.definir_callback_exportar(self._exportar_logs)
        
        # Barra de status
        self.status_bar = ttk.Frame(main_frame)
        self.status_bar.grid(row=2, column=0, sticky="ew", pady=(5, 0))
        
        # Status do sistema
        self.lbl_status = ttk.Label(self.status_bar, text="Sistema: Pronto")
        self.lbl_status.pack(side=tk.LEFT)
        
        # Status do Planka
        self.lbl_status_planka = ttk.Label(self.status_bar, text="Planka: Desconhecido")
        self.lbl_status_planka.pack(side=tk.LEFT, padx=(20, 0))
        
        # Status de conexão
        self.lbl_status_conexao = ttk.Label(self.status_bar, text="Conexões: 0")
        self.lbl_status_conexao.pack(side=tk.LEFT, padx=(20, 0))
        
        # Status da base de dados
        self.lbl_status_db = ttk.Label(self.status_bar, text="Base de Dados: Desconhecido")
        self.lbl_status_db.pack(side=tk.LEFT, padx=(20, 0))
        
        # Configurar evento de mudança de aba
        self.notebook.bind("<<NotebookTabChanged>>", self._on_aba_mudou)
    
    def _configurar_menu(self):
        """Configura o menu principal."""
        # Menu principal
        menubar = tk.Menu(self.parent)
        self.parent.config(menu=menubar)
        
        # Menu Arquivo
        menu_arquivo = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Arquivo", menu=menu_arquivo)
        menu_arquivo.add_command(label="Configurações", command=self._abrir_configuracoes)
        menu_arquivo.add_separator()
        menu_arquivo.add_command(label="Sair", command=self._sair)
        
        # Menu Ferramentas
        menu_ferramentas = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Ferramentas", menu=menu_ferramentas)
        menu_ferramentas.add_command(label="Verificar Dependências", command=self._verificar_dependencias)
        menu_ferramentas.add_command(label="Limpar Logs Antigos", command=self._limpar_logs_antigos)
        
        # Menu Ajuda
        menu_ajuda = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Ajuda", menu=menu_ajuda)
        menu_ajuda.add_command(label="Sobre", command=self._sobre)
        menu_ajuda.add_command(label="Documentação", command=self._documentacao)
    
    def _inicializar_abas(self):
        """Inicializa todas as abas do dashboard."""
        try:
            # Aba Principal (Planka)
            self.abas["principal"] = AbaPrincipal(self.notebook, self.log_manager, self.settings)
            self.notebook.add(self.abas["principal"], text="🏠 Principal")
            
            # Aba Base de Dados
            self.abas["base_dados"] = AbaBaseDados(self.notebook, self.log_manager, self.settings)
            self.notebook.add(self.abas["base_dados"], text="🗄️ Base de Dados")
            
            # Aba Servidores
            self.abas["servidores"] = AbaServidores(self.notebook, self.log_manager, self.settings)
            self.notebook.add(self.abas["servidores"], text="🖥️ Servidores")
            
            # Aba Logs
            self.abas["logs"] = AbaLogs(self.notebook, self.log_manager, self.settings)
            self.notebook.add(self.abas["logs"], text="📋 Logs")
            
            # Definir aba atual
            self.aba_atual = "principal"
            
            self.log_manager.log_sistema("SUCCESS", "Todas as abas inicializadas")
            
        except Exception as e:
            self.log_manager.log_sistema("ERROR", f"Erro ao inicializar abas: {e}")
            messagebox.showerror("Erro", f"Erro ao inicializar abas: {e}")
    
    def _on_aba_mudou(self, event):
        """Chamado quando a aba ativa muda."""
        try:
            # Obter índice da aba ativa
            indice_ativo = self.notebook.index(self.notebook.select())
            
            # Mapear índice para nome da aba
            nomes_abas = ["principal", "base_dados", "servidores", "logs"]
            if 0 <= indice_ativo < len(nomes_abas):
                self.aba_atual = nomes_abas[indice_ativo]
                self.log_manager.log_sistema("INFO", f"Aba ativa: {self.aba_atual}")
                
                # Atualizar status
                self._atualizar_status()
        except Exception as e:
            self.log_manager.log_sistema("ERROR", f"Erro ao mudar aba: {e}")
    
    def _atualizar_status(self):
        """Atualiza a barra de status."""
        try:
            # Status do sistema
            self.lbl_status.config(text="Sistema: Ativo")
            
            # Status do Planka (será atualizado pela aba principal)
            # self.lbl_status_planka.config(text="Planka: Verificando...")
            
            # Status de conexões (será atualizado pela aba servidores)
            # self.lbl_status_conexao.config(text="Conexões: 0")
            
            # Status da base de dados (será atualizado pela aba base de dados)
            # self.lbl_status_db.config(text="Base de Dados: Verificando...")
            
        except Exception as e:
            self.log_manager.log_sistema("ERROR", f"Erro ao atualizar status: {e}")
    
    def atualizar_status_planka(self, status: str):
        """Atualiza o status do Planka na barra de status."""
        try:
            self.lbl_status_planka.config(text=f"Planka: {status}")
        except Exception as e:
            self.log_manager.log_sistema("ERROR", f"Erro ao atualizar status do Planka: {e}")
    
    def atualizar_status_conexoes(self, num_conexoes: int):
        """Atualiza o status de conexões na barra de status."""
        try:
            self.lbl_status_conexao.config(text=f"Conexões: {num_conexoes}")
        except Exception as e:
            self.log_manager.log_sistema("ERROR", f"Erro ao atualizar status de conexões: {e}")
    
    def atualizar_status_base_dados(self, status: str):
        """Atualiza o status da base de dados na barra de status."""
        try:
            self.lbl_status_db.config(text=f"Base de Dados: {status}")
        except Exception as e:
            self.log_manager.log_sistema("ERROR", f"Erro ao atualizar status da base de dados: {e}")
    
    def adicionar_log_console(self, nivel: str, mensagem: str, origem: str = "sistema", 
                             detalhes: Optional[dict] = None):
        """Adiciona um log à console global."""
        if self.console:
            self.console.adicionar_log(nivel, mensagem, origem, detalhes)
    
    def _limpar_console(self):
        """Limpa a console global."""
        if self.console:
            self.console._limpar_console()
        self.log_manager.log_sistema("INFO", "Console limpa")
    
    def _exportar_logs(self):
        """Exporta logs para arquivo."""
        try:
            caminho = self.log_manager.exportar_logs("sistema", "txt")
            if caminho:
                messagebox.showinfo("Sucesso", f"Logs exportados para:\n{caminho}")
            else:
                messagebox.showerror("Erro", "Erro ao exportar logs")
        except Exception as e:
            self.log_manager.log_sistema("ERROR", f"Erro ao exportar logs: {e}")
            messagebox.showerror("Erro", f"Erro ao exportar logs: {e}")
    
    def _abrir_configuracoes(self):
        """Abre a janela de configurações."""
        # TODO: Implementar janela de configurações
        messagebox.showinfo("Configurações", "Janela de configurações será implementada na Fase 6")
    
    def _sair(self):
        """Sai da aplicação."""
        if messagebox.askokcancel("Sair", "Deseja realmente sair?"):
            self.log_manager.log_sistema("INFO", "Aplicação encerrada pelo usuário")
            self.parent.quit()
    
    def _verificar_dependencias(self):
        """Verifica as dependências do sistema."""
        # TODO: Implementar verificação de dependências
        messagebox.showinfo("Verificar Dependências", "Verificação de dependências será implementada na Fase 6")
    
    def _limpar_logs_antigos(self):
        """Limpa logs antigos do sistema."""
        try:
            # Limpar logs com mais de 30 dias
            dias_limite = 30
            arquivos_removidos = self.log_manager.limpar_logs_antigos(dias_limite)
            
            if arquivos_removidos > 0:
                messagebox.showinfo("Sucesso", f"Removidos {arquivos_removidos} arquivos de log antigos")
            else:
                messagebox.showinfo("Info", "Nenhum arquivo de log antigo encontrado")
                
        except Exception as e:
            self.log_manager.log_sistema("ERROR", f"Erro ao limpar logs antigos: {e}")
            messagebox.showerror("Erro", f"Erro ao limpar logs antigos: {e}")
    
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
    
    def _documentacao(self):
        """Abre a documentação."""
        # TODO: Implementar abertura da documentação
        messagebox.showinfo("Documentação", "Documentação será implementada na Fase 6")
    
    def salvar_configuracoes(self):
        """Salva as configurações do sistema."""
        try:
            self.settings.salvar()
            self.log_manager.log_sistema("SUCCESS", "Configurações salvas")
        except Exception as e:
            self.log_manager.log_sistema("ERROR", f"Erro ao salvar configurações: {e}")
    
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