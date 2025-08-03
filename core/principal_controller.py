# -*- coding: utf-8 -*-
"""
Controlador Principal - Coordenação dos componentes da aba principal.
"""
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
from typing import Dict, Callable, Optional

class PrincipalController:
    """
    Controlador principal da aba principal.
    Responsável por coordenar todos os componentes e gerenciar a comunicação entre eles.
    """
    def __init__(self, parent, settings, log_manager):
        self.parent = parent
        self.settings = settings
        self.log_manager = log_manager
        
        # Importar módulos
        self._importar_modulos()
        
        # Inicializar managers
        self._inicializar_managers()
        
        # Inicializar componentes
        self._inicializar_componentes()
        
        # Configurar callbacks
        self._configurar_callbacks()
        
        # Verificar status inicial
        self._verificar_status_inicial()
    
    def _importar_modulos(self):
        """Importa os módulos necessários."""
        try:
            from core.planka import PlankaManager
            from core.diagnostics import DiagnosticManager
            from core.repository import RepositoryManager
            from core.status_checker import StatusChecker
            
            from interface.componentes.planka_controls import PlankaControls
            from interface.componentes.diagnostic_panel import DiagnosticPanel
            from interface.componentes.repository_manager import RepositoryManager as RepoManagerUI
            from interface.componentes.status_monitor import StatusMonitor
            from interface.componentes.sync_manager import SyncManager
            
            self.PlankaManager = PlankaManager
            self.DiagnosticManager = DiagnosticManager
            self.RepositoryManager = RepositoryManager
            self.StatusChecker = StatusChecker
            
            self.PlankaControls = PlankaControls
            self.DiagnosticPanel = DiagnosticPanel
            self.RepoManagerUI = RepoManagerUI
            self.StatusMonitor = StatusMonitor
            self.SyncManager = SyncManager
            
        except ImportError as e:
            messagebox.showerror("Erro de Importação", f"Erro ao importar módulos: {str(e)}")
            raise
    
    def _inicializar_managers(self):
        """Inicializa os managers de lógica de negócio."""
        try:
            # Planka Manager
            self.planka_manager = self.PlankaManager(self.settings)
            
            # Diagnostic Manager
            self.diagnostic_manager = self.DiagnosticManager(self.settings, self.planka_manager)
            
            # Repository Manager
            self.repository_manager = self.RepositoryManager(self.settings)
            
            # Status Checker
            self.status_checker = self.StatusChecker(self.settings, self.planka_manager)
            
        except Exception as e:
            messagebox.showerror("Erro de Inicialização", f"Erro ao inicializar managers: {str(e)}")
            raise
    
    def _inicializar_componentes(self):
        """Inicializa os componentes de interface."""
        try:
            # Frame principal
            self.frame_principal = ttk.Frame(self.parent)
            self.frame_principal.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
            
            # Configurar grid
            self.frame_principal.columnconfigure(0, weight=1)
            self.frame_principal.columnconfigure(1, weight=1)
            
            # Frame esquerdo (controles e status)
            self.frame_esquerdo = ttk.Frame(self.frame_principal)
            self.frame_esquerdo.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
            self.frame_esquerdo.columnconfigure(0, weight=1)
            
            # Frame direito (logs e diagnósticos)
            self.frame_direito = ttk.Frame(self.frame_principal)
            self.frame_direito.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
            self.frame_direito.columnconfigure(0, weight=1)
            
            # Componente de controles do Planka
            self.planka_controls = self.PlankaControls(
                self.frame_esquerdo,
                self.planka_manager,
                self.log_manager,
                self.settings,
                self._callback_atualizar_status
            )
            self.planka_controls.obter_widget().pack(fill=tk.X, pady=(0, 10))
            
            # Componente de monitoramento de status
            self.status_monitor = self.StatusMonitor(
                self.frame_esquerdo,
                self.status_checker,
                self._callback_atualizar_status
            )
            self.status_monitor.obter_widget().pack(fill=tk.BOTH, expand=True, pady=(0, 10))
            
            # Componente de sincronização produção/desenvolvimento
            self.sync_manager = self.SyncManager(
                self.frame_esquerdo,
                self
            )
            self.sync_manager.pack(fill=tk.X, pady=(0, 10))
            
            # Componente de gestão de repositório
            self.repo_manager_ui = self.RepoManagerUI(
                self.frame_esquerdo,
                self.repository_manager,
                self.log_manager,
                self._callback_adicionar_log
            )
            self.repo_manager_ui.obter_widget().pack(fill=tk.X)
            
            # Componente de painel de diagnósticos
            self.diagnostic_panel = self.DiagnosticPanel(
                self.frame_direito,
                self.diagnostic_manager,
                self.log_manager,
                self._callback_adicionar_log
            )
            self.diagnostic_panel.obter_widget().pack(fill=tk.BOTH, expand=True)
            
        except Exception as e:
            messagebox.showerror("Erro de Interface", f"Erro ao inicializar componentes: {str(e)}")
            raise
    
    def _configurar_callbacks(self):
        """Configura os callbacks entre componentes."""
        try:
            # Configurar callbacks de logs
            self.planka_controls.definir_callback_atualizar_status(self._callback_atualizar_status)
            self.repo_manager_ui.definir_callback_adicionar_log(self._callback_adicionar_log)
            self.diagnostic_panel.definir_callback_adicionar_log(self._callback_adicionar_log)
            self.status_monitor.definir_callback_atualizar_status(self._callback_atualizar_status)
            
        except Exception as e:
            print(f"Erro ao configurar callbacks: {str(e)}")
    
    def _verificar_status_inicial(self):
        """Verifica o status inicial do sistema de forma otimizada."""
        try:
            # Executar verificação em thread separada com delay
            threading.Thread(target=self._executar_verificacao_inicial, daemon=True).start()
            
        except Exception as e:
            self._callback_adicionar_log(f"Erro na verificação inicial: {str(e)}", "error")
    
    def _executar_verificacao_inicial(self):
        """Executa a verificação inicial em thread separada com otimizações."""
        try:
            # Aguardar um pouco para não interferir na inicialização da UI
            time.sleep(1)
            
            self._callback_adicionar_log("Iniciando verificação do sistema...", "info")
            
            # Verificar status do Planka (com timeout reduzido)
            try:
                status_info = self.status_checker.verificar_status_inicial()
                self._callback_adicionar_log(f"Status do Planka: {status_info.get('status', 'Desconhecido')}", "info")
            except Exception as e:
                self._callback_adicionar_log(f"Erro ao verificar status do Planka: {str(e)}", "warning")
            
            # Verificar dependências (usando cache para evitar verificações constantes)
            try:
                dependencias = self.repository_manager.verificar_dependencias()
                
                todas_disponiveis = all(dependencias.values())
                if todas_disponiveis:
                    self._callback_adicionar_log("Todas as dependências estão disponíveis", "success")
                else:
                    self._callback_adicionar_log("Algumas dependências estão em falta", "warning")
                    for dep, disponivel in dependencias.items():
                        if not disponivel:
                            self._callback_adicionar_log(f"  - {dep}: Não encontrado", "error")
                
                # Informar sobre o cache se disponível
                info_cache = self.planka_manager.obter_info_cache_dependencias()
                if info_cache.get("cache_existe"):
                    self._callback_adicionar_log("Cache de dependências ativo - verificações otimizadas", "info")
                    
            except Exception as e:
                self._callback_adicionar_log(f"Erro ao verificar dependências: {str(e)}", "warning")
            
            self._callback_adicionar_log("Verificação inicial concluída", "info")
            
        except Exception as e:
            self._callback_adicionar_log(f"Erro na verificação inicial: {str(e)}", "error")
    
    def _callback_atualizar_status(self, status_info: Dict):
        """Callback para atualização de status."""
        try:
            # Atualizar estado dos botões
            self.planka_controls.atualizar_estado_botoes(status_info.get('status', 'Desconhecido'))
            
            # Atualizar informações do repositório
            self.repo_manager_ui.atualizar_informacoes()
            
        except Exception as e:
            print(f"Erro no callback de atualização de status: {str(e)}")
    
    def _callback_adicionar_log(self, mensagem: str, nivel: str = "info"):
        """Callback para adicionar logs."""
        try:
            self.log_manager.registrar_log(nivel, mensagem, "sistema")
        except Exception as e:
            print(f"Erro no callback de adicionar log: {str(e)}")
    
    def obter_widget(self) -> ttk.Frame:
        """Retorna o widget principal do controlador."""
        return self.frame_principal
    
    def atualizar_status(self):
        """Atualiza o status de todos os componentes."""
        try:
            # Atualizar status monitor
            self.status_monitor._atualizar_status_manual()
            
            # Atualizar informações do repositório
            self.repo_manager_ui.atualizar_informacoes()
            
        except Exception as e:
            self._callback_adicionar_log(f"Erro ao atualizar status: {str(e)}", "error")
    
    def parar_monitoramento(self):
        """Para o monitoramento automático."""
        try:
            self.status_monitor.parar_monitoramento()
        except Exception as e:
            print(f"Erro ao parar monitoramento: {str(e)}")
    
    def iniciar_monitoramento(self):
        """Inicia o monitoramento automático."""
        try:
            self.status_monitor.iniciar_monitoramento()
        except Exception as e:
            print(f"Erro ao iniciar monitoramento: {str(e)}")
    
    def limpar_logs(self):
        """Limpa todos os logs."""
        try:
            self.log_manager.limpar_logs()
        except Exception as e:
            print(f"Erro ao limpar logs: {str(e)}")
    
    def obter_status_atual(self) -> Dict:
        """Retorna o status atual do sistema."""
        try:
            return self.status_checker.verificar_status_planka()
        except Exception as e:
            return {"status": "Erro", "erro": str(e)}
    
    def executar_diagnostico_rapido(self):
        """Executa diagnóstico rápido."""
        try:
            self.diagnostic_panel._diagnostico_rapido()
        except Exception as e:
            self._callback_adicionar_log(f"Erro ao executar diagnóstico rápido: {str(e)}", "error")
    
    def executar_diagnostico_completo(self):
        """Executa diagnóstico completo."""
        try:
            self.diagnostic_panel._diagnostico_completo()
        except Exception as e:
            self._callback_adicionar_log(f"Erro ao executar diagnóstico completo: {str(e)}", "error")
    
    def sincronizar_producao_com_desenvolvimento(self):
        """Sincroniza a versão de produção com a de desenvolvimento."""
        try:
            self._callback_adicionar_log("Iniciando sincronização de produção com desenvolvimento...", "info")
            
            # Executar sincronização
            sucesso, mensagem = self.planka_manager.sincronizar_producao_com_desenvolvimento()
            
            if sucesso:
                self._callback_adicionar_log(f"✅ {mensagem}", "success")
                self._callback_adicionar_log("A versão de produção agora usa o mesmo código da versão de desenvolvimento", "info")
                self._callback_adicionar_log("Reinicie o Planka para aplicar as mudanças", "warning")
            else:
                self._callback_adicionar_log(f"❌ Erro na sincronização: {mensagem}", "error")
                
        except Exception as e:
            self._callback_adicionar_log(f"Erro ao sincronizar produção com desenvolvimento: {str(e)}", "error")
    
    def restaurar_producao_original(self):
        """Restaura a versão de produção original."""
        try:
            self._callback_adicionar_log("Restaurando versão de produção original...", "info")
            
            # Executar restauração
            sucesso, mensagem = self.planka_manager.restaurar_producao_original()
            
            if sucesso:
                self._callback_adicionar_log(f"✅ {mensagem}", "success")
                self._callback_adicionar_log("A versão de produção voltou a usar a imagem oficial", "info")
                self._callback_adicionar_log("Reinicie o Planka para aplicar as mudanças", "warning")
            else:
                self._callback_adicionar_log(f"❌ Erro na restauração: {mensagem}", "error")
                
        except Exception as e:
            self._callback_adicionar_log(f"Erro ao restaurar produção original: {str(e)}", "error")
    
    def verificar_sincronizacao_producao(self) -> Dict:
        """Verifica se a produção está sincronizada com desenvolvimento."""
        try:
            return self.planka_manager.verificar_sincronizacao_producao()
        except Exception as e:
            return {
                "sincronizada": False,
                "motivo": f"Erro ao verificar: {str(e)}",
                "backup_existe": False,
                "modo_atual": "erro"
            }
    
    def configurar_producao_sempre_desenvolvimento(self):
        """Configura produção para sempre usar desenvolvimento."""
        try:
            self._callback_adicionar_log("Configurando produção para sempre usar desenvolvimento...", "info")
            
            # Executar configuração
            sucesso, mensagem = self.planka_manager.configurar_producao_sempre_desenvolvimento()
            
            if sucesso:
                self._callback_adicionar_log(f"✅ {mensagem}", "success")
                self._callback_adicionar_log("A partir de agora, produção sempre usará código de desenvolvimento", "info")
                self._callback_adicionar_log("Reinicie o Planka para aplicar as mudanças", "warning")
            else:
                self._callback_adicionar_log(f"❌ Erro na configuração: {mensagem}", "error")
                
        except Exception as e:
            self._callback_adicionar_log(f"Erro ao configurar produção: {str(e)}", "error") 