# -*- coding: utf-8 -*-
"""
Módulo para gerenciamento de logs do Planka.
Gerenciamento de logs e obtenção de logs detalhados.
"""

import subprocess
from typing import Dict
from pathlib import Path


class LogsManager:
    """
    Gerenciador de logs do sistema Planka.
    """
    
    def __init__(self, settings):
        """
        Inicializa o gerenciador de logs.
        
        Args:
            settings: Instância das configurações do sistema
        """
        self.settings = settings
        self.planka_dir = Path(settings.obter("planka", "diretorio"))
    
    def obter_logs(self, linhas: int = 50) -> str:
        """
        Obtém logs do Planka.
        
        Args:
            linhas: Número de linhas de log para retornar
            
        Returns:
            Logs do Planka
        """
        try:
            # Obter logs dos containers Docker
            result = subprocess.run(
                ["docker-compose", "logs", "--tail", str(linhas)],
                cwd=self.planka_dir,
                capture_output=True,
                text=True,
                timeout=30,
                encoding='utf-8', errors='replace'
            )
            
            if result.returncode == 0:
                return result.stdout
            else:
                return f"Erro ao obter logs: {result.stderr}"
                
        except Exception as e:
            return f"Erro ao obter logs: {str(e)}"
    
    def obter_logs_producao_detalhados(self, linhas: int = 100) -> str:
        """
        Obtém logs detalhados de produção.
        
        Args:
            linhas: Número de linhas de log
            
        Returns:
            Logs detalhados
        """
        try:
            # Logs completos de todos os containers
            result = subprocess.run(
                ["docker-compose", "-f", "docker-compose-local.yml", "logs", "--tail", str(linhas)],
                cwd=self.planka_dir,
                capture_output=True,
                text=True,
                timeout=60,
                encoding='utf-8', errors='replace'
            )
            
            if result.returncode == 0:
                return result.stdout
            else:
                return f"Erro ao obter logs: {result.stderr}"
                
        except Exception as e:
            return f"Erro ao obter logs: {str(e)}"
    
    def _obter_logs_producao(self) -> Dict[str, str]:
        """
        Obtém logs específicos de produção.
        
        Returns:
            Dicionário com logs
        """
        try:
            logs = {}
            
            # Logs do container Planka
            result = subprocess.run(
                ["docker-compose", "-f", "docker-compose-local.yml", "logs", "--tail", "50", "planka"],
                cwd=self.planka_dir,
                capture_output=True,
                text=True,
                timeout=30,
                encoding='utf-8', errors='replace'
            )
            
            if result.returncode == 0:
                logs["planka"] = result.stdout
            else:
                logs["planka"] = f"Erro ao obter logs: {result.stderr}"
            
            # Logs do PostgreSQL
            result = subprocess.run(
                ["docker-compose", "-f", "docker-compose-local.yml", "logs", "--tail", "20", "postgres"],
                cwd=self.planka_dir,
                capture_output=True,
                text=True,
                timeout=30,
                encoding='utf-8', errors='replace'
            )
            
            if result.returncode == 0:
                logs["postgres"] = result.stdout
            else:
                logs["postgres"] = f"Erro ao obter logs: {result.stderr}"
            
            return logs
            
        except Exception as e:
            return {"erro": str(e)} 