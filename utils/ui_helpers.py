# -*- coding: utf-8 -*-
"""
Helpers de UI - Funções auxiliares para interface.
"""

import tkinter as tk
from tkinter import ttk
from typing import Dict, Any, Optional


class UIHelpers:
    """
    Classe com helpers para criação e formatação de widgets.
    """
    
    @staticmethod
    def criar_frame_titulo(parent, titulo: str, icone: str = "") -> ttk.Frame:
        """
        Cria um frame com título e ícone.
        
        Args:
            parent: Widget pai
            titulo: Texto do título
            icone: Ícone (emoji) opcional
            
        Returns:
            ttk.Frame configurado
        """
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.X, pady=(0, 20))
        
        texto_titulo = f"{icone} {titulo}" if icone else titulo
        ttk.Label(frame, text=texto_titulo, 
                 font=("Arial", 16, "bold")).pack(side=tk.LEFT)
        
        return frame
    
    @staticmethod
    def criar_label_frame(parent, titulo: str, padding: int = 20) -> ttk.LabelFrame:
        """
        Cria um LabelFrame com título.
        
        Args:
            parent: Widget pai
            titulo: Texto do título
            padding: Padding interno
            
        Returns:
            ttk.LabelFrame configurado
        """
        return ttk.LabelFrame(parent, text=titulo, padding=padding)
    
    @staticmethod
    def criar_botao(parent, texto: str, comando, icone: str = "", 
                   estilo: str = "TButton", **kwargs) -> ttk.Button:
        """
        Cria um botão com ícone e estilo.
        
        Args:
            parent: Widget pai
            texto: Texto do botão
            comando: Função a ser executada
            icone: Ícone (emoji) opcional
            estilo: Estilo do botão
            **kwargs: Argumentos adicionais
            
        Returns:
            ttk.Button configurado
        """
        texto_botao = f"{icone} {texto}" if icone else texto
        return ttk.Button(parent, text=texto_botao, command=comando, 
                         style=estilo, **kwargs)
    
    @staticmethod
    def criar_botao_linha(parent, botoes: list, padx: int = 10) -> ttk.Frame:
        """
        Cria uma linha de botões.
        
        Args:
            parent: Widget pai
            botoes: Lista de dicionários com configurações dos botões
            padx: Espaçamento horizontal entre botões
            
        Returns:
            ttk.Frame com os botões
        """
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.X, pady=(0, 10))
        
        for i, botao_config in enumerate(botoes):
            botao = UIHelpers.criar_botao(frame, **botao_config)
            botao.pack(side=tk.LEFT, padx=(0 if i == 0 else padx, 0))
        
        return frame
    
    @staticmethod
    def criar_area_logs(parent, altura: int = 10, **kwargs) -> tuple:
        """
        Cria uma área de logs com scrollbar.
        
        Args:
            parent: Widget pai
            altura: Altura em linhas
            **kwargs: Argumentos adicionais para o Text
            
        Returns:
            Tuple (Text, Scrollbar)
        """
        # Frame para a área de logs
        logs_frame = ttk.Frame(parent)
        logs_frame.pack(fill=tk.BOTH, expand=True)
        
        # Área de texto
        text_logs = tk.Text(logs_frame, height=altura, font=("Consolas", 9),
                           bg="black", fg="white", wrap=tk.WORD, **kwargs)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(logs_frame, orient="vertical", command=text_logs.yview)
        text_logs.configure(yscrollcommand=scrollbar.set)
        
        # Layout
        text_logs.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Configurar tags para cores
        text_logs.tag_configure("info", foreground="lightblue")
        text_logs.tag_configure("warning", foreground="yellow")
        text_logs.tag_configure("error", foreground="red")
        text_logs.tag_configure("success", foreground="lightgreen")
        
        return text_logs, scrollbar
    
    @staticmethod
    def criar_grid_info(parent, informacoes: Dict[str, str]) -> ttk.Frame:
        """
        Cria um grid de informações.
        
        Args:
            parent: Widget pai
            informacoes: Dicionário com chave-valor das informações
            
        Returns:
            ttk.Frame com o grid
        """
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.X)
        
        for i, (chave, valor) in enumerate(informacoes.items()):
            ttk.Label(frame, text=f"{chave}:").grid(row=i, column=0, sticky="w", pady=2)
            ttk.Label(frame, text=valor, foreground="blue").grid(row=i, column=1, sticky="w", padx=(10, 0), pady=2)
        
        return frame
    
    @staticmethod
    def criar_controles_logs(parent, comandos: Dict[str, callable]) -> ttk.Frame:
        """
        Cria controles para logs.
        
        Args:
            parent: Widget pai
            comandos: Dicionário com nome do botão e função
            
        Returns:
            ttk.Frame com os controles
        """
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.X, pady=(10, 0))
        
        for i, (nome, comando) in enumerate(comandos.items()):
            ttk.Button(frame, text=nome, command=comando).pack(side=tk.LEFT, padx=(0 if i == 0 else 10, 0))
        
        return frame
    
    @staticmethod
    def adicionar_log(text_widget: tk.Text, mensagem: str, nivel: str = "info"):
        """
        Adiciona um log à área de texto.
        
        Args:
            text_widget: Widget Text
            mensagem: Mensagem a adicionar
            nivel: Nível do log (info, warning, error, success)
        """
        try:
            import datetime
            timestamp = datetime.datetime.now().strftime("%H:%M:%S")
            log_entry = f"[{timestamp}] {mensagem}\n"
            
            text_widget.insert(tk.END, log_entry, nivel)
            text_widget.see(tk.END)
            
        except Exception as e:
            print(f"Erro ao adicionar log: {e}")
    
    @staticmethod
    def limpar_logs(text_widget: tk.Text):
        """
        Limpa a área de logs.
        
        Args:
            text_widget: Widget Text
        """
        text_widget.delete(1.0, tk.END)
    
    @staticmethod
    def criar_indicador_status(parent, texto_inicial: str = "Status: Verificando...") -> ttk.Label:
        """
        Cria um indicador de status.
        
        Args:
            parent: Widget pai
            texto_inicial: Texto inicial do indicador
            
        Returns:
            ttk.Label configurado
        """
        return ttk.Label(parent, text=texto_inicial, font=("Arial", 10))
    
    @staticmethod
    def atualizar_indicador_status(label: ttk.Label, status_info: Dict):
        """
        Atualiza o indicador de status.
        
        Args:
            label: Label do indicador
            status_info: Informações do status
        """
        try:
            status = status_info.get("status", "desconhecido")
            modo_ativo = status_info.get("modo_ativo", "desconhecido")
            cor = status_info.get("cor", "black")
            icone = status_info.get("icone", "❓")
            
            if status == "online":
                if modo_ativo == "desenvolvimento":
                    texto = f"Status: {icone} Desenvolvimento"
                elif modo_ativo == "producao":
                    texto = f"Status: {icone} Produção"
                else:
                    texto = f"Status: {icone} Rodando"
            elif status == "offline":
                texto = f"Status: {icone} Parado"
            else:
                texto = f"Status: {icone} Erro"
            
            label.config(text=texto, foreground=cor)
            
        except Exception as e:
            label.config(text="Status: ⚠️ Erro", foreground="orange")
    
    @staticmethod
    def criar_progresso(parent, texto: str = "Processando...") -> tuple:
        """
        Cria um indicador de progresso.
        
        Args:
            parent: Widget pai
            texto: Texto do progresso
            
        Returns:
            Tuple (Label, Progressbar)
        """
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.X, pady=5)
        
        label = ttk.Label(frame, text=texto)
        label.pack(side=tk.LEFT)
        
        progressbar = ttk.Progressbar(frame, mode='indeterminate')
        progressbar.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(10, 0))
        
        return label, progressbar
    
    @staticmethod
    def iniciar_progresso(progressbar: ttk.Progressbar):
        """
        Inicia a animação do progresso.
        
        Args:
            progressbar: Widget Progressbar
        """
        progressbar.start()
    
    @staticmethod
    def parar_progresso(progressbar: ttk.Progressbar):
        """
        Para a animação do progresso.
        
        Args:
            progressbar: Widget Progressbar
        """
        progressbar.stop()
    
    @staticmethod
    def criar_tooltip(widget: tk.Widget, texto: str):
        """
        Cria um tooltip para um widget.
        
        Args:
            widget: Widget alvo
            texto: Texto do tooltip
        """
        def mostrar_tooltip(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
            
            label = ttk.Label(tooltip, text=texto, background="#ffffe0", 
                             relief="solid", borderwidth=1)
            label.pack()
            
            def esconder_tooltip(event):
                tooltip.destroy()
            
            widget.bind('<Leave>', esconder_tooltip)
            tooltip.bind('<Leave>', esconder_tooltip)
        
        widget.bind('<Enter>', mostrar_tooltip)
    
    @staticmethod
    def formatar_tamanho(bytes_size: int) -> str:
        """
        Formata tamanho em bytes para formato legível.
        
        Args:
            bytes_size: Tamanho em bytes
            
        Returns:
            String formatada
        """
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes_size < 1024.0:
                return f"{bytes_size:.1f} {unit}"
            bytes_size /= 1024.0
        return f"{bytes_size:.1f} TB"
    
    @staticmethod
    def formatar_tempo(segundos: float) -> str:
        """
        Formata tempo em segundos para formato legível.
        
        Args:
            segundos: Tempo em segundos
            
        Returns:
            String formatada
        """
        if segundos < 60:
            return f"{segundos:.1f}s"
        elif segundos < 3600:
            minutos = segundos / 60
            return f"{minutos:.1f}min"
        else:
            horas = segundos / 3600
            return f"{horas:.1f}h"
    
    @staticmethod
    def criar_estilo_botao_accent():
        """
        Cria estilo para botão de destaque.
        
        Returns:
            Nome do estilo criado
        """
        style = ttk.Style()
        style.configure("Accent.TButton", 
                       background="#0078d4", 
                       foreground="white",
                       font=("Arial", 10, "bold"))
        return "Accent.TButton" 