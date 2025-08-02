# -*- coding: utf-8 -*-
"""
Aba Tarefas - Gerenciamento de Tarefas.
"""

import tkinter as tk
from tkinter import ttk, messagebox


class AbaTarefas(ttk.Frame):
    """
    Aba de gerenciamento de tarefas.
    """
    
    def __init__(self, parent, log_manager, settings, **kwargs):
        """
        Inicializa a aba de tarefas.
        
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
        
        self.log_manager.log_sistema("SUCCESS", "Aba tarefas inicializada")
    
    def _criar_interface(self):
        """Cria a interface da aba de tarefas."""
        # Frame principal
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Título
        titulo_frame = ttk.Frame(main_frame)
        titulo_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(titulo_frame, text="⚙️ Gerenciamento de Tarefas", 
                 font=("Arial", 16, "bold")).pack(side=tk.LEFT)
        
        # Frame de controles
        controles_frame = ttk.Frame(main_frame)
        controles_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Botão Nova Tarefa
        self.btn_nova_tarefa = ttk.Button(controles_frame, text="➕ Nova Tarefa", 
                                         command=self._nova_tarefa)
        self.btn_nova_tarefa.pack(side=tk.LEFT, padx=(0, 10))
        
        # Botão Executar Tarefa
        self.btn_executar = ttk.Button(controles_frame, text="▶️ Executar Tarefa", 
                                      command=self._executar_tarefa)
        self.btn_executar.pack(side=tk.LEFT, padx=(0, 10))
        
        # Botão Editar Tarefa
        self.btn_editar = ttk.Button(controles_frame, text="✏️ Editar Tarefa", 
                                    command=self._editar_tarefa)
        self.btn_editar.pack(side=tk.LEFT, padx=(0, 10))
        
        # Botão Excluir Tarefa
        self.btn_excluir = ttk.Button(controles_frame, text="🗑️ Excluir Tarefa", 
                                     command=self._excluir_tarefa)
        self.btn_excluir.pack(side=tk.LEFT, padx=(0, 10))
        
        # Frame de filtros
        filtros_frame = ttk.LabelFrame(main_frame, text="Filtros", padding=10)
        filtros_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Filtros
        ttk.Label(filtros_frame, text="Tipo:").pack(side=tk.LEFT)
        self.tipo_var = tk.StringVar(value="Todos")
        self.cb_tipo = ttk.Combobox(filtros_frame, textvariable=self.tipo_var,
                                   values=["Todos", "Windows", "Linux", "Ambos"],
                                   width=10, state="readonly")
        self.cb_tipo.pack(side=tk.LEFT, padx=(5, 15))
        
        ttk.Label(filtros_frame, text="Status:").pack(side=tk.LEFT)
        self.status_var = tk.StringVar(value="Todos")
        self.cb_status = ttk.Combobox(filtros_frame, textvariable=self.status_var,
                                     values=["Todos", "Ativo", "Inativo"],
                                     width=10, state="readonly")
        self.cb_status.pack(side=tk.LEFT, padx=(5, 15))
        
        ttk.Label(filtros_frame, text="Servidor:").pack(side=tk.LEFT)
        self.servidor_var = tk.StringVar(value="Todos")
        self.cb_servidor = ttk.Combobox(filtros_frame, textvariable=self.servidor_var,
                                       values=["Todos", "Local", "Remoto"],
                                       width=10, state="readonly")
        self.cb_servidor.pack(side=tk.LEFT, padx=(5, 15))
        
        # Botão Aplicar Filtros
        ttk.Button(filtros_frame, text="Aplicar Filtros", 
                  command=self._aplicar_filtros).pack(side=tk.LEFT, padx=(10, 0))
        
        # Frame da lista de tarefas
        lista_frame = ttk.LabelFrame(main_frame, text="Lista de Tarefas", padding=10)
        lista_frame.pack(fill=tk.BOTH, expand=True)
        
        # TreeView para lista de tarefas
        colunas = ("ID", "Nome", "Tipo", "Servidor", "Status", "Última Execução", "Próxima Execução")
        self.tree_tarefas = ttk.Treeview(lista_frame, columns=colunas, show="headings", height=15)
        
        # Configurar colunas
        for col in colunas:
            self.tree_tarefas.heading(col, text=col)
            self.tree_tarefas.column(col, width=120)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(lista_frame, orient="vertical", command=self.tree_tarefas.yview)
        self.tree_tarefas.configure(yscrollcommand=scrollbar.set)
        
        self.tree_tarefas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind para seleção
        self.tree_tarefas.bind("<<TreeviewSelect>>", self._on_tarefa_selecionada)
        
        # Frame de informações
        info_frame = ttk.LabelFrame(main_frame, text="Informações da Tarefa", padding=10)
        info_frame.pack(fill=tk.X, pady=(20, 0))
        
        # Grid de informações
        info_grid = ttk.Frame(info_frame)
        info_grid.pack(fill=tk.X)
        
        ttk.Label(info_grid, text="Tarefa Selecionada:").grid(row=0, column=0, sticky="w", pady=2)
        self.lbl_tarefa_selecionada = ttk.Label(info_grid, text="Nenhuma tarefa selecionada", 
                                               foreground="gray")
        self.lbl_tarefa_selecionada.grid(row=0, column=1, sticky="w", padx=(10, 0), pady=2)
        
        ttk.Label(info_grid, text="Total de Tarefas:").grid(row=1, column=0, sticky="w", pady=2)
        self.lbl_total_tarefas = ttk.Label(info_grid, text="0")
        self.lbl_total_tarefas.grid(row=1, column=1, sticky="w", padx=(10, 0), pady=2)
        
        ttk.Label(info_grid, text="Tarefas Ativas:").grid(row=2, column=0, sticky="w", pady=2)
        self.lbl_tarefas_ativas = ttk.Label(info_grid, text="0")
        self.lbl_tarefas_ativas.grid(row=2, column=1, sticky="w", padx=(10, 0), pady=2)
        
        # Carregar dados iniciais
        self._carregar_tarefas()
    
    def _nova_tarefa(self):
        """Abre formulário para nova tarefa."""
        # TODO: Implementar na Fase 3
        messagebox.showinfo("Nova Tarefa", "Formulário de nova tarefa será implementado na Fase 3")
    
    def _executar_tarefa(self):
        """Executa a tarefa selecionada."""
        # TODO: Implementar na Fase 3
        messagebox.showinfo("Executar Tarefa", "Execução de tarefas será implementada na Fase 3")
    
    def _editar_tarefa(self):
        """Edita a tarefa selecionada."""
        # TODO: Implementar na Fase 3
        messagebox.showinfo("Editar Tarefa", "Edição de tarefas será implementada na Fase 3")
    
    def _excluir_tarefa(self):
        """Exclui a tarefa selecionada."""
        # TODO: Implementar na Fase 3
        messagebox.showinfo("Excluir Tarefa", "Exclusão de tarefas será implementada na Fase 3")
    
    def _aplicar_filtros(self):
        """Aplica os filtros configurados."""
        # TODO: Implementar na Fase 3
        messagebox.showinfo("Filtros", "Sistema de filtros será implementado na Fase 3")
    
    def _on_tarefa_selecionada(self, event):
        """Chamado quando uma tarefa é selecionada."""
        selecao = self.tree_tarefas.selection()
        if selecao:
            item = self.tree_tarefas.item(selecao[0])
            nome = item['values'][1] if item['values'] else "Desconhecida"
            self.lbl_tarefa_selecionada.config(text=nome)
        else:
            self.lbl_tarefa_selecionada.config(text="Nenhuma tarefa selecionada")
    
    def _carregar_tarefas(self):
        """Carrega a lista de tarefas."""
        # TODO: Implementar na Fase 3
        # Por enquanto, apenas limpar a lista
        for item in self.tree_tarefas.get_children():
            self.tree_tarefas.delete(item)
        
        # Dados de exemplo
        dados_exemplo = [
            ("1", "Backup MySQL", "Linux", "Servidor Web", "Ativo", "2024-01-15 02:00", "2024-01-16 02:00"),
            ("2", "Limpeza de Logs", "Windows", "Local", "Ativo", "2024-01-15 03:00", "2024-01-16 03:00"),
            ("3", "Deploy Aplicação", "Linux", "Servidor App", "Inativo", "2024-01-14 10:00", "Não agendado")
        ]
        
        for dados in dados_exemplo:
            self.tree_tarefas.insert("", "end", values=dados)
        
        # Atualizar contadores
        self.lbl_total_tarefas.config(text=str(len(dados_exemplo)))
        self.lbl_tarefas_ativas.config(text="2")  # Exemplo
    
    def atualizar(self):
        """Atualiza a aba de tarefas."""
        self._carregar_tarefas() 