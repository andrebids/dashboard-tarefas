# -*- coding: utf-8 -*-
"""
Módulo para diagnósticos do sistema Planka.
Diagnósticos do sistema e verificação de problemas.
"""

import subprocess
import time
import socket
from typing import Dict
from pathlib import Path


class DiagnosticManager:
    """
    Gerenciador de diagnósticos do sistema Planka.
    """
    
    def __init__(self, settings):
        """
        Inicializa o gerenciador de diagnósticos.
        
        Args:
            settings: Instância das configurações do sistema
        """
        self.settings = settings
        self.planka_dir = Path(settings.obter("planka", "diretorio"))
    
    def diagnostico_detalhado(self) -> Dict:
        """
        Realiza diagnóstico detalhado do sistema Planka.
        
        Returns:
            Dict com informações de diagnóstico
        """
        try:
            diagnostico = {
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "status_geral": "unknown",
                "dependencias": {},
                "containers": {},
                "configuracoes": {},
                "problemas": [],
                "recomendacoes": []
            }
            
            # Verificar dependências
            from .dependency_checker import DependencyChecker
            dependency_checker = DependencyChecker(self.settings)
            diagnostico["dependencias"] = dependency_checker.verificar_dependencias()
            
            # Verificar status geral
            from .status_monitor import StatusMonitor
            status_monitor = StatusMonitor(self.settings)
            status = status_monitor.verificar_status()
            diagnostico["status_geral"] = status
            
            # Verificar containers
            containers = status_monitor.verificar_containers_ativos()
            diagnostico["containers"] = containers
            
            # Verificar configurações
            diagnostico["configuracoes"] = self._verificar_configuracoes_producao()
            
            # Identificar problemas
            problemas = []
            
            # Problema 1: Docker não instalado
            if not diagnostico["dependencias"].get("docker", False):
                problemas.append("Docker não está instalado")
                diagnostico["recomendacoes"].append("Instalar Docker Desktop")
            
            # Problema 2: Docker não rodando
            if diagnostico["dependencias"].get("docker", False) and not diagnostico["dependencias"].get("docker_rodando", False):
                problemas.append("Docker não está rodando")
                diagnostico["recomendacoes"].append("Iniciar Docker Desktop")
            
            # Problema 3: Container não está rodando
            if not containers.get("producao", False) and not containers.get("desenvolvimento", False):
                problemas.append("Nenhum container está rodando")
                diagnostico["recomendacoes"].append("Iniciar o Planka")
            
            # Problema 4: Container reiniciando
            if self._verificar_container_reiniciando():
                problemas.append("Container está reiniciando constantemente")
                diagnostico["recomendacoes"].append("Verificar logs e configurações")
            
            # Problema 5: Admin user não criado
            if not self._verificar_admin_user():
                problemas.append("Admin user não foi criado")
                diagnostico["recomendacoes"].append("Executar comando para criar admin user")
            
            # Problema 6: Porta não acessível
            if not self._verificar_porta_acessivel():
                problemas.append("Porta 3000 não está acessível")
                diagnostico["recomendacoes"].append("Verificar se a porta está sendo usada por outro processo")
            
            diagnostico["problemas"] = problemas
            
            return diagnostico
            
        except Exception as e:
            return {
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "status_geral": "erro",
                "dependencias": {},
                "containers": {},
                "configuracoes": {},
                "problemas": [f"Erro no diagnóstico: {str(e)}"],
                "recomendacoes": ["Verificar se o Docker está funcionando corretamente"]
            }
    
    def diagnosticar_producao(self) -> Dict:
        """
        Diagnostica problemas específicos da versão de produção.
        
        Returns:
            Dicionário com informações de diagnóstico
        """
        try:
            diagnostico = {
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "status_geral": "unknown",
                "problemas": [],
                "configuracoes": {},
                "containers": {},
                "logs": {},
                "recomendacoes": []
            }
            
            # Verificar status geral
            from .status_monitor import StatusMonitor
            status_monitor = StatusMonitor(self.settings)
            status = status_monitor.verificar_status()
            diagnostico["status_geral"] = status
            
            # Verificar containers
            containers = status_monitor.verificar_containers_ativos()
            diagnostico["containers"] = containers
            
            # Verificar configurações
            diagnostico["configuracoes"] = self._verificar_configuracoes_producao()
            
            # Verificar logs
            diagnostico["logs"] = self._obter_logs_producao()
            
            # Identificar problemas
            problemas = []
            
            # Problema 1: Container não está rodando
            if not containers.get("producao", False):
                problemas.append("Container Planka não está rodando")
                diagnostico["recomendacoes"].append("Verificar logs do container e tentar reiniciar")
            
            # Problema 2: Container reiniciando
            if self._verificar_container_reiniciando():
                problemas.append("Container Planka está reiniciando constantemente")
                diagnostico["recomendacoes"].append("Verificar logs de erro e configurações")
            
            # Problema 3: Secret key inválido
            if "notsecretkey" in str(diagnostico["configuracoes"]):
                problemas.append("Secret key não foi configurado adequadamente")
                diagnostico["recomendacoes"].append("Gerar novo secret key com openssl rand -hex 64")
            
            # Problema 4: Admin user não criado
            if not self._verificar_admin_user():
                problemas.append("Admin user não foi criado")
                diagnostico["recomendacoes"].append("Executar comando para criar admin user")
            
            # Problema 5: Porta não acessível
            if not self._verificar_porta_acessivel():
                problemas.append("Porta 3000 não está acessível")
                diagnostico["recomendacoes"].append("Verificar se a porta está sendo usada por outro processo")
            
            diagnostico["problemas"] = problemas
            
            return diagnostico
            
        except Exception as e:
            return {
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "status_geral": "erro",
                "problemas": [f"Erro no diagnóstico: {str(e)}"],
                "configuracoes": {},
                "containers": {},
                "logs": {},
                "recomendacoes": ["Verificar se o Docker está funcionando corretamente"]
            }
    
    def _verificar_configuracoes_producao(self) -> Dict:
        """
        Verifica configurações específicas de produção.
        
        Returns:
            Dicionário com configurações
        """
        try:
            configs = {}
            
            # Verificar arquivo docker-compose-local.yml
            local_compose_file = self.planka_dir / "docker-compose-local.yml"
            if local_compose_file.exists():
                with open(local_compose_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                configs["arquivo_existe"] = True
                configs["tem_secret_key"] = "SECRET_KEY=" in content
                configs["tem_admin_config"] = "DEFAULT_ADMIN_EMAIL" in content
                configs["usa_dockerfile_local"] = "build:" in content
            else:
                configs["arquivo_existe"] = False
            
            # Verificar Dockerfile
            dockerfile = self.planka_dir / "Dockerfile"
            configs["dockerfile_existe"] = dockerfile.exists()
            
            return configs
            
        except Exception as e:
            return {"erro": str(e)}
    
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
    
    def _verificar_container_reiniciando(self) -> bool:
        """
        Verifica se o container está reiniciando constantemente.
        
        Returns:
            True se está reiniciando, False caso contrário
        """
        try:
            result = subprocess.run(
                ["docker-compose", "-f", "docker-compose-local.yml", "ps"],
                cwd=self.planka_dir,
                capture_output=True,
                text=True,
                timeout=30,
                encoding='utf-8', errors='replace'
            )
            
            if result.returncode == 0:
                # Verificar se há indicação de reinicialização
                return "Restarting" in result.stdout or "Exit" in result.stdout
            else:
                return False
                
        except Exception:
            return False
    
    def _verificar_admin_user(self) -> bool:
        """
        Verifica se o admin user existe.
        
        Returns:
            True se existe, False caso contrário
        """
        try:
            # Tentar conectar ao banco e verificar usuários
            result = subprocess.run(
                ["docker-compose", "-f", "docker-compose-local.yml", "exec", "-T", "postgres", "psql", "-U", "postgres", "-d", "planka", "-c", "SELECT COUNT(*) FROM user_account WHERE role = 'admin';"],
                cwd=self.planka_dir,
                capture_output=True,
                text=True,
                timeout=30,
                encoding='utf-8', errors='replace'
            )
            
            if result.returncode == 0:
                # Se retornou um número maior que 0, há admin users
                return "0" not in result.stdout.strip()
            else:
                return False
                
        except Exception:
            return False
    
    def _verificar_porta_acessivel(self) -> bool:
        """
        Verifica se a porta 3000 está acessível.
        
        Returns:
            True se acessível, False caso contrário
        """
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('localhost', 3000))
            sock.close()
            return result == 0
        except Exception:
            return False 