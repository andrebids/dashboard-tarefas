# -*- coding: utf-8 -*-
"""
Módulo para monitoramento de status do Planka.
Monitoramento de status do Planka e verificação de containers ativos.
"""

import subprocess
import requests
from typing import Dict, List
from pathlib import Path


class StatusMonitor:
    """
    Monitor de status do sistema Planka.
    """
    
    def __init__(self, settings):
        """
        Inicializa o monitor de status.
        
        Args:
            settings: Instância das configurações do sistema
        """
        self.settings = settings
        self.planka_dir = Path(settings.obter("planka", "diretorio"))
        self.planka_url = settings.obter("planka", "url")
        self.planka_porta = settings.obter("planka", "porta")
        self.status = "desconhecido"
    
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