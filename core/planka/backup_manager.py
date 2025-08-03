# -*- coding: utf-8 -*-
"""
Módulo para gerenciamento de backups do Planka.
Backup de banco de dados e gerenciamento de arquivos de backup.
"""

import subprocess
from datetime import datetime
from typing import Tuple
from pathlib import Path


class BackupManager:
    """
    Gerenciador de backups do sistema Planka.
    """
    
    def __init__(self, settings):
        """
        Inicializa o gerenciador de backups.
        
        Args:
            settings: Instância das configurações do sistema
        """
        self.settings = settings
        self.planka_dir = Path(settings.obter("planka", "diretorio"))
    
    def backup_database(self) -> Tuple[bool, str]:
        """
        Faz backup da base de dados do Planka.
        
        Returns:
            (sucesso, mensagem)
        """
        try:
            # Verificar se está rodando
            from .status_monitor import StatusMonitor
            status_monitor = StatusMonitor(self.settings)
            if status_monitor.verificar_status() != "online":
                return False, "Planka não está rodando"
            
            # Criar diretório de backup se não existir
            backup_dir = self.planka_dir / "backups"
            backup_dir.mkdir(exist_ok=True)
            
            # Nome do arquivo de backup
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = backup_dir / f"planka_backup_{timestamp}.sql"
            
            # Fazer backup usando docker-compose
            result = subprocess.run(
                ["docker-compose", "exec", "-T", "postgres", "pg_dump", "-U", "planka", "planka"],
                cwd=self.planka_dir,
                capture_output=True,
                text=True, 
                encoding='utf-8', errors='replace'
            )
            
            if result.returncode == 0:
                # Salvar backup
                with open(backup_file, 'w', encoding='utf-8') as f:
                    f.write(result.stdout)
                
                return True, f"Backup criado: {backup_file.name}"
            else:
                return False, f"Erro ao fazer backup: {result.stderr}"
                
        except Exception as e:
            return False, f"Erro ao fazer backup: {str(e)}" 