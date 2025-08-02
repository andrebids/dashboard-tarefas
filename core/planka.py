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
            # Primeiro verificar qual modo está ativo
            modo_ativo = self.verificar_modo_ativo()
            
            if modo_ativo == "nenhum":
                self.status = "offline"
                return "offline"
            
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
    
    def verificar_modo_ativo(self) -> str:
        """
        Verifica qual modo está ativo (produção ou desenvolvimento).
        
        Returns:
            "producao", "desenvolvimento", "nenhum"
        """
        try:
            # Usar o método mais preciso para verificar containers ativos
            containers_ativos = self.verificar_containers_ativos()
            
            # Priorizar modo desenvolvimento se ambos estiverem ativos
            if containers_ativos["desenvolvimento"]:
                return "desenvolvimento"
            elif containers_ativos["producao"]:
                return "producao"
            else:
                return "nenhum"
                
        except Exception as e:
            print(f"Erro ao verificar modo ativo: {e}")
            return "nenhum"
    
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
    
    def verificar_containers_ativos(self) -> Dict[str, bool]:
        """
        Verifica quais containers estão ativos em cada modo.
        
        Returns:
            Dict com status de cada modo
        """
        status = {
            "producao": False,
            "desenvolvimento": False
        }
        
        try:
            # Verificar containers de produção
            resultado_prod = subprocess.run(
                ["docker-compose", "-f", "docker-compose-local.yml", "ps"],
                cwd=self.planka_dir,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if resultado_prod.returncode == 0:
                # Verificar se o container planka está rodando
                linhas_prod = resultado_prod.stdout.strip().split('\n')
                for linha in linhas_prod:
                    if "planka-personalizado-planka-1" in linha and "Up" in linha:
                        status["producao"] = True
                        break
            
            # Verificar containers de desenvolvimento
            resultado_dev = subprocess.run(
                ["docker-compose", "-f", "docker-compose-dev.yml", "ps"],
                cwd=self.planka_dir,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if resultado_dev.returncode == 0:
                # Verificar se os containers específicos do desenvolvimento estão rodando
                linhas_dev = resultado_dev.stdout.strip().split('\n')
                server_rodando = False
                client_rodando = False
                
                for linha in linhas_dev:
                    if "planka-personalizado-planka-server-1" in linha and "Up" in linha:
                        server_rodando = True
                    elif "planka-personalizado-planka-client-1" in linha and "Up" in linha:
                        client_rodando = True
                
                if server_rodando and client_rodando:
                    status["desenvolvimento"] = True
                    
        except Exception as e:
            print(f"Erro ao verificar containers ativos: {e}")
            
        return status
    
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
        Inicia o Planka em modo desenvolvimento usando docker-compose-dev.yml.
        
        Returns:
            (sucesso, mensagem)
        """
        try:
            # Verificar se Docker está disponível
            dependencias = self.verificar_dependencias()
            if not dependencias["docker"]:
                return False, "Docker não encontrado"
            
            if not dependencias["docker_compose"]:
                return False, "Docker Compose não encontrado"
            
            # Verificar se o diretório existe
            if not self.verificar_diretorio_planka():
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
                timeout=60
            )
            
            if resultado.returncode == 0:
                # Aguardar inicialização
                time.sleep(10)
                
                # Verificar se iniciou
                if self.verificar_status() == "online":
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
                timeout=30
            )
            
            if resultado.returncode == 0:
                return True, "Modo desenvolvimento parado"
            else:
                return False, f"Erro ao parar modo desenvolvimento: {resultado.stderr}"
                
        except subprocess.TimeoutExpired:
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
    
    def diagnostico_detalhado(self) -> Dict:
        """
        Executa um diagnóstico detalhado do sistema Planka.
        
        Returns:
            Dict com resultados do diagnóstico
        """
        diagnostico = {
            "timestamp": datetime.now().isoformat(),
            "dependencias": {},
            "diretorio": {},
            "docker": {},
            "conectividade": {},
            "logs": {},
            "problemas": [],
            "sugestoes": []
        }
        
        try:
            # 1. Verificar dependências
            dependencias = self.verificar_dependencias()
            diagnostico["dependencias"] = dependencias
            
            for dep, status in dependencias.items():
                if not status:
                    diagnostico["problemas"].append(f"Dependência {dep} não encontrada")
                    if dep == "docker":
                        diagnostico["sugestoes"].append("Instale o Docker Desktop")
                    elif dep == "docker_compose":
                        diagnostico["sugestoes"].append("Instale o Docker Compose")
                    elif dep == "nodejs":
                        diagnostico["sugestoes"].append("Instale o Node.js")
                    elif dep == "git":
                        diagnostico["sugestoes"].append("Instale o Git")
            
            # 2. Verificar diretório
            dir_valido = self.verificar_diretorio_planka()
            diagnostico["diretorio"]["valido"] = dir_valido
            diagnostico["diretorio"]["caminho"] = str(self.planka_dir)
            
            if not dir_valido:
                diagnostico["problemas"].append("Diretório do Planka não encontrado ou inválido")
                diagnostico["sugestoes"].append("Use 'Descarregar Planka' para baixar o repositório")
            else:
                # Verificar arquivos importantes
                arquivos_importantes = [
                    "docker-compose.yml",
                    "docker-compose-local.yml",
                    "docker-compose-dev.yml",
                    "package.json"
                ]
                
                arquivos_faltando = []
                for arquivo in arquivos_importantes:
                    if not (self.planka_dir / arquivo).exists():
                        arquivos_faltando.append(arquivo)
                
                if arquivos_faltando:
                    diagnostico["problemas"].append(f"Arquivos importantes faltando: {', '.join(arquivos_faltando)}")
                    diagnostico["sugestoes"].append("Reinstale o repositório do Planka")
            
            # 3. Verificar Docker
            processos = self.verificar_processos_docker()
            diagnostico["docker"]["processos"] = processos
            
            if not processos:
                diagnostico["problemas"].append("Nenhum processo Docker do Planka encontrado")
                diagnostico["sugestoes"].append("Inicie o Planka usando 'Iniciar Planka' ou 'Modo Desenvolvimento'")
            
            # 4. Verificar conectividade
            try:
                response = requests.get(self.planka_url, timeout=5)
                diagnostico["conectividade"]["status_code"] = response.status_code
                diagnostico["conectividade"]["acessivel"] = response.status_code == 200
                
                if response.status_code != 200:
                    diagnostico["problemas"].append(f"Planka retornou status HTTP {response.status_code}")
                    diagnostico["sugestoes"].append("Verifique se o Planka está iniciando corretamente")
                    
            except requests.RequestException as e:
                diagnostico["conectividade"]["erro"] = str(e)
                diagnostico["conectividade"]["acessivel"] = False
                diagnostico["problemas"].append(f"Erro de conectividade: {str(e)}")
                diagnostico["sugestoes"].append("Verifique se o Planka está rodando e acessível")
            
            # 5. Verificar logs
            try:
                logs = self.obter_logs(linhas=50)
                diagnostico["logs"]["disponivel"] = True
                diagnostico["logs"]["tamanho"] = len(logs)
                
                # Procurar por erros nos logs
                erros_log = []
                linhas_log = logs.split('\n')
                for linha in linhas_log:
                    if any(palavra in linha.lower() for palavra in ['error', 'erro', 'failed', 'exception', 'fatal']):
                        erros_log.append(linha.strip())
                
                if erros_log:
                    diagnostico["logs"]["erros"] = erros_log[-5:]  # Últimos 5 erros
                    diagnostico["problemas"].append(f"Encontrados {len(erros_log)} erros nos logs")
                    diagnostico["sugestoes"].append("Verifique os logs detalhados para identificar o problema")
                else:
                    diagnostico["logs"]["erros"] = []
                    
            except Exception as e:
                diagnostico["logs"]["disponivel"] = False
                diagnostico["logs"]["erro"] = str(e)
                diagnostico["problemas"].append("Não foi possível obter logs")
            
            # 6. Verificar status geral
            status = self.verificar_status()
            modo_ativo = self.verificar_modo_ativo()
            
            diagnostico["status_geral"] = {
                "status": status,
                "modo_ativo": modo_ativo
            }
            
            if status != "online":
                diagnostico["problemas"].append("Planka não está online")
                if status == "offline":
                    diagnostico["sugestoes"].append("Inicie o Planka usando 'Iniciar Planka'")
                else:
                    diagnostico["sugestoes"].append("Verifique se há erros na inicialização")
            
            # 7. Verificar recursos do sistema
            try:
                # Verificar uso de memória dos containers
                result = subprocess.run(
                    ["docker", "stats", "--no-stream", "--format", "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                if result.returncode == 0:
                    diagnostico["recursos"] = {
                        "stats_disponivel": True,
                        "output": result.stdout
                    }
                else:
                    diagnostico["recursos"] = {
                        "stats_disponivel": False,
                        "erro": result.stderr
                    }
                    
            except Exception as e:
                diagnostico["recursos"] = {
                    "stats_disponivel": False,
                    "erro": str(e)
                }
            
        except Exception as e:
            diagnostico["erro_geral"] = str(e)
            diagnostico["problemas"].append(f"Erro durante diagnóstico: {str(e)}")
        
        return diagnostico 