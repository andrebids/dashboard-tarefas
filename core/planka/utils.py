# -*- coding: utf-8 -*-
"""
Utilitários compartilhados para o sistema Planka.
Funções auxiliares e logging.
"""

import time
from datetime import datetime
from typing import Dict
from pathlib import Path


class PlankaUtils:
    """
    Utilitários compartilhados do sistema Planka.
    """
    
    def __init__(self, settings):
        """
        Inicializa os utilitários.
        
        Args:
            settings: Instância das configurações do sistema
        """
        self.settings = settings
        self.planka_dir = Path(settings.obter("planka", "diretorio"))
        self.planka_url = settings.obter("planka", "url")
        self.planka_porta = settings.obter("planka", "porta")
    
    def adicionar_log(self, mensagem: str):
        """
        Adiciona mensagem de log para acompanhamento.
        
        Args:
            mensagem: Mensagem a ser logada
        """
        timestamp = time.strftime("%H:%M:%S")
        print(f"[{timestamp}] {mensagem}")
        
        # Também logar no sistema se disponível
        try:
            if hasattr(self, 'log_manager'):
                self.log_manager.log_sistema("INFO", mensagem)
        except:
            pass
    
    def obter_informacoes(self) -> Dict:
        """
        Obtém informações básicas do sistema Planka.
        
        Returns:
            Dict com informações do sistema
        """
        info = {
            "status": "desconhecido",
            "diretorio": str(self.planka_dir),
            "url": self.planka_url,
            "porta": self.planka_porta,
            "timestamp": datetime.now().isoformat()
        }
        
        return info
    
    def verificar_diretorio_planka(self) -> bool:
        """
        Verifica se o diretório do Planka existe e tem a estrutura correta.
        
        Returns:
            True se o diretório existe e é válido
        """
        if not self.planka_dir.exists():
            return False
            
        # Verificar arquivos essenciais
        arquivos_essenciais = [
            "docker-compose.yml",
            "package.json",
            "README.md"
        ]
        
        for arquivo in arquivos_essenciais:
            if not (self.planka_dir / arquivo).exists():
                return False
                
        return True 