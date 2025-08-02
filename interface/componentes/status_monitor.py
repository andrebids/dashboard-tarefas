# -*- coding: utf-8 -*-
"""
Componente de Monitoramento de Status - Exibição de status em tempo real do Planka.
"""
import tkinter as tk
from tkinter import ttk
import threading
import time
from typing import Dict, Callable, Optional

class StatusMonitor:
    """
    Componente de monitoramento de status.
    Responsável por exibir informações em tempo real sobre o estado do Planka.
    """
    def __init__(self, parent, status_checker, callback_atualizar_status: Optional[Callable] = None):
        self.parent = parent
        self.status_checker = status_checker
        self.callback_atualizar_status = callback_atualizar_status
        self.monitoramento_ativo = False
        self.thread_monitoramento = None
        self._criar_interface()
        self._iniciar_monitoramento()
    
    def _criar_interface(self):
        """Cria a interface do componente."""
        # Frame principal
        self.frame = ttk.LabelFrame(self.parent, text="Status do Sistema", padding=20)
        
        # Grid de informações
        self.frame_info = ttk.Frame(self.frame)
        self.frame_info.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        
        # Status do Planka
        self.label_status_titulo = ttk.Label(self.frame_info, text="Status do Planka:", font=("Arial", 10, "bold"))
        self.label_status_titulo.grid(row=0, column=0, sticky="w", pady=(0, 5))
        
        self.label_status = ttk.Label(self.frame_info, text="Verificando...", font=("Arial", 10))
        self.label_status.grid(row=1, column=0, sticky="w", pady=(0, 10))
        
        # Modo ativo
        self.label_modo_titulo = ttk.Label(self.frame_info, text="Modo Ativo:", font=("Arial", 10, "bold"))
        self.label_modo_titulo.grid(row=2, column=0, sticky="w", pady=(0, 5))
        
        self.label_modo = ttk.Label(self.frame_info, text="Verificando...", font=("Arial", 10))
        self.label_modo.grid(row=3, column=0, sticky="w", pady=(0, 10))
        
        # Conectividade
        self.label_conectividade_titulo = ttk.Label(self.frame_info, text="Conectividade:", font=("Arial", 10, "bold"))
        self.label_conectividade_titulo.grid(row=4, column=0, sticky="w", pady=(0, 5))
        
        self.label_conectividade = ttk.Label(self.frame_info, text="Verificando...", font=("Arial", 10))
        self.label_conectividade.grid(row=5, column=0, sticky="w", pady=(0, 10))
        
        # Processos Docker
        self.label_docker_titulo = ttk.Label(self.frame_info, text="Processos Docker:", font=("Arial", 10, "bold"))
        self.label_docker_titulo.grid(row=6, column=0, sticky="w", pady=(0, 5))
        
        self.label_docker = ttk.Label(self.frame_info, text="Verificando...", font=("Arial", 10))
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
        self.btn_atualizar.grid(row=0, column=0, padx=(0, 10))
        
        # Botão de parar/iniciar monitoramento
        self.btn_monitoramento = ttk.Button(
            self.frame_controles,
            text="Parar Monitoramento",
            command=self._alternar_monitoramento,
            style="TButton"
        )
        self.btn_monitoramento.grid(row=0, column=1)
        
        # Frame de informações detalhadas
        self.frame_detalhes = ttk.LabelFrame(self.frame, text="Informações Detalhadas", padding=10)
        self.frame_detalhes.grid(row=2, column=0, sticky="ew", pady=(10, 0))
        
        # Área de texto para informações detalhadas
        self.text_detalhes = tk.Text(self.frame_detalhes, height=6, width=60, wrap=tk.WORD)
        self.text_detalhes.grid(row=0, column=0, sticky="ew")
        
        # Scrollbar para a área de texto
        self.scrollbar_detalhes = ttk.Scrollbar(self.frame_detalhes, orient="vertical", command=self.text_detalhes.yview)
        self.scrollbar_detalhes.grid(row=0, column=1, sticky="ns")
        self.text_detalhes.configure(yscrollcommand=self.scrollbar_detalhes.set)
        
        # Configurar grid weights
        self.frame_info.columnconfigure(0, weight=1)
        self.frame_detalhes.columnconfigure(0, weight=1)
    
    def _iniciar_monitoramento(self):
        """Inicia o monitoramento automático."""
        self.monitoramento_ativo = True
        self.thread_monitoramento = threading.Thread(target=self._loop_monitoramento)
        self.thread_monitoramento.daemon = True
        self.thread_monitoramento.start()
        self.btn_monitoramento.config(text="Parar Monitoramento")
    
    def _parar_monitoramento(self):
        """Para o monitoramento automático."""
        self.monitoramento_ativo = False
        self.btn_monitoramento.config(text="Iniciar Monitoramento")
    
    def _alternar_monitoramento(self):
        """Alterna entre iniciar e parar o monitoramento."""
        if self.monitoramento_ativo:
            self._parar_monitoramento()
        else:
            self._iniciar_monitoramento()
    
    def _loop_monitoramento(self):
        """Loop principal do monitoramento."""
        while self.monitoramento_ativo:
            try:
                self._atualizar_status()
                time.sleep(30)  # Atualizar a cada 30 segundos
            except Exception as e:
                print(f"Erro no monitoramento: {str(e)}")
                time.sleep(60)  # Aguardar mais tempo em caso de erro
    
    def _atualizar_status_manual(self):
        """Atualiza o status manualmente."""
        try:
            # Obter status do Planka
            status_info = self.status_checker.verificar_status_planka()
            
            # Atualizar UI diretamente (já estamos na thread principal)
            self._atualizar_ui(status_info)
                
        except Exception as e:
            print(f"Erro ao atualizar status manual: {str(e)}")
    
    def _atualizar_status(self):
        """Atualiza as informações de status."""
        try:
            # Obter status do Planka
            status_info = self.status_checker.verificar_status_planka()
            
            # Agendar atualização da UI na thread principal
            self.frame.after(0, lambda: self._atualizar_ui(status_info))
                
        except Exception as e:
            print(f"Erro ao atualizar status: {str(e)}")
    
    def _atualizar_ui(self, status_info: Dict):
        """Atualiza a interface na thread principal."""
        try:
            # Atualizar labels principais
            self._atualizar_label_status(status_info.get('status', 'Desconhecido'))
            self._atualizar_label_modo(status_info.get('modo', 'desconhecido'))
            self._atualizar_label_conectividade(status_info.get('conectividade', False))
            self._atualizar_label_docker(status_info.get('processos_docker', []))
            
            # Atualizar informações detalhadas
            self._atualizar_informacoes_detalhadas(status_info)
            
            # Chamar callback se definido
            if self.callback_atualizar_status:
                self.callback_atualizar_status(status_info)
                
        except Exception as e:
            print(f"Erro ao atualizar UI: {str(e)}")
    
    def _atualizar_label_status(self, status: str):
        """Atualiza o label de status."""
        cores = {
            'Rodando': 'green',
            'Parado': 'red',
            'Iniciando': 'orange',
            'Parando': 'orange',
            'Erro': 'red',
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
        texto_modo = modo.capitalize()
        self.label_modo.config(text=texto_modo, foreground=cor)
    
    def _atualizar_label_conectividade(self, conectividade_info: Dict):
        """Atualiza o label de conectividade com informações detalhadas."""
        if isinstance(conectividade_info, bool):
            # Compatibilidade com versão antiga
            if conectividade_info:
                self.label_conectividade.config(text="✓ Acessível", foreground="green")
            else:
                self.label_conectividade.config(text="✗ Não acessível", foreground="red")
            return
        
        # Nova versão com informações detalhadas
        if conectividade_info.get("acessivel", False):
            tempo = conectividade_info.get("tempo_resposta", 0)
            self.label_conectividade.config(text=f"✓ Acessível ({tempo:.2f}s)", foreground="green")
        else:
            erro = conectividade_info.get("erro", "Desconhecido")
            sugestao = conectividade_info.get("sugestao", "")
            
            # Texto mais curto para o label principal
            if "não está rodando" in erro.lower():
                texto = "✗ Planka parado"
            elif "timeout" in erro.lower():
                texto = "✗ Timeout"
            elif "connectionerror" in erro.lower():
                texto = "✗ Não responde"
            else:
                texto = "✗ Não acessível"
            
            self.label_conectividade.config(text=texto, foreground="red")
            
            # Adicionar tooltip com detalhes
            self._criar_tooltip_conectividade(sugestao)
    
    def _criar_tooltip_conectividade(self, sugestao: str):
        """Cria tooltip para mostrar sugestão de conectividade."""
        def mostrar_tooltip(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
            
            label = tk.Label(tooltip, text=f"Sugestão: {sugestao}", justify=tk.LEFT,
                           background="#ffffe0", relief=tk.SOLID, borderwidth=1,
                           font=("Arial", 8))
            label.pack()
            
            def esconder_tooltip(event):
                tooltip.destroy()
            
            self.label_conectividade.bind('<Leave>', esconder_tooltip)
            tooltip.bind('<Leave>', esconder_tooltip)
        
        self.label_conectividade.bind('<Enter>', mostrar_tooltip)
    
    def _atualizar_label_docker(self, processos: list):
        """Atualiza o label de processos Docker."""
        if not processos:
            self.label_docker.config(text="Nenhum processo ativo", foreground="gray")
        else:
            texto = f"{len(processos)} processo(s) ativo(s)"
            self.label_docker.config(text=texto, foreground="green")
    
    def _atualizar_informacoes_detalhadas(self, status_info: Dict):
        """Atualiza as informações detalhadas."""
        self.text_detalhes.delete(1.0, tk.END)
        
        detalhes = []
        
        # Informações básicas
        detalhes.append("=== INFORMAÇÕES BÁSICAS ===")
        detalhes.append(f"Status: {status_info.get('status', 'N/A')}")
        detalhes.append(f"Modo: {status_info.get('modo', 'N/A')}")
        detalhes.append(f"Conectividade: {'Sim' if status_info.get('conectividade', False) else 'Não'}")
        detalhes.append("")
        
        # Processos Docker
        processos = status_info.get('processos_docker', [])
        detalhes.append("=== PROCESSOS DOCKER ===")
        if processos:
            for processo in processos:
                detalhes.append(f"• {processo.get('nome', 'N/A')} - {processo.get('status', 'N/A')}")
        else:
            detalhes.append("Nenhum processo Docker ativo")
        detalhes.append("")
        
        # Recursos do sistema
        recursos = status_info.get('recursos_sistema', {})
        if recursos:
            detalhes.append("=== RECURSOS DO SISTEMA ===")
            detalhes.append(f"CPU: {recursos.get('cpu', 'N/A')}")
            detalhes.append(f"Memória: {recursos.get('memoria', 'N/A')}")
            detalhes.append(f"Disco: {recursos.get('disco', 'N/A')}")
            detalhes.append("")
        
        # Logs recentes
        logs = status_info.get('logs_recentes', [])
        if logs:
            detalhes.append("=== LOGS RECENTES ===")
            for log in logs[-5:]:  # Últimos 5 logs
                detalhes.append(f"[{log.get('timestamp', 'N/A')}] {log.get('mensagem', 'N/A')}")
        
        # Inserir detalhes no texto
        self.text_detalhes.insert(1.0, "\n".join(detalhes))
    
    def definir_callback_atualizar_status(self, callback: Callable):
        """Define callback para atualização de status."""
        self.callback_atualizar_status = callback
    
    def obter_widget(self) -> ttk.Frame:
        """Retorna o widget principal do componente."""
        return self.frame
    
    def parar_monitoramento(self):
        """Para o monitoramento."""
        self._parar_monitoramento()
    
    def iniciar_monitoramento(self):
        """Inicia o monitoramento."""
        self._iniciar_monitoramento() 