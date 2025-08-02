# -*- coding: utf-8 -*-
"""
Sistema de logs do Dashboard de Tarefas.
"""

import os
import logging
import datetime
from pathlib import Path
from typing import Optional, Dict, Any


class LogManager:
    """
    Gerenciador de logs do sistema.
    """
    
    def __init__(self, settings=None):
        """
        Inicializa o gerenciador de logs.
        
        Args:
            settings: Instância das configurações do sistema
        """
        self.settings = settings
        self.loggers = {}
        self._configurar_loggers()
    
    def _configurar_loggers(self):
        """Configura os loggers para diferentes tipos de log."""
        if not self.settings:
            return
        
        # Configurar logger do sistema
        self._configurar_logger("sistema", self.settings.obter_diretorio_logs("sistema"))
        self._configurar_logger("tarefas", self.settings.obter_diretorio_logs("tarefas"))
        self._configurar_logger("servidores", self.settings.obter_diretorio_logs("servidores"))
    
    def _configurar_logger(self, nome: str, diretorio: Path):
        """
        Configura um logger específico.
        
        Args:
            nome: Nome do logger
            diretorio: Diretório onde salvar os logs
        """
        # Criar diretório se não existir
        diretorio.mkdir(parents=True, exist_ok=True)
        
        # Criar logger
        logger = logging.getLogger(f"dashboard.{nome}")
        logger.setLevel(logging.INFO)
        
        # Evitar duplicação de handlers
        if logger.handlers:
            return
        
        # Configurar formato
        formato = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Handler para arquivo
        arquivo_log = diretorio / f"{nome}_{datetime.date.today()}.log"
        file_handler = logging.FileHandler(arquivo_log, encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formato)
        
        # Handler para console
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formato)
        
        # Adicionar handlers
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        self.loggers[nome] = logger
    
    def registrar_log(self, nivel: str, mensagem: str, origem: str = "sistema", 
                     detalhes: Optional[Dict[str, Any]] = None):
        """
        Registra um log no sistema.
        
        Args:
            nivel: Nível do log (INFO, WARNING, ERROR, SUCCESS, DEBUG)
            mensagem: Mensagem do log
            origem: Origem do log (sistema, tarefas, servidores, planka)
            detalhes: Detalhes adicionais do log
        """
        # Normalizar nível
        nivel = nivel.upper()
        
        # Mapear níveis customizados para níveis padrão
        nivel_mapping = {
            "SUCCESS": "INFO",
            "DEBUG": "DEBUG",
            "INFO": "INFO",
            "WARNING": "WARNING",
            "ERROR": "ERROR",
            "CRITICAL": "CRITICAL"
        }
        
        nivel_logging = nivel_mapping.get(nivel, "INFO")
        
        # Preparar mensagem completa
        mensagem_completa = mensagem
        if detalhes:
            mensagem_completa += f" | Detalhes: {detalhes}"
        
        # Registrar no logger apropriado
        logger = self.loggers.get(origem, self.loggers.get("sistema"))
        if logger:
            if nivel_logging == "DEBUG":
                logger.debug(mensagem_completa)
            elif nivel_logging == "INFO":
                logger.info(mensagem_completa)
            elif nivel_logging == "WARNING":
                logger.warning(mensagem_completa)
            elif nivel_logging == "ERROR":
                logger.error(mensagem_completa)
            elif nivel_logging == "CRITICAL":
                logger.critical(mensagem_completa)
        
        # Log de sucesso com formatação especial
        if nivel == "SUCCESS":
            print(f"✅ {mensagem_completa}")
        elif nivel == "ERROR":
            print(f"❌ {mensagem_completa}")
        elif nivel == "WARNING":
            print(f"⚠️ {mensagem_completa}")
        else:
            print(f"ℹ️ {mensagem_completa}")
    
    def log_sistema(self, nivel: str, mensagem: str, detalhes: Optional[Dict[str, Any]] = None):
        """Registra log do sistema."""
        self.registrar_log(nivel, mensagem, "sistema", detalhes)
    
    def log_tarefa(self, nivel: str, mensagem: str, tarefa_id: Optional[str] = None, 
                   detalhes: Optional[Dict[str, Any]] = None):
        """Registra log de tarefa."""
        if tarefa_id:
            mensagem = f"[Tarefa {tarefa_id}] {mensagem}"
        self.registrar_log(nivel, mensagem, "tarefas", detalhes)
    
    def log_servidor(self, nivel: str, mensagem: str, servidor_id: Optional[str] = None,
                     detalhes: Optional[Dict[str, Any]] = None):
        """Registra log de servidor."""
        if servidor_id:
            mensagem = f"[Servidor {servidor_id}] {mensagem}"
        self.registrar_log(nivel, mensagem, "servidores", detalhes)
    
    def log_planka(self, nivel: str, mensagem: str, detalhes: Optional[Dict[str, Any]] = None):
        """Registra log do Planka."""
        self.registrar_log(nivel, mensagem, "sistema", detalhes)
    
    def obter_logs(self, tipo: str = "sistema", limite: int = 100) -> list:
        """
        Obtém logs de um tipo específico.
        
        Args:
            tipo: Tipo de log (sistema, tarefas, servidores)
            limite: Número máximo de linhas a retornar
            
        Returns:
            Lista de logs
        """
        try:
            diretorio = self.settings.obter_diretorio_logs(tipo)
            arquivo_log = diretorio / f"{tipo}_{datetime.date.today()}.log"
            
            if not arquivo_log.exists():
                return []
            
            with open(arquivo_log, 'r', encoding='utf-8') as f:
                linhas = f.readlines()
                return linhas[-limite:] if len(linhas) > limite else linhas
                
        except Exception as e:
            self.log_sistema("ERROR", f"Erro ao obter logs: {e}")
            return []
    
    def limpar_logs_antigos(self, dias: int = 30):
        """
        Remove logs mais antigos que o número de dias especificado.
        
        Args:
            dias: Número de dias para manter os logs
        """
        try:
            data_limite = datetime.date.today() - datetime.timedelta(days=dias)
            
            for tipo in ["sistema", "tarefas", "servidores"]:
                diretorio = self.settings.obter_diretorio_logs(tipo)
                
                if not diretorio.exists():
                    continue
                
                for arquivo in diretorio.glob(f"{tipo}_*.log"):
                    try:
                        # Extrair data do nome do arquivo
                        nome_arquivo = arquivo.stem
                        data_str = nome_arquivo.split("_")[-1]
                        data_arquivo = datetime.datetime.strptime(data_str, "%Y-%m-%d").date()
                        
                        if data_arquivo < data_limite:
                            arquivo.unlink()
                            self.log_sistema("INFO", f"Log antigo removido: {arquivo.name}")
                    except Exception as e:
                        self.log_sistema("WARNING", f"Erro ao processar arquivo {arquivo}: {e}")
                        
        except Exception as e:
            self.log_sistema("ERROR", f"Erro ao limpar logs antigos: {e}")
    
    def exportar_logs(self, tipo: str = "sistema", formato: str = "txt", 
                     data_inicio: Optional[str] = None, data_fim: Optional[str] = None) -> str:
        """
        Exporta logs para um arquivo.
        
        Args:
            tipo: Tipo de log a exportar
            formato: Formato de exportação (txt, csv, json)
            data_inicio: Data de início (YYYY-MM-DD)
            data_fim: Data de fim (YYYY-MM-DD)
            
        Returns:
            Caminho do arquivo exportado
        """
        try:
            diretorio = self.settings.obter_diretorio_logs(tipo)
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            nome_arquivo = f"logs_{tipo}_{timestamp}.{formato}"
            caminho_exportacao = diretorio / nome_arquivo
            
            # Coletar logs
            logs = []
            for arquivo in diretorio.glob(f"{tipo}_*.log"):
                try:
                    nome_arquivo = arquivo.stem
                    data_str = nome_arquivo.split("_")[-1]
                    
                    # Filtrar por data se especificado
                    if data_inicio and data_str < data_inicio:
                        continue
                    if data_fim and data_str > data_fim:
                        continue
                    
                    with open(arquivo, 'r', encoding='utf-8') as f:
                        logs.extend(f.readlines())
                except Exception as e:
                    self.log_sistema("WARNING", f"Erro ao ler arquivo {arquivo}: {e}")
            
            # Exportar no formato especificado
            if formato == "txt":
                with open(caminho_exportacao, 'w', encoding='utf-8') as f:
                    f.writelines(logs)
            elif formato == "csv":
                import csv
                with open(caminho_exportacao, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(["Timestamp", "Logger", "Level", "Message"])
                    for log in logs:
                        # Parsear linha de log
                        partes = log.strip().split(" - ")
                        if len(partes) >= 4:
                            writer.writerow(partes)
            
            self.log_sistema("SUCCESS", f"Logs exportados para: {caminho_exportacao}")
            return str(caminho_exportacao)
            
        except Exception as e:
            self.log_sistema("ERROR", f"Erro ao exportar logs: {e}")
            return "" 