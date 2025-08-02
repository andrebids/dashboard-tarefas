# -*- coding: utf-8 -*-
"""
Componente de Tooltip personalizado para o Dashboard.
"""

import tkinter as tk
from tkinter import ttk


class Tooltip:
    """
    Tooltip personalizado para widgets Tkinter.
    """
    
    def __init__(self, widget, texto, delay=1000, duracao=3000):
        """
        Inicializa o tooltip.
        
        Args:
            widget: Widget que receberá o tooltip
            texto: Texto do tooltip
            delay: Delay em ms antes de mostrar
            duracao: Duração em ms que o tooltip fica visível
        """
        self.widget = widget
        self.texto = texto
        self.delay = delay
        self.duracao = duracao
        self.tooltip = None
        self.timer_id = None
        
        # Bind eventos
        self.widget.bind("<Enter>", self._on_enter)
        self.widget.bind("<Leave>", self._on_leave)
        self.widget.bind("<Button-1>", self._on_click)
    
    def _on_enter(self, event):
        """Chamado quando o mouse entra no widget."""
        self._agendar_tooltip()
    
    def _on_leave(self, event):
        """Chamado quando o mouse sai do widget."""
        self._cancelar_tooltip()
        self._esconder_tooltip()
    
    def _on_click(self, event):
        """Chamado quando o widget é clicado."""
        self._cancelar_tooltip()
        self._esconder_tooltip()
    
    def _agendar_tooltip(self):
        """Agenda a exibição do tooltip."""
        self._cancelar_tooltip()
        self.timer_id = self.widget.after(self.delay, self._mostrar_tooltip)
    
    def _cancelar_tooltip(self):
        """Cancela o timer do tooltip."""
        if self.timer_id:
            self.widget.after_cancel(self.timer_id)
            self.timer_id = None
    
    def _mostrar_tooltip(self):
        """Mostra o tooltip."""
        try:
            # Obter posição do widget
            x, y, _, _ = self.widget.bbox("insert")
            x += self.widget.winfo_rootx() + 25
            y += self.widget.winfo_rooty() + 20
            
            # Criar janela do tooltip
            self.tooltip = tk.Toplevel(self.widget)
            self.tooltip.wm_overrideredirect(True)
            self.tooltip.wm_geometry(f"+{x}+{y}")
            
            # Configurar estilo
            self.tooltip.configure(bg="black", relief="solid", bd=1)
            
            # Label com o texto
            label = tk.Label(self.tooltip, text=self.texto, 
                           bg="black", fg="white", 
                           font=("Arial", 9),
                           padx=5, pady=3,
                           justify=tk.LEFT)
            label.pack()
            
            # Agendar para esconder
            self.widget.after(self.duracao, self._esconder_tooltip)
            
        except Exception as e:
            # Em caso de erro, apenas ignorar
            pass
    
    def _esconder_tooltip(self):
        """Esconde o tooltip."""
        if self.tooltip:
            try:
                self.tooltip.destroy()
            except:
                pass
            self.tooltip = None


def criar_tooltip(widget, texto, delay=1000, duracao=3000):
    """
    Função helper para criar tooltips rapidamente.
    
    Args:
        widget: Widget que receberá o tooltip
        texto: Texto do tooltip
        delay: Delay em ms antes de mostrar
        duracao: Duração em ms que o tooltip fica visível
    
    Returns:
        Tooltip: Instância do tooltip criado
    """
    return Tooltip(widget, texto, delay, duracao) 