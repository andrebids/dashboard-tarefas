# -*- coding: utf-8 -*-
"""
Módulo de gestão da base de dados PostgreSQL do Planka.
Gerencia criação, backup, restauração, upload e substituição da base de dados.
"""

import os
import subprocess
import time
import psycopg2
import zipfile
import shutil
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import threading

# Importar configuração segura
from config.database_config import DatabaseConfig


class PlankaDatabaseManager:
    """
    Gerenciador da base de dados PostgreSQL do Planka.
    Controla criação, backup, restauração e gestão da base de dados.
    """
    
    def __init__(self, settings):
        """
        Inicializa o gerenciador da base de dados do Planka.
        
        Args:
            settings: Instância das configurações do sistema
        """
        self.settings = settings
        self.planka_dir = Path(settings.obter("planka", "diretorio"))
        self.backup_dir = self.planka_dir / "backups"
        self.backup_dir.mkdir(exist_ok=True)
        
        # Configuração segura da base de dados
        try:
            config_dir = settings.obter_diretorio_config()
        except:
            # Fallback para diretório padrão
            config_dir = Path(__file__).parent.parent / "config"
        
        self.db_config = DatabaseConfig(config_dir)
        
        # Status da conexão
        self.connection = None
        self.is_connected = False
        
    def verificar_conectividade(self) -> Dict[str, bool]:
        """
        Verifica a conectividade com a base de dados PostgreSQL.
        
        Returns:
            Dict com status de conectividade
        """
        status = {
            "postgres_running": False,
            "database_exists": False,
            "connection_ok": False,
            "tables_exist": False,
            "config_valid": False
        }
        
        try:
            # Verificar se a configuração está válida
            status["config_valid"] = self.db_config.validate_config()
            
            if not status["config_valid"]:
                return status
            
            # Verificar se o container PostgreSQL está rodando
            result = subprocess.run(
                ["docker", "ps", "--filter", "name=postgres", "--format", "{{.Status}}"],
                capture_output=True,
                text=True, encoding='utf-8', errors='replace'
            )
            status["postgres_running"] = "Up" in result.stdout
            
            if status["postgres_running"]:
                # Tentar conectar na base de dados via docker exec
                try:
                    config = self.db_config.get_database_config()
                    
                    # Verificar se a base existe
                    result = subprocess.run(
                        ["docker-compose", "exec", "-T", "postgres", "psql", "-U", config["user"], 
                         "-d", "postgres", "-c", f"SELECT 1 FROM pg_database WHERE datname = '{config['database']}'"],
                        cwd=self.planka_dir,
                        capture_output=True,
                        text=True, encoding='utf-8', errors='replace'
                    )
                    status["database_exists"] = result.returncode == 0 and "1 row" in result.stdout
                    
                    if status["database_exists"]:
                        # Verificar se as tabelas existem
                        result = subprocess.run(
                            ["docker-compose", "exec", "-T", "postgres", "psql", "-U", config["user"], 
                             "-d", config["database"], "-c", "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'user_account'"],
                            cwd=self.planka_dir,
                            capture_output=True,
                            text=True,
                            timeout=10
                        )
                        status["tables_exist"] = result.returncode == 0 and "1" in result.stdout
                        status["connection_ok"] = True
                        
                except subprocess.TimeoutExpired:
                    print("Timeout ao verificar conectividade")
                except Exception as e:
                    print(f"Erro ao verificar conectividade: {e}")
                    
        except Exception as e:
            print(f"Erro ao verificar conectividade: {e}")
            
        return status
    
    def obter_estrutura_base(self) -> Dict:
        """
        Obtém a estrutura completa da base de dados.
        
        Returns:
            Dict com informações da estrutura
        """
        estrutura = {
            "tabelas": [],
            "total_tabelas": 0,
            "total_registros": 0,
            "tamanho_base": "0 MB"
        }
        
        try:
            config = self.db_config.get_database_config()
            
            # Listar tabelas via docker exec
            result = subprocess.run(
                ["docker-compose", "exec", "-T", "postgres", "psql", "-U", config["user"], 
                 "-d", config["database"], "-c", """
                 SELECT table_name, 
                        (SELECT COUNT(*) FROM information_schema.columns 
                         WHERE table_name = t.table_name) as colunas
                 FROM information_schema.tables t
                 WHERE table_schema = 'public'
                 ORDER BY table_name
                 """],
                cwd=self.planka_dir,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                linhas = result.stdout.strip().split('\n')[2:]  # Pular cabeçalho
                tabelas = []
                total_registros = 0
                
                for linha in linhas:
                    if linha.strip() and '|' in linha:
                        partes = linha.split('|')
                        if len(partes) >= 2:
                            nome_tabela = partes[0].strip()
                            num_colunas = int(partes[1].strip())
                            
                            # Contar registros na tabela
                            try:
                                result_count = subprocess.run(
                                    ["docker-compose", "exec", "-T", "postgres", "psql", "-U", config["user"], 
                                     "-d", config["database"], "-c", f"SELECT COUNT(*) FROM {nome_tabela}"],
                                    cwd=self.planka_dir,
                                    capture_output=True,
                                    text=True,
                                    timeout=10
                                )
                                if result_count.returncode == 0:
                                    num_registros = int(result_count.stdout.strip().split('\n')[2])
                                    total_registros += num_registros
                                else:
                                    num_registros = 0
                            except:
                                num_registros = 0
                            
                            tabelas.append({
                                "nome": nome_tabela,
                                "colunas": num_colunas,
                                "registros": num_registros
                            })
                
                estrutura["tabelas"] = tabelas
                estrutura["total_tabelas"] = len(tabelas)
                estrutura["total_registros"] = total_registros
                
                # Obter tamanho da base de dados
                result_size = subprocess.run(
                    ["docker-compose", "exec", "-T", "postgres", "psql", "-U", config["user"], 
                     "-d", config["database"], "-c", "SELECT pg_size_pretty(pg_database_size(current_database()))"],
                    cwd=self.planka_dir,
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                if result_size.returncode == 0:
                    estrutura["tamanho_base"] = result_size.stdout.strip().split('\n')[2]
                else:
                    estrutura["tamanho_base"] = "N/A"
                    
        except Exception as e:
            print(f"Erro ao obter estrutura: {e}")
            
        return estrutura
    
    def criar_base_dados(self) -> Tuple[bool, str]:
        """
        Cria uma nova base de dados PostgreSQL para o Planka.
        
        Returns:
            (sucesso, mensagem)
        """
        try:
            # Verificar se PostgreSQL está rodando
            status = self.verificar_conectividade()
            if not status["postgres_running"]:
                return False, "PostgreSQL não está rodando"
            
            if not status["config_valid"]:
                return False, "Configuração da base de dados inválida"
            
            # Verificar se a base já existe
            if status["database_exists"]:
                return False, f"Base de dados já existe"
            
            config = self.db_config.get_database_config()
            
            # Criar base de dados via docker exec
            result = subprocess.run(
                ["docker-compose", "exec", "-T", "postgres", "createdb", "-U", config["user"], config["database"]],
                cwd=self.planka_dir,
                capture_output=True,
                text=True, encoding='utf-8', errors='replace'
            )
            
            if result.returncode == 0:
                return True, f"Base de dados '{config['database']}' criada com sucesso"
            else:
                return False, f"Erro ao criar base de dados: {result.stderr}"
            
        except Exception as e:
            return False, f"Erro ao criar base de dados: {str(e)}"
    
    def inicializar_base_dados(self) -> Tuple[bool, str]:
        """
        Inicializa a base de dados com as migrações do Planka.
        
        Returns:
            (sucesso, mensagem)
        """
        try:
            # Verificar se a base existe
            status = self.verificar_conectividade()
            if not status["database_exists"]:
                return False, "Base de dados não existe"
            
            # Executar migrações via docker-compose
            result = subprocess.run(
                ["docker-compose", "exec", "-T", "planka", "npm", "run", "db:migrate"],
                cwd=self.planka_dir,
                capture_output=True,
                text=True, encoding='utf-8', errors='replace'
            )
            
            if result.returncode == 0:
                return True, "Base de dados inicializada com sucesso"
            else:
                return False, f"Erro ao inicializar: {result.stderr}"
                
        except Exception as e:
            return False, f"Erro ao inicializar base de dados: {str(e)}"
    

    
    def backup_completo(self, nome_backup: str = None) -> Tuple[bool, str]:
        """
        Faz backup completo da base de dados.
        
        Args:
            nome_backup: Nome personalizado para o backup
            
        Returns:
            (sucesso, mensagem)
        """
        try:
            # Verificar se a base existe
            status = self.verificar_conectividade()
            if not status["database_exists"]:
                return False, "Base de dados não existe"
            
            # Gerar nome do backup
            if not nome_backup:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                nome_backup = f"planka_backup_{timestamp}"
            
            backup_file = self.backup_dir / f"{nome_backup}.sql"
            
            config = self.db_config.get_database_config()
            
            # Fazer backup usando pg_dump via docker exec
            result = subprocess.run(
                ["docker-compose", "exec", "-T", "postgres", "pg_dump", 
                 "-U", config["user"], "-d", config["database"], "-f", f"/tmp/{nome_backup}.sql"],
                cwd=self.planka_dir,
                capture_output=True,
                text=True, encoding='utf-8', errors='replace'
            )
            
            if result.returncode == 0:
                # Copiar arquivo do container para o host
                result_copy = subprocess.run(
                    ["docker", "cp", f"planka-personalizado-postgres-1:/tmp/{nome_backup}.sql", str(backup_file)],
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                
                if result_copy.returncode == 0:
                    return True, f"Backup criado: {backup_file.name}"
                else:
                    return False, f"Erro ao copiar backup: {result_copy.stderr}"
            else:
                return False, f"Erro ao fazer backup: {result.stderr}"
                
        except Exception as e:
            return False, f"Erro ao fazer backup: {str(e)}"
    
    def comprimir_backup(self, arquivo_backup: str) -> Tuple[bool, str]:
        """
        Comprime um arquivo de backup.
        
        Args:
            arquivo_backup: Nome do arquivo de backup
            
        Returns:
            (sucesso, mensagem)
        """
        try:
            backup_path = self.backup_dir / arquivo_backup
            if not backup_path.exists():
                return False, "Arquivo de backup não encontrado"
            
            # Criar arquivo ZIP
            zip_path = backup_path.with_suffix('.zip')
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                zipf.write(backup_path, backup_path.name)
            
            # Remover arquivo original
            backup_path.unlink()
            
            return True, f"Backup comprimido: {zip_path.name}"
            
        except Exception as e:
            return False, f"Erro ao comprimir backup: {str(e)}"
    
    def listar_backups(self) -> List[Dict]:
        """
        Lista todos os backups disponíveis.
        
        Returns:
            Lista de backups com informações
        """
        backups = []
        
        try:
            for arquivo in self.backup_dir.glob("*.sql"):
                stat = arquivo.stat()
                backups.append({
                    "nome": arquivo.name,
                    "tamanho": arquivo.stat().st_size,
                    "data_criacao": datetime.fromtimestamp(stat.st_mtime),
                    "tipo": "SQL"
                })
            
            for arquivo in self.backup_dir.glob("*.zip"):
                stat = arquivo.stat()
                backups.append({
                    "nome": arquivo.name,
                    "tamanho": arquivo.stat().st_size,
                    "data_criacao": datetime.fromtimestamp(stat.st_mtime),
                    "tipo": "ZIP"
                })
            
            # Ordenar por data de criação (mais recente primeiro)
            backups.sort(key=lambda x: x["data_criacao"], reverse=True)
            
        except Exception as e:
            print(f"Erro ao listar backups: {e}")
            
        return backups
    
    def validar_backup(self, arquivo_backup: str) -> Tuple[bool, str]:
        """
        Valida a integridade de um arquivo de backup.
        
        Args:
            arquivo_backup: Nome do arquivo de backup
            
        Returns:
            (sucesso, mensagem)
        """
        try:
            backup_path = self.backup_dir / arquivo_backup
            
            if not backup_path.exists():
                return False, "Arquivo de backup não encontrado"
            
            # Verificar se é um arquivo SQL válido
            with open(backup_path, 'r', encoding='utf-8') as f:
                conteudo = f.read(1000)  # Ler primeiros 1000 caracteres
                
                if "PostgreSQL database dump" in conteudo:
                    return True, "Backup válido"
                else:
                    return False, "Arquivo não parece ser um backup PostgreSQL válido"
                    
        except Exception as e:
            return False, f"Erro ao validar backup: {str(e)}"
    
    def restaurar_backup_arquivo(self, arquivo_backup: str, modo_teste: bool = False) -> Tuple[bool, str]:
        """
        Restaura um backup de um arquivo específico (caminho completo).
        
        Args:
            arquivo_backup: Caminho completo do arquivo de backup
            modo_teste: Se True, restaura em uma base de teste
            
        Returns:
            (sucesso, mensagem)
        """
        try:
            backup_path = Path(arquivo_backup)
            
            if not backup_path.exists():
                return False, "Arquivo de backup não encontrado"
            
            # Verificar se é um arquivo SQL válido
            if not backup_path.suffix.lower() in ['.sql', '.backup', '.gz']:
                return False, "Arquivo deve ser .sql, .backup ou .gz"
            
            config = self.db_config.get_database_config()
            
            # Nome da base de dados de destino
            db_destino = f"{config['database']}_test" if modo_teste else config["database"]
            
            # Se for modo teste, criar a base de teste primeiro
            if modo_teste:
                result_create = subprocess.run(
                    ["docker-compose", "exec", "-T", "postgres", "createdb", 
                     "-U", config["user"], db_destino],
                    cwd=self.planka_dir,
                    capture_output=True,
                    text=True, encoding='utf-8', errors='replace'
                )
                
                if result_create.returncode != 0 and "already exists" not in result_create.stderr:
                    return False, f"Erro ao criar base de teste: {result_create.stderr}"
            
            # Parar o Planka se não for modo teste
            if not modo_teste:
                subprocess.run(["docker-compose", "down"], cwd=self.planka_dir, encoding='utf-8', errors='replace')
            
            # Copiar arquivo para o container
            result_copy = subprocess.run(
                ["docker", "cp", str(backup_path), f"planka-personalizado-postgres-1:/tmp/{backup_path.name}"],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result_copy.returncode != 0:
                return False, f"Erro ao copiar backup: {result_copy.stderr}"
            
            # Restaurar backup
            if backup_path.suffix.lower() == '.gz':
                # Arquivo comprimido - descomprimir primeiro
                result_restore = subprocess.run(
                    ["docker-compose", "exec", "-T", "postgres", "bash", "-c", 
                     f"gunzip -c /tmp/{backup_path.name} | psql -U {config['user']} -d {db_destino}"],
                    cwd=self.planka_dir,
                    capture_output=True,
                    text=True, encoding='utf-8', errors='replace'
                )
            else:
                # Arquivo SQL normal
                result_restore = subprocess.run(
                    ["docker-compose", "exec", "-T", "postgres", "psql", 
                     "-U", config["user"], "-d", db_destino, "-f", f"/tmp/{backup_path.name}"],
                    cwd=self.planka_dir,
                    capture_output=True,
                    text=True, encoding='utf-8', errors='replace'
                )
            
            if result_restore.returncode == 0:
                if not modo_teste:
                    # Reiniciar o Planka
                    subprocess.run(["docker-compose", "up", "-d"], cwd=self.planka_dir, encoding='utf-8', errors='replace')
                
                return True, f"Backup restaurado com sucesso em '{db_destino}'"
            else:
                return False, f"Erro ao restaurar backup: {result_restore.stderr}"
                
        except Exception as e:
            return False, f"Erro ao restaurar backup: {str(e)}"
    
    def restaurar_backup(self, arquivo_backup: str, modo_teste: bool = False) -> Tuple[bool, str]:
        """
        Restaura um backup da base de dados.
        
        Args:
            arquivo_backup: Nome do arquivo de backup
            modo_teste: Se True, restaura em uma base de teste
            
        Returns:
            (sucesso, mensagem)
        """
        try:
            backup_path = self.backup_dir / arquivo_backup
            
            if not backup_path.exists():
                return False, "Arquivo de backup não encontrado"
            
            # Validar backup
            valido, msg = self.validar_backup(arquivo_backup)
            if not valido:
                return False, f"Backup inválido: {msg}"
            
            config = self.db_config.get_database_config()
            
            # Nome da base de dados de destino
            db_destino = f"{config['database']}_test" if modo_teste else config["database"]
            
            # Parar o Planka se não for modo teste
            if not modo_teste:
                subprocess.run(["docker-compose", "down"], cwd=self.planka_dir, encoding='utf-8', errors='replace')
            
            # Copiar arquivo para o container
            result_copy = subprocess.run(
                ["docker", "cp", str(backup_path), f"planka-personalizado-postgres-1:/tmp/{arquivo_backup}"],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result_copy.returncode != 0:
                return False, f"Erro ao copiar backup: {result_copy.stderr}"
            
            # Restaurar backup
            result_restore = subprocess.run(
                ["docker-compose", "exec", "-T", "postgres", "psql", 
                 "-U", config["user"], "-d", db_destino, "-f", f"/tmp/{arquivo_backup}"],
                cwd=self.planka_dir,
                capture_output=True,
                text=True, encoding='utf-8', errors='replace'
            )
            
            if result_restore.returncode == 0:
                if not modo_teste:
                    # Reiniciar o Planka
                    subprocess.run(["docker-compose", "up", "-d"], cwd=self.planka_dir, encoding='utf-8', errors='replace')
                
                return True, f"Backup restaurado com sucesso em '{db_destino}'"
            else:
                return False, f"Erro ao restaurar backup: {result_restore.stderr}"
                
        except Exception as e:
            return False, f"Erro ao restaurar backup: {str(e)}"
    
    def upload_backup(self, arquivo_origem: str) -> Tuple[bool, str]:
        """
        Faz upload de um arquivo de backup.
        
        Args:
            arquivo_origem: Caminho do arquivo de backup
            
        Returns:
            (sucesso, mensagem)
        """
        try:
            origem_path = Path(arquivo_origem)
            
            if not origem_path.exists():
                return False, "Arquivo de origem não encontrado"
            
            # Validar se é um arquivo de backup
            if not (origem_path.suffix.lower() in ['.sql', '.zip']):
                return False, "Arquivo deve ser .sql ou .zip"
            
            # Copiar para diretório de backups
            destino_path = self.backup_dir / origem_path.name
            
            # Se já existe, adicionar timestamp
            if destino_path.exists():
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                nome_base = destino_path.stem
                extensao = destino_path.suffix
                destino_path = self.backup_dir / f"{nome_base}_{timestamp}{extensao}"
            
            shutil.copy2(origem_path, destino_path)
            
            return True, f"Upload realizado: {destino_path.name}"
            
        except Exception as e:
            return False, f"Erro ao fazer upload: {str(e)}"
    
    def substituir_base(self, arquivo_backup: str) -> Tuple[bool, str]:
        """
        Substitui a base de dados atual por um backup.
        
        Args:
            arquivo_backup: Nome do arquivo de backup
            
        Returns:
            (sucesso, mensagem)
        """
        try:
            # Fazer backup da base atual antes da substituição
            sucesso_backup, msg_backup = self.backup_atual()
            if not sucesso_backup:
                return False, f"Erro ao fazer backup da base atual: {msg_backup}"
            
            # Restaurar o backup
            sucesso_restore, msg_restore = self.restaurar_backup(arquivo_backup, modo_teste=False)
            if not sucesso_restore:
                return False, f"Erro ao restaurar backup: {msg_restore}"
            
            return True, f"Base de dados substituída com sucesso. Backup anterior: {msg_backup}"
            
        except Exception as e:
            return False, f"Erro ao substituir base: {str(e)}"
    
    def backup_atual(self) -> Tuple[bool, str]:
        """
        Faz backup da base de dados atual antes de uma substituição.
        
        Returns:
            (sucesso, mensagem)
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            nome_backup = f"backup_antes_substituicao_{timestamp}"
            
            return self.backup_completo(nome_backup)
            
        except Exception as e:
            return False, f"Erro ao fazer backup atual: {str(e)}"
    
    def conectar_editor(self, editor: str = "pgadmin") -> Tuple[bool, str]:
        """
        Conecta ao editor de base de dados (pgAdmin no navegador).
        
        Args:
            editor: Tipo de editor (apenas pgadmin suportado)
            
        Returns:
            (sucesso, mensagem)
        """
        try:
            if editor == "pgadmin":
                return self._abrir_pgadmin()
            
            else:
                return False, f"Editor '{editor}' não suportado"
                
        except Exception as e:
            return False, f"Erro ao conectar editor: {str(e)}"
    
    def _abrir_pgadmin(self) -> Tuple[bool, str]:
        """Abre o pgAdmin no navegador."""
        try:
            # Verificar se o pgAdmin está rodando
            pgadmin_status = self._verificar_pgadmin_rodando()
            
            if not pgadmin_status["rodando"]:
                # Tentar iniciar o pgAdmin
                sucesso_inicio = self._iniciar_pgadmin()
                if not sucesso_inicio:
                    return False, "pgAdmin não está rodando. Use o arquivo docker-compose-pgadmin.yml para incluir o pgAdmin."
            
            # Aguardar um pouco para o pgAdmin inicializar
            time.sleep(2)
            
            # Abrir pgAdmin no navegador
            import webbrowser
            webbrowser.open("http://localhost:5050")
            return True, "pgAdmin aberto no navegador em http://localhost:5050"
            
        except Exception as e:
            return False, f"Erro ao abrir pgAdmin: {str(e)}"
    

    
    def _verificar_pgadmin_rodando(self) -> Dict[str, any]:
        """
        Verifica se o pgAdmin está rodando.
        
        Returns:
            Dict com status do pgAdmin
        """
        try:
            # Verificar se o container pgAdmin está rodando
            result = subprocess.run(
                ["docker", "ps", "--filter", "name=pgadmin", "--format", "{{.Status}}"],
                capture_output=True,
                text=True, encoding='utf-8', errors='replace'
            )
            
            rodando = "Up" in result.stdout
            
            return {
                "rodando": rodando,
                "status": result.stdout.strip() if rodando else "Não encontrado"
            }
            
        except Exception as e:
            return {
                "rodando": False,
                "status": f"Erro ao verificar: {str(e)}"
            }
    
    def _iniciar_pgadmin(self) -> bool:
        """
        Tenta iniciar o pgAdmin usando o docker-compose-pgadmin.yml.
        
        Returns:
            True se conseguiu iniciar, False caso contrário
        """
        try:
            # Verificar se o arquivo docker-compose-pgadmin.yml existe
            compose_file = self.planka_dir / "docker-compose-pgadmin.yml"
            
            if not compose_file.exists():
                return False
            
            # Tentar iniciar apenas o pgAdmin
            result = subprocess.run(
                ["docker-compose", "-f", str(compose_file), "up", "-d", "pgadmin"],
                cwd=self.planka_dir,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            return result.returncode == 0
            
        except Exception as e:
            print(f"Erro ao iniciar pgAdmin: {str(e)}")
            return False
    
    def executar_query(self, query: str) -> Tuple[bool, str, List]:
        """
        Executa uma query SQL na base de dados.
        
        Args:
            query: Query SQL a executar
            
        Returns:
            (sucesso, mensagem, resultados)
        """
        try:
            config = self.db_config.get_database_config()
            
            # Executar query via docker exec
            result = subprocess.run(
                ["docker-compose", "exec", "-T", "postgres", "psql", 
                 "-U", config["user"], "-d", config["database"], "-c", query],
                cwd=self.planka_dir,
                capture_output=True,
                text=True, encoding='utf-8', errors='replace'
            )
            
            if result.returncode == 0:
                return True, "Query executada com sucesso", result.stdout
            else:
                return False, f"Erro ao executar query: {result.stderr}", []
                
        except Exception as e:
            return False, f"Erro ao executar query: {str(e)}", []
    
    def obter_informacoes(self) -> Dict:
        """
        Obtém informações completas da base de dados.
        
        Returns:
            Dict com informações da base de dados
        """
        info = {
            "conectividade": self.verificar_conectividade(),
            "estrutura": self.obter_estrutura_base(),
            "backups": self.listar_backups(),
            "config_info": self.db_config.get_config_info(),
            "timestamp": datetime.now().isoformat()
        }
        
        return info
    
    def configurar_credenciais(self):
        """
        Configura as credenciais da base de dados de forma segura.
        """
        self.db_config.setup_environment_variable()
    
 