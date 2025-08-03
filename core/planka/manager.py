# -*- coding: utf-8 -*-
"""
Classe principal do PlankaManager.
Coordena todos os módulos especializados.
"""

from .dependency_checker import DependencyChecker
from .status_monitor import StatusMonitor
from .container_manager import ContainerManager
from .production_manager import ProductionManager
from .logs_manager import LogsManager
from .diagnostic_manager import DiagnosticManager
from .backup_manager import BackupManager
from .utils import PlankaUtils


class PlankaManager:
    """
    Gerenciador principal do Planka personalizado.
    Coordena todos os módulos especializados.
    """
    
    def __init__(self, settings):
        """
        Inicializa o gerenciador do Planka.
        
        Args:
            settings: Instância das configurações do sistema
        """
        self.settings = settings
        
        # Inicializar todos os módulos especializados
        self.utils = PlankaUtils(settings)
        self.dependency_checker = DependencyChecker(settings)
        self.status_monitor = StatusMonitor(settings)
        self.container_manager = ContainerManager(settings)
        self.production_manager = ProductionManager(settings)
        self.logs_manager = LogsManager(settings)
        self.diagnostic_manager = DiagnosticManager(settings)
        self.backup_manager = BackupManager(settings)
        
        # Status interno
        self.status = "desconhecido"
    
    # Métodos públicos que delegam para módulos especializados
    
    def verificar_dependencias(self, forcar_verificacao: bool = False):
        """Delega para DependencyChecker."""
        return self.dependency_checker.verificar_dependencias(forcar_verificacao)
    
    def forcar_verificacao_dependencias(self):
        """Delega para DependencyChecker."""
        return self.dependency_checker.forcar_verificacao_dependencias()
    
    def obter_info_cache_dependencias(self):
        """Delega para DependencyChecker."""
        return self.dependency_checker.obter_info_cache_dependencias()
    
    def verificar_status(self):
        """Delega para StatusMonitor."""
        return self.status_monitor.verificar_status()
    
    def verificar_modo_ativo(self):
        """Delega para StatusMonitor."""
        return self.status_monitor.verificar_modo_ativo()
    
    def verificar_processos_docker(self):
        """Delega para StatusMonitor."""
        return self.status_monitor.verificar_processos_docker()
    
    def verificar_containers_ativos(self):
        """Delega para StatusMonitor."""
        return self.status_monitor.verificar_containers_ativos()
    
    def verificar_diretorio_planka(self):
        """Delega para Utils."""
        return self.utils.verificar_diretorio_planka()
    
    def iniciar_planka(self):
        """Delega para ContainerManager."""
        return self.container_manager.iniciar_planka()
    
    def parar_planka(self):
        """Delega para ContainerManager."""
        return self.container_manager.parar_planka()
    
    def reiniciar_planka(self):
        """Delega para ContainerManager."""
        return self.container_manager.reiniciar_planka()
    
    def modo_desenvolvimento(self):
        """Delega para ContainerManager."""
        return self.container_manager.modo_desenvolvimento()
    
    def parar_modo_desenvolvimento(self):
        """Delega para ContainerManager."""
        return self.container_manager.parar_modo_desenvolvimento()
    
    def obter_logs(self, linhas: int = 50):
        """Delega para LogsManager."""
        return self.logs_manager.obter_logs(linhas)
    
    def backup_database(self):
        """Delega para BackupManager."""
        return self.backup_manager.backup_database()
    
    def obter_informacoes(self):
        """Delega para Utils."""
        return self.utils.obter_informacoes()
    
    def obter_logs_producao_detalhados(self, linhas: int = 100):
        """Delega para LogsManager."""
        return self.logs_manager.obter_logs_producao_detalhados(linhas)
    
    # Métodos de produção
    def executar_producao_com_modificacoes_locais(self):
        """Delega para ProductionManager."""
        return self.production_manager.executar_producao_com_modificacoes_locais()
    
    def sincronizar_producao_com_desenvolvimento(self):
        """Delega para ProductionManager."""
        return self.production_manager.sincronizar_producao_com_desenvolvimento()
    
    def restaurar_producao_original(self):
        """Delega para ProductionManager."""
        return self.production_manager.restaurar_producao_original()
    
    def verificar_sincronizacao_producao(self):
        """Delega para ProductionManager."""
        return self.production_manager.verificar_sincronizacao_producao()
    
    def configurar_producao_sempre_desenvolvimento(self):
        """Delega para ProductionManager."""
        return self.production_manager.configurar_producao_sempre_desenvolvimento()
    
    # Métodos de diagnóstico
    def diagnostico_detalhado(self):
        """Delega para DiagnosticManager."""
        return self.diagnostic_manager.diagnostico_detalhado()
    
    def diagnosticar_producao(self):
        """Delega para DiagnosticManager."""
        return self.diagnostic_manager.diagnosticar_producao()
    
    # Método de compatibilidade para logging
    def _adicionar_log(self, mensagem: str):
        """Delega para Utils."""
        self.utils.adicionar_log(mensagem) 