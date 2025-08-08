# -*- coding: utf-8 -*-
"""
Configuração segura da base de dados PostgreSQL do Planka.
Gerencia credenciais de forma segura usando variáveis de ambiente e criptografia.
"""

import os
import json
from pathlib import Path
from cryptography.fernet import Fernet
from typing import Dict, Optional


class DatabaseConfig:
    """
    Gerenciador de configuração segura da base de dados.
    """
    
    def __init__(self, config_dir: Path):
        """
        Inicializa o gerenciador de configuração.
        
        Args:
            config_dir: Diretório de configuração
        """
        self.config_dir = config_dir
        self.config_file = config_dir / "database_config.json"
        self.key_file = config_dir / "database_key.key"
        
        # Configurações padrão (sem credenciais sensíveis)
        self.default_config = {
            "host": "localhost",  # Para conexão via Docker exec
            "port": 5432,
            "database": "planka",
            "user": "postgres",
            "password": "",  # Será definido via variável de ambiente ou arquivo seguro
            "use_environment": True,  # Usar variáveis de ambiente por padrão
            "encrypted": False,
            "use_docker": True,  # Usar Docker para conectar
            "docker_container": "planka-personalizado-postgres-1"
        }
        
        # Inicializar configuração
        self.config = self.default_config.copy()
        
        # Inicializar ou carregar configuração
        self._initialize_config()
    
    def _initialize_config(self):
        """Inicializa ou carrega a configuração da base de dados."""
        try:
            # Criar diretório se não existir
            self.config_dir.mkdir(parents=True, exist_ok=True)
            
            # Verificar se arquivo de configuração existe
            if not self.config_file.exists():
                self._create_default_config()
            else:
                self._load_config()
                
        except Exception as e:
            print(f"Erro ao inicializar configuração: {e}")
            self._create_default_config()
    
    def _create_default_config(self):
        """Cria configuração padrão."""
        try:
            # Salvar configuração padrão
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.default_config, f, indent=2, ensure_ascii=False)
            
            # Gerar chave de criptografia
            if not self.key_file.exists():
                key = Fernet.generate_key()
                with open(self.key_file, 'wb') as f:
                    f.write(key)
                    
        except Exception as e:
            print(f"Erro ao criar configuração padrão: {e}")
    
    def _load_config(self):
        """Carrega configuração do arquivo."""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        except Exception as e:
            print(f"Erro ao carregar configuração: {e}")
            self.config = self.default_config.copy()
    
    def _save_config(self):
        """Salva configuração no arquivo."""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Erro ao salvar configuração: {e}")
    
    def _get_encryption_key(self) -> Optional[bytes]:
        """Obtém chave de criptografia."""
        try:
            if self.key_file.exists():
                with open(self.key_file, 'rb') as f:
                    return f.read()
            return None
        except Exception as e:
            print(f"Erro ao obter chave de criptografia: {e}")
            return None
    
    def _encrypt_value(self, value: str) -> str:
        """Criptografa um valor."""
        try:
            key = self._get_encryption_key()
            if key:
                fernet = Fernet(key)
                encrypted = fernet.encrypt(value.encode())
                return encrypted.decode()
            return value
        except Exception as e:
            print(f"Erro ao criptografar valor: {e}")
            return value
    
    def _decrypt_value(self, encrypted_value: str) -> str:
        """Descriptografa um valor."""
        try:
            key = self._get_encryption_key()
            if key:
                fernet = Fernet(key)
                decrypted = fernet.decrypt(encrypted_value.encode())
                return decrypted.decode()
            return encrypted_value
        except Exception as e:
            print(f"Erro ao descriptografar valor: {e}")
            return encrypted_value
    
    def get_database_config(self) -> Dict[str, any]:
        """
        Obtém configuração da base de dados de forma segura.
        
        Returns:
            Dict com configuração da base de dados
        """
        config = self.config.copy()
        
        # Prioridade: Variáveis de ambiente
        if config.get("use_environment", True):
            env_password = os.getenv("PLANKA_DB_PASSWORD")
            if env_password:
                config["password"] = env_password
                return config
        
        # Segunda prioridade: Arquivo de configuração
        if config.get("encrypted", False) and config.get("password"):
            config["password"] = self._decrypt_value(config["password"])
        
        return config
    
    def set_database_config(self, host: str = None, port: int = None, 
                           database: str = None, user: str = None, 
                           password: str = None, use_environment: bool = None):
        """
        Define configuração da base de dados.
        
        Args:
            host: Host da base de dados
            port: Porta da base de dados
            database: Nome da base de dados
            user: Usuário da base de dados
            password: Senha da base de dados
            use_environment: Se deve usar variáveis de ambiente
        """
        if host is not None:
            self.config["host"] = host
        if port is not None:
            self.config["port"] = port
        if database is not None:
            self.config["database"] = database
        if user is not None:
            self.config["user"] = user
        if use_environment is not None:
            self.config["use_environment"] = use_environment
        
        # Tratar senha de forma especial
        if password is not None:
            if self.config.get("use_environment", True):
                # Se usar variáveis de ambiente, não salvar senha no arquivo
                print("Aviso: Senha não será salva no arquivo (usando variáveis de ambiente)")
            else:
                # Criptografar senha antes de salvar
                self.config["password"] = self._encrypt_value(password)
                self.config["encrypted"] = True
        
        self._save_config()
    
    def get_connection_string(self) -> str:
        """
        Obtém string de conexão da base de dados.
        
        Returns:
            String de conexão PostgreSQL
        """
        config = self.get_database_config()
        
        return (f"host={config['host']} "
                f"port={config['port']} "
                f"dbname={config['database']} "
                f"user={config['user']} "
                f"password={config['password']}")
    
    def validate_config(self) -> bool:
        """
        Valida se a configuração está completa.
        
        Returns:
            True se configuração está válida
        """
        config = self.get_database_config()
        
        required_fields = ["host", "port", "database", "user", "password"]
        for field in required_fields:
            if not config.get(field):
                return False
        
        return True
    
    def setup_environment_variable(self):
        """Configura variável de ambiente para senha da base de dados."""
        print("=== CONFIGURAÇÃO SEGURA DA BASE DE DADOS ===")
        print("Para maior segurança, configure a senha como variável de ambiente.")
        print()
        print("Opção 1: Variável de ambiente (RECOMENDADO)")
        print("Defina a variável de ambiente PLANKA_DB_PASSWORD:")
        print("Windows (PowerShell):")
        print("  $env:PLANKA_DB_PASSWORD = 'sua_senha_aqui'")
        print("Windows (CMD):")
        print("  set PLANKA_DB_PASSWORD=sua_senha_aqui")
        print("Linux/Mac:")
        print("  export PLANKA_DB_PASSWORD='sua_senha_aqui'")
        print()
        print("Opção 2: Arquivo de configuração")
        print("A senha será criptografada e salva no arquivo de configuração.")
        print()
        
        choice = input("Escolha a opção (1 ou 2): ").strip()
        
        if choice == "1":
            self.set_database_config(use_environment=True)
            print("✅ Configurado para usar variável de ambiente.")
            print("Lembre-se de definir a variável PLANKA_DB_PASSWORD!")
        elif choice == "2":
            password = input("Digite a senha da base de dados: ").strip()
            if password:
                self.set_database_config(password=password, use_environment=False)
                print("✅ Senha salva de forma criptografada no arquivo de configuração.")
            else:
                print("❌ Senha não pode estar vazia.")
        else:
            print("❌ Opção inválida. Usando configuração padrão.")
    
    def get_config_info(self) -> Dict[str, any]:
        """
        Obtém informações sobre a configuração (sem expor senhas).
        
        Returns:
            Dict com informações da configuração
        """
        config = self.get_database_config()
        
        return {
            "host": config["host"],
            "port": config["port"],
            "database": config["database"],
            "user": config["user"],
            "password_set": bool(config["password"]),
            "use_environment": self.config.get("use_environment", True),
            "encrypted": self.config.get("encrypted", False),
            "valid": self.validate_config()
        } 