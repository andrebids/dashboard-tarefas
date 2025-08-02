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
                "diretorio": str(self.base_dir.parent / "planka-personalizado"),
                "porta": 3000,
                "url": "http://localhost:3000",
                "docker_compose_file": "docker-compose.yml"
            },
            "database": {
                "arquivo": str(self.base_dir / "database" / "dashboard.db"),
                "backup_automatico": True,
                "backup_intervalo_horas": 24
            },
            "logs": {
                "nivel": "INFO",
                "max_arquivos": 10,
                "tamanho_maximo_mb": 10,
                "diretorio_sistema": str(self.base_dir / "logs" / "sistema"),
                "diretorio_tarefas": str(self.base_dir / "logs" / "tarefas"),
                "diretorio_servidores": str(self.base_dir / "logs" / "servidores")
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
    
    def obter_diretorio_planka(self):
        """Obtém o diretório do Planka personalizado."""
        return Path(self.obter("planka", "diretorio"))
    
    def obter_arquivo_database(self):
        """Obtém o caminho do arquivo de banco de dados."""
        return Path(self.obter("database", "arquivo"))
    
    def obter_diretorio_logs(self, tipo="sistema"):
        """Obtém o diretório de logs por tipo."""
        return Path(self.obter("logs", f"diretorio_{tipo}"))
    
    def criar_diretorios_necessarios(self):
        """Cria todos os diretórios necessários para o funcionamento."""
        diretorios = [
            self.obter_arquivo_database().parent,
            self.obter_diretorio_logs("sistema"),
            self.obter_diretorio_logs("tarefas"),
            self.obter_diretorio_logs("servidores"),
            self.config_file.parent
        ]
        
        for diretorio in diretorios:
            diretorio.mkdir(parents=True, exist_ok=True) 