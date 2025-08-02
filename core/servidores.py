# -*- coding: utf-8 -*-
"""
Módulo de gerenciamento de servidores SSH.
Controla conexões, execução de comandos e pool de conexões.
"""

import os
import json
import sqlite3
import threading
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
import paramiko
from cryptography.fernet import Fernet


class ServidorSSH:
    """
    Classe para representar um servidor SSH.
    """
    
    def __init__(self, id: int = None, nome: str = "", host: str = "", 
                 porta: int = 22, usuario: str = "", senha: str = "", 
                 chave_privada: str = "", timeout: int = 30, 
                 descricao: str = "", ativo: bool = True):
        """
        Inicializa um servidor SSH.
        
        Args:
            id: ID único do servidor
            nome: Nome do servidor
            host: Endereço IP ou hostname
            porta: Porta SSH (padrão: 22)
            usuario: Nome de usuário
            senha: Senha (será criptografada)
            chave_privada: Caminho para chave privada SSH
            timeout: Timeout da conexão em segundos
            descricao: Descrição do servidor
            ativo: Se o servidor está ativo
        """
        self.id = id
        self.nome = nome
        self.host = host
        self.porta = porta
        self.usuario = usuario
        self.senha = senha
        self.chave_privada = chave_privada
        self.timeout = timeout
        self.descricao = descricao
        self.ativo = ativo
        self.data_criacao = datetime.now()
        self.data_modificacao = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte o servidor para dicionário."""
        return {
            "id": self.id,
            "nome": self.nome,
            "host": self.host,
            "porta": self.porta,
            "usuario": self.usuario,
            "senha": self.senha,
            "chave_privada": self.chave_privada,
            "timeout": self.timeout,
            "descricao": self.descricao,
            "ativo": self.ativo,
            "data_criacao": self.data_criacao.isoformat(),
            "data_modificacao": self.data_modificacao.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ServidorSSH':
        """Cria um servidor a partir de dicionário."""
        return cls(
            id=data.get("id"),
            nome=data.get("nome", ""),
            host=data.get("host", ""),
            porta=data.get("porta", 22),
            usuario=data.get("usuario", ""),
            senha=data.get("senha", ""),
            chave_privada=data.get("chave_privada", ""),
            timeout=data.get("timeout", 30),
            descricao=data.get("descricao", ""),
            ativo=data.get("ativo", True)
        )


class ConexaoSSH:
    """
    Classe para gerenciar uma conexão SSH individual.
    """
    
    def __init__(self, servidor: ServidorSSH):
        """
        Inicializa uma conexão SSH.
        
        Args:
            servidor: Servidor SSH para conectar
        """
        self.servidor = servidor
        self.client = None
        self.shell = None
        self.conectado = False
        self.data_conexao = None
        self.ultima_atividade = None
        self.lock = threading.Lock()
    
    def conectar(self) -> Tuple[bool, str]:
        """
        Estabelece conexão SSH com o servidor.
        
        Returns:
            (sucesso, mensagem)
        """
        try:
            with self.lock:
                if self.conectado:
                    return True, "Já conectado"
                
                # Criar cliente SSH
                self.client = paramiko.SSHClient()
                self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                
                # Configurar parâmetros de conexão
                connect_kwargs = {
                    "hostname": self.servidor.host,
                    "port": self.servidor.porta,
                    "username": self.servidor.usuario,
                    "timeout": self.servidor.timeout
                }
                
                # Adicionar autenticação
                if self.servidor.chave_privada and os.path.exists(self.servidor.chave_privada):
                    # Autenticação por chave privada
                    connect_kwargs["key_filename"] = self.servidor.chave_privada
                elif self.servidor.senha:
                    # Autenticação por senha
                    connect_kwargs["password"] = self.servidor.senha
                else:
                    return False, "Nenhum método de autenticação configurado"
                
                # Estabelecer conexão
                self.client.connect(**connect_kwargs)
                
                # Criar shell interativo
                self.shell = self.client.invoke_shell()
                self.shell.settimeout(self.servidor.timeout)
                
                self.conectado = True
                self.data_conexao = datetime.now()
                self.ultima_atividade = datetime.now()
                
                return True, "Conexão estabelecida com sucesso"
                
        except paramiko.AuthenticationException:
            return False, "Falha na autenticação (usuário/senha incorretos)"
        except paramiko.SSHException as e:
            return False, f"Erro SSH: {str(e)}"
        except Exception as e:
            return False, f"Erro de conexão: {str(e)}"
    
    def desconectar(self):
        """Fecha a conexão SSH."""
        try:
            with self.lock:
                if self.shell:
                    self.shell.close()
                if self.client:
                    self.client.close()
                
                self.conectado = False
                self.shell = None
                self.client = None
                
        except Exception as e:
            print(f"Erro ao desconectar: {e}")
    
    def executar_comando(self, comando: str) -> Tuple[bool, str, str, str]:
        """
        Executa um comando no servidor SSH.
        
        Args:
            comando: Comando a executar
            
        Returns:
            (sucesso, stdout, stderr, mensagem)
        """
        try:
            with self.lock:
                if not self.conectado:
                    return False, "", "", "Não conectado"
                
                # Executar comando
                stdin, stdout, stderr = self.client.exec_command(comando, timeout=self.servidor.timeout)
                
                # Aguardar conclusão
                exit_status = stdout.channel.recv_exit_status()
                
                # Ler saída
                stdout_text = stdout.read().decode('utf-8', errors='ignore')
                stderr_text = stderr.read().decode('utf-8', errors='ignore')
                
                self.ultima_atividade = datetime.now()
                
                if exit_status == 0:
                    return True, stdout_text, stderr_text, "Comando executado com sucesso"
                else:
                    return False, stdout_text, stderr_text, f"Comando falhou com código {exit_status}"
                
        except Exception as e:
            return False, "", "", f"Erro ao executar comando: {str(e)}"
    
    def testar_conexao(self) -> Tuple[bool, str]:
        """
        Testa a conectividade com o servidor.
        
        Returns:
            (sucesso, mensagem)
        """
        try:
            # Tentar conectar
            sucesso, mensagem = self.conectar()
            if sucesso:
                # Testar comando simples
                sucesso_cmd, stdout, stderr, msg_cmd = self.executar_comando("echo 'teste'")
                if sucesso_cmd:
                    return True, "Conexão e comando de teste OK"
                else:
                    return False, f"Conexão OK, mas comando falhou: {msg_cmd}"
            else:
                return False, mensagem
                
        except Exception as e:
            return False, f"Erro no teste: {str(e)}"
        finally:
            # Sempre desconectar após teste
            self.desconectar()


class PoolConexoesSSH:
    """
    Pool de conexões SSH para reutilização.
    """
    
    def __init__(self, max_conexoes: int = 5, timeout_idle: int = 300):
        """
        Inicializa o pool de conexões.
        
        Args:
            max_conexoes: Número máximo de conexões simultâneas
            timeout_idle: Timeout para conexões ociosas (segundos)
        """
        self.max_conexoes = max_conexoes
        self.timeout_idle = timeout_idle
        self.conexoes = {}  # servidor_id -> ConexaoSSH
        self.lock = threading.Lock()
        self.thread_limpeza = None
        self._iniciar_limpeza_automatica()
    
    def _iniciar_limpeza_automatica(self):
        """Inicia thread de limpeza automática de conexões ociosas."""
        def limpeza_automatica():
            while True:
                try:
                    time.sleep(60)  # Verificar a cada minuto
                    self._limpar_conexoes_ociosas()
                except Exception as e:
                    print(f"Erro na limpeza automática: {e}")
        
        self.thread_limpeza = threading.Thread(target=limpeza_automatica, daemon=True)
        self.thread_limpeza.start()
    
    def _limpar_conexoes_ociosas(self):
        """Remove conexões que estão ociosas há muito tempo."""
        try:
            with self.lock:
                agora = datetime.now()
                servidores_remover = []
                
                for servidor_id, conexao in self.conexoes.items():
                    if conexao.ultima_atividade:
                        tempo_ocioso = (agora - conexao.ultima_atividade).total_seconds()
                        if tempo_ocioso > self.timeout_idle:
                            servidores_remover.append(servidor_id)
                
                for servidor_id in servidores_remover:
                    self.conexoes[servidor_id].desconectar()
                    del self.conexoes[servidor_id]
                    
        except Exception as e:
            print(f"Erro ao limpar conexões ociosas: {e}")
    
    def obter_conexao(self, servidor: ServidorSSH) -> Tuple[bool, ConexaoSSH, str]:
        """
        Obtém uma conexão do pool ou cria uma nova.
        
        Args:
            servidor: Servidor para conectar
            
        Returns:
            (sucesso, conexao, mensagem)
        """
        try:
            with self.lock:
                # Verificar se já existe conexão
                if servidor.id in self.conexoes:
                    conexao = self.conexoes[servidor.id]
                    if conexao.conectado:
                        return True, conexao, "Conexão reutilizada"
                    else:
                        # Remover conexão inválida
                        del self.conexoes[servidor.id]
                
                # Verificar limite de conexões
                if len(self.conexoes) >= self.max_conexoes:
                    # Remover conexão mais antiga
                    servidor_mais_antigo = min(
                        self.conexoes.keys(),
                        key=lambda x: self.conexoes[x].data_conexao or datetime.min
                    )
                    self.conexoes[servidor_mais_antigo].desconectar()
                    del self.conexoes[servidor_mais_antigo]
                
                # Criar nova conexão
                conexao = ConexaoSSH(servidor)
                sucesso, mensagem = conexao.conectar()
                
                if sucesso:
                    self.conexoes[servidor.id] = conexao
                    return True, conexao, mensagem
                else:
                    return False, None, mensagem
                    
        except Exception as e:
            return False, None, f"Erro ao obter conexão: {str(e)}"
    
    def liberar_conexao(self, servidor_id: int):
        """Libera uma conexão do pool."""
        try:
            with self.lock:
                if servidor_id in self.conexoes:
                    self.conexoes[servidor_id].desconectar()
                    del self.conexoes[servidor_id]
        except Exception as e:
            print(f"Erro ao liberar conexão: {e}")
    
    def fechar_todas_conexoes(self):
        """Fecha todas as conexões do pool."""
        try:
            with self.lock:
                for conexao in self.conexoes.values():
                    conexao.desconectar()
                self.conexoes.clear()
        except Exception as e:
            print(f"Erro ao fechar conexões: {e}")


class GerenciadorCredenciais:
    """
    Gerenciador seguro de credenciais SSH.
    """
    
    def __init__(self, config_dir: Path):
        """
        Inicializa o gerenciador de credenciais.
        
        Args:
            config_dir: Diretório de configuração
        """
        self.config_dir = config_dir
        self.credentials_file = config_dir / "ssh_credentials.json"
        self.key_file = config_dir / "ssh_key.key"
        
        # Criar diretório se não existir
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # Gerar chave de criptografia se não existir
        if not self.key_file.exists():
            key = Fernet.generate_key()
            with open(self.key_file, 'wb') as f:
                f.write(key)
    
    def _get_encryption_key(self) -> bytes:
        """Obtém chave de criptografia."""
        with open(self.key_file, 'rb') as f:
            return f.read()
    
    def _encrypt_value(self, value: str) -> str:
        """Criptografa um valor."""
        if not value:
            return ""
        
        key = self._get_encryption_key()
        fernet = Fernet(key)
        encrypted = fernet.encrypt(value.encode())
        return encrypted.decode()
    
    def _decrypt_value(self, encrypted_value: str) -> str:
        """Descriptografa um valor."""
        if not encrypted_value:
            return ""
        
        try:
            key = self._get_encryption_key()
            fernet = Fernet(key)
            decrypted = fernet.decrypt(encrypted_value.encode())
            return decrypted.decode()
        except Exception:
            return ""
    
    def salvar_credenciais(self, servidor: ServidorSSH):
        """Salva credenciais de um servidor de forma criptografada."""
        try:
            # Carregar credenciais existentes
            credenciais = self._carregar_credenciais()
            
            # Criptografar senha
            senha_criptografada = self._encrypt_value(servidor.senha)
            
            # Atualizar credenciais
            credenciais[servidor.id] = {
                "senha": senha_criptografada,
                "chave_privada": servidor.chave_privada,
                "data_modificacao": datetime.now().isoformat()
            }
            
            # Salvar arquivo
            with open(self.credentials_file, 'w', encoding='utf-8') as f:
                json.dump(credenciais, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"Erro ao salvar credenciais: {e}")
    
    def carregar_credenciais(self, servidor_id: int) -> Tuple[str, str]:
        """
        Carrega credenciais de um servidor.
        
        Returns:
            (senha_descriptografada, chave_privada)
        """
        try:
            credenciais = self._carregar_credenciais()
            
            if servidor_id in credenciais:
                dados = credenciais[servidor_id]
                senha = self._decrypt_value(dados.get("senha", ""))
                chave_privada = dados.get("chave_privada", "")
                return senha, chave_privada
            
            return "", ""
            
        except Exception as e:
            print(f"Erro ao carregar credenciais: {e}")
            return "", ""
    
    def _carregar_credenciais(self) -> Dict:
        """Carrega todas as credenciais do arquivo."""
        try:
            if self.credentials_file.exists():
                with open(self.credentials_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {}
        except Exception:
            return {}
    
    def remover_credenciais(self, servidor_id: int):
        """Remove credenciais de um servidor."""
        try:
            credenciais = self._carregar_credenciais()
            
            if servidor_id in credenciais:
                del credenciais[servidor_id]
                
                with open(self.credentials_file, 'w', encoding='utf-8') as f:
                    json.dump(credenciais, f, indent=2, ensure_ascii=False)
                    
        except Exception as e:
            print(f"Erro ao remover credenciais: {e}")


class ServidoresManager:
    """
    Gerenciador principal de servidores SSH.
    """
    
    def __init__(self, settings):
        """
        Inicializa o gerenciador de servidores.
        
        Args:
            settings: Instância das configurações do sistema
        """
        self.settings = settings
        self.db_file = Path(settings.obter("database", "arquivo"))
        self.db_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Inicializar componentes
        try:
            config_dir = settings.obter_diretorio_config()
        except:
            # Fallback para diretório padrão
            config_dir = Path(__file__).parent.parent / "config"
        self.credentials_manager = GerenciadorCredenciais(config_dir)
        self.pool_conexoes = PoolConexoesSSH(
            max_conexoes=settings.obter("servidores", "max_conexoes", 5),
            timeout_idle=settings.obter("servidores", "timeout_idle", 300)
        )
        
        # Inicializar banco de dados
        self._inicializar_banco()
    
    def _inicializar_banco(self):
        """Inicializa o banco de dados de servidores."""
        try:
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                
                # Tabela de servidores
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS servidores (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        nome TEXT NOT NULL,
                        host TEXT NOT NULL,
                        porta INTEGER DEFAULT 22,
                        usuario TEXT NOT NULL,
                        senha TEXT,
                        chave_privada TEXT,
                        timeout INTEGER DEFAULT 30,
                        descricao TEXT,
                        ativo BOOLEAN DEFAULT 1,
                        data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        data_modificacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Tabela de conexões
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS conexoes (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        servidor_id INTEGER,
                        data_conexao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        data_desconexao TIMESTAMP,
                        status TEXT,
                        comando_executado TEXT,
                        resultado TEXT,
                        FOREIGN KEY (servidor_id) REFERENCES servidores (id)
                    )
                """)
                
                conn.commit()
                
        except Exception as e:
            print(f"Erro ao inicializar banco de servidores: {e}")
    
    def adicionar_servidor(self, servidor: ServidorSSH) -> Tuple[bool, str]:
        """
        Adiciona um novo servidor.
        
        Args:
            servidor: Servidor a adicionar
            
        Returns:
            (sucesso, mensagem)
        """
        try:
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT INTO servidores (nome, host, porta, usuario, senha, 
                                          chave_privada, timeout, descricao, ativo)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    servidor.nome, servidor.host, servidor.porta, servidor.usuario,
                    servidor.senha, servidor.chave_privada, servidor.timeout,
                    servidor.descricao, servidor.ativo
                ))
                
                servidor.id = cursor.lastrowid
                
                # Salvar credenciais criptografadas
                self.credentials_manager.salvar_credenciais(servidor)
                
                conn.commit()
                return True, f"Servidor '{servidor.nome}' adicionado com sucesso"
                
        except Exception as e:
            return False, f"Erro ao adicionar servidor: {str(e)}"
    
    def atualizar_servidor(self, servidor: ServidorSSH) -> Tuple[bool, str]:
        """
        Atualiza um servidor existente.
        
        Args:
            servidor: Servidor a atualizar
            
        Returns:
            (sucesso, mensagem)
        """
        try:
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    UPDATE servidores 
                    SET nome=?, host=?, porta=?, usuario=?, senha=?, chave_privada=?,
                        timeout=?, descricao=?, ativo=?, data_modificacao=CURRENT_TIMESTAMP
                    WHERE id=?
                """, (
                    servidor.nome, servidor.host, servidor.porta, servidor.usuario,
                    servidor.senha, servidor.chave_privada, servidor.timeout,
                    servidor.descricao, servidor.ativo, servidor.id
                ))
                
                # Atualizar credenciais
                self.credentials_manager.salvar_credenciais(servidor)
                
                conn.commit()
                return True, f"Servidor '{servidor.nome}' atualizado com sucesso"
                
        except Exception as e:
            return False, f"Erro ao atualizar servidor: {str(e)}"
    
    def remover_servidor(self, servidor_id: int) -> Tuple[bool, str]:
        """
        Remove um servidor.
        
        Args:
            servidor_id: ID do servidor a remover
            
        Returns:
            (sucesso, mensagem)
        """
        try:
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                
                # Verificar se existe
                cursor.execute("SELECT nome FROM servidores WHERE id=?", (servidor_id,))
                resultado = cursor.fetchone()
                
                if not resultado:
                    return False, "Servidor não encontrado"
                
                nome_servidor = resultado[0]
                
                # Remover do banco
                cursor.execute("DELETE FROM servidores WHERE id=?", (servidor_id,))
                
                # Remover credenciais
                self.credentials_manager.remover_credenciais(servidor_id)
                
                # Fechar conexão se estiver ativa
                self.pool_conexoes.liberar_conexao(servidor_id)
                
                conn.commit()
                return True, f"Servidor '{nome_servidor}' removido com sucesso"
                
        except Exception as e:
            return False, f"Erro ao remover servidor: {str(e)}"
    
    def listar_servidores(self) -> List[ServidorSSH]:
        """
        Lista todos os servidores.
        
        Returns:
            Lista de servidores
        """
        servidores = []
        
        try:
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT id, nome, host, porta, usuario, senha, chave_privada,
                           timeout, descricao, ativo, data_criacao, data_modificacao
                    FROM servidores
                    ORDER BY nome
                """)
                
                for row in cursor.fetchall():
                    servidor = ServidorSSH(
                        id=row[0],
                        nome=row[1],
                        host=row[2],
                        porta=row[3],
                        usuario=row[4],
                        senha=row[5] or "",
                        chave_privada=row[6] or "",
                        timeout=row[7],
                        descricao=row[8] or "",
                        ativo=bool(row[9])
                    )
                    
                    # Carregar credenciais criptografadas
                    senha_real, chave_real = self.credentials_manager.carregar_credenciais(servidor.id)
                    servidor.senha = senha_real
                    servidor.chave_privada = chave_real
                    
                    servidores.append(servidor)
                    
        except Exception as e:
            print(f"Erro ao listar servidores: {e}")
        
        return servidores
    
    def obter_servidor(self, servidor_id: int) -> Optional[ServidorSSH]:
        """
        Obtém um servidor específico.
        
        Args:
            servidor_id: ID do servidor
            
        Returns:
            Servidor ou None se não encontrado
        """
        try:
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT id, nome, host, porta, usuario, senha, chave_privada,
                           timeout, descricao, ativo, data_criacao, data_modificacao
                    FROM servidores
                    WHERE id=?
                """, (servidor_id,))
                
                row = cursor.fetchone()
                
                if row:
                    servidor = ServidorSSH(
                        id=row[0],
                        nome=row[1],
                        host=row[2],
                        porta=row[3],
                        usuario=row[4],
                        senha=row[5] or "",
                        chave_privada=row[6] or "",
                        timeout=row[7],
                        descricao=row[8] or "",
                        ativo=bool(row[9])
                    )
                    
                    # Carregar credenciais criptografadas
                    senha_real, chave_real = self.credentials_manager.carregar_credenciais(servidor.id)
                    servidor.senha = senha_real
                    servidor.chave_privada = chave_real
                    
                    return servidor
                
                return None
                
        except Exception as e:
            print(f"Erro ao obter servidor: {e}")
            return None
    
    def testar_conexao(self, servidor_id: int) -> Tuple[bool, str]:
        """
        Testa a conexão com um servidor.
        
        Args:
            servidor_id: ID do servidor
            
        Returns:
            (sucesso, mensagem)
        """
        try:
            servidor = self.obter_servidor(servidor_id)
            if not servidor:
                return False, "Servidor não encontrado"
            
            conexao = ConexaoSSH(servidor)
            return conexao.testar_conexao()
            
        except Exception as e:
            return False, f"Erro ao testar conexão: {str(e)}"
    
    def executar_comando(self, servidor_id: int, comando: str) -> Tuple[bool, str, str, str]:
        """
        Executa um comando em um servidor.
        
        Args:
            servidor_id: ID do servidor
            comando: Comando a executar
            
        Returns:
            (sucesso, stdout, stderr, mensagem)
        """
        try:
            servidor = self.obter_servidor(servidor_id)
            if not servidor:
                return False, "", "", "Servidor não encontrado"
            
            # Obter conexão do pool
            sucesso, conexao, msg = self.pool_conexoes.obter_conexao(servidor)
            if not sucesso:
                return False, "", "", f"Erro ao conectar: {msg}"
            
            # Executar comando
            return conexao.executar_comando(comando)
            
        except Exception as e:
            return False, "", "", f"Erro ao executar comando: {str(e)}"
    
    def registrar_conexao(self, servidor_id: int, status: str, comando: str = "", resultado: str = ""):
        """Registra uma conexão no banco de dados."""
        try:
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT INTO conexoes (servidor_id, status, comando_executado, resultado)
                    VALUES (?, ?, ?, ?)
                """, (servidor_id, status, comando, resultado))
                
                conn.commit()
                
        except Exception as e:
            print(f"Erro ao registrar conexão: {e}")
    
    def obter_estatisticas(self) -> Dict[str, Any]:
        """
        Obtém estatísticas dos servidores.
        
        Returns:
            Dict com estatísticas
        """
        try:
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                
                # Total de servidores
                cursor.execute("SELECT COUNT(*) FROM servidores")
                total_servidores = cursor.fetchone()[0]
                
                # Servidores ativos
                cursor.execute("SELECT COUNT(*) FROM servidores WHERE ativo=1")
                servidores_ativos = cursor.fetchone()[0]
                
                # Total de conexões
                cursor.execute("SELECT COUNT(*) FROM conexoes")
                total_conexoes = cursor.fetchone()[0]
                
                # Conexões hoje
                cursor.execute("""
                    SELECT COUNT(*) FROM conexoes 
                    WHERE DATE(data_conexao) = DATE('now')
                """)
                conexoes_hoje = cursor.fetchone()[0]
                
                return {
                    "total_servidores": total_servidores,
                    "servidores_ativos": servidores_ativos,
                    "total_conexoes": total_conexoes,
                    "conexoes_hoje": conexoes_hoje,
                    "conexoes_ativas": len(self.pool_conexoes.conexoes)
                }
                
        except Exception as e:
            print(f"Erro ao obter estatísticas: {e}")
            return {}
    
    def fechar_todas_conexoes(self):
        """Fecha todas as conexões ativas."""
        self.pool_conexoes.fechar_todas_conexoes() 