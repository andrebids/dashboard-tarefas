#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de inicialização inteligente do Dashboard de Tarefas.
Detecta automaticamente o ambiente e configura os caminhos corretos.
"""

import os
import sys
import json
from pathlib import Path

def detectar_ambiente():
    """Detecta automaticamente o ambiente e configura os caminhos."""
    print("🔍 Detectando ambiente...")
    
    # Obter diretório home do utilizador
    home_dir = Path.home()
    print(f"📁 Diretório home: {home_dir}")
    
    # Procurar por diretório DEV em locais comuns
    locais_possiveis = [
        home_dir / "Desktop" / "DEV",
        home_dir / "Área de Trabalho" / "DEV",  # Português
        home_dir / "Escritorio" / "DEV",        # Espanhol
        home_dir / "DEV",
        Path.cwd().parent if Path.cwd().name == "dashboard-tarefas" else Path.cwd()
    ]
    
    dev_path = None
    for local in locais_possiveis:
        if local.exists():
            dev_path = local
            print(f"✅ Diretório DEV encontrado: {dev_path}")
            break
    
    if not dev_path:
        print("⚠️ Diretório DEV não encontrado. Usando diretório atual.")
        dev_path = Path.cwd()
    
    return dev_path

def configurar_caminhos(dev_path):
    """Configura os caminhos baseados no diretório DEV detectado."""
    print("⚙️ Configurando caminhos...")
    
    # Caminhos base
    dashboard_path = dev_path / "dashboard-tarefas"
    planka_path = dev_path / "planka-personalizado"
    
    # Verificar se os diretórios existem
    if not dashboard_path.exists():
        print(f"⚠️ Diretório dashboard-tarefas não encontrado em {dashboard_path}")
        dashboard_path = Path.cwd()
    
    if not planka_path.exists():
        print(f"⚠️ Diretório planka-personalizado não encontrado em {planka_path}")
        planka_path = dashboard_path.parent / "planka-personalizado"
    
    # Configurações padrão
    config = {
        "interface": {
            "tamanho_janela": "1200x800",
            "tamanho_minimo": "800x600",
            "tema": "default",
            "console_altura": 200
        },
        "planka": {
            "diretorio": str(planka_path),
            "porta": 3000,
            "url": "http://localhost:3000",
            "docker_compose_file": "docker-compose.yml"
        },
        "database": {
            "arquivo": str(dashboard_path / "database" / "dashboard.db"),
            "backup_automatico": True,
            "backup_intervalo_horas": 24
        },
        "config": {
            "diretorio": str(dashboard_path / "config")
        },
        "logs": {
            "nivel": "INFO",
            "max_arquivos": 10,
            "tamanho_maximo_mb": 10,
            "diretorio_sistema": str(dashboard_path / "logs" / "sistema"),
            "diretorio_tarefas": str(dashboard_path / "logs" / "tarefas"),
            "diretorio_servidores": str(dashboard_path / "logs" / "servidores")
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
    
    # Salvar configuração
    config_file = dashboard_path / "config" / "settings.json"
    config_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=4, ensure_ascii=False)
    
    print(f"✅ Configuração salva em: {config_file}")
    return dashboard_path

def main():
    """Função principal do script de inicialização."""
    print("🚀 Inicializador Inteligente do Dashboard de Tarefas")
    print("=" * 50)
    
    try:
        # Detectar ambiente
        dev_path = detectar_ambiente()
        
        # Configurar caminhos
        dashboard_path = configurar_caminhos(dev_path)
        
        # Mudar para o diretório do dashboard
        os.chdir(dashboard_path)
        print(f"📂 Diretório de trabalho: {dashboard_path}")
        
        # Verificar se main.py existe
        main_file = dashboard_path / "main.py"
        if not main_file.exists():
            print(f"❌ Arquivo main.py não encontrado em {main_file}")
            return 1
        
        print("✅ Ambiente configurado com sucesso!")
        print("🎯 Iniciando dashboard...")
        print("-" * 50)
        
        # Importar e executar main.py
        sys.path.insert(0, str(dashboard_path))
        
        # Executar o dashboard
        import main
        main.main()
        
    except Exception as e:
        print(f"❌ Erro durante a inicialização: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 