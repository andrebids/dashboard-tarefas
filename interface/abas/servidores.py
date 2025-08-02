# -*- coding: utf-8 -*-
"""
Aba Servidores - Gerenciamento de Conexões SSH.
"""

import tkinter as tk
from tkinter import ttk, messagebox


class AbaServidores(ttk.Frame):
    """
    Aba de gerenciamento de servidores SSH.
    """
    
    def __init__(self, parent, log_manager, settings, **kwargs):
        """
        Inicializa a aba de servidores.
        
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
        
        self._criar_interface()
        
        self.log_manager.log_sistema("SUCCESS", "Aba servidores inicializada")
    
    def _criar_interface(self):
        """Cria a interface da aba de servidores."""
        # Frame principal
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Título
        titulo_frame = ttk.Frame(main_frame)
        titulo_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(titulo_frame, text="🖥️ Gerenciamento de Servidores", 
                 font=("Arial", 16, "bold")).pack(side=tk.LEFT)
        
        # Frame de controles
        controles_frame = ttk.Frame(main_frame)
        controles_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Botão Adicionar Servidor
        self.btn_adicionar = ttk.Button(controles_frame, text="➕ Adicionar Servidor", 
                                       command=self._adicionar_servidor)
        self.btn_adicionar.pack(side=tk.LEFT, padx=(0, 10))
        
        # Botão Editar Servidor
        self.btn_editar = ttk.Button(controles_frame, text="✏️ Editar Servidor", 
                                    command=self._editar_servidor)
        self.btn_editar.pack(side=tk.LEFT, padx=(0, 10))
        
        # Botão Excluir Servidor
        self.btn_excluir = ttk.Button(controles_frame, text="🗑️ Excluir Servidor", 
                                     command=self._excluir_servidor)
        self.btn_excluir.pack(side=tk.LEFT, padx=(0, 10))
        
        # Botão Testar Conexão
        self.btn_testar = ttk.Button(controles_frame, text="🔍 Testar Conexão", 
                                    command=self._testar_conexao)
        self.btn_testar.pack(side=tk.LEFT, padx=(0, 10))
        
        # Botão Conectar
        self.btn_conectar = ttk.Button(controles_frame, text="🔗 Conectar", 
                                      command=self._conectar_servidor)
        self.btn_conectar.pack(side=tk.LEFT, padx=(0, 10))
        
        # Frame de filtros
        filtros_frame = ttk.LabelFrame(main_frame, text="Filtros", padding=10)
        filtros_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Filtros
        ttk.Label(filtros_frame, text="Status:").pack(side=tk.LEFT)
        self.status_var = tk.StringVar(value="Todos")
        self.cb_status = ttk.Combobox(filtros_frame, textvariable=self.status_var,
                                     values=["Todos", "Online", "Offline", "Erro"],
                                     width=10, state="readonly")
        self.cb_status.pack(side=tk.LEFT, padx=(5, 15))
        
        ttk.Label(filtros_frame, text="Tipo:").pack(side=tk.LEFT)
        self.tipo_var = tk.StringVar(value="Todos")
        self.cb_tipo = ttk.Combobox(filtros_frame, textvariable=self.tipo_var,
                                   values=["Todos", "SSH", "FTP", "SFTP", "RDP"],
                                   width=10, state="readonly")
        self.cb_tipo.pack(side=tk.LEFT, padx=(5, 15))
        
        # Botão Aplicar Filtros
        ttk.Button(filtros_frame, text="Aplicar Filtros", 
                  command=self._aplicar_filtros).pack(side=tk.LEFT, padx=(10, 0))
        
        # Frame da lista de servidores
        lista_frame = ttk.LabelFrame(main_frame, text="Lista de Servidores", padding=10)
        lista_frame.pack(fill=tk.BOTH, expand=True)
        
        # TreeView para lista de servidores
        colunas = ("ID", "Nome", "Host", "Porta", "Tipo", "Status", "Última Conexão")
        self.tree_servidores = ttk.Treeview(lista_frame, columns=colunas, show="headings", height=15)
        
        # Configurar colunas
        for col in colunas:
            self.tree_servidores.heading(col, text=col)
            self.tree_servidores.column(col, width=120)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(lista_frame, orient="vertical", command=self.tree_servidores.yview)
        self.tree_servidores.configure(yscrollcommand=scrollbar.set)
        
        self.tree_servidores.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind para seleção
        self.tree_servidores.bind("<<TreeviewSelect>>", self._on_servidor_selecionado)
        
        # Frame de informações
        info_frame = ttk.LabelFrame(main_frame, text="Informações do Servidor", padding=10)
        info_frame.pack(fill=tk.X, pady=(20, 0))
        
        # Grid de informações
        info_grid = ttk.Frame(info_frame)
        info_grid.pack(fill=tk.X)
        
        ttk.Label(info_grid, text="Servidor Selecionado:").grid(row=0, column=0, sticky="w", pady=2)
        self.lbl_servidor_selecionado = ttk.Label(info_grid, text="Nenhum servidor selecionado", 
                                                 foreground="gray")
        self.lbl_servidor_selecionado.grid(row=0, column=1, sticky="w", padx=(10, 0), pady=2)
        
        ttk.Label(info_grid, text="Total de Servidores:").grid(row=1, column=0, sticky="w", pady=2)
        self.lbl_total_servidores = ttk.Label(info_grid, text="0")
        self.lbl_total_servidores.grid(row=1, column=1, sticky="w", padx=(10, 0), pady=2)
        
        ttk.Label(info_grid, text="Servidores Online:").grid(row=2, column=0, sticky="w", pady=2)
        self.lbl_servidores_online = ttk.Label(info_grid, text="0")
        self.lbl_servidores_online.grid(row=2, column=1, sticky="w", padx=(10, 0), pady=2)
        
        # Carregar dados iniciais
        self._carregar_servidores()
    
    def _adicionar_servidor(self):
        """Abre formulário para adicionar servidor."""
        # TODO: Implementar na Fase 4
        messagebox.showinfo("Adicionar Servidor", "Formulário de adicionar servidor será implementado na Fase 4")
    
    def _editar_servidor(self):
        """Edita o servidor selecionado."""
        # TODO: Implementar na Fase 4
        messagebox.showinfo("Editar Servidor", "Edição de servidores será implementada na Fase 4")
    
    def _excluir_servidor(self):
        """Exclui o servidor selecionado."""
        # TODO: Implementar na Fase 4
        messagebox.showinfo("Excluir Servidor", "Exclusão de servidores será implementada na Fase 4")
    
    def _testar_conexao(self):
        """Testa a conexão com o servidor selecionado."""
        # TODO: Implementar na Fase 4
        messagebox.showinfo("Testar Conexão", "Teste de conexão será implementado na Fase 4")
    
    def _conectar_servidor(self):
        """Conecta ao servidor selecionado."""
        # TODO: Implementar na Fase 4
        messagebox.showinfo("Conectar", "Conexão SSH será implementada na Fase 4")
    
    def _aplicar_filtros(self):
        """Aplica os filtros configurados."""
        # TODO: Implementar na Fase 4
        messagebox.showinfo("Filtros", "Sistema de filtros será implementado na Fase 4")
    
    def _on_servidor_selecionado(self, event):
        """Chamado quando um servidor é selecionado."""
        selecao = self.tree_servidores.selection()
        if selecao:
            item = self.tree_servidores.item(selecao[0])
            nome = item['values'][1] if item['values'] else "Desconhecido"
            self.lbl_servidor_selecionado.config(text=nome)
        else:
            self.lbl_servidor_selecionado.config(text="Nenhum servidor selecionado")
    
    def _carregar_servidores(self):
        """Carrega a lista de servidores."""
        # TODO: Implementar na Fase 4
        # Por enquanto, apenas limpar a lista
        for item in self.tree_servidores.get_children():
            self.tree_servidores.delete(item)
        
        # Dados de exemplo
        dados_exemplo = [
            ("1", "Servidor Web", "192.168.1.100", "22", "SSH", "🟢 Online", "2024-01-15 10:30"),
            ("2", "Servidor App", "192.168.1.101", "22", "SSH", "🔴 Offline", "2024-01-15 09:15"),
            ("3", "Servidor DB", "192.168.1.102", "22", "SSH", "🟡 Erro", "2024-01-15 08:45")
        ]
        
        for dados in dados_exemplo:
            self.tree_servidores.insert("", "end", values=dados)
        
        # Atualizar contadores
        self.lbl_total_servidores.config(text=str(len(dados_exemplo)))
        self.lbl_servidores_online.config(text="1")  # Exemplo
    
    def atualizar(self):
        """Atualiza a aba de servidores."""
        self._carregar_servidores() 