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
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime

# Importar sistema de cache
try:
    from config.dependency_cache import DependencyCache
except ImportError:
    # Fallback se o módulo não estiver disponível
    DependencyCache = None


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
            # Verificar Docker (timeout reduzido para 3 segundos)
            self._adicionar_log("  • Verificando Docker...")
            result = subprocess.run(
                ["docker", "--version"], 
                capture_output=True, 
                text=True, 
                timeout=3,
                encoding='utf-8', errors='replace'
            )
            dependencias["docker"] = result.returncode == 0
            
            if dependencias["docker"]:
                versao_docker = result.stdout.strip() if result.stdout else "Versão desconhecida"
                self._adicionar_log(f"    ✅ Docker encontrado: {versao_docker}")
            else:
                self._adicionar_log(f"    ❌ Docker não encontrado: {result.stderr}")
            
            # Verificar se Docker está rodando
            if dependencias["docker"]:
                self._adicionar_log("  • Verificando se Docker está rodando...")
                try:
                    result = subprocess.run(
                        ["docker", "info"], 
                        capture_output=True, 
                        text=True, 
                        timeout=3,
                        encoding='utf-8', errors='replace'
                    )
                    dependencias["docker_rodando"] = result.returncode == 0
                    
                    if dependencias["docker_rodando"]:
                        self._adicionar_log("    ✅ Docker está rodando")
                        # Extrair informações úteis do docker info
                        if result.stdout:
                            linhas_info = result.stdout.split('\n')
                            for linha in linhas_info:
                                if "Server Version:" in linha:
                                    self._adicionar_log(f"    • Versão do servidor: {linha.split(':', 1)[1].strip()}")
                                elif "Operating System:" in linha:
                                    self._adicionar_log(f"    • Sistema operacional: {linha.split(':', 1)[1].strip()}")
                                elif "Kernel Version:" in linha:
                                    self._adicionar_log(f"    • Versão do kernel: {linha.split(':', 1)[1].strip()}")
                    else:
                        self._adicionar_log(f"    ❌ Docker não está rodando: {result.stderr}")
                except Exception as e:
                    dependencias["docker_rodando"] = False
                    self._adicionar_log(f"    ❌ Erro ao verificar se Docker está rodando: {e}")
            
            # Verificar Docker Compose (timeout reduzido para 3 segundos)
            self._adicionar_log("  • Verificando Docker Compose...")
            result = subprocess.run(
                ["docker-compose", "--version"], 
                capture_output=True, 
                text=True, 
                timeout=3,
                encoding='utf-8', errors='replace'
            )
            dependencias["docker_compose"] = result.returncode == 0
            
            if dependencias["docker_compose"]:
                versao_compose = result.stdout.strip() if result.stdout else "Versão desconhecida"
                self._adicionar_log(f"    ✅ Docker Compose encontrado: {versao_compose}")
            else:
                self._adicionar_log(f"    ❌ Docker Compose não encontrado: {result.stderr}")
            
            # Verificar Node.js (timeout reduzido para 3 segundos)
            self._adicionar_log("  • Verificando Node.js...")
            result = subprocess.run(
                ["node", "--version"], 
                capture_output=True, 
                text=True, 
                timeout=3,
                encoding='utf-8', errors='replace'
            )
            dependencias["nodejs"] = result.returncode == 0
            
            if dependencias["nodejs"]:
                versao_node = result.stdout.strip() if result.stdout else "Versão desconhecida"
                self._adicionar_log(f"    ✅ Node.js encontrado: {versao_node}")
            else:
                self._adicionar_log(f"    ❌ Node.js não encontrado: {result.stderr}")
            
            # Verificar Git (timeout reduzido para 3 segundos)
            self._adicionar_log("  • Verificando Git...")
            result = subprocess.run(
                ["git", "--version"], 
                capture_output=True, 
                text=True, 
                timeout=3,
                encoding='utf-8', errors='replace'
            )
            dependencias["git"] = result.returncode == 0
            
            if dependencias["git"]:
                versao_git = result.stdout.strip() if result.stdout else "Versão desconhecida"
                self._adicionar_log(f"    ✅ Git encontrado: {versao_git}")
            else:
                self._adicionar_log(f"    ❌ Git não encontrado: {result.stderr}")
            
            # Resumo das dependências
            self._adicionar_log("  📋 RESUMO DAS DEPENDÊNCIAS:")
            for dependencia, status in dependencias.items():
                self._adicionar_log(f"    • {dependencia}: {'✅ OK' if status else '❌ FALTANDO'}")
            
            # Salvar no cache (se disponível)
            if self.dependency_cache:
                self.dependency_cache.salvar_dependencias_cache(dependencias)
            
        except (subprocess.TimeoutExpired, FileNotFoundError, Exception) as e:
            self._adicionar_log(f"  ❌ Erro ao verificar dependências: {e}")
            
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
            
            # Tentar conectar na URL do Planka (timeout reduzido para 3 segundos)
            response = requests.get(
                self.planka_url, 
                timeout=3,
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
                timeout=10,
                encoding='utf-8', errors='replace'
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
                ["docker-compose", "ps"],
                cwd=self.planka_dir,
                capture_output=True,
                text=True,
                timeout=10,
                encoding='utf-8', errors='replace'
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
                timeout=10,
                encoding='utf-8', errors='replace'
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
                text=True, encoding='utf-8', errors='replace'
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
                text=True, encoding='utf-8', errors='replace'
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
                text=True, encoding='utf-8', errors='replace'
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
                    text=True, encoding='utf-8', errors='replace'
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

    def sincronizar_producao_com_desenvolvimento(self) -> Tuple[bool, str]:
        """
        Sincroniza a versão de produção com a de desenvolvimento.
        Cria um novo docker-compose que usa o build local em vez da imagem oficial.
        
        Returns:
            (sucesso, mensagem)
        """
        try:
            # Verificar se o diretório existe
            if not self.verificar_diretorio_planka():
                return False, "Diretório do Planka não encontrado"
            
            # Verificar se docker-compose-dev.yml existe
            dev_compose_file = self.planka_dir / "docker-compose-dev.yml"
            if not dev_compose_file.exists():
                return False, "docker-compose-dev.yml não encontrado"
            
            # Verificar se docker-compose.yml existe (original)
            prod_compose_file = self.planka_dir / "docker-compose.yml"
            if not prod_compose_file.exists():
                return False, "docker-compose.yml não encontrado"
            
            # Fazer backup do arquivo original
            backup_file = self.planka_dir / "docker-compose.yml.backup"
            if not backup_file.exists():
                shutil.copy2(prod_compose_file, backup_file)
            
            # Criar novo docker-compose baseado no dev mas para produção
            novo_compose_content = self._criar_docker_compose_producao()
            
            # Salvar novo arquivo
            with open(prod_compose_file, 'w', encoding='utf-8') as f:
                f.write(novo_compose_content)
            
            return True, "Versão de produção sincronizada com desenvolvimento"
            
        except Exception as e:
            return False, f"Erro ao sincronizar produção com desenvolvimento: {str(e)}"
    
    def _criar_docker_compose_producao(self) -> str:
        """
        Cria conteúdo do docker-compose para produção baseado no desenvolvimento.
        
        Returns:
            Conteúdo do arquivo docker-compose
        """
        return '''services:
  planka:
    build:
      context: .
      dockerfile: Dockerfile.dev
    image: planka-producao
    pull_policy: never
    restart: on-failure
    volumes:
      - favicons:/app/public/favicons
      - user-avatars:/app/public/user-avatars
      - background-images:/app/public/background-images
      - attachments:/app/private/attachments
    ports:
      - 3000:1337
    environment:
      - BASE_URL=http://localhost:3000
      - DATABASE_URL=postgresql://postgres@postgres/planka
      - SECRET_KEY=notsecretkey
    depends_on:
      postgres:
        condition: service_healthy

  postgres:
    image: postgres:15-alpine
    restart: on-failure
    volumes:
      - postgres:/var/lib/postgresql/data
    environment:
      - POSTGRES_DB=planka
      - POSTGRES_USER=postgres
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  favicons:
  user-avatars:
  background-images:
  attachments:
  postgres:
'''
    
    def restaurar_producao_original(self) -> Tuple[bool, str]:
        """
        Restaura a versão de produção original (usando imagem oficial).
        
        Returns:
            (sucesso, mensagem)
        """
        try:
            # Verificar se o diretório existe
            if not self.verificar_diretorio_planka():
                return False, "Diretório do Planka não encontrado"
            
            # Verificar se backup existe
            backup_file = self.planka_dir / "docker-compose.yml.backup"
            if not backup_file.exists():
                return False, "Backup do docker-compose.yml não encontrado"
            
            # Restaurar backup
            prod_compose_file = self.planka_dir / "docker-compose.yml"
            shutil.copy2(backup_file, prod_compose_file)
            
            return True, "Versão de produção original restaurada"
            
        except Exception as e:
            return False, f"Erro ao restaurar produção original: {str(e)}"
    
    def verificar_sincronizacao_producao(self) -> Dict[str, any]:
        """
        Verifica se a produção está sincronizada com desenvolvimento.
        
        Returns:
            Dict com informações sobre a sincronização
        """
        try:
            # Verificar se o diretório existe
            if not self.verificar_diretorio_planka():
                return {
                    "sincronizada": False,
                    "motivo": "Diretório do Planka não encontrado",
                    "backup_existe": False,
                    "modo_atual": "desconhecido"
                }
            
            prod_compose_file = self.planka_dir / "docker-compose.yml"
            backup_file = self.planka_dir / "docker-compose.yml.backup"
            
            # Verificar se arquivo atual usa build local
            if prod_compose_file.exists():
                with open(prod_compose_file, 'r', encoding='utf-8') as f:
                    conteudo = f.read()
                    usa_build_local = "build:" in conteudo and "dockerfile: Dockerfile.dev" in conteudo
            else:
                usa_build_local = False
            
            # Verificar modo atual
            modo_atual = self.verificar_modo_ativo()
            
            return {
                "sincronizada": usa_build_local,
                "motivo": "Usa build local" if usa_build_local else "Usa imagem oficial",
                "backup_existe": backup_file.exists(),
                "modo_atual": modo_atual,
                "arquivo_existe": prod_compose_file.exists()
            }
            
        except Exception as e:
            return {
                "sincronizada": False,
                "motivo": f"Erro ao verificar: {str(e)}",
                "backup_existe": False,
                "modo_atual": "erro"
            }
    
    def configurar_producao_sempre_desenvolvimento(self) -> Tuple[bool, str]:
        """
        Configura produção para sempre usar o código de desenvolvimento.
        Isso modifica permanentemente o docker-compose.yml.
        
        Returns:
            (sucesso, mensagem)
        """
        try:
            # Verificar se o diretório existe
            if not self.verificar_diretorio_planka():
                return False, "Diretório do Planka não encontrado"
            
            # Verificar se docker-compose-dev.yml existe
            dev_compose_file = self.planka_dir / "docker-compose-dev.yml"
            if not dev_compose_file.exists():
                return False, "docker-compose-dev.yml não encontrado"
            
            # Verificar se docker-compose.yml existe (original)
            prod_compose_file = self.planka_dir / "docker-compose.yml"
            if not prod_compose_file.exists():
                return False, "docker-compose.yml não encontrado"
            
            # Fazer backup do arquivo original (apenas se não existir)
            backup_file = self.planka_dir / "docker-compose.yml.backup"
            if not backup_file.exists():
                shutil.copy2(prod_compose_file, backup_file)
            
            # Criar novo docker-compose que sempre usa desenvolvimento
            novo_compose_content = self._criar_docker_compose_sempre_desenvolvimento()
            
            # Salvar novo arquivo
            with open(prod_compose_file, 'w', encoding='utf-8') as f:
                f.write(novo_compose_content)
            
            return True, "Produção configurada para sempre usar código de desenvolvimento"
            
        except Exception as e:
            return False, f"Erro ao configurar produção: {str(e)}"
    
    def _criar_docker_compose_sempre_desenvolvimento(self) -> str:
        """
        Cria conteúdo do docker-compose que sempre usa desenvolvimento.
        
        Returns:
            Conteúdo do arquivo docker-compose
        """
        return '''services:
  planka:
    build:
      context: .
      dockerfile: Dockerfile.dev
    image: planka-producao-desenvolvimento
    pull_policy: never
    restart: on-failure
    volumes:
      - favicons:/app/public/favicons
      - user-avatars:/app/public/user-avatars
      - background-images:/app/public/background-images
      - attachments:/app/private/attachments
    ports:
      - 3000:1337
    environment:
      - BASE_URL=http://localhost:3000
      - DATABASE_URL=postgresql://postgres@postgres/planka
      - SECRET_KEY=notsecretkey
    depends_on:
      postgres:
        condition: service_healthy

  postgres:
    image: postgres:15-alpine
    restart: on-failure
    volumes:
      - postgres:/var/lib/postgresql/data
    environment:
      - POSTGRES_DB=planka
      - POSTGRES_USER=postgres
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  favicons:
  user-avatars:
  background-images:
  attachments:
  postgres:
''' 

    def executar_producao_com_modificacoes_locais(self) -> Tuple[bool, str]:
        """
        Executa o Planka em produção com modificações locais.
        Implementa as melhores práticas da documentação oficial.
        
        Returns:
            (sucesso, mensagem)
        """
        try:
            self._adicionar_log("🚀 INICIANDO PRODUÇÃO COM MODIFICAÇÕES LOCAIS")
            self._adicionar_log("=" * 60)
            
            # Verificar dependências com detalhes
            self._adicionar_log("📋 VERIFICANDO DEPENDÊNCIAS...")
            dependencias = self.verificar_dependencias()
            
            self._adicionar_log(f"  • Docker instalado: {'✅ Sim' if dependencias['docker'] else '❌ Não'}")
            self._adicionar_log(f"  • Docker rodando: {'✅ Sim' if dependencias['docker_rodando'] else '❌ Não'}")
            self._adicionar_log(f"  • Docker Compose: {'✅ Sim' if dependencias['docker_compose'] else '❌ Não'}")
            self._adicionar_log(f"  • Node.js: {'✅ Sim' if dependencias['nodejs'] else '❌ Não'}")
            self._adicionar_log(f"  • Git: {'✅ Sim' if dependencias['git'] else '❌ Não'}")
            
            if not dependencias["docker"]:
                return False, "Docker não está instalado. Instale o Docker Desktop."
            if not dependencias["docker_rodando"]:
                return False, "Docker não está rodando. Inicie o Docker Desktop e aguarde até estar completamente carregado."
            if not dependencias["docker_compose"]:
                return False, "Docker Compose não encontrado"
            
            # Verificar diretório com detalhes
            self._adicionar_log("📁 VERIFICANDO DIRETÓRIO DO PLANKA...")
            dir_planka = self.settings.obter_diretorio_planka()
            self._adicionar_log(f"  • Caminho: {dir_planka}")
            self._adicionar_log(f"  • Existe: {'✅ Sim' if dir_planka.exists() else '❌ Não'}")
            
            if not self.verificar_diretorio_planka():
                return False, "Diretório do Planka não encontrado"
            
            # Verificar arquivos importantes
            arquivos_importantes = ["docker-compose.yml", "docker-compose-local.yml", "package.json"]
            for arquivo in arquivos_importantes:
                caminho_arquivo = dir_planka / arquivo
                self._adicionar_log(f"  • {arquivo}: {'✅ Existe' if caminho_arquivo.exists() else '❌ Não encontrado'}")
            
            # Verificar status atual
            self._adicionar_log("🔍 VERIFICANDO STATUS ATUAL...")
            status_atual = self.verificar_status()
            modo_atual = self.verificar_modo_ativo()
            self._adicionar_log(f"  • Status atual: {status_atual}")
            self._adicionar_log(f"  • Modo atual: {modo_atual}")
            
            # Verificar containers ativos
            containers_ativos = self.verificar_containers_ativos()
            self._adicionar_log("  • Containers ativos:")
            for container, ativo in containers_ativos.items():
                self._adicionar_log(f"    - {container}: {'🟢 Ativo' if ativo else '🔴 Parado'}")
            
            # Parar containers existentes
            self._adicionar_log("⏹️ PARANDO CONTAINERS EXISTENTES...")
            self._adicionar_log("  • Executando parar_planka()...")
            self.parar_planka()
            self._adicionar_log("  • Aguardando 5 segundos para garantir parada...")
            time.sleep(5)
            
            # Verificar se containers pararam
            containers_apos_parar = self.verificar_containers_ativos()
            self._adicionar_log("  • Status após parar:")
            for container, ativo in containers_apos_parar.items():
                self._adicionar_log(f"    - {container}: {'🟢 Ainda ativo' if ativo else '🔴 Parado'}")
            
            # Gerar secret key adequado
            self._adicionar_log("🔑 GERANDO SECRET KEY...")
            self._adicionar_log("  • Tentando gerar com openssl...")
            secret_key = self._gerar_secret_key()
            if not secret_key:
                return False, "Erro ao gerar secret key"
            
            self._adicionar_log(f"  • Secret key gerado: {secret_key[:20]}...{secret_key[-20:]}")
            
            # Criar docker-compose otimizado para produção local
            self._adicionar_log("📝 CRIANDO CONFIGURAÇÃO DE PRODUÇÃO...")
            self._adicionar_log("  • Modificando docker-compose-local.yml...")
            sucesso_config = self._criar_configuracao_producao_local(secret_key)
            if not sucesso_config:
                return False, "Erro ao criar configuração de produção"
            
            self._adicionar_log("  • Configuração criada com sucesso")
            
            # Fazer build da imagem
            self._adicionar_log("🔨 FAZENDO BUILD DA IMAGEM...")
            self._adicionar_log("  • Comando: docker-compose -f docker-compose-local.yml build --no-cache")
            self._adicionar_log("  • Timeout: 5 minutos")
            sucesso_build = self._fazer_build_producao()
            if not sucesso_build:
                return False, "Erro no build da imagem"
            
            # Iniciar containers
            self._adicionar_log("🚀 INICIANDO CONTAINERS...")
            self._adicionar_log("  • Comando: docker-compose -f docker-compose-local.yml up -d")
            self._adicionar_log("  • Timeout: 1 minuto")
            sucesso_inicio = self._iniciar_containers_producao()
            if not sucesso_inicio:
                return False, "Erro ao iniciar containers"
            
            # Aguardar inicialização
            self._adicionar_log("⏳ AGUARDANDO INICIALIZAÇÃO...")
            self._adicionar_log("  • Aguardando 15 segundos para inicialização completa...")
            time.sleep(15)
            
            # Verificar containers após inicialização
            containers_apos_inicio = self.verificar_containers_ativos()
            self._adicionar_log("  • Status após inicialização:")
            for container, ativo in containers_apos_inicio.items():
                self._adicionar_log(f"    - {container}: {'🟢 Ativo' if ativo else '🔴 Parado'}")
            
            # Criar admin user se necessário
            self._adicionar_log("👤 VERIFICANDO ADMIN USER...")
            self._adicionar_log("  • Comando: npm run db:create-admin-user")
            sucesso_admin = self._criar_admin_user_se_necessario()
            if not sucesso_admin:
                self._adicionar_log("⚠️ Aviso: Erro ao criar admin user, mas continuando...")
            
            # Verificar se está funcionando
            self._adicionar_log("🔍 VERIFICANDO FUNCIONAMENTO...")
            status_final = self.verificar_status()
            self._adicionar_log(f"  • Status final: {status_final}")
            
            if status_final == "online":
                self._adicionar_log("✅ PLANKA EM PRODUÇÃO INICIADO COM SUCESSO!")
                self._adicionar_log("🌐 Acesso: http://localhost:3000")
                self._adicionar_log("=" * 60)
                return True, "Planka em produção iniciado com sucesso"
            else:
                self._adicionar_log("❌ PLANKA INICIADO MAS NÃO ESTÁ RESPONDENDO")
                self._adicionar_log("  • Verifique os logs do container para mais detalhes")
                self._adicionar_log("=" * 60)
                return False, "Planka iniciado mas não está respondendo"
                
        except Exception as e:
            self._adicionar_log(f"❌ ERRO CRÍTICO: {str(e)}")
            self._adicionar_log("=" * 60)
            return False, f"Erro ao executar produção: {str(e)}"
    
    def _gerar_secret_key(self) -> str:
        """
        Gera um secret key adequado usando openssl.
        
        Returns:
            Secret key gerado ou string vazia se erro
        """
        try:
            self._adicionar_log("  • Tentando gerar secret key com openssl...")
            
            comando = ["openssl", "rand", "-hex", "64"]
            self._adicionar_log(f"  • Comando: {' '.join(comando)}")
            self._adicionar_log(f"  • Tamanho da chave: 64 bytes (128 caracteres hex)")
            
            result = subprocess.run(
                comando,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            self._adicionar_log(f"  • Código de retorno: {result.returncode}")
            
            if result.returncode == 0:
                secret_key = result.stdout.strip()
                self._adicionar_log(f"  ✅ Secret key gerado com sucesso via openssl")
                self._adicionar_log(f"  • Tamanho da chave gerada: {len(secret_key)} caracteres")
                self._adicionar_log(f"  • Primeiros 20 caracteres: {secret_key[:20]}...")
                self._adicionar_log(f"  • Últimos 20 caracteres: ...{secret_key[-20:]}")
                return secret_key
            else:
                self._adicionar_log(f"  ⚠️ Erro ao gerar com openssl: {result.stderr}")
                self._adicionar_log(f"  • Tentando fallback com Python secrets...")
                
                # Fallback: gerar secret key simples
                import secrets
                secret_key = secrets.token_hex(64)
                self._adicionar_log(f"  ✅ Secret key gerado com fallback (Python secrets)")
                self._adicionar_log(f"  • Tamanho da chave gerada: {len(secret_key)} caracteres")
                self._adicionar_log(f"  • Primeiros 20 caracteres: {secret_key[:20]}...")
                self._adicionar_log(f"  • Últimos 20 caracteres: ...{secret_key[-20:]}")
                return secret_key
                
        except subprocess.TimeoutExpired:
            self._adicionar_log(f"  ⏰ Timeout ao gerar secret key com openssl")
            self._adicionar_log(f"  • Tentando fallback com Python secrets...")
            
            try:
                import secrets
                secret_key = secrets.token_hex(64)
                self._adicionar_log(f"  ✅ Secret key gerado com fallback (Python secrets)")
                self._adicionar_log(f"  • Tamanho da chave gerada: {len(secret_key)} caracteres")
                return secret_key
            except Exception as e2:
                self._adicionar_log(f"  ❌ Erro no fallback: {e2}")
                return ""
                
        except Exception as e:
            self._adicionar_log(f"  ❌ Erro ao gerar secret key: {e}")
            self._adicionar_log(f"  • Tipo de erro: {type(e).__name__}")
            self._adicionar_log(f"  • Usando secret key padrão...")
            
            # Fallback: secret key padrão
            secret_key = "planka_secret_key_local_development_" + str(int(time.time()))
            self._adicionar_log(f"  ⚠️ Usando secret key padrão (não seguro para produção)")
            self._adicionar_log(f"  • Secret key padrão: {secret_key}")
            return secret_key
    
    def _criar_configuracao_producao_local(self, secret_key: str) -> bool:
        """
        Cria configuração de produção otimizada para modificações locais.
        
        Args:
            secret_key: Secret key gerado
            
        Returns:
            True se sucesso, False caso contrário
        """
        try:
            # Verificar se docker-compose-local.yml existe
            local_compose_file = self.planka_dir / "docker-compose-local.yml"
            if not local_compose_file.exists():
                return False
            
            # Ler arquivo atual
            with open(local_compose_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Substituir secret key
            content = content.replace(
                'SECRET_KEY=your-secret-key-change-this',
                f'SECRET_KEY={secret_key}'
            )
            
            # Adicionar configurações de admin se não existirem
            if 'DEFAULT_ADMIN_EMAIL' not in content:
                admin_config = '''
      - DEFAULT_ADMIN_EMAIL=admin@planka.local
      - DEFAULT_ADMIN_PASSWORD=admin123
      - DEFAULT_ADMIN_NAME=Admin User
      - DEFAULT_ADMIN_USERNAME=admin'''
                
                # Inserir após SECRET_KEY
                content = content.replace(
                    f'- SECRET_KEY={secret_key}',
                    f'- SECRET_KEY={secret_key}{admin_config}'
                )
            
            # Salvar arquivo atualizado
            with open(local_compose_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return True
            
        except Exception as e:
            self._adicionar_log(f"❌ Erro ao criar configuração: {e}")
            return False
    
    def _fazer_build_producao(self) -> bool:
        """
        Faz build da imagem de produção.
        
        Returns:
            True se sucesso, False caso contrário
        """
        try:
            self._adicionar_log("  • Iniciando processo de build...")
            
            comando = ["docker-compose", "-f", "docker-compose-local.yml", "build", "--no-cache"]
            self._adicionar_log(f"  • Comando completo: {' '.join(comando)}")
            self._adicionar_log(f"  • Diretório de trabalho: {self.planka_dir}")
            self._adicionar_log(f"  • Timeout configurado: 300 segundos (5 minutos)")
            
            # Verificar se o arquivo docker-compose-local.yml existe
            arquivo_compose = self.planka_dir / "docker-compose-local.yml"
            if not arquivo_compose.exists():
                self._adicionar_log(f"  ❌ Arquivo docker-compose-local.yml não encontrado em {arquivo_compose}")
                return False
            
            self._adicionar_log(f"  ✅ Arquivo docker-compose-local.yml encontrado")
            
            # Verificar espaço em disco antes do build
            try:
                import shutil
                total, usado, livre = shutil.disk_usage(self.planka_dir)
                livre_gb = livre / (1024**3)
                self._adicionar_log(f"  • Espaço livre em disco: {livre_gb:.2f} GB")
                if livre_gb < 2:
                    self._adicionar_log(f"  ⚠️ Aviso: Pouco espaço em disco ({livre_gb:.2f} GB)")
            except Exception as e:
                self._adicionar_log(f"  ⚠️ Não foi possível verificar espaço em disco: {e}")
            
            self._adicionar_log("  • Executando comando de build...")
            result = subprocess.run(
                comando,
                cwd=self.planka_dir,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minutos
                encoding='utf-8', errors='replace'
            )
            
            self._adicionar_log(f"  • Código de retorno: {result.returncode}")
            self._adicionar_log(f"  • Tamanho da saída stdout: {len(result.stdout)} caracteres")
            self._adicionar_log(f"  • Tamanho da saída stderr: {len(result.stderr)} caracteres")
            
            if result.returncode == 0:
                self._adicionar_log("  ✅ Build concluído com sucesso")
                
                # Analisar saída para informações úteis
                if result.stdout:
                    linhas_saida = result.stdout.split('\n')
                    self._adicionar_log(f"  • Linhas de saída: {len(linhas_saida)}")
                    
                    # Procurar por informações importantes na saída
                    for linha in linhas_saida[-10:]:  # Últimas 10 linhas
                        if "Successfully built" in linha:
                            self._adicionar_log(f"  • {linha.strip()}")
                        elif "Step" in linha and ":" in linha:
                            self._adicionar_log(f"  • {linha.strip()}")
                
                return True
            else:
                self._adicionar_log("  ❌ Erro no build")
                
                # Mostrar detalhes do erro
                if result.stderr:
                    self._adicionar_log("  • Detalhes do erro:")
                    linhas_erro = result.stderr.split('\n')
                    for linha in linhas_erro[-5:]:  # Últimas 5 linhas de erro
                        if linha.strip():
                            self._adicionar_log(f"    {linha.strip()}")
                
                # Mostrar parte da saída padrão se houver
                if result.stdout:
                    self._adicionar_log("  • Parte da saída padrão:")
                    linhas_saida = result.stdout.split('\n')
                    for linha in linhas_saida[-3:]:  # Últimas 3 linhas
                        if linha.strip():
                            self._adicionar_log(f"    {linha.strip()}")
                
                return False
                
        except subprocess.TimeoutExpired:
            self._adicionar_log("  ⏰ Timeout no build após 5 minutos")
            self._adicionar_log("  • O processo de build demorou mais que o esperado")
            self._adicionar_log("  • Verifique se há problemas de rede ou recursos do sistema")
            return False
        except Exception as e:
            self._adicionar_log(f"  ❌ Erro inesperado no build: {e}")
            self._adicionar_log(f"  • Tipo de erro: {type(e).__name__}")
            return False
    
    def _iniciar_containers_producao(self) -> bool:
        """
        Inicia os containers de produção.
        
        Returns:
            True se sucesso, False caso contrário
        """
        try:
            self._adicionar_log("  • Iniciando processo de inicialização dos containers...")
            
            comando = ["docker-compose", "-f", "docker-compose-local.yml", "up", "-d"]
            self._adicionar_log(f"  • Comando completo: {' '.join(comando)}")
            self._adicionar_log(f"  • Diretório de trabalho: {self.planka_dir}")
            self._adicionar_log(f"  • Timeout configurado: 60 segundos")
            
            # Verificar status dos containers antes de iniciar
            self._adicionar_log("  • Verificando status dos containers antes da inicialização...")
            containers_antes = self.verificar_containers_ativos()
            for container, ativo in containers_antes.items():
                self._adicionar_log(f"    - {container}: {'🟢 Ativo' if ativo else '🔴 Parado'}")
            
            # Verificar se há containers rodando que possam conflitar
            containers_rodando = sum(1 for ativo in containers_antes.values() if ativo)
            if containers_rodando > 0:
                self._adicionar_log(f"  ⚠️ Aviso: {containers_rodando} container(s) já está(ão) rodando")
            
            self._adicionar_log("  • Executando comando de inicialização...")
            result = subprocess.run(
                comando,
                cwd=self.planka_dir,
                capture_output=True,
                text=True,
                timeout=60,
                encoding='utf-8', errors='replace'
            )
            
            self._adicionar_log(f"  • Código de retorno: {result.returncode}")
            self._adicionar_log(f"  • Tamanho da saída stdout: {len(result.stdout)} caracteres")
            self._adicionar_log(f"  • Tamanho da saída stderr: {len(result.stderr)} caracteres")
            
            if result.returncode == 0:
                self._adicionar_log("  ✅ Comando de inicialização executado com sucesso")
                
                # Aguardar um pouco para os containers inicializarem
                self._adicionar_log("  • Aguardando 3 segundos para containers inicializarem...")
                time.sleep(3)
                
                # Verificar status dos containers após inicialização
                self._adicionar_log("  • Verificando status dos containers após inicialização...")
                containers_depois = self.verificar_containers_ativos()
                for container, ativo in containers_depois.items():
                    self._adicionar_log(f"    - {container}: {'🟢 Ativo' if ativo else '🔴 Parado'}")
                
                # Verificar se pelo menos um container está ativo
                containers_ativos = sum(1 for ativo in containers_depois.values() if ativo)
                if containers_ativos > 0:
                    self._adicionar_log(f"  ✅ {containers_ativos} container(s) ativo(s) após inicialização")
                    
                    # Mostrar informações úteis da saída
                    if result.stdout:
                        linhas_saida = result.stdout.split('\n')
                        self._adicionar_log(f"  • Linhas de saída: {len(linhas_saida)}")
                        
                        # Procurar por informações importantes na saída
                        for linha in linhas_saida:
                            if "Creating" in linha or "Started" in linha or "Up" in linha:
                                self._adicionar_log(f"    {linha.strip()}")
                else:
                    self._adicionar_log("  ⚠️ Nenhum container está ativo após inicialização")
                
                return True
            else:
                self._adicionar_log("  ❌ Erro ao executar comando de inicialização")
                
                # Mostrar detalhes do erro
                if result.stderr:
                    self._adicionar_log("  • Detalhes do erro:")
                    linhas_erro = result.stderr.split('\n')
                    for linha in linhas_erro[-5:]:  # Últimas 5 linhas de erro
                        if linha.strip():
                            self._adicionar_log(f"    {linha.strip()}")
                
                # Mostrar parte da saída padrão se houver
                if result.stdout:
                    self._adicionar_log("  • Parte da saída padrão:")
                    linhas_saida = result.stdout.split('\n')
                    for linha in linhas_saida[-3:]:  # Últimas 3 linhas
                        if linha.strip():
                            self._adicionar_log(f"    {linha.strip()}")
                
                return False
                
        except subprocess.TimeoutExpired:
            self._adicionar_log("  ⏰ Timeout ao iniciar containers após 60 segundos")
            self._adicionar_log("  • O processo de inicialização demorou mais que o esperado")
            self._adicionar_log("  • Verifique se há problemas de rede ou recursos do sistema")
            return False
        except Exception as e:
            self._adicionar_log(f"  ❌ Erro inesperado ao iniciar containers: {e}")
            self._adicionar_log(f"  • Tipo de erro: {type(e).__name__}")
            return False
    
    def _criar_admin_user_se_necessario(self) -> bool:
        """
        Cria admin user se não existir.
        
        Returns:
            True se sucesso, False caso contrário
        """
        try:
            self._adicionar_log("  • Iniciando verificação/criação do admin user...")
            
            comando = ["docker-compose", "-f", "docker-compose-local.yml", "exec", "-T", "planka", "npm", "run", "db:create-admin-user"]
            self._adicionar_log(f"  • Comando completo: {' '.join(comando)}")
            self._adicionar_log(f"  • Diretório de trabalho: {self.planka_dir}")
            self._adicionar_log(f"  • Timeout configurado: 30 segundos")
            
            # Verificar se o container planka está rodando antes de executar o comando
            self._adicionar_log("  • Verificando se o container planka está rodando...")
            containers_ativos = self.verificar_containers_ativos()
            if not containers_ativos.get("planka", False):
                self._adicionar_log("  ⚠️ Container planka não está rodando")
                self._adicionar_log("  • Não é possível criar admin user sem o container ativo")
                return False
            
            self._adicionar_log("  ✅ Container planka está rodando")
            self._adicionar_log("  • Executando comando para criar/verificar admin user...")
            
            result = subprocess.run(
                comando,
                cwd=self.planka_dir,
                capture_output=True,
                text=True,
                timeout=30,
                encoding='utf-8', errors='replace'
            )
            
            self._adicionar_log(f"  • Código de retorno: {result.returncode}")
            self._adicionar_log(f"  • Tamanho da saída stdout: {len(result.stdout)} caracteres")
            self._adicionar_log(f"  • Tamanho da saída stderr: {len(result.stderr)} caracteres")
            
            # Se retornou 0, admin user foi criado ou já existe
            if result.returncode == 0:
                self._adicionar_log("  ✅ Admin user verificado/criado com sucesso")
                
                # Analisar saída para informações úteis
                if result.stdout:
                    linhas_saida = result.stdout.split('\n')
                    self._adicionar_log(f"  • Linhas de saída: {len(linhas_saida)}")
                    
                    # Procurar por informações importantes na saída
                    for linha in linhas_saida:
                        if "admin" in linha.lower() or "user" in linha.lower() or "created" in linha.lower():
                            self._adicionar_log(f"    {linha.strip()}")
                
                return True
            else:
                self._adicionar_log("  ⚠️ Erro ao verificar/criar admin user")
                
                # Mostrar detalhes do erro
                if result.stderr:
                    self._adicionar_log("  • Detalhes do erro:")
                    linhas_erro = result.stderr.split('\n')
                    for linha in linhas_erro[-5:]:  # Últimas 5 linhas de erro
                        if linha.strip():
                            self._adicionar_log(f"    {linha.strip()}")
                
                # Mostrar parte da saída padrão se houver
                if result.stdout:
                    self._adicionar_log("  • Parte da saída padrão:")
                    linhas_saida = result.stdout.split('\n')
                    for linha in linhas_saida[-3:]:  # Últimas 3 linhas
                        if linha.strip():
                            self._adicionar_log(f"    {linha.strip()}")
                
                # Verificar se é um erro comum
                if "already exists" in result.stderr.lower() or "already exists" in result.stdout.lower():
                    self._adicionar_log("  ℹ️ Admin user já existe (não é um erro)")
                    return True
                
                return False
                
        except subprocess.TimeoutExpired:
            self._adicionar_log("  ⏰ Timeout ao verificar/criar admin user após 30 segundos")
            self._adicionar_log("  • O processo demorou mais que o esperado")
            self._adicionar_log("  • Verifique se o container está funcionando corretamente")
            return False
        except Exception as e:
            self._adicionar_log(f"  ❌ Erro inesperado ao verificar/criar admin user: {e}")
            self._adicionar_log(f"  • Tipo de erro: {type(e).__name__}")
            return False
    
    def _adicionar_log(self, mensagem: str):
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

    def diagnosticar_producao(self) -> Dict[str, any]:
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
            status = self.verificar_status()
            diagnostico["status_geral"] = status
            
            # Verificar containers
            containers = self.verificar_containers_ativos()
            diagnostico["containers"] = containers
            
            # Verificar configurações
            diagnostico["configuracoes"] = self._verificar_configuracoes_producao()
            
            # Verificar logs
            diagnostico["logs"] = self._obter_logs_producao()
            
            # Identificar problemas
            problemas = []
            
            # Problema 1: Container não está rodando
            if not containers.get("planka", False):
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
    
    def _verificar_configuracoes_producao(self) -> Dict[str, any]:
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
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('localhost', 3000))
            sock.close()
            return result == 0
        except Exception:
            return False
    
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