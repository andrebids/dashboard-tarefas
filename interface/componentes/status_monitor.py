# -*- coding: utf-8 -*-
"""
Componente de Monitoramento de Status - Exibição de status do Planka.
"""
import tkinter as tk
from tkinter import ttk
from typing import Dict, Callable, Optional

class StatusMonitor:
    """
    Componente de monitoramento de status.
    Responsável por exibir informações sobre o estado do Planka.
    """
    def __init__(self, parent, status_checker, callback_atualizar_status: Optional[Callable] = None):
        self.parent = parent
        self.status_checker = status_checker
        self.callback_atualizar_status = callback_atualizar_status
        self._criar_interface()
        self._verificar_status_inicial()
    
    def _criar_interface(self):
        """Cria a interface do componente."""
        # Frame principal
        self.frame = ttk.LabelFrame(self.parent, text="Status do Sistema", padding=15)
        
        # Grid de informações
        self.frame_info = ttk.Frame(self.frame)
        self.frame_info.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        
        # Status do Planka
        self.label_status_titulo = ttk.Label(self.frame_info, text="Status do Planka:", font=("Arial", 9, "bold"))
        self.label_status_titulo.grid(row=0, column=0, sticky="w", pady=(0, 5))
        
        self.label_status = ttk.Label(self.frame_info, text="Verificando...", font=("Arial", 9))
        self.label_status.grid(row=1, column=0, sticky="w", pady=(0, 10))
        
        # Modo ativo
        self.label_modo_titulo = ttk.Label(self.frame_info, text="Modo Ativo:", font=("Arial", 9, "bold"))
        self.label_modo_titulo.grid(row=2, column=0, sticky="w", pady=(0, 5))
        
        self.label_modo = ttk.Label(self.frame_info, text="Verificando...", font=("Arial", 9))
        self.label_modo.grid(row=3, column=0, sticky="w", pady=(0, 10))
        
        # Conectividade
        self.label_conectividade_titulo = ttk.Label(self.frame_info, text="Conectividade:", font=("Arial", 9, "bold"))
        self.label_conectividade_titulo.grid(row=4, column=0, sticky="w", pady=(0, 5))
        
        self.label_conectividade = ttk.Label(self.frame_info, text="Verificando...", font=("Arial", 9))
        self.label_conectividade.grid(row=5, column=0, sticky="w", pady=(0, 10))
        
        # Processos Docker
        self.label_docker_titulo = ttk.Label(self.frame_info, text="Processos Docker:", font=("Arial", 9, "bold"))
        self.label_docker_titulo.grid(row=6, column=0, sticky="w", pady=(0, 5))
        
        self.label_docker = ttk.Label(self.frame_info, text="Verificando...", font=("Arial", 9))
        self.label_docker.grid(row=7, column=0, sticky="w", pady=(0, 10))
        
        # Frame de controles
        self.frame_controles = ttk.Frame(self.frame)
        self.frame_controles.grid(row=1, column=0, sticky="ew")
        
        # Botão de atualização manual
        self.btn_atualizar = ttk.Button(
            self.frame_controles,
            text="Atualizar Status",
            command=self._atualizar_status_manual,
            style="TButton"
        )
        self.btn_atualizar.grid(row=0, column=0)
        
        # Configurar grid weights
        self.frame_info.columnconfigure(0, weight=1)
    
    def _verificar_status_inicial(self):
        """Verifica o status inicial."""
        try:
            self._atualizar_status_manual()
        except Exception as e:
            print(f"Erro na verificação inicial: {str(e)}")
    
    def _atualizar_status_manual(self):
        """Atualiza o status manualmente."""
        try:
            # Obter status do Planka
            status_info = self.status_checker.verificar_status_planka()
            
            # Atualizar UI
            self._atualizar_ui(status_info)
                
        except Exception as e:
            print(f"Erro ao atualizar status manual: {str(e)}")
            self._atualizar_ui({"status": "Erro", "modo_ativo": "desconhecido", "conectividade": False, "processos_docker": []})
    
    def _atualizar_ui(self, status_info: Dict):
        """Atualiza a interface."""
        try:
            # Atualizar labels principais
            self._atualizar_label_status(status_info.get('status', 'Desconhecido'))
            self._atualizar_label_modo(status_info.get('modo_ativo', 'desconhecido'))
            self._atualizar_label_conectividade(status_info.get('conectividade', False))
            self._atualizar_label_docker(status_info.get('processos_docker', []))
            
            # Chamar callback se definido
            if self.callback_atualizar_status:
                self.callback_atualizar_status(status_info)
                
        except Exception as e:
            print(f"Erro ao atualizar UI: {str(e)}")
    
    def _atualizar_label_status(self, status: str):
        """Atualiza o label de status."""
        cores = {
            'online': 'green',
            'offline': 'red',
            'erro': 'red',
            'Desconhecido': 'gray'
        }
        
        cor = cores.get(status, 'black')
        self.label_status.config(text=status, foreground=cor)
    
    def _atualizar_label_modo(self, modo: str):
        """Atualiza o label de modo."""
        cores = {
            'producao': 'green',
            'desenvolvimento': 'blue',
            'desconhecido': 'gray'
        }
        
        cor = cores.get(modo, 'black')
        texto_modo = modo.capitalize() if modo != 'desconhecido' else 'Desconhecido'
        self.label_modo.config(text=texto_modo, foreground=cor)
    
    def _atualizar_label_conectividade(self, conectividade: bool):
        """Atualiza o label de conectividade."""
        if conectividade:
            self.label_conectividade.config(text="✅ Acessível", foreground="green")
        else:
            self.label_conectividade.config(text="❌ Não acessível", foreground="red")
    
    def _atualizar_label_docker(self, processos: list):
        """Atualiza o label de processos Docker."""
        if processos and len(processos) > 0:
            self.label_docker.config(text=f"{len(processos)} processo(s) ativo(s)", foreground="green")
        else:
            self.label_docker.config(text="Nenhum processo ativo", foreground="gray")
    
    def definir_callback_atualizar_status(self, callback: Callable):
        """Define o callback para atualização de status."""
        self.callback_atualizar_status = callback
    
    def obter_widget(self) -> ttk.Frame:
        """Retorna o widget principal."""
        return self.frame
    
    def atualizar_status(self):
        """Atualiza o status."""
        self._atualizar_status_manual() 