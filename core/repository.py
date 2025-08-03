# -*- coding: utf-8 -*-
"""
Módulo de Gestão de Repositório - Controle do repositório do Planka.
"""

import subprocess
import shutil
from pathlib import Path
from typing import Dict, Tuple, Optional


class RepositoryManager:
    """
    Gerenciador de repositório para o Planka.
    Responsável por clone, pull e verificação de dependências.
    """
    
    def __init__(self, settings):
        """
        Inicializa o gerenciador de repositório.
        
        Args:
            settings: Configurações do sistema
        """
        self.settings = settings
        self.repo_url = "https://github.com/plankanban/planka.git"
    
    def verificar_dependencias(self) -> Dict[str, bool]:
        """
        Verifica se as dependências necessárias estão instaladas.
        
        Returns:
            Dict com status das dependências
        """
        dependencias = {}
        
        # Verificar Docker
        dependencias["docker"] = self._verificar_comando("docker")
        
        # Verificar Docker Compose
        dependencias["docker_compose"] = self._verificar_comando("docker-compose")
        
        # Verificar Git
        dependencias["git"] = self._verificar_comando("git")
        
        return dependencias
    
    def verificar_diretorio_existe(self) -> bool:
        """
        Verifica se o diretório do Planka já existe.
        
        Returns:
            bool: True se o diretório existe
        """
        dir_planka = self.settings.obter_diretorio_planka()
        return dir_planka.exists()
    
    def clone_repositorio(self) -> Tuple[bool, str]:
        """
        Clona o repositório do Planka.
        
        Returns:
            Tuple[bool, str]: (sucesso, mensagem)
        """
        try:
            dir_planka = self.settings.obter_diretorio_planka()
            dir_pai = dir_planka.parent
            
            # Verificar se o diretório já existe
            if dir_planka.exists():
                return False, f"Diretório {dir_planka} já existe"
            
            # Comando git clone
            comando = ["git", "clone", self.repo_url, str(dir_planka)]
            
            # Executar clone
            resultado = subprocess.run(
                comando,
                cwd=dir_pai,
                capture_output=True,
                text=True,
                timeout=600  # 10 minutos
            )
            
            if resultado.returncode == 0:
                return True, f"Repositório clonado com sucesso em {dir_planka}"
            else:
                erro = resultado.stderr if resultado.stderr else resultado.stdout
                return False, f"Erro no clone: {erro}"
                
        except subprocess.TimeoutExpired:
            return False, "Timeout no clone do repositório"
        except Exception as e:
            return False, f"Erro inesperado no clone: {str(e)}"
    
    def pull_repositorio(self) -> Tuple[bool, str]:
        """
        Atualiza o repositório do Planka (git pull).
        
        Returns:
            Tuple[bool, str]: (sucesso, mensagem)
        """
        try:
            dir_planka = self.settings.obter_diretorio_planka()
            
            # Verificar se o diretório existe
            if not dir_planka.exists():
                return False, "Diretório do repositório não encontrado"
            
            # Comando git pull
            comando = ["git", "pull", "origin", "main"]
            
            # Executar pull
            resultado = subprocess.run(
                comando,
                cwd=dir_planka,
                capture_output=True,
                text=True,
                timeout=300  # 5 minutos
            )
            
            if resultado.returncode == 0:
                return True, "Repositório atualizado com sucesso"
            else:
                erro = resultado.stderr if resultado.stderr else resultado.stdout
                return False, f"Erro na atualização: {erro}"
                
        except subprocess.TimeoutExpired:
            return False, "Timeout na atualização do repositório"
        except Exception as e:
            return False, f"Erro inesperado na atualização: {str(e)}"
    
    def verificar_estado_repositorio(self) -> Dict:
        """
        Verifica o estado atual do repositório.
        
        Returns:
            Dict com informações do repositório
        """
        try:
            dir_planka = self.settings.obter_diretorio_planka()
            
            if not dir_planka.exists():
                return {
                    "existe": False,
                    "mensagem": "Diretório não encontrado"
                }
            
            # Verificar se é um repositório Git válido
            resultado = subprocess.run(
                ["git", "status"],
                cwd=dir_planka,
                capture_output=True,
                text=True, encoding='utf-8', errors='replace'
            )
            
            if resultado.returncode != 0:
                return {
                    "existe": True,
                    "valido": False,
                    "mensagem": "Não é um repositório Git válido"
                }
            
            # Verificar branch atual
            resultado_branch = subprocess.run(
                ["git", "branch", "--show-current"],
                cwd=dir_planka,
                capture_output=True,
                text=True, encoding='utf-8', errors='replace'
            )
            
            branch_atual = resultado_branch.stdout.strip() if resultado_branch.returncode == 0 else "desconhecida"
            
            # Verificar se há mudanças não commitadas
            resultado_status = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=dir_planka,
                capture_output=True,
                text=True, encoding='utf-8', errors='replace'
            )
            
            tem_mudancas = bool(resultado_status.stdout.strip())
            
            return {
                "existe": True,
                "valido": True,
                "branch": branch_atual,
                "tem_mudancas": tem_mudancas,
                "mensagem": "Repositório válido"
            }
            
        except Exception as e:
            return {
                "existe": False,
                "mensagem": f"Erro ao verificar repositório: {str(e)}"
            }
    
    def limpar_repositorio(self) -> Tuple[bool, str]:
        """
        Remove o diretório do repositório.
        
        Returns:
            Tuple[bool, str]: (sucesso, mensagem)
        """
        try:
            dir_planka = self.settings.obter_diretorio_planka()
            
            if not dir_planka.exists():
                return True, "Diretório não existe"
            
            # Remover diretório
            shutil.rmtree(dir_planka)
            
            return True, f"Diretório {dir_planka} removido com sucesso"
            
        except Exception as e:
            return False, f"Erro ao remover diretório: {str(e)}"
    
    def obter_informacoes_repositorio(self) -> Dict:
        """
        Obtém informações detalhadas do repositório.
        
        Returns:
            Dict com informações do repositório
        """
        try:
            dir_planka = self.settings.obter_diretorio_planka()
            
            if not dir_planka.exists():
                return {
                    "existe": False,
                    "mensagem": "Diretório não encontrado"
                }
            
            # Último commit
            resultado_commit = subprocess.run(
                ["git", "log", "-1", "--format=%H|%an|%ad|%s"],
                cwd=dir_planka,
                capture_output=True,
                text=True, encoding='utf-8', errors='replace'
            )
            
            ultimo_commit = {}
            if resultado_commit.returncode == 0 and resultado_commit.stdout.strip():
                partes = resultado_commit.stdout.strip().split('|')
                if len(partes) >= 4:
                    ultimo_commit = {
                        "hash": partes[0][:8],
                        "autor": partes[1],
                        "data": partes[2],
                        "mensagem": partes[3]
                    }
            
            # Contagem de commits
            resultado_count = subprocess.run(
                ["git", "rev-list", "--count", "HEAD"],
                cwd=dir_planka,
                capture_output=True,
                text=True, encoding='utf-8', errors='replace'
            )
            
            total_commits = resultado_count.stdout.strip() if resultado_count.returncode == 0 else "0"
            
            # Tamanho do diretório
            tamanho = self._calcular_tamanho_diretorio(dir_planka)
            
            return {
                "existe": True,
                "caminho": str(dir_planka),
                "ultimo_commit": ultimo_commit,
                "total_commits": total_commits,
                "tamanho": tamanho,
                "mensagem": "Informações obtidas com sucesso"
            }
            
        except Exception as e:
            return {
                "existe": False,
                "mensagem": f"Erro ao obter informações: {str(e)}"
            }
    
    def _verificar_comando(self, comando: str) -> bool:
        """
        Verifica se um comando está disponível no sistema.
        
        Args:
            comando: Nome do comando a verificar
            
        Returns:
            bool: True se o comando está disponível
        """
        try:
            resultado = subprocess.run(
                [comando, "--version"],
                capture_output=True,
                text=True, encoding='utf-8', errors='replace'
            )
            return resultado.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    def _calcular_tamanho_diretorio(self, diretorio: Path) -> str:
        """
        Calcula o tamanho de um diretório.
        
        Args:
            diretorio: Caminho do diretório
            
        Returns:
            str: Tamanho formatado
        """
        try:
            total_size = 0
            for dirpath, dirnames, filenames in diretorio.rglob('*'):
                for filename in filenames:
                    filepath = dirpath / filename
                    if filepath.is_file():
                        total_size += filepath.stat().st_size
            
            # Converter para MB
            tamanho_mb = total_size / (1024 * 1024)
            return f"{tamanho_mb:.1f} MB"
            
        except Exception:
            return "Desconhecido" 