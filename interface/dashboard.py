# -*- coding: utf-8 -*-
"""
Interface principal do Dashboard de Tarefas.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Dict, Any
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
        self.settings.criar_diretorios_necessarios()
        
        # Abas do dashboard
        self.abas = {}
        self.aba_atual = None
        
        # Sistema de comunicação entre abas
        self.eventos = {}
        self.callbacks = {}
        
        # Sistema de notificações
        self.notificacoes = []
        self.notificacao_atual = None
        
        # Status do sistema
        self.status_sistema = {
            "planka": "Desconhecido",
            "base_dados": "Desconhecido", 
            "conexoes": 0
        }
        
        # Thread para atualizações automáticas
        self.thread_atualizacao = None
        self.executando = True
        
        self._criar_interface()
        self._configurar_menu()
        self._inicializar_abas()
        self._configurar_comunicacao()
        self._iniciar_atualizacoes()
        
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
        
        # Notebook (sistema de abas) - com tamanho mínimo
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
        
        # Frame para notificações
        self.frame_notificacoes = ttk.Frame(main_frame)
        self.frame_notificacoes.grid(row=2, column=0, sticky="ew", pady=(5, 0))
        self.frame_notificacoes.grid_columnconfigure(0, weight=1)
        
        # Label para notificações
        self.lbl_notificacao = ttk.Label(self.frame_notificacoes, text="", foreground="blue")
        self.lbl_notificacao.grid(row=0, column=0, sticky="w")
        
        # Botão para fechar notificação
        self.btn_fechar_notif = ttk.Button(self.frame_notificacoes, text="✕", width=3, 
                                          command=self._fechar_notificacao)
        self.btn_fechar_notif.grid(row=0, column=1, sticky="e")
        
        # Inicialmente esconder notificações
        self.frame_notificacoes.grid_remove()
        
        # Configurar evento de mudança de aba
        self.notebook.bind("<<NotebookTabChanged>>", self._on_aba_mudou)
        
        # Adicionar tooltips
        self._adicionar_tooltips()
    
    def _configurar_comunicacao(self):
        """Configura o sistema de comunicação entre abas."""
        try:
            # Registrar eventos padrão
            self.registrar_evento("planka_status_changed", self._on_planka_status_changed)
            self.registrar_evento("base_dados_status_changed", self._on_base_dados_status_changed)
            self.registrar_evento("servidores_status_changed", self._on_servidores_status_changed)
            self.registrar_evento("notificacao", self._on_notificacao)
            
            self.log_manager.log_sistema("INFO", "Sistema de comunicação configurado")
        except Exception as e:
            self.log_manager.log_sistema("ERROR", f"Erro ao configurar comunicação: {e}")
    
    def _iniciar_atualizacoes(self):
        """Inicia thread para atualizações automáticas."""
        try:
            self.thread_atualizacao = threading.Thread(target=self._loop_atualizacoes, daemon=True)
            self.thread_atualizacao.start()
            self.log_manager.log_sistema("INFO", "Thread de atualizações iniciada")
        except Exception as e:
            self.log_manager.log_sistema("ERROR", f"Erro ao iniciar atualizações: {e}")
    
    def _loop_atualizacoes(self):
        """Loop principal para atualizações automáticas."""
        while self.executando:
            try:
                # Atualizar status do sistema
                self._atualizar_status_sistema()
                
                # Processar notificações pendentes
                self._processar_notificacoes()
                
                # Aguardar 2 segundos
                time.sleep(2)
            except Exception as e:
                self.log_manager.log_sistema("ERROR", f"Erro no loop de atualizações: {e}")
                time.sleep(5)
    
    def registrar_evento(self, evento: str, callback):
        """Registra um callback para um evento."""
        if evento not in self.callbacks:
            self.callbacks[evento] = []
        self.callbacks[evento].append(callback)
    
    def disparar_evento(self, evento: str, dados: Any = None):
        """Dispara um evento para todos os callbacks registrados."""
        try:
            if evento in self.callbacks:
                for callback in self.callbacks[evento]:
                    try:
                        callback(dados)
                    except Exception as e:
                        self.log_manager.log_sistema("ERROR", f"Erro no callback do evento {evento}: {e}")
        except Exception as e:
            self.log_manager.log_sistema("ERROR", f"Erro ao disparar evento {evento}: {e}")
    
    def mostrar_notificacao(self, mensagem: str, tipo: str = "info", duracao: int = 5):
        """Mostra uma notificação na interface."""
        try:
            notificacao = {
                "mensagem": mensagem,
                "tipo": tipo,
                "duracao": duracao,
                "timestamp": time.time()
            }
            self.notificacoes.append(notificacao)
            
            # Se não há notificação atual, mostrar imediatamente
            if not self.notificacao_atual:
                self._mostrar_proxima_notificacao()
                
        except Exception as e:
            self.log_manager.log_sistema("ERROR", f"Erro ao criar notificação: {e}")
    
    def _processar_notificacoes(self):
        """Processa notificações pendentes."""
        try:
            agora = time.time()
            
            # Remover notificações expiradas
            self.notificacoes = [n for n in self.notificacoes 
                               if agora - n["timestamp"] < n["duracao"]]
            
            # Se não há notificação atual e há pendentes, mostrar próxima
            if not self.notificacao_atual and self.notificacoes:
                self._mostrar_proxima_notificacao()
                
        except Exception as e:
            self.log_manager.log_sistema("ERROR", f"Erro ao processar notificações: {e}")
    
    def _mostrar_proxima_notificacao(self):
        """Mostra a próxima notificação na fila."""
        try:
            if not self.notificacoes:
                return
                
            self.notificacao_atual = self.notificacoes.pop(0)
            
            # Configurar cor baseada no tipo
            cores = {
                "info": "blue",
                "success": "green", 
                "warning": "orange",
                "error": "red"
            }
            cor = cores.get(self.notificacao_atual["tipo"], "blue")
            
            # Mostrar notificação
            self.lbl_notificacao.config(text=self.notificacao_atual["mensagem"], foreground=cor)
            self.frame_notificacoes.grid()
            
        except Exception as e:
            self.log_manager.log_sistema("ERROR", f"Erro ao mostrar notificação: {e}")
    
    def _fechar_notificacao(self):
        """Fecha a notificação atual."""
        try:
            self.notificacao_atual = None
            self.frame_notificacoes.grid_remove()
        except Exception as e:
            self.log_manager.log_sistema("ERROR", f"Erro ao fechar notificação: {e}")
    
    def _atualizar_status_sistema(self):
        """Atualiza o status do sistema na interface."""
        try:
            # Atualizar labels na thread principal
            self.parent.after(0, self._atualizar_labels_status)
        except Exception as e:
            self.log_manager.log_sistema("ERROR", f"Erro ao atualizar status do sistema: {e}")
    
    def _atualizar_labels_status(self):
        """Atualiza os labels de status na thread principal."""
        try:
            self.lbl_status_planka.config(text=f"Planka: {self.status_sistema['planka']}")
            self.lbl_status_db.config(text=f"Base de Dados: {self.status_sistema['base_dados']}")
            self.lbl_status_conexao.config(text=f"Conexões: {self.status_sistema['conexoes']}")
        except Exception as e:
            self.log_manager.log_sistema("ERROR", f"Erro ao atualizar labels de status: {e}")
    
    # Callbacks de eventos
    def _on_planka_status_changed(self, status: str):
        """Callback quando o status do Planka muda."""
        self.status_sistema["planka"] = status
    
    def _on_base_dados_status_changed(self, status: str):
        """Callback quando o status da base de dados muda."""
        self.status_sistema["base_dados"] = status
    
    def _on_servidores_status_changed(self, num_conexoes: int):
        """Callback quando o status dos servidores muda."""
        self.status_sistema["conexoes"] = num_conexoes
    

    
    def _on_notificacao(self, dados: Dict[str, Any]):
        """Callback para notificações."""
        self.mostrar_notificacao(dados["mensagem"], dados.get("tipo", "info"), dados.get("duracao", 5))
    
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
            
            # Tooltip para notificação
            criar_tooltip(self.btn_fechar_notif, "Fechar notificação atual")
            
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
            
            # Aba Build Planka
            self.abas["build_planka"] = AbaBuildPlanka(self.notebook, self.log_manager, self.settings)
            self.notebook.add(self.abas["build_planka"], text="🔨 Build Planka")
            
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
            nomes_abas = ["principal", "base_dados", "servidores", "build_planka"]
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
            # Parar thread de atualizações
            self.executando = False
            if self.thread_atualizacao and self.thread_atualizacao.is_alive():
                self.thread_atualizacao.join(timeout=2)
            
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