# -*- coding: utf-8 -*-
"""
Módulo de controle do Planka personalizado.
Gerencia inicialização, parada, desenvolvimento e monitoramento.
"""

import os
import subprocess
import time
import requests
import threading
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime


class PlankaManager:
    """
    Gerenciador do Planka personalizado.
    Controla inicialização, parada, desenvolvimento e monitoramento.
    """
    
    def __init__(self, settings):
        """
        Inicializa o gerenciador do Planka.
        
        Args:
            settings: Instância das configurações do sistema
        """
        self.settings = settings
        self.planka_dir = Path(settings.obter("planka", "diretorio"))
        self.planka_url = settings.obter("planka", "url")
        self.planka_porta = settings.obter("planka", "porta")
        self.docker_compose_file = settings.obter("planka", "docker_compose_file")
        self.status = "desconhecido"
        self.process = None
        self.dev_process = None
        
    def verificar_dependencias(self) -> Dict[str, bool]:
        """
        Verifica se as dependências necessárias estão instaladas.
        
        Returns:
            Dict com status de cada dependência
        """
        dependencias = {
            "docker": False,
            "nodejs": False,
            "git": False,
            "docker_compose": False
        }
        
        try:
            # Verificar Docker
            result = subprocess.run(
                ["docker", "--version"], 
                capture_output=True, 
                text=True, 
                timeout=10
            )
            dependencias["docker"] = result.returncode == 0
            
            # Verificar Docker Compose
            result = subprocess.run(
                ["docker-compose", "--version"], 
                capture_output=True, 
                text=True, 
                timeout=10
            )
            dependencias["docker_compose"] = result.returncode == 0
            
            # Verificar Node.js
            result = subprocess.run(
                ["node", "--version"], 
                capture_output=True, 
                text=True, 
                timeout=10
            )
            dependencias["nodejs"] = result.returncode == 0
            
            # Verificar Git
            result = subprocess.run(
                ["git", "--version"], 
                capture_output=True, 
                text=True, 
                timeout=10
            )
            dependencias["git"] = result.returncode == 0
            
        except (subprocess.TimeoutExpired, FileNotFoundError, Exception) as e:
            print(f"Erro ao verificar dependências: {e}")
            
        return dependencias
    
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
    
    def verificar_status(self) -> str:
        """
        Verifica se o Planka está rodando.
        
        Returns:
            Status: "online", "offline", "erro"
        """
        try:
            # Tentar conectar na URL do Planka
            response = requests.get(
                self.planka_url, 
                timeout=5,
                headers={'User-Agent': 'Dashboard-Planka-Manager'}
            )
            
            if response.status_code == 200:
                self.status = "online"
                return "online"
            else:
                self.status = "offline"
                return "offline"
                
        except requests.RequestException:
            self.status = "offline"
            return "offline"
        except Exception as e:
            self.status = "erro"
            return "erro"
    
    def verificar_processos_docker(self) -> List[Dict]:
        """
        Verifica processos Docker relacionados ao Planka.
        
        Returns:
            Lista de processos Docker encontrados
        """
        processos = []
        
        try:
            # Listar containers do Planka
            result = subprocess.run(
                ["docker", "ps", "--filter", "name=planka", "--format", "table {{.Names}}\t{{.Status}}\t{{.Ports}}"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                linhas = result.stdout.strip().split('\n')[1:]  # Pular cabeçalho
                for linha in linhas:
                    if linha.strip():
                        partes = linha.split('\t')
                        if len(partes) >= 3:
                            processos.append({
                                "nome": partes[0],
                                "status": partes[1],
                                "portas": partes[2]
                            })
                            
        except Exception as e:
            print(f"Erro ao verificar processos Docker: {e}")
            
        return processos
    
    def iniciar_planka(self) -> Tuple[bool, str]:
        """
        Inicia o Planka usando docker-compose.
        
        Returns:
            (sucesso, mensagem)
        """
        try:
            # Verificar se já está rodando
            if self.verificar_status() == "online":
                return True, "Planka já está rodando"
            
            # Verificar dependências
            dependencias = self.verificar_dependencias()
            if not dependencias["docker"] or not dependencias["docker_compose"]:
                return False, "Docker ou Docker Compose não encontrados"
            
            # Verificar diretório
            if not self.verificar_diretorio_planka():
                return False, "Diretório do Planka não encontrado ou inválido"
            
            # Iniciar com docker-compose
            result = subprocess.run(
                ["docker-compose", "up", "-d"],
                cwd=self.planka_dir,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                # Aguardar inicialização
                time.sleep(10)
                
                # Verificar se iniciou corretamente
                if self.verificar_status() == "online":
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
            if self.verificar_status() == "offline":
                return True, "Planka já está parado"
            
            # Parar com docker-compose
            result = subprocess.run(
                ["docker-compose", "down"],
                cwd=self.planka_dir,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                # Aguardar parada
                time.sleep(5)
                
                # Verificar se parou
                if self.verificar_status() == "offline":
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
        Inicia o Planka em modo desenvolvimento.
        
        Returns:
            (sucesso, mensagem)
        """
        try:
            # Verificar se Node.js está disponível
            dependencias = self.verificar_dependencias()
            if not dependencias["nodejs"]:
                return False, "Node.js não encontrado"
            
            # Verificar se package.json existe
            package_json = self.planka_dir / "package.json"
            if not package_json.exists():
                return False, "package.json não encontrado"
            
            # Parar containers Docker se estiverem rodando
            self.parar_planka()
            
            # Iniciar em modo desenvolvimento
            self.dev_process = subprocess.Popen(
                ["npm", "start"],
                cwd=self.planka_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Aguardar inicialização
            time.sleep(15)
            
            # Verificar se iniciou
            if self.verificar_status() == "online":
                return True, "Planka iniciado em modo desenvolvimento"
            else:
                return False, "Planka não iniciou em modo desenvolvimento"
                
        except Exception as e:
            return False, f"Erro ao iniciar modo desenvolvimento: {str(e)}"
    
    def parar_modo_desenvolvimento(self) -> Tuple[bool, str]:
        """
        Para o modo desenvolvimento.
        
        Returns:
            (sucesso, mensagem)
        """
        try:
            if self.dev_process:
                self.dev_process.terminate()
                self.dev_process.wait(timeout=10)
                self.dev_process = None
                return True, "Modo desenvolvimento parado"
            else:
                return True, "Nenhum processo de desenvolvimento ativo"
                
        except subprocess.TimeoutExpired:
            if self.dev_process:
                self.dev_process.kill()
                self.dev_process = None
            return False, "Timeout ao parar modo desenvolvimento"
        except Exception as e:
            return False, f"Erro ao parar modo desenvolvimento: {str(e)}"
    
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
                timeout=30
            )
            
            if result.returncode == 0:
                return result.stdout
            else:
                return f"Erro ao obter logs: {result.stderr}"
                
        except Exception as e:
            return f"Erro ao obter logs: {str(e)}"
    
    def backup_database(self) -> Tuple[bool, str]:
        """
        Faz backup da base de dados do Planka.
        
        Returns:
            (sucesso, mensagem)
        """
        try:
            # Verificar se está rodando
            if self.verificar_status() != "online":
                return False, "Planka não está rodando"
            
            # Criar diretório de backup se não existir
            backup_dir = self.planka_dir / "backups"
            backup_dir.mkdir(exist_ok=True)
            
            # Nome do arquivo de backup
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = backup_dir / f"planka_backup_{timestamp}.sql"
            
            # Fazer backup usando docker-compose
            result = subprocess.run(
                ["docker-compose", "exec", "-T", "postgres", "pg_dump", "-U", "planka", "planka"],
                cwd=self.planka_dir,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                # Salvar backup
                with open(backup_file, 'w') as f:
                    f.write(result.stdout)
                
                return True, f"Backup criado: {backup_file.name}"
            else:
                return False, f"Erro ao fazer backup: {result.stderr}"
                
        except Exception as e:
            return False, f"Erro ao fazer backup: {str(e)}"
    
    def obter_informacoes(self) -> Dict:
        """
        Obtém informações detalhadas do Planka.
        
        Returns:
            Dict com informações do sistema
        """
        info = {
            "status": self.verificar_status(),
            "diretorio": str(self.planka_dir),
            "url": self.planka_url,
            "porta": self.planka_porta,
            "dependencias": self.verificar_dependencias(),
            "processos_docker": self.verificar_processos_docker(),
            "diretorio_valido": self.verificar_diretorio_planka(),
            "timestamp": datetime.now().isoformat()
        }
        
        return info 