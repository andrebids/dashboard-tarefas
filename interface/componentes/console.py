# -*- coding: utf-8 -*-
"""
Componente Console para exibir logs em tempo real.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
import datetime
from typing import Optional, Callable


class Console(ttk.Frame):
    """
    Componente de console para exibir logs em tempo real.
    """
    
    def __init__(self, parent, **kwargs):
        """
        Inicializa o componente console.
        
        Args:
            parent: Widget pai
            **kwargs: Argumentos adicionais para ttk.Frame
        """
        super().__init__(parent, **kwargs)
        
        self.parent = parent
        self.callback_limpar = None
        self.callback_exportar = None
        
        self._criar_interface()
        self._configurar_cores()
    
    def _criar_interface(self):
        """Cria a interface do console."""
        # Frame principal
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Frame superior com controles
        controls_frame = ttk.Frame(main_frame)
        controls_frame.pack(fill=tk.X, pady=(0, 5))
        
        # Label do console
        ttk.Label(controls_frame, text="Console de Logs", 
                 font=("Arial", 10, "bold")).pack(side=tk.LEFT)
        
        # Frame para botões
        buttons_frame = ttk.Frame(controls_frame)
        buttons_frame.pack(side=tk.RIGHT)
        
        # Botão Limpar
        self.btn_limpar = ttk.Button(buttons_frame, text="Limpar", 
                                    command=self._limpar_console)
        self.btn_limpar.pack(side=tk.LEFT, padx=(0, 5))
        
        # Botão Exportar
        self.btn_exportar = ttk.Button(buttons_frame, text="Exportar", 
                                      command=self._exportar_logs)
        self.btn_exportar.pack(side=tk.LEFT, padx=(0, 5))
        
        # Checkbox Auto-scroll
        self.auto_scroll_var = tk.BooleanVar(value=True)
        self.cb_auto_scroll = ttk.Checkbutton(buttons_frame, text="Auto-scroll", 
                                             variable=self.auto_scroll_var)
        self.cb_auto_scroll.pack(side=tk.LEFT)
        
        # Frame para filtros
        filters_frame = ttk.Frame(main_frame)
        filters_frame.pack(fill=tk.X, pady=(0, 5))
        
        # Label filtros
        ttk.Label(filters_frame, text="Filtros:").pack(side=tk.LEFT)
        
        # Combobox para nível de log
        ttk.Label(filters_frame, text="Nível:").pack(side=tk.LEFT, padx=(10, 0))
        self.nivel_var = tk.StringVar(value="Todos")
        self.cb_nivel = ttk.Combobox(filters_frame, textvariable=self.nivel_var, 
                                    values=["Todos", "INFO", "WARNING", "ERROR", "SUCCESS", "DEBUG"],
                                    width=10, state="readonly")
        self.cb_nivel.pack(side=tk.LEFT, padx=(5, 10))
        self.cb_nivel.bind("<<ComboboxSelected>>", self._aplicar_filtros)
        
        # Combobox para origem
        ttk.Label(filters_frame, text="Origem:").pack(side=tk.LEFT)
        self.origem_var = tk.StringVar(value="Todos")
        self.cb_origem = ttk.Combobox(filters_frame, textvariable=self.origem_var,
                                     values=["Todos", "sistema", "tarefas", "servidores", "planka"],
                                     width=10, state="readonly")
        self.cb_origem.pack(side=tk.LEFT, padx=(5, 10))
        self.cb_origem.bind("<<ComboboxSelected>>", self._aplicar_filtros)
        
        # Campo de busca
        ttk.Label(filters_frame, text="Buscar:").pack(side=tk.LEFT)
        self.busca_var = tk.StringVar()
        self.entry_busca = ttk.Entry(filters_frame, textvariable=self.busca_var, width=20)
        self.entry_busca.pack(side=tk.LEFT, padx=(5, 10))
        self.entry_busca.bind("<KeyRelease>", self._aplicar_filtros)
        
        # Área de texto para logs
        self.text_area = scrolledtext.ScrolledText(
            main_frame,
            wrap=tk.WORD,
            height=10,
            font=("Consolas", 9),
            bg="black",
            fg="white",
            insertbackground="white"
        )
        self.text_area.pack(fill=tk.BOTH, expand=True)
        
        # Configurar tags para cores
        self.text_area.tag_configure("info", foreground="lightblue")
        self.text_area.tag_configure("warning", foreground="yellow")
        self.text_area.tag_configure("error", foreground="red")
        self.text_area.tag_configure("success", foreground="lightgreen")
        self.text_area.tag_configure("debug", foreground="gray")
        self.text_area.tag_configure("timestamp", foreground="cyan")
        self.text_area.tag_configure("origem", foreground="magenta")
        
        # Lista para armazenar logs
        self.logs = []
        self.logs_filtrados = []
        
        # Contador de mensagens
        self.contador_frame = ttk.Frame(main_frame)
        self.contador_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.lbl_total = ttk.Label(self.contador_frame, text="Total: 0")
        self.lbl_total.pack(side=tk.LEFT)
        
        self.lbl_info = ttk.Label(self.contador_frame, text="INFO: 0", foreground="blue")
        self.lbl_info.pack(side=tk.LEFT, padx=(10, 0))
        
        self.lbl_warning = ttk.Label(self.contador_frame, text="WARNING: 0", foreground="orange")
        self.lbl_warning.pack(side=tk.LEFT, padx=(10, 0))
        
        self.lbl_error = ttk.Label(self.contador_frame, text="ERROR: 0", foreground="red")
        self.lbl_error.pack(side=tk.LEFT, padx=(10, 0))
        
        self.lbl_success = ttk.Label(self.contador_frame, text="SUCCESS: 0", foreground="green")
        self.lbl_success.pack(side=tk.LEFT, padx=(10, 0))
    
    def _configurar_cores(self):
        """Configura as cores do console."""
        # Configurar cores do tema
        style = ttk.Style()
        
        # Cores para diferentes níveis de log
        self.cores = {
            "INFO": "lightblue",
            "WARNING": "yellow", 
            "ERROR": "red",
            "SUCCESS": "lightgreen",
            "DEBUG": "gray"
        }
    
    def adicionar_log(self, nivel: str, mensagem: str, origem: str = "sistema", 
                     detalhes: Optional[dict] = None):
        """
        Adiciona um log ao console.
        
        Args:
            nivel: Nível do log
            mensagem: Mensagem do log
            origem: Origem do log
            detalhes: Detalhes adicionais
        """
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        
        # Criar entrada de log
        log_entry = {
            "timestamp": timestamp,
            "nivel": nivel.upper(),
            "mensagem": mensagem,
            "origem": origem,
            "detalhes": detalhes,
            "linha_completa": f"[{timestamp}] [{nivel.upper()}] [{origem}] {mensagem}"
        }
        
        # Adicionar à lista de logs
        self.logs.append(log_entry)
        
        # Aplicar filtros
        self._aplicar_filtros()
        
        # Atualizar contadores
        self._atualizar_contadores()
    
    def _aplicar_filtros(self, event=None):
        """Aplica os filtros configurados."""
        nivel_filtro = self.nivel_var.get()
        origem_filtro = self.origem_var.get()
        busca_texto = self.busca_var.get().lower()
        
        # Filtrar logs
        self.logs_filtrados = []
        for log in self.logs:
            # Filtro por nível
            if nivel_filtro != "Todos" and log["nivel"] != nivel_filtro:
                continue
            
            # Filtro por origem
            if origem_filtro != "Todos" and log["origem"] != origem_filtro:
                continue
            
            # Filtro por texto
            if busca_texto and busca_texto not in log["linha_completa"].lower():
                continue
            
            self.logs_filtrados.append(log)
        
        # Atualizar exibição
        self._atualizar_exibicao()
    
    def _atualizar_exibicao(self):
        """Atualiza a exibição dos logs filtrados."""
        # Limpar área de texto
        self.text_area.delete(1.0, tk.END)
        
        # Adicionar logs filtrados
        for log in self.logs_filtrados:
            # Formatar linha
            linha = f"[{log['timestamp']}] [{log['nivel']}] [{log['origem']}] {log['mensagem']}\n"
            
            # Inserir com cores
            pos_inicio = self.text_area.index(tk.END)
            self.text_area.insert(tk.END, linha)
            pos_fim = self.text_area.index(tk.END)
            
            # Aplicar tags de cor
            self.text_area.tag_add("timestamp", pos_inicio, f"{pos_inicio}+8c")
            self.text_area.tag_add("origem", f"{pos_inicio}+{len(log['nivel'])+4}c", 
                                 f"{pos_inicio}+{len(log['nivel'])+len(log['origem'])+4}c")
            
            # Cor do nível
            cor_tag = log["nivel"].lower()
            if cor_tag in self.cores:
                self.text_area.tag_add(cor_tag, f"{pos_inicio}+{len(log['timestamp'])+3}c",
                                     f"{pos_inicio}+{len(log['timestamp'])+len(log['nivel'])+3}c")
        
        # Auto-scroll se habilitado
        if self.auto_scroll_var.get():
            self.text_area.see(tk.END)
    
    def _atualizar_contadores(self):
        """Atualiza os contadores de mensagens."""
        contadores = {"INFO": 0, "WARNING": 0, "ERROR": 0, "SUCCESS": 0, "DEBUG": 0}
        
        for log in self.logs:
            nivel = log["nivel"]
            if nivel in contadores:
                contadores[nivel] += 1
        
        # Atualizar labels
        self.lbl_total.config(text=f"Total: {len(self.logs)}")
        self.lbl_info.config(text=f"INFO: {contadores['INFO']}")
        self.lbl_warning.config(text=f"WARNING: {contadores['WARNING']}")
        self.lbl_error.config(text=f"ERROR: {contadores['ERROR']}")
        self.lbl_success.config(text=f"SUCCESS: {contadores['SUCCESS']}")
    
    def _limpar_console(self):
        """Limpa o console."""
        self.logs = []
        self.logs_filtrados = []
        self.text_area.delete(1.0, tk.END)
        self._atualizar_contadores()
        
        # Chamar callback se definido
        if self.callback_limpar:
            self.callback_limpar()
    
    def _exportar_logs(self):
        """Exporta os logs para arquivo."""
        # Chamar callback se definido
        if self.callback_exportar:
            self.callback_exportar()
    
    def definir_callback_limpar(self, callback: Callable):
        """Define callback para limpar console."""
        self.callback_limpar = callback
    
    def definir_callback_exportar(self, callback: Callable):
        """Define callback para exportar logs."""
        self.callback_exportar = callback
    
    def obter_logs(self) -> list:
        """Retorna todos os logs."""
        return self.logs.copy()
    
    def obter_logs_filtrados(self) -> list:
        """Retorna os logs filtrados."""
        return self.logs_filtrados.copy()
    
    def limpar_logs_antigos(self, max_logs: int = 1000):
        """Remove logs antigos mantendo apenas os mais recentes."""
        if len(self.logs) > max_logs:
            self.logs = self.logs[-max_logs:]
            self._aplicar_filtros()
            self._atualizar_contadores() 