# -*- coding: utf-8 -*-
"""
Configurações gerais do Dashboard de Tarefas.
"""

import os
import json
from pathlib import Path


class Settings:
    """
    Classe para gerenciar configurações do sistema.
    """
    
    def __init__(self):
        """Inicializa as configurações do sistema."""
        self.base_dir = Path(__file__).parent.parent
        self.config_file = self.base_dir / "config" / "settings.json"
        self.config = self._carregar_configuracoes()
        
        # Verificar e corrigir caminhos problemáticos
        self._corrigir_caminhos_problematicos()
        
        # Normalizar caminhos para serem independentes do utilizador
        self._normalizar_caminhos()
        
        # Carregar configurações de segurança
        self._carregar_configuracoes_seguranca()
    
    def _carregar_configuracoes(self):
        """
        Carrega as configurações do arquivo JSON.
        Se o arquivo não existir, cria com configurações padrão.
        """
        configuracoes_padrao = {
            "interface": {
                "tamanho_janela": "1200x800",
                "tamanho_minimo": "800x600",
                "tema": "default",
                "console_altura": 200
            },
                    "planka": {
            "diretorio": "~/Desktop/DEV/planka-personalizado",
            "porta": 3001,
            "url": "http://localhost:3001",
            "docker_compose_file": "docker-compose.yml"
        },
            "database": {
                "arquivo": "~/Desktop/DEV/dashboard-tarefas/database/dashboard.db",
                "backup_automatico": True,
                "backup_intervalo_horas": 24
            },
            "config": {
                "diretorio": "~/Desktop/DEV/dashboard-tarefas/config"
            },
            "logs": {
                "nivel": "INFO",
                "max_arquivos": 10,
                "tamanho_maximo_mb": 10,
                "diretorio_sistema": "~/Desktop/DEV/dashboard-tarefas/logs/sistema",
                "diretorio_tarefas": "~/Desktop/DEV/dashboard-tarefas/logs/tarefas",
                "diretorio_servidores": "~/Desktop/DEV/dashboard-tarefas/logs/servidores"
            },
            "servidores": {
                "timeout_conexao": 30,
                "max_conexoes": 5,
                "criptografia": "AES-256"
            },
            "tarefas": {
                "execucao_paralela": False,
                "max_tarefas_simultaneas": 1,
                "timeout_execucao": 300
            }
        }
        
        # Criar diretório de configuração se não existir
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Carregar configurações existentes ou criar com padrão
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config_carregada = json.load(f)
                    # Mesclar com configurações padrão (atualizar se necessário)
                    return self._mesclar_configuracoes(configuracoes_padrao, config_carregada)
            except Exception as e:
                print(f"Erro ao carregar configurações: {e}")
                return configuracoes_padrao
        else:
            # Criar arquivo com configurações padrão
            self._salvar_configuracoes(configuracoes_padrao)
            return configuracoes_padrao
    
    def _carregar_configuracoes_seguranca(self):
        """Carrega configurações de segurança de variáveis de ambiente."""
        # Configurações de segurança padrão
        self.seguranca = {
            "database": {
                "password": os.getenv("PLANKA_DB_PASSWORD", ""),
                "user": os.getenv("PLANKA_DB_USER", "postgres"),
                "host": os.getenv("PLANKA_DB_HOST", "localhost"),
                "port": int(os.getenv("PLANKA_DB_PORT", "5432"))
            },
            "admin": {
                "email": os.getenv("PLANKA_ADMIN_EMAIL", "admin@planka.local"),
                "password": os.getenv("PLANKA_ADMIN_PASSWORD", ""),
                "username": os.getenv("PLANKA_ADMIN_USERNAME", "admin")
            },
            "ssh": {
                "username": os.getenv("PLANKA_SSH_USERNAME", ""),
                "key_path": os.getenv("PLANKA_SSH_KEY_PATH", ""),
                "host": os.getenv("PLANKA_SSH_HOST", ""),
                "port": int(os.getenv("PLANKA_SSH_PORT", "22"))
            },
            "github": {
                "token": os.getenv("GITHUB_TOKEN", ""),
                "username": os.getenv("GITHUB_USERNAME", "")
            },
            "docker": {
                "secret_key": os.getenv("PLANKA_SECRET_KEY", ""),
                "postgres_password": os.getenv("POSTGRES_PASSWORD", ""),
                "postgres_user": os.getenv("POSTGRES_USER", "postgres")
            }
        }
    
    def obter_seguranca(self, secao, chave=None, valor_padrao=None):
        """
        Obtém uma configuração de segurança.
        
        Args:
            secao (str): Nome da seção de segurança
            chave (str, optional): Nome da chave
            valor_padrao: Valor padrão se não encontrado
            
        Returns:
            Valor da configuração de segurança
        """
        if secao not in self.seguranca:
            return valor_padrao
        
        if chave is None:
            return self.seguranca[secao]
        
        return self.seguranca[secao].get(chave, valor_padrao)
    
    def validar_configuracoes_seguranca(self):
        """
        Valida se as configurações de segurança estão corretas.
        
        Returns:
            dict: Resultado da validação
        """
        problemas = []
        avisos = []
        
        # Verificar passwords vazias
        if not self.seguranca["database"]["password"]:
            problemas.append("PLANKA_DB_PASSWORD não configurada")
        
        if not self.seguranca["admin"]["password"]:
            avisos.append("PLANKA_ADMIN_PASSWORD não configurada (usando padrão)")
        
        if not self.seguranca["ssh"]["username"]:
            avisos.append("PLANKA_SSH_USERNAME não configurada")
        
        if not self.seguranca["github"]["token"]:
            avisos.append("GITHUB_TOKEN não configurado")
        
        if not self.seguranca["docker"]["secret_key"]:
            avisos.append("PLANKA_SECRET_KEY não configurada")
        
        return {
            "valido": len(problemas) == 0,
            "problemas": problemas,
            "avisos": avisos
        }
    
    def _mesclar_configuracoes(self, padrao, carregada):
        """
        Mescla configurações carregadas com padrão, mantendo valores existentes.
        """
        resultado = padrao.copy()
        
        for secao, valores in carregada.items():
            if secao in resultado:
                if isinstance(valores, dict):
                    resultado[secao].update(valores)
                else:
                    resultado[secao] = valores
            else:
                resultado[secao] = valores
        
        return resultado
    
    def _salvar_configuracoes(self, configuracoes):
        """Salva as configurações no arquivo JSON."""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(configuracoes, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Erro ao salvar configurações: {e}")
    
    def obter(self, secao, chave=None, valor_padrao=None):
        """
        Obtém um valor de configuração.
        
        Args:
            secao (str): Nome da seção
            chave (str, optional): Nome da chave. Se None, retorna toda a seção
            valor_padrao: Valor padrão se a chave não existir
            
        Returns:
            Valor da configuração ou valor padrão
        """
        if secao not in self.config:
            return valor_padrao
        
        if chave is None:
            return self.config[secao]
        
        return self.config[secao].get(chave, valor_padrao)
    
    def definir(self, secao, chave, valor):
        """
        Define um valor de configuração.
        
        Args:
            secao (str): Nome da seção
            chave (str): Nome da chave
            valor: Valor a ser definido
        """
        if secao not in self.config:
            self.config[secao] = {}
        
        self.config[secao][chave] = valor
        self._salvar_configuracoes(self.config)
    
    def salvar(self):
        """Salva todas as configurações no arquivo."""
        self._salvar_configuracoes(self.config)
    
    def _expandir_caminho(self, caminho):
        """Expande caminhos com ~ para o diretório home do utilizador."""
        if isinstance(caminho, str):
            if caminho.startswith("~"):
                return Path(caminho).expanduser()
            elif "~" in caminho:
                # Substituir ~ por Path.home()
                caminho_expandido = caminho.replace("~", str(Path.home()))
                return Path(caminho_expandido)
        return Path(caminho)
    
    def obter_diretorio_planka(self):
        """Obtém o diretório do Planka personalizado."""
        caminho = self.obter("planka", "diretorio")
        return self._expandir_caminho(caminho)
    
    def obter_arquivo_database(self):
        """Obtém o caminho do arquivo de banco de dados."""
        caminho = self.obter("database", "arquivo")
        return self._expandir_caminho(caminho)
    
    def obter_diretorio_logs(self, tipo="sistema"):
        """Obtém o diretório de logs por tipo."""
        caminho = self.obter("logs", f"diretorio_{tipo}")
        return self._expandir_caminho(caminho)
    
    def obter_diretorio_config(self):
        """Obtém o diretório de configuração."""
        caminho = self.obter("config", "diretorio")
        return self._expandir_caminho(caminho)
    
    def criar_diretorios_necessarios(self):
        """Cria todos os diretórios necessários para o funcionamento."""
        diretorios = [
            self.obter_arquivo_database().parent,
            self.obter_diretorio_logs("sistema"),
            self.obter_diretorio_logs("tarefas"),
            self.obter_diretorio_logs("servidores"),
            self.obter_diretorio_config(),
            self.config_file.parent
        ]
        
        for diretorio in diretorios:
            try:
                diretorio.mkdir(parents=True, exist_ok=True)
            except PermissionError as e:
                print(f"Aviso: Não foi possível criar diretório {diretorio}: {e}")
                # Tentar criar em local alternativo se for diretório de logs
                if "logs" in str(diretorio):
                    diretorio_alt = self.base_dir / "logs_temp" / diretorio.name
                    try:
                        diretorio_alt.mkdir(parents=True, exist_ok=True)
                        print(f"Diretório alternativo criado: {diretorio_alt}")
                    except Exception as e2:
                        print(f"Erro ao criar diretório alternativo: {e2}")
            except Exception as e:
                print(f"Erro ao criar diretório {diretorio}: {e}")
    
    def _corrigir_caminhos_problematicos(self):
        """Corrige caminhos que podem causar problemas de permissão."""
        try:
            # Verificar se o diretório do Planka existe e é acessível
            planka_dir = self.obter_diretorio_planka()
            if not planka_dir.exists():
                # Se não existir, usar um caminho relativo ao projeto
                novo_planka_dir = self.base_dir.parent / "planka-personalizado"
                if novo_planka_dir.exists():
                    self.config["planka"]["diretorio"] = str(novo_planka_dir)
                    print(f"Diretório do Planka corrigido para: {novo_planka_dir}")
                else:
                    # Se ainda não existir, usar um caminho padrão
                    self.config["planka"]["diretorio"] = str(self.base_dir / "planka")
                    print(f"Diretório do Planka definido como: {self.config['planka']['diretorio']}")
            
            # Verificar se os diretórios de log são acessíveis
            for tipo in ["sistema", "tarefas", "servidores"]:
                log_dir = self.obter_diretorio_logs(tipo)
                if not log_dir.exists():
                    try:
                        log_dir.mkdir(parents=True, exist_ok=True)
                    except PermissionError:
                        # Se não conseguir criar, usar diretório temporário
                        temp_log_dir = self.base_dir / "logs_temp" / tipo
                        temp_log_dir.mkdir(parents=True, exist_ok=True)
                        self.config["logs"][f"diretorio_{tipo}"] = str(temp_log_dir)
                        print(f"Diretório de logs {tipo} corrigido para: {temp_log_dir}")
            
        except Exception as e:
            print(f"Erro ao corrigir caminhos problemáticos: {e}")
    
    def _normalizar_caminhos(self):
        """Normaliza caminhos para serem independentes do utilizador."""
        try:
            # Detectar automaticamente o diretório DEV no Desktop
            desktop_path = Path.home() / "Desktop"
            dev_path = desktop_path / "DEV"
            
            if dev_path.exists():
                # Normalizar caminhos para usar ~/Desktop/DEV
                self.config["planka"]["diretorio"] = "~/Desktop/DEV/planka-personalizado"
                self.config["database"]["arquivo"] = "~/Desktop/DEV/dashboard-tarefas/database/dashboard.db"
                self.config["config"]["diretorio"] = "~/Desktop/DEV/dashboard-tarefas/config"
                self.config["logs"]["diretorio_sistema"] = "~/Desktop/DEV/dashboard-tarefas/logs/sistema"
                self.config["logs"]["diretorio_tarefas"] = "~/Desktop/DEV/dashboard-tarefas/logs/tarefas"
                self.config["logs"]["diretorio_servidores"] = "~/Desktop/DEV/dashboard-tarefas/logs/servidores"
                
                print(f"✅ Caminhos normalizados para: {dev_path}")
            else:
                # Se não encontrar DEV no Desktop, usar caminhos relativos ao projeto
                print(f"⚠️ Diretório DEV não encontrado em {dev_path}")
                print("Usando caminhos relativos ao projeto atual")
                
                self.config["planka"]["diretorio"] = str(self.base_dir.parent / "planka-personalizado")
                self.config["database"]["arquivo"] = str(self.base_dir / "database/dashboard.db")
                self.config["config"]["diretorio"] = str(self.base_dir / "config")
                self.config["logs"]["diretorio_sistema"] = str(self.base_dir / "logs/sistema")
                self.config["logs"]["diretorio_tarefas"] = str(self.base_dir / "logs/tarefas")
                self.config["logs"]["diretorio_servidores"] = str(self.base_dir / "logs/servidores")
            
            # Salvar configurações normalizadas
            self._salvar_configuracoes(self.config)
            
        except Exception as e:
            print(f"Erro ao normalizar caminhos: {e}") 