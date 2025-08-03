# -*- coding: utf-8 -*-
"""
Módulo para verificação de dependências do Planka.
Gerencia cache e verificação de Docker, Node.js, Git, etc.
"""

import subprocess
import time
from typing import Dict
from pathlib import Path

# Importar sistema de cache
try:
    from config.dependency_cache import DependencyCache
except ImportError:
    DependencyCache = None


class DependencyChecker:
    """
    Verificador de dependências do sistema Planka.
    """
    
    def __init__(self, settings):
        """
        Inicializa o verificador de dependências.
        
        Args:
            settings: Instância das configurações do sistema
        """
        self.settings = settings
        self.planka_dir = Path(settings.obter("planka", "diretorio"))
        
        # Inicializar sistema de cache para dependências
        self.dependency_cache = None
        if DependencyCache:
            cache_duration = settings.obter("performance", "cache_dependencias", 300)
            self.dependency_cache = DependencyCache(cache_duration=cache_duration)
    
    def verificar_dependencias(self, forcar_verificacao: bool = False) -> Dict[str, bool]:
        """
        Verifica se as dependências necessárias estão instaladas.
        Usa cache para evitar verificações constantes.
        
        Args:
            forcar_verificacao: Se True, ignora o cache e força nova verificação
            
        Returns:
            Dict com status de cada dependência
        """
        # Verificar cache primeiro (se disponível e não forçar verificação)
        if self.dependency_cache and not forcar_verificacao:
            dependencias_cache = self.dependency_cache.obter_dependencias_cache()
            if dependencias_cache:
                return dependencias_cache
        
        # Se não há cache válido, fazer verificação completa
        dependencias = {
            "docker": False,
            "docker_rodando": False,
            "nodejs": False,
            "git": False,
            "docker_compose": False
        }
        
        try:
            # Verificar Docker
            dependencias["docker"] = self._verificar_docker()
            
            # Verificar se Docker está rodando
            if dependencias["docker"]:
                dependencias["docker_rodando"] = self._verificar_docker_rodando()
            
            # Verificar Docker Compose
            dependencias["docker_compose"] = self._verificar_docker_compose()
            
            # Verificar Node.js
            dependencias["nodejs"] = self._verificar_nodejs()
            
            # Verificar Git
            dependencias["git"] = self._verificar_git()
            
            # Salvar no cache (se disponível)
            if self.dependency_cache:
                self.dependency_cache.salvar_dependencias_cache(dependencias)
            
        except Exception as e:
            print(f"Erro ao verificar dependências: {e}")
            
        return dependencias
    
    def forcar_verificacao_dependencias(self) -> Dict[str, bool]:
        """
        Força uma nova verificação de dependências, ignorando o cache.
        
        Returns:
            Dict com status de cada dependência
        """
        # Limpar cache se disponível
        if self.dependency_cache:
            self.dependency_cache.forcar_verificacao()
        
        # Fazer verificação completa
        return self.verificar_dependencias(forcar_verificacao=True)
    
    def obter_info_cache_dependencias(self) -> Dict:
        """
        Obtém informações sobre o cache de dependências.
        
        Returns:
            Dict com informações do cache
        """
        if self.dependency_cache:
            return self.dependency_cache.obter_info_cache()
        return {"cache_disponivel": False}
    
    def _verificar_docker(self) -> bool:
        """Verifica se Docker está instalado."""
        try:
            result = subprocess.run(
                ["docker", "--version"], 
                capture_output=True, 
                text=True, 
                timeout=3,
                encoding='utf-8', errors='replace'
            )
            return result.returncode == 0
        except Exception:
            return False
    
    def _verificar_docker_rodando(self) -> bool:
        """Verifica se Docker está rodando."""
        try:
            result = subprocess.run(
                ["docker", "info"], 
                capture_output=True, 
                text=True, 
                timeout=3,
                encoding='utf-8', errors='replace'
            )
            return result.returncode == 0
        except Exception:
            return False
    
    def _verificar_docker_compose(self) -> bool:
        """Verifica se Docker Compose está disponível."""
        try:
            result = subprocess.run(
                ["docker-compose", "--version"], 
                capture_output=True, 
                text=True, 
                timeout=3,
                encoding='utf-8', errors='replace'
            )
            return result.returncode == 0
        except Exception:
            return False
    
    def _verificar_nodejs(self) -> bool:
        """Verifica se Node.js está instalado."""
        try:
            result = subprocess.run(
                ["node", "--version"], 
                capture_output=True, 
                text=True, 
                timeout=3,
                encoding='utf-8', errors='replace'
            )
            return result.returncode == 0
        except Exception:
            return False
    
    def _verificar_git(self) -> bool:
        """Verifica se Git está instalado."""
        try:
            result = subprocess.run(
                ["git", "--version"], 
                capture_output=True, 
                text=True, 
                timeout=3,
                encoding='utf-8', errors='replace'
            )
            return result.returncode == 0
        except Exception:
            return False 