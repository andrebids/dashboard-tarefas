# -*- coding: utf-8 -*-
"""
Módulo de Diagnósticos - Análise e diagnóstico do sistema Planka.
"""

import subprocess
import time
import requests
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional


class DiagnosticManager:
    """
    Gerenciador de diagnósticos para o sistema Planka.
    Responsável por executar análises completas e rápidas do sistema.
    """
    
    def __init__(self, settings, planka_manager):
        """
        Inicializa o gerenciador de diagnósticos.
        
        Args:
            settings: Configurações do sistema
            planka_manager: Instância do PlankaManager
        """
        self.settings = settings
        self.planka_manager = planka_manager
    
    def diagnostico_detalhado(self) -> Dict:
        """
        Executa um diagnóstico detalhado e completo do sistema.
        
        Returns:
            Dict com informações detalhadas do diagnóstico
        """
        diagnostico = {
            "timestamp": datetime.now().isoformat(),
            "dependencias": {},
            "diretorio": {},
            "docker": {},
            "conectividade": {},
            "logs": {},
            "recursos": {},
            "problemas": [],
            "sugestoes": []
        }
        
        # 1. Verificar dependências
        diagnostico["dependencias"] = self.planka_manager.verificar_dependencias()
        
        # 2. Verificar diretório do Planka
        dir_planka = self.settings.obter_diretorio_planka()
        diagnostico["diretorio"] = {
            "caminho": str(dir_planka),
            "valido": dir_planka.exists(),
            "arquivos_importantes": self._verificar_arquivos_importantes(dir_planka)
        }
        
        # 3. Verificar processos Docker
        diagnostico["docker"] = {
            "processos": self.planka_manager.verificar_processos_docker(),
            "stats_disponivel": False,
            "output": ""
        }
        
        # 4. Verificar status geral
        status = self.planka_manager.verificar_status()
        modo_ativo = self.planka_manager.verificar_modo_ativo()
        diagnostico["status_geral"] = {
            "status": status,
            "modo_ativo": modo_ativo
        }
        
        # 5. Verificar conectividade
        diagnostico["conectividade"] = self._verificar_conectividade()
        
        # 6. Analisar logs
        diagnostico["logs"] = self._analisar_logs()
        
        # 7. Verificar recursos do sistema (se Docker estiver rodando)
        if diagnostico["docker"]["processos"]:
            diagnostico["recursos"] = self._verificar_recursos_sistema()
        
        # 8. Identificar problemas e sugestões
        diagnostico["problemas"], diagnostico["sugestoes"] = self._identificar_problemas(diagnostico)
        
        return diagnostico
    
    def diagnostico_rapido(self) -> Dict:
        """
        Executa um diagnóstico rápido focado em problemas comuns.
        
        Returns:
            Dict com informações do diagnóstico rápido
        """
        problemas_encontrados = []
        sugestoes = []
        
        # 1. Verificar se Docker está rodando
        try:
            resultado = subprocess.run(
                ["docker", "info"], 
                capture_output=True, 
                text=True, encoding='utf-8', errors='replace'
            )
            docker_ok = resultado.returncode == 0
            if not docker_ok:
                problemas_encontrados.append("Docker não está rodando")
                sugestoes.append("Inicie o Docker Desktop")
        except Exception:
            problemas_encontrados.append("Docker não encontrado")
            sugestoes.append("Instale o Docker Desktop")
        
        # 2. Verificar se o diretório existe
        dir_planka = self.settings.obter_diretorio_planka()
        if not dir_planka.exists():
            problemas_encontrados.append("Diretório do Planka não encontrado")
            sugestoes.append("Use 'Descarregar Planka' para baixar o repositório")
        
        # 3. Verificar processos Docker do Planka
        processos = self.planka_manager.verificar_processos_docker()
        if not processos:
            problemas_encontrados.append("Nenhum container Docker do Planka rodando")
            sugestoes.append("Inicie o Planka usando 'Iniciar Planka'")
        
        # 4. Testar conectividade
        conectividade = self._verificar_conectividade()
        if not conectividade.get("acessivel", False):
            problemas_encontrados.append("Planka não está acessível")
            sugestoes.append("Verifique se o Planka está rodando")
        
        # 5. Verificar logs recentes para erros críticos
        logs = self._analisar_logs()
        if logs.get("erros"):
            problemas_encontrados.append("Erros críticos encontrados nos logs")
            sugestoes.append("Reinicie o Planka ou verifique a configuração")
        
        return {
            "timestamp": datetime.now().isoformat(),
            "problemas": problemas_encontrados,
            "sugestoes": sugestoes,
            "total_problemas": len(problemas_encontrados)
        }
    
    def forcar_reinicializacao(self) -> Tuple[bool, str]:
        """
        Força uma reinicialização completa do Planka.
        
        Returns:
            Tuple[bool, str]: (sucesso, mensagem)
        """
        try:
            # 1. Parar todos os containers do Planka
            dir_planka = self.settings.obter_diretorio_planka()
            
            # Parar containers de produção
            resultado = subprocess.run(
                ["docker-compose", "-f", "docker-compose-local.yml", "down"],
                cwd=dir_planka,
                capture_output=True,
                text=True, encoding='utf-8', errors='replace'
            )
            
            # Parar containers de desenvolvimento
            resultado = subprocess.run(
                ["docker-compose", "-f", "docker-compose-dev.yml", "down"],
                cwd=dir_planka,
                capture_output=True,
                text=True, encoding='utf-8', errors='replace'
            )
            
            # 2. Limpar containers órfãos
            subprocess.run(
                ["docker", "container", "prune", "-f"],
                capture_output=True,
                text=True, encoding='utf-8', errors='replace'
            )
            
            # 3. Limpar redes não utilizadas
            subprocess.run(
                ["docker", "network", "prune", "-f"],
                capture_output=True,
                text=True, encoding='utf-8', errors='replace'
            )
            
            # 4. Aguardar um pouco
            time.sleep(5)
            
            # 5. Reiniciar o Planka
            sucesso, mensagem = self.planka_manager.iniciar_planka()
            
            if sucesso:
                return True, "Reinicialização forçada concluída com sucesso"
            else:
                return False, f"Erro ao reiniciar: {mensagem}"
                
        except Exception as e:
            return False, f"Erro durante reinicialização forçada: {str(e)}"
    
    def _verificar_arquivos_importantes(self, dir_planka: Path) -> Dict[str, bool]:
        """
        Verifica se arquivos importantes existem no diretório.
        
        Args:
            dir_planka: Caminho do diretório do Planka
            
        Returns:
            Dict com status dos arquivos importantes
        """
        arquivos_importantes = [
            "docker-compose.yml",
            "docker-compose-local.yml", 
            "docker-compose-dev.yml",
            "package.json"
        ]
        
        resultado = {}
        for arquivo in arquivos_importantes:
            caminho_arquivo = dir_planka / arquivo
            resultado[arquivo] = caminho_arquivo.exists()
        
        return resultado
    
    def _verificar_conectividade(self) -> Dict:
        """
        Verifica a conectividade com o Planka.
        
        Returns:
            Dict com informações de conectividade
        """
        try:
            url = self.settings.obter("planka", "url", "http://localhost:3000")
            response = requests.get(url, timeout=5)
            
            return {
                "acessivel": True,
                "status_code": response.status_code,
                "url": url
            }
        except requests.exceptions.ConnectionError:
            return {
                "acessivel": False,
                "erro": "ConnectionError - Planka não está acessível"
            }
        except requests.exceptions.Timeout:
            return {
                "acessivel": False,
                "erro": "Timeout - Planka demorou para responder"
            }
        except Exception as e:
            return {
                "acessivel": False,
                "erro": str(e)
            }
    
    def _analisar_logs(self) -> Dict:
        """
        Analisa logs recentes em busca de erros.
        
        Returns:
            Dict com análise dos logs
        """
        try:
            logs = self.planka_manager.obter_logs(linhas=20)
            if not logs:
                return {
                    "disponivel": False,
                    "erro": "Não foi possível obter logs"
                }
            
            # Procurar por erros
            erros_encontrados = []
            linhas_log = logs.split('\n')
            
            for linha in linhas_log:
                linha_lower = linha.lower()
                if any(palavra in linha_lower for palavra in ['error', 'erro', 'failed', 'exception', 'fatal', 'panic']):
                    erros_encontrados.append(linha.strip())
            
            return {
                "disponivel": True,
                "tamanho": len(logs),
                "erros": erros_encontrados[-5:] if erros_encontrados else None  # Últimos 5 erros
            }
            
        except Exception as e:
            return {
                "disponivel": False,
                "erro": str(e)
            }
    
    def _verificar_recursos_sistema(self) -> Dict:
        """
        Verifica recursos do sistema via Docker stats.
        
        Returns:
            Dict com informações de recursos
        """
        try:
            resultado = subprocess.run(
                ["docker", "stats", "--no-stream", "--format", "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}"],
                capture_output=True,
                text=True, encoding='utf-8', errors='replace'
            )
            
            if resultado.returncode == 0:
                return {
                    "stats_disponivel": True,
                    "output": resultado.stdout
                }
            else:
                return {
                    "stats_disponivel": False,
                    "erro": "Erro ao obter estatísticas Docker"
                }
                
        except Exception as e:
            return {
                "stats_disponivel": False,
                "erro": str(e)
            }
    
    def _identificar_problemas(self, diagnostico: Dict) -> Tuple[List[str], List[str]]:
        """
        Identifica problemas baseado no diagnóstico.
        
        Args:
            diagnostico: Dicionário com informações do diagnóstico
            
        Returns:
            Tuple[List[str], List[str]]: (problemas, sugestões)
        """
        problemas = []
        sugestoes = []
        
        # Verificar dependências
        dependencias = diagnostico["dependencias"]
        if not dependencias.get("docker", False):
            problemas.append("Docker não está disponível")
            sugestoes.append("Instale o Docker Desktop")
        
        if not dependencias.get("docker_compose", False):
            problemas.append("Docker Compose não está disponível")
            sugestoes.append("Instale o Docker Compose")
        
        if not dependencias.get("git", False):
            problemas.append("Git não está disponível")
            sugestoes.append("Instale o Git")
        
        # Verificar diretório
        if not diagnostico["diretorio"]["valido"]:
            problemas.append("Diretório do Planka não encontrado")
            sugestoes.append("Use 'Descarregar Planka' para baixar o repositório")
        
        # Verificar status
        if diagnostico["status_geral"]["status"] != "online":
            problemas.append("Planka não está online")
            sugestoes.append("Use 'Iniciar Planka' ou 'Modo Desenvolvimento'")
        
        # Verificar conectividade
        if not diagnostico["conectividade"].get("acessivel", False):
            problemas.append("Planka não está acessível")
            sugestoes.append("Verifique se o Planka está rodando corretamente")
        
        # Verificar logs
        logs = diagnostico["logs"]
        if logs.get("erros"):
            problemas.append("Erros encontrados nos logs")
            sugestoes.append("Verifique a configuração ou reinicie o Planka")
        
        return problemas, sugestoes 