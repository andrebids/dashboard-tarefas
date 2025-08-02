# -*- coding: utf-8 -*-
"""
Sistema de logs avançado do Dashboard de Tarefas.
Implementa logs estruturados, filtros, busca e exportação.
"""

import os
import json
import sqlite3
import threading
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Union
from datetime import datetime, timedelta
from enum import Enum
import csv
import zipfile
import shutil


class NivelLog(Enum):
    """Níveis de log disponíveis."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"
    SUCCESS = "SUCCESS"


class OrigemLog(Enum):
    """Origens de log disponíveis."""
    SISTEMA = "sistema"
    PLANKA = "planka"
    SERVIDORES = "servidores"
    BASE_DADOS = "base_dados"
    INTERFACE = "interface"
    TAREFAS = "tarefas"


class LogEstruturado:
    """
    Classe para representar um log estruturado.
    """
    
    def __init__(self, id: int = None, timestamp: datetime = None, nivel: str = "INFO",
                 origem: str = "sistema", mensagem: str = "", detalhes: Dict = None,
                 usuario: str = "", sessao: str = "", ip: str = ""):
        """
        Inicializa um log estruturado.
        
        Args:
            id: ID único do log
            timestamp: Timestamp do log
            nivel: Nível do log
            origem: Origem do log
            mensagem: Mensagem do log
            detalhes: Detalhes adicionais (JSON)
            usuario: Usuário que gerou o log
            sessao: ID da sessão
            ip: Endereço IP
        """
        self.id = id
        self.timestamp = timestamp or datetime.now()
        self.nivel = nivel.upper()
        self.origem = origem
        self.mensagem = mensagem
        self.detalhes = detalhes or {}
        self.usuario = usuario
        self.sessao = sessao
        self.ip = ip
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte o log para dicionário."""
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat(),
            "nivel": self.nivel,
            "origem": self.origem,
            "mensagem": self.mensagem,
            "detalhes": json.dumps(self.detalhes, ensure_ascii=False),
            "usuario": self.usuario,
            "sessao": self.sessao,
            "ip": self.ip
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LogEstruturado':
        """Cria um log a partir de dicionário."""
        detalhes = {}
        if data.get("detalhes"):
            try:
                detalhes = json.loads(data["detalhes"])
            except:
                detalhes = {}
        
        return cls(
            id=data.get("id"),
            timestamp=datetime.fromisoformat(data["timestamp"]) if data.get("timestamp") else None,
            nivel=data.get("nivel", "INFO"),
            origem=data.get("origem", "sistema"),
            mensagem=data.get("mensagem", ""),
            detalhes=detalhes,
            usuario=data.get("usuario", ""),
            sessao=data.get("sessao", ""),
            ip=data.get("ip", "")
        )


class FiltroLogs:
    """
    Classe para filtrar logs.
    """
    
    def __init__(self):
        """Inicializa o filtro de logs."""
        self.niveis = []
        self.origens = []
        self.data_inicio = None
        self.data_fim = None
        self.usuario = ""
        self.sessao = ""
        self.texto_busca = ""
        self.limite = 1000
    
    def adicionar_nivel(self, nivel: str):
        """Adiciona um nível ao filtro."""
        if nivel.upper() not in self.niveis:
            self.niveis.append(nivel.upper())
    
    def adicionar_origem(self, origem: str):
        """Adiciona uma origem ao filtro."""
        if origem not in self.origens:
            self.origens.append(origem)
    
    def definir_periodo(self, data_inicio: datetime, data_fim: datetime):
        """Define o período do filtro."""
        self.data_inicio = data_inicio
        self.data_fim = data_fim
    
    def definir_usuario(self, usuario: str):
        """Define o usuário do filtro."""
        self.usuario = usuario
    
    def definir_sessao(self, sessao: str):
        """Define a sessão do filtro."""
        self.sessao = sessao
    
    def definir_texto_busca(self, texto: str):
        """Define o texto de busca."""
        self.texto_busca = texto.lower()
    
    def definir_limite(self, limite: int):
        """Define o limite de resultados."""
        self.limite = limite
    
    def limpar_filtros(self):
        """Limpa todos os filtros."""
        self.niveis = []
        self.origens = []
        self.data_inicio = None
        self.data_fim = None
        self.usuario = ""
        self.sessao = ""
        self.texto_busca = ""
        self.limite = 1000


class LogsAvancadoManager:
    """
    Gerenciador avançado de logs com banco de dados estruturado.
    """
    
    def __init__(self, settings):
        """
        Inicializa o gerenciador avançado de logs.
        
        Args:
            settings: Instância das configurações do sistema
        """
        self.settings = settings
        self.db_file = Path(settings.obter("database", "arquivo")).parent / "logs_avancado.db"
        self.db_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Cache de logs em memória para performance
        self.cache_logs = []
        self.cache_lock = threading.Lock()
        self.max_cache_size = 1000
        
        # Thread de limpeza automática
        self.thread_limpeza = None
        self._iniciar_limpeza_automatica()
        
        # Inicializar banco de dados
        self._inicializar_banco()
    
    def _inicializar_banco(self):
        """Inicializa o banco de dados de logs."""
        try:
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                
                # Tabela de logs estruturados
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS logs_detalhados (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        nivel TEXT NOT NULL,
                        origem TEXT NOT NULL,
                        mensagem TEXT NOT NULL,
                        detalhes TEXT,
                        usuario TEXT,
                        sessao TEXT,
                        ip TEXT,
                        INDEX idx_timestamp (timestamp),
                        INDEX idx_nivel (nivel),
                        INDEX idx_origem (origem),
                        INDEX idx_usuario (usuario),
                        INDEX idx_sessao (sessao)
                    )
                """)
                
                # Tabela de estatísticas
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS estatisticas_logs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        data DATE NOT NULL,
                        nivel TEXT NOT NULL,
                        origem TEXT NOT NULL,
                        quantidade INTEGER DEFAULT 0,
                        UNIQUE(data, nivel, origem)
                    )
                """)
                
                conn.commit()
                
        except Exception as e:
            print(f"Erro ao inicializar banco de logs: {e}")
    
    def _iniciar_limpeza_automatica(self):
        """Inicia thread de limpeza automática."""
        def limpeza_automatica():
            while True:
                try:
                    time.sleep(3600)  # Verificar a cada hora
                    self.limpar_logs_antigos()
                    self._atualizar_estatisticas()
                except Exception as e:
                    print(f"Erro na limpeza automática: {e}")
        
        self.thread_limpeza = threading.Thread(target=limpeza_automatica, daemon=True)
        self.thread_limpeza.start()
    
    def registrar_log(self, nivel: str, mensagem: str, origem: str = "sistema",
                     detalhes: Dict = None, usuario: str = "", sessao: str = "", ip: str = ""):
        """
        Registra um log estruturado.
        
        Args:
            nivel: Nível do log
            mensagem: Mensagem do log
            origem: Origem do log
            detalhes: Detalhes adicionais
            usuario: Usuário
            sessao: Sessão
            ip: Endereço IP
        """
        try:
            log = LogEstruturado(
                nivel=nivel,
                origem=origem,
                mensagem=mensagem,
                detalhes=detalhes or {},
                usuario=usuario,
                sessao=sessao,
                ip=ip
            )
            
            # Adicionar ao cache
            with self.cache_lock:
                self.cache_logs.append(log)
                
                # Limpar cache se necessário
                if len(self.cache_logs) > self.max_cache_size:
                    self._persistir_cache()
            
            # Persistir no banco em thread separada
            threading.Thread(target=self._persistir_log, args=(log,), daemon=True).start()
            
        except Exception as e:
            print(f"Erro ao registrar log: {e}")
    
    def _persistir_log(self, log: LogEstruturado):
        """Persiste um log no banco de dados."""
        try:
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT INTO logs_detalhados (timestamp, nivel, origem, mensagem, detalhes, usuario, sessao, ip)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    log.timestamp,
                    log.nivel,
                    log.origem,
                    log.mensagem,
                    json.dumps(log.detalhes, ensure_ascii=False),
                    log.usuario,
                    log.sessao,
                    log.ip
                ))
                
                log.id = cursor.lastrowid
                conn.commit()
                
        except Exception as e:
            print(f"Erro ao persistir log: {e}")
    
    def _persistir_cache(self):
        """Persiste logs do cache no banco."""
        try:
            with self.cache_lock:
                if not self.cache_logs:
                    return
                
                logs_para_persistir = self.cache_logs.copy()
                self.cache_logs.clear()
            
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                
                for log in logs_para_persistir:
                    cursor.execute("""
                        INSERT INTO logs_detalhados (timestamp, nivel, origem, mensagem, detalhes, usuario, sessao, ip)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        log.timestamp,
                        log.nivel,
                        log.origem,
                        log.mensagem,
                        json.dumps(log.detalhes, ensure_ascii=False),
                        log.usuario,
                        log.sessao,
                        log.ip
                    ))
                
                conn.commit()
                
        except Exception as e:
            print(f"Erro ao persistir cache: {e}")
    
    def buscar_logs(self, filtro: FiltroLogs = None) -> List[LogEstruturado]:
        """
        Busca logs com filtros.
        
        Args:
            filtro: Filtro de logs
            
        Returns:
            Lista de logs encontrados
        """
        try:
            # Persistir cache antes da busca
            self._persistir_cache()
            
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                
                # Construir query
                query = "SELECT * FROM logs_detalhados WHERE 1=1"
                params = []
                
                if filtro:
                    # Filtros de nível
                    if filtro.niveis:
                        placeholders = ",".join(["?"] * len(filtro.niveis))
                        query += f" AND nivel IN ({placeholders})"
                        params.extend(filtro.niveis)
                    
                    # Filtros de origem
                    if filtro.origens:
                        placeholders = ",".join(["?"] * len(filtro.origens))
                        query += f" AND origem IN ({placeholders})"
                        params.extend(filtro.origens)
                    
                    # Filtro de período
                    if filtro.data_inicio:
                        query += " AND timestamp >= ?"
                        params.append(filtro.data_inicio.isoformat())
                    
                    if filtro.data_fim:
                        query += " AND timestamp <= ?"
                        params.append(filtro.data_fim.isoformat())
                    
                    # Filtro de usuário
                    if filtro.usuario:
                        query += " AND usuario LIKE ?"
                        params.append(f"%{filtro.usuario}%")
                    
                    # Filtro de sessão
                    if filtro.sessao:
                        query += " AND sessao = ?"
                        params.append(filtro.sessao)
                    
                    # Filtro de texto
                    if filtro.texto_busca:
                        query += " AND (mensagem LIKE ? OR detalhes LIKE ?)"
                        params.extend([f"%{filtro.texto_busca}%", f"%{filtro.texto_busca}%"])
                
                # Ordenar e limitar
                query += " ORDER BY timestamp DESC"
                if filtro and filtro.limite:
                    query += f" LIMIT {filtro.limite}"
                
                cursor.execute(query, params)
                
                logs = []
                for row in cursor.fetchall():
                    log = LogEstruturado(
                        id=row[0],
                        timestamp=datetime.fromisoformat(row[1]),
                        nivel=row[2],
                        origem=row[3],
                        mensagem=row[4],
                        detalhes=json.loads(row[5]) if row[5] else {},
                        usuario=row[6] or "",
                        sessao=row[7] or "",
                        ip=row[8] or ""
                    )
                    logs.append(log)
                
                return logs
                
        except Exception as e:
            print(f"Erro ao buscar logs: {e}")
            return []
    
    def obter_estatisticas(self, data_inicio: datetime = None, data_fim: datetime = None) -> Dict[str, Any]:
        """
        Obtém estatísticas dos logs.
        
        Args:
            data_inicio: Data de início
            data_fim: Data de fim
            
        Returns:
            Dicionário com estatísticas
        """
        try:
            self._persistir_cache()
            
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                
                # Construir query
                query = "SELECT nivel, origem, COUNT(*) FROM logs_detalhados WHERE 1=1"
                params = []
                
                if data_inicio:
                    query += " AND timestamp >= ?"
                    params.append(data_inicio.isoformat())
                
                if data_fim:
                    query += " AND timestamp <= ?"
                    params.append(data_fim.isoformat())
                
                query += " GROUP BY nivel, origem"
                
                cursor.execute(query, params)
                
                estatisticas = {
                    "total_logs": 0,
                    "por_nivel": {},
                    "por_origem": {},
                    "por_nivel_origem": {}
                }
                
                for row in cursor.fetchall():
                    nivel, origem, quantidade = row
                    estatisticas["total_logs"] += quantidade
                    
                    # Por nível
                    if nivel not in estatisticas["por_nivel"]:
                        estatisticas["por_nivel"][nivel] = 0
                    estatisticas["por_nivel"][nivel] += quantidade
                    
                    # Por origem
                    if origem not in estatisticas["por_origem"]:
                        estatisticas["por_origem"][origem] = 0
                    estatisticas["por_origem"][origem] += quantidade
                    
                    # Por nível e origem
                    chave = f"{nivel}_{origem}"
                    if chave not in estatisticas["por_nivel_origem"]:
                        estatisticas["por_nivel_origem"][chave] = 0
                    estatisticas["por_nivel_origem"][chave] += quantidade
                
                return estatisticas
                
        except Exception as e:
            print(f"Erro ao obter estatísticas: {e}")
            return {}
    
    def limpar_logs_antigos(self, dias: int = 30):
        """
        Remove logs antigos.
        
        Args:
            dias: Número de dias para manter
        """
        try:
            data_limite = datetime.now() - timedelta(days=dias)
            
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                
                cursor.execute("DELETE FROM logs_detalhados WHERE timestamp < ?", (data_limite.isoformat(),))
                
                conn.commit()
                
        except Exception as e:
            print(f"Erro ao limpar logs antigos: {e}")
    
    def _atualizar_estatisticas(self):
        """Atualiza estatísticas diárias."""
        try:
            hoje = datetime.now().date()
            
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                
                # Obter estatísticas do dia
                cursor.execute("""
                    SELECT nivel, origem, COUNT(*) 
                    FROM logs_detalhados 
                    WHERE DATE(timestamp) = ?
                    GROUP BY nivel, origem
                """, (hoje.isoformat(),))
                
                for row in cursor.fetchall():
                    nivel, origem, quantidade = row
                    
                    cursor.execute("""
                        INSERT OR REPLACE INTO estatisticas_logs (data, nivel, origem, quantidade)
                        VALUES (?, ?, ?, ?)
                    """, (hoje.isoformat(), nivel, origem, quantidade))
                
                conn.commit()
                
        except Exception as e:
            print(f"Erro ao atualizar estatísticas: {e}")
    
    def exportar_logs(self, formato: str = "csv", filtro: FiltroLogs = None, 
                     caminho_destino: str = None) -> str:
        """
        Exporta logs para arquivo.
        
        Args:
            formato: Formato de exportação (csv, json, txt)
            filtro: Filtro de logs
            caminho_destino: Caminho do arquivo de destino
            
        Returns:
            Caminho do arquivo exportado
        """
        try:
            logs = self.buscar_logs(filtro)
            
            if not caminho_destino:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                caminho_destino = f"logs_export_{timestamp}.{formato}"
            
            if formato.lower() == "csv":
                self._exportar_csv(logs, caminho_destino)
            elif formato.lower() == "json":
                self._exportar_json(logs, caminho_destino)
            elif formato.lower() == "txt":
                self._exportar_txt(logs, caminho_destino)
            elif formato.lower() == "zip":
                self._exportar_zip(logs, caminho_destino)
            else:
                raise ValueError(f"Formato não suportado: {formato}")
            
            return caminho_destino
            
        except Exception as e:
            print(f"Erro ao exportar logs: {e}")
            return ""
    
    def _exportar_csv(self, logs: List[LogEstruturado], caminho: str):
        """Exporta logs para CSV."""
        with open(caminho, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['ID', 'Timestamp', 'Nível', 'Origem', 'Mensagem', 'Usuário', 'Sessão', 'IP', 'Detalhes'])
            
            for log in logs:
                writer.writerow([
                    log.id,
                    log.timestamp.isoformat(),
                    log.nivel,
                    log.origem,
                    log.mensagem,
                    log.usuario,
                    log.sessao,
                    log.ip,
                    json.dumps(log.detalhes, ensure_ascii=False)
                ])
    
    def _exportar_json(self, logs: List[LogEstruturado], caminho: str):
        """Exporta logs para JSON."""
        dados = [log.to_dict() for log in logs]
        with open(caminho, 'w', encoding='utf-8') as f:
            json.dump(dados, f, indent=2, ensure_ascii=False)
    
    def _exportar_txt(self, logs: List[LogEstruturado], caminho: str):
        """Exporta logs para TXT."""
        with open(caminho, 'w', encoding='utf-8') as f:
            for log in logs:
                f.write(f"[{log.timestamp}] {log.nivel} - {log.origem}: {log.mensagem}\n")
                if log.detalhes:
                    f.write(f"  Detalhes: {json.dumps(log.detalhes, ensure_ascii=False)}\n")
                f.write("\n")
    
    def _exportar_zip(self, logs: List[LogEstruturado], caminho: str):
        """Exporta logs para ZIP com múltiplos formatos."""
        with zipfile.ZipFile(caminho, 'w') as zipf:
            # CSV
            csv_path = caminho.replace('.zip', '.csv')
            self._exportar_csv(logs, csv_path)
            zipf.write(csv_path, 'logs.csv')
            os.remove(csv_path)
            
            # JSON
            json_path = caminho.replace('.zip', '.json')
            self._exportar_json(logs, json_path)
            zipf.write(json_path, 'logs.json')
            os.remove(json_path)
            
            # TXT
            txt_path = caminho.replace('.zip', '.txt')
            self._exportar_txt(logs, txt_path)
            zipf.write(txt_path, 'logs.txt')
            os.remove(txt_path)
    
    def obter_niveis_disponiveis(self) -> List[str]:
        """Obtém níveis de log disponíveis."""
        try:
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT DISTINCT nivel FROM logs_detalhados ORDER BY nivel")
                return [row[0] for row in cursor.fetchall()]
        except Exception as e:
            print(f"Erro ao obter níveis: {e}")
            return []
    
    def obter_origens_disponiveis(self) -> List[str]:
        """Obtém origens de log disponíveis."""
        try:
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT DISTINCT origem FROM logs_detalhados ORDER BY origem")
                return [row[0] for row in cursor.fetchall()]
        except Exception as e:
            print(f"Erro ao obter origens: {e}")
            return []
    
    def obter_usuarios_disponiveis(self) -> List[str]:
        """Obtém usuários disponíveis."""
        try:
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT DISTINCT usuario FROM logs_detalhados WHERE usuario != '' ORDER BY usuario")
                return [row[0] for row in cursor.fetchall()]
        except Exception as e:
            print(f"Erro ao obter usuários: {e}")
            return [] 