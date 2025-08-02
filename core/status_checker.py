# -*- coding: utf-8 -*-
"""
Módulo de Verificação de Status - Monitoramento do status do Planka.
"""

import time
from typing import Dict, List, Optional, Callable
from datetime import datetime


class StatusChecker:
    """
    Verificador de status para o sistema Planka.
    Responsável por monitorar o status e atualizar a interface.
    """
    
    def __init__(self, settings, planka_manager):
        """
        Inicializa o verificador de status.
        
        Args:
            settings: Configurações do sistema
            planka_manager: Instância do PlankaManager
        """
        self.settings = settings
        self.planka_manager = planka_manager
        self.status_atual = "Desconhecido"
        self.modo_ativo = "desconhecido"
        self.callbacks_atualizacao = []
        self.monitoramento_ativo = False
    
    def verificar_status_inicial(self) -> Dict:
        """
        Verifica o status inicial do sistema.
        
        Returns:
            Dict com informações do status inicial
        """
        try:
            # Verificar se o diretório existe
            dir_planka = self.settings.obter_diretorio_planka()
            diretorio_existe = dir_planka.exists()
            
            # Verificar se o Planka está rodando
            status_info = self.verificar_status_planka()
            
            return {
                "diretorio": {
                    "existe": diretorio_existe,
                    "caminho": str(dir_planka)
                },
                "status_planka": status_info,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "erro": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def verificar_status_planka(self) -> Dict:
        """
        Verifica se o Planka está rodando.
        
        Returns:
            Dict com informações do status do Planka
        """
        try:
            # Usar o PlankaManager para verificar status
            status = self.planka_manager.verificar_status()
            modo_ativo = self.planka_manager.verificar_modo_ativo()
            
            # Atualizar status interno
            self.status_atual = status
            self.modo_ativo = modo_ativo
            
            # Determinar status de exibição
            if status == "online":
                if modo_ativo == "desenvolvimento":
                    status_exibicao = "Desenvolvimento"
                    cor = "blue"
                    icone = "🚀"
                elif modo_ativo == "producao":
                    status_exibicao = "Produção"
                    cor = "green"
                    icone = "🏭"
                else:
                    status_exibicao = "Rodando"
                    cor = "green"
                    icone = "🟢"
            elif status == "offline":
                status_exibicao = "Parado"
                cor = "red"
                icone = "🔴"
            else:
                status_exibicao = "Erro"
                cor = "orange"
                icone = "⚠️"
            
            return {
                "status": status,
                "status_exibicao": status_exibicao,
                "modo_ativo": modo_ativo,
                "cor": cor,
                "icone": icone,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.status_atual = "Erro"
            return {
                "status": "erro",
                "status_exibicao": "Erro",
                "modo_ativo": "desconhecido",
                "cor": "orange",
                "icone": "⚠️",
                "erro": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def obter_estado_botoes(self) -> Dict[str, str]:
        """
        Obtém o estado dos botões baseado no status atual.
        
        Returns:
            Dict com estado dos botões
        """
        if self.status_atual == "online":
            return {
                "iniciar": "disabled",
                "parar": "normal",
                "reiniciar": "normal",
                "abrir": "normal",
                "desenvolvimento": "normal"
            }
        else:
            return {
                "iniciar": "normal",
                "parar": "disabled",
                "reiniciar": "disabled",
                "abrir": "disabled",
                "desenvolvimento": "normal"
            }
    
    def adicionar_callback_atualizacao(self, callback: Callable):
        """
        Adiciona um callback para ser chamado quando o status for atualizado.
        
        Args:
            callback: Função a ser chamada
        """
        if callback not in self.callbacks_atualizacao:
            self.callbacks_atualizacao.append(callback)
    
    def remover_callback_atualizacao(self, callback: Callable):
        """
        Remove um callback de atualização.
        
        Args:
            callback: Função a ser removida
        """
        if callback in self.callbacks_atualizacao:
            self.callbacks_atualizacao.remove(callback)
    
    def notificar_atualizacao(self, status_info: Dict):
        """
        Notifica todos os callbacks registrados sobre uma atualização de status.
        
        Args:
            status_info: Informações do status atualizado
        """
        for callback in self.callbacks_atualizacao:
            try:
                callback(status_info)
            except Exception as e:
                # Log do erro mas não interromper outros callbacks
                print(f"Erro no callback de atualização: {e}")
    
    def iniciar_monitoramento(self, intervalo: int = 30):
        """
        Inicia o monitoramento automático do status.
        
        Args:
            intervalo: Intervalo em segundos entre verificações
        """
        if self.monitoramento_ativo:
            return
        
        self.monitoramento_ativo = True
        
        def monitorar():
            while self.monitoramento_ativo:
                try:
                    status_info = self.verificar_status_planka()
                    self.notificar_atualizacao(status_info)
                    time.sleep(intervalo)
                except Exception as e:
                    print(f"Erro no monitoramento: {e}")
                    time.sleep(intervalo)
        
        # Iniciar thread de monitoramento
        import threading
        thread_monitoramento = threading.Thread(target=monitorar, daemon=True)
        thread_monitoramento.start()
    
    def parar_monitoramento(self):
        """
        Para o monitoramento automático do status.
        """
        self.monitoramento_ativo = False
    
    def verificar_conectividade(self) -> Dict:
        """
        Verifica a conectividade com o Planka.
        
        Returns:
            Dict com informações de conectividade
        """
        try:
            import requests
            url = self.settings.obter("planka", "url", "http://localhost:3000")
            
            # Verificar se o Planka está rodando primeiro
            modo_ativo = self.planka_manager.verificar_modo_ativo()
            
            if modo_ativo == "nenhum":
                return {
                    "acessivel": False,
                    "erro": "Planka não está rodando",
                    "url": url,
                    "sugestao": "Inicie o Planka primeiro",
                    "timestamp": datetime.now().isoformat()
                }
            
            # Tentar conectar
            response = requests.get(url, timeout=5)
            
            return {
                "acessivel": True,
                "status_code": response.status_code,
                "url": url,
                "tempo_resposta": response.elapsed.total_seconds(),
                "modo_ativo": modo_ativo,
                "timestamp": datetime.now().isoformat()
            }
            
        except requests.exceptions.ConnectionError:
            # Verificar se é problema de porta ou serviço
            modo_ativo = self.planka_manager.verificar_modo_ativo()
            if modo_ativo != "nenhum":
                return {
                    "acessivel": False,
                    "erro": "ConnectionError - Serviço não responde",
                    "url": url,
                    "sugestao": "Aguarde alguns segundos para o serviço inicializar",
                    "modo_ativo": modo_ativo,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {
                    "acessivel": False,
                    "erro": "ConnectionError - Planka não está rodando",
                    "url": url,
                    "sugestao": "Inicie o Planka primeiro",
                    "timestamp": datetime.now().isoformat()
                }
        except requests.exceptions.Timeout:
            return {
                "acessivel": False,
                "erro": "Timeout - Serviço demorou para responder",
                "url": url,
                "sugestao": "Verifique se o Planka está funcionando corretamente",
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "acessivel": False,
                "erro": str(e),
                "url": url,
                "sugestao": "Verifique a configuração da URL",
                "timestamp": datetime.now().isoformat()
            }
    
    def obter_informacoes_sistema(self) -> Dict:
        """
        Obtém informações gerais do sistema.
        
        Returns:
            Dict com informações do sistema
        """
        try:
            dir_planka = self.settings.obter_diretorio_planka()
            url_planka = self.settings.obter("planka", "url", "http://localhost:3000")
            porta = self.settings.obter("planka", "porta", "3000")
            
            return {
                "diretorio": str(dir_planka),
                "url": url_planka,
                "porta": porta,
                "status_atual": self.status_atual,
                "modo_ativo": self.modo_ativo,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "erro": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def verificar_processos_docker(self) -> List[Dict]:
        """
        Verifica os processos Docker relacionados ao Planka.
        
        Returns:
            List[Dict] com informações dos processos
        """
        try:
            return self.planka_manager.verificar_processos_docker()
        except Exception as e:
            return [{"erro": str(e)}]
    
    def obter_logs_recentes(self, linhas: int = 10) -> str:
        """
        Obtém logs recentes do Planka.
        
        Args:
            linhas: Número de linhas a obter
            
        Returns:
            str com os logs
        """
        try:
            return self.planka_manager.obter_logs(linhas=linhas) or "Nenhum log disponível"
        except Exception as e:
            return f"Erro ao obter logs: {e}"
    
    def verificar_dependencias(self) -> Dict[str, bool]:
        """
        Verifica as dependências do sistema.
        
        Returns:
            Dict com status das dependências
        """
        try:
            return self.planka_manager.verificar_dependencias()
        except Exception as e:
            return {"erro": str(e)}
    
    def obter_resumo_status(self) -> Dict:
        """
        Obtém um resumo completo do status do sistema.
        
        Returns:
            Dict com resumo do status
        """
        try:
            status_planka = self.verificar_status_planka()
            conectividade = self.verificar_conectividade()
            processos = self.verificar_processos_docker()
            dependencias = self.verificar_dependencias()
            
            return {
                "status_planka": status_planka,
                "conectividade": conectividade,
                "processos_docker": processos,
                "dependencias": dependencias,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "erro": str(e),
                "timestamp": datetime.now().isoformat()
            } 