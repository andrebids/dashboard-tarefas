#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Validação de Segurança - Dashboard de Tarefas
Executa verificações de segurança no projeto.
"""

import sys
import os
from pathlib import Path

# Adicionar o diretório raiz ao path
sys.path.append(str(Path(__file__).parent.parent))

try:
    from core.seguranca import seguranca_manager
    from config.settings import Settings
except ImportError as e:
    print(f"❌ Erro ao importar módulos: {e}")
    sys.exit(1)


def main():
    """Função principal do script de validação."""
    print("🔒 VALIDAÇÃO DE SEGURANÇA - DASHBOARD DE TAREFAS")
    print("=" * 60)
    print()
    
    # Obter caminho do projeto
    projeto_path = Path(__file__).parent.parent
    
    # 1. Validar configurações de segurança
    print("📋 1. VALIDANDO CONFIGURAÇÕES DE SEGURANÇA")
    print("-" * 40)
    
    try:
        settings = Settings()
        resultado_config = settings.validar_configuracoes_seguranca()
        
        if resultado_config["valido"]:
            print("✅ Configurações de segurança válidas")
        else:
            print("❌ Problemas encontrados:")
            for problema in resultado_config["problemas"]:
                print(f"   - {problema}")
        
        if resultado_config["avisos"]:
            print("⚠️ Avisos:")
            for aviso in resultado_config["avisos"]:
                print(f"   - {aviso}")
        
    except Exception as e:
        print(f"❌ Erro ao validar configurações: {e}")
    
    print()
    
    # 2. Verificar variáveis de ambiente
    print("🌍 2. VERIFICANDO VARIÁVEIS DE AMBIENTE")
    print("-" * 40)
    
    vars_env = seguranca_manager.verificar_variaveis_ambiente()
    
    print("Obrigatórias:")
    for var, status in vars_env["obrigatorias"].items():
        print(f"   {var}: {status}")
    
    print()
    print("Opcionais:")
    for var, status in vars_env["opcionais"].items():
        print(f"   {var}: {status}")
    
    print()
    
    # 3. Validar arquivos do projeto
    print("📁 3. VALIDANDO ARQUIVOS DO PROJETO")
    print("-" * 40)
    
    resultados = seguranca_manager.validar_diretorio(str(projeto_path))
    
    if resultados:
        print(f"⚠️ Encontrados {len(resultados)} arquivos com possíveis problemas:")
        for resultado in resultados:
            print(f"\n📄 {resultado['arquivo']}")
            if resultado["problemas"]:
                print("   ❌ Problemas:")
                for problema in resultado["problemas"]:
                    print(f"      - {problema}")
            if resultado["avisos"]:
                print("   ⚠️ Avisos:")
                for aviso in resultado["avisos"]:
                    print(f"      - {aviso}")
    else:
        print("✅ Nenhum problema de segurança encontrado nos arquivos")
    
    print()
    
    # 4. Gerar relatório completo
    print("📊 4. RELATÓRIO COMPLETO")
    print("-" * 40)
    
    relatorio = seguranca_manager.gerar_relatorio_seguranca(str(projeto_path))
    print(relatorio)
    
    print()
    
    # 5. Resumo final
    print("🎯 RESUMO FINAL")
    print("-" * 40)
    
    total_problemas = len(vars_env["faltando_obrigatorias"]) + len(resultados)
    
    if total_problemas == 0:
        print("✅ PROJETO SEGURO!")
        print("   Todas as verificações de segurança passaram com sucesso.")
    else:
        print(f"⚠️ ATENÇÃO: {total_problemas} problema(s) encontrado(s)")
        print("   Revise as configurações antes de prosseguir.")
    
    print()
    print("💡 DICAS DE SEGURANÇA:")
    print("   - Configure as variáveis de ambiente obrigatórias")
    print("   - Use senhas fortes e únicas")
    print("   - Nunca commite credenciais no código")
    print("   - Execute este script regularmente")
    print("   - Mantenha as dependências atualizadas")
    
    return total_problemas == 0


if __name__ == "__main__":
    try:
        sucesso = main()
        sys.exit(0 if sucesso else 1)
    except KeyboardInterrupt:
        print("\n\n⏹️ Validação interrompida pelo utilizador")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        sys.exit(1) 