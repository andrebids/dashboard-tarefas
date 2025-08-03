# -*- coding: utf-8 -*-
"""
Módulo para gerenciamento de containers do Planka.
Gerenciamento de containers Docker e controle de modo desenvolvimento vs produção.
"""

import subprocess
import time
from typing import Tuple
from pathlib import Path


class ContainerManager:
    """
    Gerenciador de containers do sistema Planka.
    """
    
    def __init__(self, settings):
        """
        Inicializa o gerenciador de containers.
        
        Args:
            settings: Instância das configurações do sistema
        """
        self.settings = settings
        self.planka_dir = Path(settings.obter("planka", "diretorio"))
    
    def iniciar_planka(self) -> Tuple[bool, str]:
        """
        Inicia o Planka usando docker-compose.
        
        Returns:
            (sucesso, mensagem)
        """
        try:
            # Verificar se já está rodando
            from .status_monitor import StatusMonitor
            status_monitor = StatusMonitor(self.settings)
            if status_monitor.verificar_status() == "online":
                return True, "Planka já está rodando"
            
            # Verificar dependências
            from .dependency_checker import DependencyChecker
            dependency_checker = DependencyChecker(self.settings)
            dependencias = dependency_checker.verificar_dependencias()
            if not dependencias["docker"] or not dependencias["docker_compose"]:
                return False, "Docker ou Docker Compose não encontrados"
            
            # Verificar diretório
            from .utils import PlankaUtils
            utils = PlankaUtils(self.settings)
            if not utils.verificar_diretorio_planka():
                return False, "Diretório do Planka não encontrado ou inválido"
            
            # Iniciar com docker-compose.yml (produção)
            result = subprocess.run(
                ["docker-compose", "up", "-d"],
                cwd=self.planka_dir,
                capture_output=True,
                text=True,
                timeout=60,
                encoding='utf-8', errors='replace'
            )
            
            if result.returncode == 0:
                # Aguardar inicialização
                time.sleep(10)
                
                # Verificar se iniciou corretamente
                if status_monitor.verificar_status() == "online":
                    return True, "Planka iniciado com sucesso"
                else:
                    return False, "Planka iniciado mas não está respondendo"
            else:
                return False, f"Erro ao iniciar Planka: {result.stderr}"
                
        except subprocess.TimeoutExpired:
            return False, "Timeout ao iniciar Planka"
        except Exception as e:
            return False, f"Erro inesperado: {str(e)}"
    
    def parar_planka(self) -> Tuple[bool, str]:
        """
        Para o Planka usando docker-compose.
        
        Returns:
            (sucesso, mensagem)
        """
        try:
            # Verificar se está rodando
            from .status_monitor import StatusMonitor
            status_monitor = StatusMonitor(self.settings)
            if status_monitor.verificar_status() == "offline":
                return True, "Planka já está parado"
            
            # Parar com docker-compose.yml (produção)
            result = subprocess.run(
                ["docker-compose", "down"],
                cwd=self.planka_dir,
                capture_output=True,
                text=True,
                timeout=30,
                encoding='utf-8', errors='replace'
            )
            
            if result.returncode == 0:
                # Aguardar parada
                time.sleep(5)
                
                # Verificar se parou
                if status_monitor.verificar_status() == "offline":
                    return True, "Planka parado com sucesso"
                else:
                    return False, "Planka parado mas ainda está respondendo"
            else:
                return False, f"Erro ao parar Planka: {result.stderr}"
                
        except subprocess.TimeoutExpired:
            return False, "Timeout ao parar Planka"
        except Exception as e:
            return False, f"Erro inesperado: {str(e)}"
    
    def reiniciar_planka(self) -> Tuple[bool, str]:
        """
        Reinicia o Planka (para e inicia novamente).
        
        Returns:
            (sucesso, mensagem)
        """
        # Parar primeiro
        sucesso_parar, msg_parar = self.parar_planka()
        if not sucesso_parar:
            return False, f"Erro ao parar: {msg_parar}"
        
        # Aguardar um pouco
        time.sleep(3)
        
        # Iniciar novamente
        sucesso_iniciar, msg_iniciar = self.iniciar_planka()
        if not sucesso_iniciar:
            return False, f"Erro ao reiniciar: {msg_iniciar}"
        
        return True, "Planka reiniciado com sucesso"
    
    def modo_desenvolvimento(self) -> Tuple[bool, str]:
        """
        Inicia o Planka em modo desenvolvimento usando docker-compose-dev.yml.
        
        Returns:
            (sucesso, mensagem)
        """
        try:
            # Verificar se Docker está disponível
            from .dependency_checker import DependencyChecker
            dependency_checker = DependencyChecker(self.settings)
            dependencias = dependency_checker.verificar_dependencias()
            if not dependencias["docker"]:
                return False, "Docker não encontrado"
            
            if not dependencias["docker_compose"]:
                return False, "Docker Compose não encontrado"
            
            # Verificar se o diretório existe
            from .utils import PlankaUtils
            utils = PlankaUtils(self.settings)
            if not utils.verificar_diretorio_planka():
                return False, "Diretório do Planka não encontrado"
            
            # Verificar se docker-compose-dev.yml existe
            dev_compose_file = self.planka_dir / "docker-compose-dev.yml"
            if not dev_compose_file.exists():
                return False, "docker-compose-dev.yml não encontrado"
            
            # Parar containers de produção se estiverem rodando
            self.parar_planka()
            
            # Iniciar modo desenvolvimento
            resultado = subprocess.run(
                ["docker-compose", "-f", "docker-compose-dev.yml", "up", "-d"],
                cwd=self.planka_dir,
                capture_output=True,
                text=True, 
                encoding='utf-8', errors='replace'
            )
            
            if resultado.returncode == 0:
                # Aguardar inicialização
                time.sleep(10)
                
                # Verificar se iniciou
                from .status_monitor import StatusMonitor
                status_monitor = StatusMonitor(self.settings)
                if status_monitor.verificar_status() == "online":
                    return True, "Planka iniciado em modo desenvolvimento"
                else:
                    return False, "Planka não iniciou em modo desenvolvimento"
            else:
                return False, f"Erro ao iniciar modo desenvolvimento: {resultado.stderr}"
                
        except subprocess.TimeoutExpired:
            return False, "Timeout ao iniciar modo desenvolvimento"
        except Exception as e:
            return False, f"Erro ao iniciar modo desenvolvimento: {str(e)}"
    
    def parar_modo_desenvolvimento(self) -> Tuple[bool, str]:
        """
        Para o modo desenvolvimento.
        
        Returns:
            (sucesso, mensagem)
        """
        try:
            # Verificar se docker-compose-dev.yml existe
            dev_compose_file = self.planka_dir / "docker-compose-dev.yml"
            if not dev_compose_file.exists():
                return False, "docker-compose-dev.yml não encontrado"
            
            # Parar containers de desenvolvimento
            resultado = subprocess.run(
                ["docker-compose", "-f", "docker-compose-dev.yml", "down"],
                cwd=self.planka_dir,
                capture_output=True,
                text=True, 
                encoding='utf-8', errors='replace'
            )
            
            if resultado.returncode == 0:
                return True, "Modo desenvolvimento parado"
            else:
                return False, f"Erro ao parar modo desenvolvimento: {resultado.stderr}"
                
        except subprocess.TimeoutExpired:
            return False, "Timeout ao parar modo desenvolvimento"
        except Exception as e:
            return False, f"Erro ao parar modo desenvolvimento: {str(e)}" 