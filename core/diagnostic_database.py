# -*- coding: utf-8 -*-
"""
Módulo de diagnóstico da base de dados PostgreSQL do Planka.
Verifica conectividade, configuração e estado dos containers.
"""

import subprocess
import json
import time
from pathlib import Path
from typing import Dict, List, Tuple
import psycopg2

# Importar configuração segura
from config.database_config import DatabaseConfig


class DatabaseDiagnostic:
    """
    Diagnóstico completo da base de dados PostgreSQL do Planka.
    """
    
    def __init__(self, settings):
        """
        Inicializa o diagnóstico da base de dados.
        
        Args:
            settings: Instância das configurações do sistema
        """
        self.settings = settings
        self.planka_dir = Path(settings.obter("planka", "diretorio"))
        
        # Configuração segura da base de dados
        try:
            config_dir = settings.obter_diretorio_config()
        except:
            # Fallback para diretório padrão
            config_dir = Path(__file__).parent.parent / "config"
        
        self.db_config = DatabaseConfig(config_dir)
    
    def executar_diagnostico_completo(self) -> Dict:
        """
        Executa diagnóstico completo da base de dados.
        
        Returns:
            Dict com resultados do diagnóstico
        """
        resultado = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "docker": self._verificar_docker(),
            "containers": self._verificar_containers(),
            "configuracao": self._verificar_configuracao(),
            "conectividade": self._verificar_conectividade(),
            "estrutura": self._verificar_estrutura_base(),
            "pgadmin": self._verificar_pgadmin(),
            "problemas": [],
            "recomendacoes": []
        }
        
        # Analisar problemas
        self._analisar_problemas(resultado)
        
        # Gerar recomendações
        self._gerar_recomendacoes(resultado)
        
        return resultado
    
    def _verificar_docker(self) -> Dict:
        """Verifica se o Docker está instalado e rodando."""
        resultado = {
            "instalado": False,
            "rodando": False,
            "versao": None,
            "erro": None
        }
        
        try:
            # Verificar se Docker está instalado
            result = subprocess.run(
                ["docker", "--version"],
                capture_output=True,
                text=True, encoding='utf-8', errors='replace'
            )
            
            if result.returncode == 0:
                resultado["instalado"] = True
                resultado["versao"] = result.stdout.strip()
                
                # Verificar se Docker está rodando
                result = subprocess.run(
                    ["docker", "info"],
                    capture_output=True,
                    text=True, encoding='utf-8', errors='replace'
                )
                
                if result.returncode == 0:
                    resultado["rodando"] = True
                else:
                    resultado["erro"] = "Docker não está rodando"
            else:
                resultado["erro"] = "Docker não está instalado"
                
        except subprocess.TimeoutExpired:
            resultado["erro"] = "Timeout ao verificar Docker"
        except Exception as e:
            resultado["erro"] = str(e)
        
        return resultado
    
    def _verificar_containers(self) -> Dict:
        """Verifica o estado dos containers Docker."""
        resultado = {
            "postgres": {"rodando": False, "status": None, "erro": None},
            "planka": {"rodando": False, "status": None, "erro": None},
            "pgadmin": {"rodando": False, "status": None, "erro": None}
        }
        
        try:
            # Listar containers
            result = subprocess.run(
                ["docker", "ps", "--format", "{{.Names}}:{{.Status}}"],
                capture_output=True,
                text=True, encoding='utf-8', errors='replace'
            )
            
            if result.returncode == 0:
                containers = result.stdout.strip().split('\n')
                
                for container in containers:
                    if container:
                        name, status = container.split(':', 1)
                        
                        if 'postgres' in name:
                            resultado["postgres"]["rodando"] = "Up" in status
                            resultado["postgres"]["status"] = status
                        elif 'planka' in name:
                            resultado["planka"]["rodando"] = "Up" in status
                            resultado["planka"]["status"] = status
                        elif 'pgadmin' in name:
                            resultado["pgadmin"]["rodando"] = "Up" in status
                            resultado["pgadmin"]["status"] = status
            else:
                resultado["postgres"]["erro"] = "Erro ao listar containers"
                resultado["planka"]["erro"] = "Erro ao listar containers"
                resultado["pgadmin"]["erro"] = "Erro ao listar containers"
                
        except subprocess.TimeoutExpired:
            resultado["postgres"]["erro"] = "Timeout ao verificar containers"
            resultado["planka"]["erro"] = "Timeout ao verificar containers"
            resultado["pgadmin"]["erro"] = "Timeout ao verificar containers"
        except Exception as e:
            resultado["postgres"]["erro"] = str(e)
            resultado["planka"]["erro"] = str(e)
            resultado["pgadmin"]["erro"] = str(e)
        
        return resultado
    
    def _verificar_configuracao(self) -> Dict:
        """Verifica a configuração da base de dados."""
        resultado = {
            "arquivo_existe": False,
            "config_valida": False,
            "campos": {},
            "erro": None
        }
        
        try:
            # Verificar se arquivo de configuração existe
            config_file = self.db_config.config_file
            resultado["arquivo_existe"] = config_file.exists()
            
            if resultado["arquivo_existe"]:
                # Obter informações da configuração
                info = self.db_config.get_config_info()
                resultado["config_valida"] = info["valid"]
                resultado["campos"] = {
                    "host": info["host"],
                    "port": info["port"],
                    "database": info["database"],
                    "user": info["user"],
                    "password_set": info["password_set"],
                    "use_environment": info["use_environment"],
                    "encrypted": info["encrypted"]
                }
            else:
                resultado["erro"] = "Arquivo de configuração não encontrado"
                
        except Exception as e:
            resultado["erro"] = str(e)
        
        return resultado
    
    def _verificar_conectividade(self) -> Dict:
        """Verifica conectividade com a base de dados."""
        resultado = {
            "postgres_acessivel": False,
            "base_existe": False,
            "tabelas_existem": False,
            "erro": None
        }
        
        try:
            config = self.db_config.get_database_config()
            
            # Verificar se PostgreSQL está acessível
            result = subprocess.run(
                ["docker-compose", "exec", "-T", "postgres", "pg_isready", "-U", config["user"]],
                cwd=self.planka_dir,
                capture_output=True,
                text=True, encoding='utf-8', errors='replace'
            )
            
            resultado["postgres_acessivel"] = result.returncode == 0
            
            if resultado["postgres_acessivel"]:
                # Verificar se base existe
                result = subprocess.run(
                    ["docker-compose", "exec", "-T", "postgres", "psql", "-U", config["user"], 
                     "-d", "postgres", "-c", f"SELECT 1 FROM pg_database WHERE datname = '{config['database']}'"],
                    cwd=self.planka_dir,
                    capture_output=True,
                    text=True, encoding='utf-8', errors='replace'
                )
                
                resultado["base_existe"] = result.returncode == 0 and "1 row" in result.stdout
                
                if resultado["base_existe"]:
                    # Verificar se tabelas existem
                    result = subprocess.run(
                        ["docker-compose", "exec", "-T", "postgres", "psql", "-U", config["user"], 
                         "-d", config["database"], "-c", "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public'"],
                        cwd=self.planka_dir,
                        capture_output=True,
                        text=True,
                        timeout=10
                    )
                    
                    if result.returncode == 0:
                        lines = result.stdout.strip().split('\n')
                        # Procurar pela linha que contém apenas um número
                        count = None
                        for line in lines:
                            line = line.strip()
                            if line.isdigit():
                                count = line
                                break
                        
                        if count:
                            resultado["tabelas_existem"] = int(count) > 0
                        else:
                            resultado["erro"] = "Não foi possível obter o número de tabelas"
                    else:
                        resultado["erro"] = "Erro ao verificar tabelas"
            else:
                resultado["erro"] = "PostgreSQL não está acessível"
                
        except subprocess.TimeoutExpired:
            resultado["erro"] = "Timeout ao verificar conectividade"
        except Exception as e:
            resultado["erro"] = str(e)
        
        return resultado
    
    def _verificar_estrutura_base(self) -> Dict:
        """Verifica a estrutura da base de dados."""
        resultado = {
            "tabelas": [],
            "total_tabelas": 0,
            "tamanho_base": "0 MB",
            "erro": None
        }
        
        try:
            config = self.db_config.get_database_config()
            
            # Listar tabelas
            result = subprocess.run(
                ["docker-compose", "exec", "-T", "postgres", "psql", "-U", config["user"], 
                 "-d", config["database"], "-c", """
                 SELECT table_name 
                 FROM information_schema.tables 
                 WHERE table_schema = 'public'
                 ORDER BY table_name"""],
                cwd=self.planka_dir,
                capture_output=True,
                text=True, encoding='utf-8', errors='replace'
            )
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                if len(lines) > 2:  # Tem cabeçalho e linhas de dados
                    resultado["tabelas"] = [line.strip() for line in lines[2:-1] if line.strip()]
                    resultado["total_tabelas"] = len(resultado["tabelas"])
                
                # Verificar tamanho da base
                result = subprocess.run(
                    ["docker-compose", "exec", "-T", "postgres", "psql", "-U", config["user"], 
                     "-d", config["database"], "-c", """
                     SELECT pg_size_pretty(pg_database_size(current_database()))"""],
                    cwd=self.planka_dir,
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                if result.returncode == 0:
                    lines = result.stdout.strip().split('\n')
                    if len(lines) > 2:
                        resultado["tamanho_base"] = lines[-2].strip()
            else:
                resultado["erro"] = "Erro ao verificar estrutura da base"
                
        except subprocess.TimeoutExpired:
            resultado["erro"] = "Timeout ao verificar estrutura"
        except Exception as e:
            resultado["erro"] = str(e)
        
        return resultado
    
    def _verificar_pgadmin(self) -> Dict:
        """Verifica o estado do pgAdmin."""
        resultado = {
            "container_rodando": False,
            "porta_acessivel": False,
            "url": "http://localhost:5050",
            "erro": None
        }
        
        try:
            # Verificar se container pgAdmin está rodando
            result = subprocess.run(
                ["docker", "ps", "--filter", "name=pgadmin", "--format", "{{.Status}}"],
                capture_output=True,
                text=True, encoding='utf-8', errors='replace'
            )
            
            resultado["container_rodando"] = "Up" in result.stdout
            
            if resultado["container_rodando"]:
                # Verificar se porta está acessível
                import socket
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(5)
                resultado["porta_acessivel"] = sock.connect_ex(('localhost', 5050)) == 0
                sock.close()
            else:
                resultado["erro"] = "Container pgAdmin não está rodando"
                
        except Exception as e:
            resultado["erro"] = str(e)
        
        return resultado
    
    def _analisar_problemas(self, resultado: Dict):
        """Analisa problemas encontrados no diagnóstico."""
        problemas = []
        
        # Verificar Docker
        if not resultado["docker"]["instalado"]:
            problemas.append("Docker não está instalado")
        elif not resultado["docker"]["rodando"]:
            problemas.append("Docker não está rodando")
        
        # Verificar containers
        if not resultado["containers"]["postgres"]["rodando"]:
            problemas.append("Container PostgreSQL não está rodando")
        if not resultado["containers"]["planka"]["rodando"]:
            problemas.append("Container Planka não está rodando")
        
        # Verificar configuração
        if not resultado["configuracao"]["arquivo_existe"]:
            problemas.append("Arquivo de configuração da base de dados não existe")
        elif not resultado["configuracao"]["config_valida"]:
            problemas.append("Configuração da base de dados inválida")
        
        # Verificar conectividade
        if not resultado["conectividade"]["postgres_acessivel"]:
            problemas.append("PostgreSQL não está acessível")
        elif not resultado["conectividade"]["base_existe"]:
            problemas.append("Base de dados 'planka' não existe")
        elif not resultado["conectividade"]["tabelas_existem"]:
            problemas.append("Base de dados existe mas não tem tabelas")
        
        resultado["problemas"] = problemas
    
    def _gerar_recomendacoes(self, resultado: Dict):
        """Gera recomendações baseadas nos problemas encontrados."""
        recomendacoes = []
        
        # Recomendações para Docker
        if not resultado["docker"]["instalado"]:
            recomendacoes.append("Instalar Docker Desktop")
        elif not resultado["docker"]["rodando"]:
            recomendacoes.append("Iniciar Docker Desktop")
        
        # Recomendações para containers
        if not resultado["containers"]["postgres"]["rodando"]:
            recomendacoes.append("Executar 'docker-compose up -d postgres' no diretório do Planka")
        if not resultado["containers"]["planka"]["rodando"]:
            recomendacoes.append("Executar 'docker-compose up -d' no diretório do Planka")
        
        # Recomendações para configuração
        if not resultado["configuracao"]["arquivo_existe"]:
            recomendacoes.append("Executar configuração da base de dados no dashboard")
        elif not resultado["configuracao"]["config_valida"]:
            recomendacoes.append("Verificar configuração da base de dados")
        
        # Recomendações para base de dados
        if not resultado["conectividade"]["base_existe"]:
            recomendacoes.append("Criar base de dados 'planka' usando o botão 'Criar Base de Dados'")
        elif not resultado["conectividade"]["tabelas_existem"]:
            recomendacoes.append("Inicializar base de dados usando o botão 'Inicializar Base de Dados'")
        
        # Recomendações para pgAdmin (removido - não é mais necessário)
        # if not resultado["pgadmin"]["container_rodando"]:
        #     recomendacoes.append("Executar 'docker-compose -f docker-compose-pgadmin.yml up -d pgadmin' para incluir pgAdmin")
        
        resultado["recomendacoes"] = recomendacoes
    
    def gerar_relatorio(self, resultado: Dict) -> str:
        """
        Gera relatório de diagnóstico em formato texto.
        
        Args:
            resultado: Resultado do diagnóstico
            
        Returns:
            Relatório formatado
        """
        relatorio = []
        relatorio.append("=" * 60)
        relatorio.append("DIAGNÓSTICO DA BASE DE DADOS POSTGRESQL")
        relatorio.append("=" * 60)
        relatorio.append(f"Data/Hora: {resultado['timestamp']}")
        relatorio.append("")
        
        # Docker
        relatorio.append("🐳 DOCKER:")
        docker = resultado["docker"]
        if docker["instalado"]:
            relatorio.append(f"  ✅ Instalado: {docker['versao']}")
            if docker["rodando"]:
                relatorio.append("  ✅ Rodando")
            else:
                relatorio.append(f"  ❌ Não está rodando: {docker['erro']}")
        else:
            relatorio.append(f"  ❌ Não instalado: {docker['erro']}")
        relatorio.append("")
        
        # Containers
        relatorio.append("📦 CONTAINERS:")
        containers = resultado["containers"]
        for nome, info in containers.items():
            if info["rodando"]:
                relatorio.append(f"  ✅ {nome.title()}: {info['status']}")
            else:
                relatorio.append(f"  ❌ {nome.title()}: {info['erro'] or 'Não está rodando'}")
        relatorio.append("")
        
        # Configuração
        relatorio.append("⚙️ CONFIGURAÇÃO:")
        config = resultado["configuracao"]
        if config["arquivo_existe"]:
            relatorio.append("  ✅ Arquivo de configuração existe")
            if config["config_valida"]:
                relatorio.append("  ✅ Configuração válida")
                campos = config["campos"]
                relatorio.append(f"    Host: {campos['host']}:{campos['port']}")
                relatorio.append(f"    Database: {campos['database']}")
                relatorio.append(f"    User: {campos['user']}")
                relatorio.append(f"    Password: {'✅ Definida' if campos['password_set'] else '❌ Não definida'}")
            else:
                relatorio.append("  ❌ Configuração inválida")
        else:
            relatorio.append("  ❌ Arquivo de configuração não existe")
        relatorio.append("")
        
        # Conectividade
        relatorio.append("🔌 CONECTIVIDADE:")
        conect = resultado["conectividade"]
        if conect["postgres_acessivel"]:
            relatorio.append("  ✅ PostgreSQL acessível")
            if conect["base_existe"]:
                relatorio.append("  ✅ Base de dados existe")
                if conect["tabelas_existem"]:
                    relatorio.append("  ✅ Tabelas existem")
                else:
                    relatorio.append("  ⚠️ Base vazia (sem tabelas)")
            else:
                relatorio.append("  ❌ Base de dados não existe")
        else:
            relatorio.append(f"  ❌ PostgreSQL não acessível: {conect['erro']}")
        relatorio.append("")
        
        # Estrutura
        relatorio.append("🗄️ ESTRUTURA:")
        estrutura = resultado["estrutura"]
        if not estrutura["erro"]:
            relatorio.append(f"  Tabelas: {estrutura['total_tabelas']}")
            relatorio.append(f"  Tamanho: {estrutura['tamanho_base']}")
            if estrutura["tabelas"]:
                relatorio.append("  Principais tabelas:")
                for tabela in estrutura["tabelas"][:5]:  # Mostrar apenas as primeiras 5
                    relatorio.append(f"    - {tabela}")
                if len(estrutura["tabelas"]) > 5:
                    relatorio.append(f"    ... e mais {len(estrutura['tabelas']) - 5} tabelas")
        else:
            relatorio.append(f"  ❌ Erro: {estrutura['erro']}")
        relatorio.append("")
        
        # pgAdmin
        relatorio.append("🛠️ PGADMIN:")
        pgadmin = resultado["pgadmin"]
        if pgadmin["container_rodando"]:
            relatorio.append("  ✅ Container rodando")
            if pgadmin["porta_acessivel"]:
                relatorio.append(f"  ✅ Acessível em {pgadmin['url']}")
            else:
                relatorio.append("  ⚠️ Container rodando mas porta não acessível")
        else:
            relatorio.append(f"  ❌ Não está rodando: {pgadmin['erro']}")
        relatorio.append("")
        
        # Problemas
        if resultado["problemas"]:
            relatorio.append("🚨 PROBLEMAS ENCONTRADOS:")
            for problema in resultado["problemas"]:
                relatorio.append(f"  ❌ {problema}")
            relatorio.append("")
        
        # Recomendações
        if resultado["recomendacoes"]:
            relatorio.append("💡 RECOMENDAÇÕES:")
            for i, recomendacao in enumerate(resultado["recomendacoes"], 1):
                relatorio.append(f"  {i}. {recomendacao}")
            relatorio.append("")
        
        relatorio.append("=" * 60)
        
        return "\n".join(relatorio) 