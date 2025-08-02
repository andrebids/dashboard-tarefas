# -*- coding: utf-8 -*-
"""
Aba Logs - Sistema de Logs Avançado.
Implementa visualização, filtros, busca e exportação de logs.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
from datetime import datetime, timedelta
from typing import Optional

from core.logs_avancado import LogsAvancadoManager, FiltroLogs, LogEstruturado


class AbaLogs(ttk.Frame):
    """
    Aba de sistema de logs avançado.
    """
    
    def __init__(self, parent, log_manager, settings, **kwargs):
        """
        Inicializa a aba de logs.
        
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
        
        # Inicializar gerenciador avançado de logs
        self.logs_avancado = LogsAvancadoManager(settings)
        
        # Variáveis de controle
        self.logs_atual = []
        self.filtro_atual = FiltroLogs()
        
        self._criar_interface()
        self._carregar_logs()
        
        self.log_manager.log_sistema("SUCCESS", "Aba logs avançado inicializada")
    
    def _criar_interface(self):
        """Cria a interface da aba de logs."""
        # Frame principal
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Título
        titulo_frame = ttk.Frame(main_frame)
        titulo_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(titulo_frame, text="📋 Sistema de Logs", 
                 font=("Arial", 16, "bold")).pack(side=tk.LEFT)
        
        # Frame de controles
        controles_frame = ttk.Frame(main_frame)
        controles_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Botão Atualizar
        self.btn_atualizar = ttk.Button(controles_frame, text="🔄 Atualizar", 
                                       command=self._atualizar_logs)
        self.btn_atualizar.pack(side=tk.LEFT, padx=(0, 10))
        
        # Botão Exportar
        self.btn_exportar = ttk.Button(controles_frame, text="📤 Exportar", 
                                      command=self._exportar_logs)
        self.btn_exportar.pack(side=tk.LEFT, padx=(0, 10))
        
        # Botão Limpar
        self.btn_limpar = ttk.Button(controles_frame, text="🗑️ Limpar", 
                                    command=self._limpar_logs)
        self.btn_limpar.pack(side=tk.LEFT, padx=(0, 10))
        
        # Botão Configurações
        self.btn_config = ttk.Button(controles_frame, text="⚙️ Configurações", 
                                    command=self._configurar_logs)
        self.btn_config.pack(side=tk.LEFT, padx=(0, 10))
        
        # Frame de filtros avançados
        filtros_frame = ttk.LabelFrame(main_frame, text="🔍 Filtros Avançados", padding=10)
        filtros_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Primeira linha de filtros
        linha1 = ttk.Frame(filtros_frame)
        linha1.pack(fill=tk.X, pady=(0, 5))
        
        # Origem
        ttk.Label(linha1, text="Origem:").pack(side=tk.LEFT)
        self.origem_var = tk.StringVar(value="Todos")
        self.cb_origem = ttk.Combobox(linha1, textvariable=self.origem_var,
                                     values=["Todos", "sistema", "planka", "servidores", "base_dados", "interface", "tarefas"],
                                     width=12, state="readonly")
        self.cb_origem.pack(side=tk.LEFT, padx=(5, 15))
        
        # Nível
        ttk.Label(linha1, text="Nível:").pack(side=tk.LEFT)
        self.nivel_var = tk.StringVar(value="Todos")
        self.cb_nivel = ttk.Combobox(linha1, textvariable=self.nivel_var,
                                    values=["Todos", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL", "SUCCESS"],
                                    width=12, state="readonly")
        self.cb_nivel.pack(side=tk.LEFT, padx=(5, 15))
        
        # Usuário
        ttk.Label(linha1, text="Usuário:").pack(side=tk.LEFT)
        self.usuario_var = tk.StringVar()
        self.entry_usuario = ttk.Entry(linha1, textvariable=self.usuario_var, width=12)
        self.entry_usuario.pack(side=tk.LEFT, padx=(5, 15))
        
        # Sessão
        ttk.Label(linha1, text="Sessão:").pack(side=tk.LEFT)
        self.sessao_var = tk.StringVar()
        self.entry_sessao = ttk.Entry(linha1, textvariable=self.sessao_var, width=12)
        self.entry_sessao.pack(side=tk.LEFT, padx=(5, 15))
        
        # Segunda linha de filtros
        linha2 = ttk.Frame(filtros_frame)
        linha2.pack(fill=tk.X, pady=(0, 5))
        
        # Data Início
        ttk.Label(linha2, text="Data Início:").pack(side=tk.LEFT)
        self.data_inicio_var = tk.StringVar()
        self.entry_data_inicio = ttk.Entry(linha2, textvariable=self.data_inicio_var, width=12)
        self.entry_data_inicio.pack(side=tk.LEFT, padx=(5, 15))
        
        # Data Fim
        ttk.Label(linha2, text="Data Fim:").pack(side=tk.LEFT)
        self.data_fim_var = tk.StringVar()
        self.entry_data_fim = ttk.Entry(linha2, textvariable=self.data_fim_var, width=12)
        self.entry_data_fim.pack(side=tk.LEFT, padx=(5, 15))
        
        # Busca de texto
        ttk.Label(linha2, text="Buscar:").pack(side=tk.LEFT)
        self.busca_var = tk.StringVar()
        self.entry_busca = ttk.Entry(linha2, textvariable=self.busca_var, width=20)
        self.entry_busca.pack(side=tk.LEFT, padx=(5, 15))
        
        # Limite
        ttk.Label(linha2, text="Limite:").pack(side=tk.LEFT)
        self.limite_var = tk.StringVar(value="1000")
        self.entry_limite = ttk.Entry(linha2, textvariable=self.limite_var, width=8)
        self.entry_limite.pack(side=tk.LEFT, padx=(5, 15))
        
        # Botões de filtro
        linha3 = ttk.Frame(filtros_frame)
        linha3.pack(fill=tk.X, pady=(5, 0))
        
        self.btn_aplicar_filtros = ttk.Button(linha3, text="🔍 Aplicar Filtros", 
                                             command=self._aplicar_filtros)
        self.btn_aplicar_filtros.pack(side=tk.LEFT, padx=(0, 10))
        
        self.btn_limpar_filtros = ttk.Button(linha3, text="🧹 Limpar Filtros", 
                                            command=self._limpar_filtros)
        self.btn_limpar_filtros.pack(side=tk.LEFT, padx=(0, 10))
        
        self.btn_busca_rapida = ttk.Button(linha3, text="⚡ Busca Rápida", 
                                          command=self._busca_rapida)
        self.btn_busca_rapida.pack(side=tk.LEFT, padx=(0, 10))
        
        # Frame de estatísticas
        stats_frame = ttk.LabelFrame(main_frame, text="📊 Estatísticas", padding=10)
        stats_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Estatísticas em linha
        stats_linha = ttk.Frame(stats_frame)
        stats_linha.pack(fill=tk.X)
        
        self.lbl_total_logs = ttk.Label(stats_linha, text="Total: 0")
        self.lbl_total_logs.pack(side=tk.LEFT, padx=(0, 20))
        
        self.lbl_logs_hoje = ttk.Label(stats_linha, text="Hoje: 0")
        self.lbl_logs_hoje.pack(side=tk.LEFT, padx=(0, 20))
        
        self.lbl_erros = ttk.Label(stats_linha, text="Erros: 0")
        self.lbl_erros.pack(side=tk.LEFT, padx=(0, 20))
        
        self.lbl_warnings = ttk.Label(stats_linha, text="Warnings: 0")
        self.lbl_warnings.pack(side=tk.LEFT, padx=(0, 20))
        
        self.lbl_sucessos = ttk.Label(stats_linha, text="Sucessos: 0")
        self.lbl_sucessos.pack(side=tk.LEFT, padx=(0, 20))
        
        # Frame de visualização de logs
        logs_frame = ttk.LabelFrame(main_frame, text="📋 Logs", padding=10)
        logs_frame.pack(fill=tk.BOTH, expand=True)
        
        # TreeView para logs
        colunas = ("ID", "Timestamp", "Nível", "Origem", "Mensagem", "Usuário", "Sessão")
        self.tree_logs = ttk.Treeview(logs_frame, columns=colunas, show="headings", height=15)
        
        # Configurar colunas
        self.tree_logs.heading("ID", text="ID")
        self.tree_logs.heading("Timestamp", text="Data/Hora")
        self.tree_logs.heading("Nível", text="Nível")
        self.tree_logs.heading("Origem", text="Origem")
        self.tree_logs.heading("Mensagem", text="Mensagem")
        self.tree_logs.heading("Usuário", text="Usuário")
        self.tree_logs.heading("Sessão", text="Sessão")
        
        # Configurar larguras
        self.tree_logs.column("ID", width=50)
        self.tree_logs.column("Timestamp", width=150)
        self.tree_logs.column("Nível", width=80)
        self.tree_logs.column("Origem", width=100)
        self.tree_logs.column("Mensagem", width=300)
        self.tree_logs.column("Usuário", width=100)
        self.tree_logs.column("Sessão", width=100)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(logs_frame, orient=tk.VERTICAL, command=self.tree_logs.yview)
        self.tree_logs.configure(yscrollcommand=scrollbar.set)
        
        # Layout
        self.tree_logs.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Eventos
        self.tree_logs.bind("<<TreeviewSelect>>", self._on_log_selecionado)
        self.tree_logs.bind("<Double-1>", self._on_log_double_click)
        
        # Frame de detalhes
        detalhes_frame = ttk.LabelFrame(main_frame, text="🔍 Detalhes do Log", padding=10)
        detalhes_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.text_detalhes = tk.Text(detalhes_frame, height=6, wrap=tk.WORD)
        self.text_detalhes.pack(fill=tk.BOTH, expand=True)
        
        # Segunda linha de filtros
        linha2 = ttk.Frame(filtros_frame)
        linha2.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(linha2, text="Buscar:").pack(side=tk.LEFT)
        self.busca_var = tk.StringVar()
        self.entry_busca = ttk.Entry(linha2, textvariable=self.busca_var, width=30)
        self.entry_busca.pack(side=tk.LEFT, padx=(5, 15))
        
        ttk.Label(linha2, text="Limite:").pack(side=tk.LEFT)
        self.limite_var = tk.StringVar(value="100")
        self.entry_limite = ttk.Entry(linha2, textvariable=self.limite_var, width=8)
        self.entry_limite.pack(side=tk.LEFT, padx=(5, 15))
        
        # Botão Aplicar Filtros
        ttk.Button(linha2, text="🔍 Aplicar Filtros", 
                  command=self._aplicar_filtros).pack(side=tk.LEFT, padx=(10, 0))
        
        # Botão Limpar Filtros
        ttk.Button(linha2, text="❌ Limpar Filtros", 
                  command=self._limpar_filtros).pack(side=tk.LEFT, padx=(10, 0))
        
        # Frame da lista de logs
        lista_frame = ttk.LabelFrame(main_frame, text="Logs do Sistema", padding=10)
        lista_frame.pack(fill=tk.BOTH, expand=True)
        
        # TreeView para lista de logs
        colunas = ("Timestamp", "Tipo", "Nível", "Origem", "Mensagem")
        self.tree_logs = ttk.Treeview(lista_frame, columns=colunas, show="headings", height=15)
        
        # Configurar colunas
        for col in colunas:
            self.tree_logs.heading(col, text=col)
            if col == "Mensagem":
                self.tree_logs.column(col, width=400)
            else:
                self.tree_logs.column(col, width=120)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(lista_frame, orient="vertical", command=self.tree_logs.yview)
        self.tree_logs.configure(yscrollcommand=scrollbar.set)
        
        self.tree_logs.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind para seleção
        self.tree_logs.bind("<<TreeviewSelect>>", self._on_log_selecionado)
        self.tree_logs.bind("<Double-1>", self._on_log_double_click)
        
        # Frame de informações
        info_frame = ttk.LabelFrame(main_frame, text="Informações dos Logs", padding=10)
        info_frame.pack(fill=tk.X, pady=(20, 0))
        
        # Grid de informações
        info_grid = ttk.Frame(info_frame)
        info_grid.pack(fill=tk.X)
        
        ttk.Label(info_grid, text="Log Selecionado:").grid(row=0, column=0, sticky="w", pady=2)
        self.lbl_log_selecionado = ttk.Label(info_grid, text="Nenhum log selecionado", 
                                            foreground="gray")
        self.lbl_log_selecionado.grid(row=0, column=1, sticky="w", padx=(10, 0), pady=2)
        
        ttk.Label(info_grid, text="Total de Logs:").grid(row=1, column=0, sticky="w", pady=2)
        self.lbl_total_logs = ttk.Label(info_grid, text="0")
        self.lbl_total_logs.grid(row=1, column=1, sticky="w", padx=(10, 0), pady=2)
        
        ttk.Label(info_grid, text="Logs de Hoje:").grid(row=2, column=0, sticky="w", pady=2)
        self.lbl_logs_hoje = ttk.Label(info_grid, text="0")
        self.lbl_logs_hoje.grid(row=2, column=1, sticky="w", padx=(10, 0), pady=2)
        
        ttk.Label(info_grid, text="Erros:").grid(row=0, column=2, sticky="w", padx=(20, 0), pady=2)
        self.lbl_erros = ttk.Label(info_grid, text="0", foreground="red")
        self.lbl_erros.grid(row=0, column=3, sticky="w", padx=(10, 0), pady=2)
        
        ttk.Label(info_grid, text="Avisos:").grid(row=1, column=2, sticky="w", padx=(20, 0), pady=2)
        self.lbl_avisos = ttk.Label(info_grid, text="0", foreground="orange")
        self.lbl_avisos.grid(row=1, column=3, sticky="w", padx=(10, 0), pady=2)
        
        ttk.Label(info_grid, text="Sucessos:").grid(row=2, column=2, sticky="w", padx=(20, 0), pady=2)
        self.lbl_sucessos = ttk.Label(info_grid, text="0", foreground="green")
        self.lbl_sucessos.grid(row=2, column=3, sticky="w", padx=(10, 0), pady=2)
        
        # Carregar dados iniciais
        self._carregar_logs()
    
    def _atualizar_logs(self):
        """Atualiza a lista de logs."""
        self._carregar_logs()
        self.log_manager.log_sistema("INFO", "Logs atualizados")
    
    def _exportar_logs(self):
        """Exporta os logs filtrados."""
        # TODO: Implementar na Fase 5
        messagebox.showinfo("Exportar Logs", "Exportação de logs será implementada na Fase 5")
    
    def _limpar_logs(self):
        """Limpa os logs antigos."""
        if messagebox.askyesno("Limpar Logs", "Deseja realmente limpar os logs antigos?"):
            # TODO: Implementar na Fase 5
            messagebox.showinfo("Limpar Logs", "Limpeza de logs será implementada na Fase 5")
    
    def _configurar_logs(self):
        """Abre configurações de logs."""
        # TODO: Implementar na Fase 5
        messagebox.showinfo("Configurar Logs", "Configurações de logs serão implementadas na Fase 5")
    
    def _aplicar_filtros(self):
        """Aplica os filtros configurados."""
        # TODO: Implementar na Fase 5
        messagebox.showinfo("Filtros", "Sistema de filtros será implementado na Fase 5")
    
    def _limpar_filtros(self):
        """Limpa todos os filtros."""
        self.tipo_var.set("Todos")
        self.nivel_var.set("Todos")
        self.data_inicio_var.set("")
        self.data_fim_var.set("")
        self.busca_var.set("")
        self.limite_var.set("100")
        self._carregar_logs()
    
    def _on_log_selecionado(self, event):
        """Chamado quando um log é selecionado."""
        selecao = self.tree_logs.selection()
        if selecao:
            item = self.tree_logs.item(selecao[0])
            timestamp = item['values'][0] if item['values'] else "Desconhecido"
            self.lbl_log_selecionado.config(text=f"Log de {timestamp}")
        else:
            self.lbl_log_selecionado.config(text="Nenhum log selecionado")
    
    def _on_log_double_click(self, event):
        """Chamado quando um log é clicado duas vezes."""
        selecao = self.tree_logs.selection()
        if selecao:
            item = self.tree_logs.item(selecao[0])
            mensagem = item['values'][4] if item['values'] else "Sem mensagem"
            messagebox.showinfo("Detalhes do Log", f"Mensagem completa:\n\n{mensagem}")
    
    def _carregar_logs(self):
        """Carrega a lista de logs."""
        # TODO: Implementar na Fase 5
        # Por enquanto, apenas limpar a lista
        for item in self.tree_logs.get_children():
            self.tree_logs.delete(item)
        
        # Dados de exemplo
        dados_exemplo = [
            ("2024-01-15 10:30:00", "sistema", "INFO", "Dashboard", "Sistema iniciado com sucesso"),
            ("2024-01-15 10:29:45", "planka", "SUCCESS", "Planka", "Planka iniciado na porta 3000"),
            ("2024-01-15 10:29:30", "tarefas", "WARNING", "Tarefas", "Tarefa de backup atrasada"),
            ("2024-01-15 10:29:15", "servidores", "ERROR", "SSH", "Falha na conexão com servidor"),
            ("2024-01-15 10:29:00", "sistema", "DEBUG", "Config", "Carregando configurações")
        ]
        
        for dados in dados_exemplo:
            self.tree_logs.insert("", "end", values=dados)
        
        # Atualizar contadores
        self.lbl_total_logs.config(text=str(len(dados_exemplo)))
        self.lbl_logs_hoje.config(text="5")  # Exemplo
        self.lbl_erros.config(text="1")  # Exemplo
        self.lbl_avisos.config(text="1")  # Exemplo
        self.lbl_sucessos.config(text="1")  # Exemplo
    
    def atualizar(self):
        """Atualiza a aba de logs."""
        self._carregar_logs() 