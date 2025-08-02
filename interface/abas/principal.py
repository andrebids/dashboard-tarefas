# -*- coding: utf-8 -*-
"""
Aba Principal - Controle do Planka (Versão Refatorada).
"""

import tkinter as tk
from tkinter import ttk
from pathlib import Path

# Importar o controlador principal
import sys
sys.path.append(str(Path(__file__).parent.parent.parent))
from core.principal_controller import PrincipalController


class AbaPrincipal(ttk.Frame):
    """
    Aba principal com controle do Planka (Versão Refatorada).
    """
    
    def __init__(self, parent, log_manager, settings, **kwargs):
        """
        Inicializa a aba principal.
        
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
        
        # Inicializar controlador principal
        self.controller = PrincipalController(self, settings, log_manager)
        
        # Log de inicialização
        self.log_manager.log_sistema("SUCCESS", "Aba principal inicializada (versão refatorada)")
    
    def obter_widget(self):
        """Retorna o widget principal do controlador."""
        return self.controller.obter_widget()
    
    def atualizar(self):
        """Atualiza a aba principal."""
        try:
            self.controller.atualizar_status()
        except Exception as e:
            self.log_manager.log_sistema("ERROR", f"Erro ao atualizar aba principal: {str(e)}")
    
    def parar_monitoramento(self):
        """Para o monitoramento automático."""
        try:
            self.controller.parar_monitoramento()
        except Exception as e:
            self.log_manager.log_sistema("ERROR", f"Erro ao parar monitoramento: {str(e)}")
    
    def iniciar_monitoramento(self):
        """Inicia o monitoramento automático."""
        try:
            self.controller.iniciar_monitoramento()
        except Exception as e:
            self.log_manager.log_sistema("ERROR", f"Erro ao iniciar monitoramento: {str(e)}")
    
    def limpar_logs(self):
        """Limpa todos os logs."""
        try:
            self.controller.limpar_logs()
        except Exception as e:
            self.log_manager.log_sistema("ERROR", f"Erro ao limpar logs: {str(e)}")
    
    def obter_status_atual(self):
        """Retorna o status atual do sistema."""
        try:
            return self.controller.obter_status_atual()
        except Exception as e:
            self.log_manager.log_sistema("ERROR", f"Erro ao obter status: {str(e)}")
            return {"status": "Erro", "erro": str(e)}
    
    def executar_diagnostico_rapido(self):
        """Executa diagnóstico rápido."""
        try:
            self.controller.executar_diagnostico_rapido()
        except Exception as e:
            self.log_manager.log_sistema("ERROR", f"Erro ao executar diagnóstico rápido: {str(e)}")
    
    def executar_diagnostico_completo(self):
        """Executa diagnóstico completo."""
        try:
            self.controller.executar_diagnostico_completo()
        except Exception as e:
            self.log_manager.log_sistema("ERROR", f"Erro ao executar diagnóstico completo: {str(e)}") 