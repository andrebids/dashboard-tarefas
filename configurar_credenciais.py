# -*- coding: utf-8 -*-
"""
Script para configurar credenciais da base de dados de forma segura.
"""

import sys
from pathlib import Path

# Adicionar o diretório raiz ao path
sys.path.append(str(Path(__file__).parent))

from config.settings import Settings
from config.database_config import DatabaseConfig


def main():
    """Função principal para configurar credenciais."""
    print("🔐 CONFIGURAÇÃO SEGURA DE CREDENCIAIS DA BASE DE DADOS")
    print("=" * 60)
    print()
    
    try:
        # Inicializar configurações
        settings = Settings()
        
        # Definir diretório de configuração (com fallback)
        try:
            config_dir = settings.obter_diretorio_config()
        except:
            # Fallback para diretório padrão
            config_dir = Path(__file__).parent / "config"
        
        print(f"📁 Diretório de configuração: {config_dir}")
        
        # Criar gerenciador de configuração da base de dados
        db_config = DatabaseConfig(config_dir)
        
        # Verificar configuração atual
        config_info = db_config.get_config_info()
        
        print("📋 CONFIGURAÇÃO ATUAL:")
        print(f"  Host: {config_info['host']}")
        print(f"  Porta: {config_info['port']}")
        print(f"  Base de Dados: {config_info['database']}")
        print(f"  Usuário: {config_info['user']}")
        print(f"  Senha configurada: {'✅ Sim' if config_info['password_set'] else '❌ Não'}")
        print(f"  Usa variáveis de ambiente: {'✅ Sim' if config_info['use_environment'] else '❌ Não'}")
        print(f"  Configuração válida: {'✅ Sim' if config_info['valid'] else '❌ Não'}")
        print()
        
        if not config_info['valid']:
            print("⚠️  CONFIGURAÇÃO INCOMPLETA!")
            print("É necessário configurar a senha da base de dados.")
            print()
            
            # Configurar credenciais
            db_config.setup_environment_variable()
            
            # Verificar novamente
            config_info = db_config.get_config_info()
            if config_info['valid']:
                print("✅ CONFIGURAÇÃO CONCLUÍDA COM SUCESSO!")
            else:
                print("❌ CONFIGURAÇÃO AINDA INCOMPLETA!")
                print("Execute este script novamente para configurar as credenciais.")
        else:
            print("✅ CONFIGURAÇÃO JÁ ESTÁ VÁLIDA!")
            print()
            
            resposta = input("Deseja reconfigurar as credenciais? (s/N): ").strip().lower()
            if resposta in ['s', 'sim', 'y', 'yes']:
                db_config.setup_environment_variable()
                print("✅ CONFIGURAÇÃO ATUALIZADA!")
        
        print()
        print("📝 PRÓXIMOS PASSOS:")
        print("1. Se escolheu variáveis de ambiente, defina a variável PLANKA_DB_PASSWORD")
        print("2. Execute o dashboard: python main.py")
        print("3. Acesse a aba 'Base de Dados' para gerenciar a base")
        
    except Exception as e:
        print(f"❌ ERRO: {e}")
        print("Verifique se todas as dependências estão instaladas.")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 