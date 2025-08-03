#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Diagnóstico e Correção do Planka
Resolve problemas de banco de dados e migrações
"""

import subprocess
import json
import time
import os
import sys
from datetime import datetime

class PlankaDiagnostico:
    def __init__(self):
        self.planka_dir = r"C:\Users\Andre\Desktop\DEV\planka-personalizado"
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
    def executar_comando(self, comando, cwd=None):
        """Executa um comando e retorna o resultado"""
        try:
            resultado = subprocess.run(
                comando,
                cwd=cwd or self.planka_dir,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace',
                shell=True
            )
            return resultado.returncode == 0, resultado.stdout, resultado.stderr
        except Exception as e:
            return False, "", str(e)
    
    def verificar_status_docker(self):
        """Verifica o status dos containers Docker"""
        print("🔍 Verificando status dos containers Docker...")
        
        sucesso, stdout, stderr = self.executar_comando("docker-compose ps")
        if sucesso:
            print("✅ Containers encontrados:")
            print(stdout)
        else:
            print("❌ Erro ao verificar containers:", stderr)
        
        return sucesso
    
    def verificar_logs_postgres(self):
        """Verifica logs específicos do PostgreSQL"""
        print("\n📋 Verificando logs do PostgreSQL...")
        
        sucesso, stdout, stderr = self.executar_comando("docker-compose logs postgres --tail=50")
        if sucesso:
            print("📊 Logs do PostgreSQL:")
            print(stdout)
        else:
            print("❌ Erro ao verificar logs:", stderr)
        
        return sucesso
    
    def verificar_logs_planka(self):
        """Verifica logs específicos do Planka"""
        print("\n📋 Verificando logs do Planka...")
        
        sucesso, stdout, stderr = self.executar_comando("docker-compose logs planka --tail=50")
        if sucesso:
            print("📊 Logs do Planka:")
            print(stdout)
        else:
            print("❌ Erro ao verificar logs:", stderr)
        
        return sucesso
    
    def executar_migracoes(self):
        """Executa as migrações do banco de dados"""
        print("\n🔄 Executando migrações do banco de dados...")
        
        # Primeiro, verifica se o container está rodando
        sucesso, stdout, stderr = self.executar_comando("docker-compose exec -T planka npm run db:migrate")
        if sucesso:
            print("✅ Migrações executadas com sucesso!")
            print(stdout)
        else:
            print("❌ Erro ao executar migrações:", stderr)
            print("Tentando reiniciar containers...")
            
            # Reinicia os containers
            self.reiniciar_containers()
            
            # Tenta novamente
            time.sleep(10)
            sucesso, stdout, stderr = self.executar_comando("docker-compose exec -T planka npm run db:migrate")
            if sucesso:
                print("✅ Migrações executadas com sucesso após reinicialização!")
                print(stdout)
            else:
                print("❌ Erro persistente nas migrações:", stderr)
        
        return sucesso
    
    def reiniciar_containers(self):
        """Reinicia os containers Docker"""
        print("\n🔄 Reiniciando containers...")
        
        sucesso, stdout, stderr = self.executar_comando("docker-compose down")
        if sucesso:
            print("✅ Containers parados")
        else:
            print("❌ Erro ao parar containers:", stderr)
        
        time.sleep(5)
        
        sucesso, stdout, stderr = self.executar_comando("docker-compose up -d")
        if sucesso:
            print("✅ Containers iniciados")
        else:
            print("❌ Erro ao iniciar containers:", stderr)
        
        return sucesso
    
    def limpar_duplicatas_email(self):
        """Limpa registros duplicados de email no banco"""
        print("\n🧹 Limpando registros duplicados de email...")
        
        # Comando SQL para limpar duplicatas
        sql_comando = """
        DELETE FROM user_account 
        WHERE id NOT IN (
            SELECT MIN(id) 
            FROM user_account 
            GROUP BY email
        );
        """
        
        sucesso, stdout, stderr = self.executar_comando(
            f'docker-compose exec -T postgres psql -U postgres -d planka -c "{sql_comando}"'
        )
        
        if sucesso:
            print("✅ Registros duplicados removidos!")
            print(stdout)
        else:
            print("❌ Erro ao limpar duplicatas:", stderr)
        
        return sucesso
    
    def verificar_tabelas(self):
        """Verifica se as tabelas necessárias existem"""
        print("\n📊 Verificando estrutura das tabelas...")
        
        sql_comando = """
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_name IN ('user_account', 'users');
        """
        
        sucesso, stdout, stderr = self.executar_comando(
            f'docker-compose exec -T postgres psql -U postgres -d planka -c "{sql_comando}"'
        )
        
        if sucesso:
            print("📋 Tabelas encontradas:")
            print(stdout)
        else:
            print("❌ Erro ao verificar tabelas:", stderr)
        
        return sucesso
    
    def corrigir_problemas(self):
        """Executa correções automáticas"""
        print("\n🔧 Iniciando correções automáticas...")
        
        # 1. Verificar se containers estão rodando
        if not self.verificar_status_docker():
            print("❌ Containers não estão rodando. Iniciando...")
            self.reiniciar_containers()
            time.sleep(15)
        
        # 2. Verificar estrutura das tabelas
        self.verificar_tabelas()
        
        # 3. Limpar duplicatas de email
        self.limpar_duplicatas_email()
        
        # 4. Executar migrações
        self.executar_migracoes()
        
        # 5. Verificar logs novamente
        print("\n📋 Verificando logs após correções...")
        self.verificar_logs_postgres()
        self.verificar_logs_planka()
        
        print("\n✅ Processo de correção concluído!")
    
    def executar_diagnostico_completo(self):
        """Executa diagnóstico completo do sistema"""
        print("=" * 60)
        print(f"🔍 DIAGNÓSTICO COMPLETO DO PLANKA")
        print(f"⏰ Timestamp: {self.timestamp}")
        print("=" * 60)
        
        # Verificações iniciais
        self.verificar_status_docker()
        self.verificar_logs_postgres()
        self.verificar_logs_planka()
        
        # Perguntar se deve executar correções
        print("\n" + "=" * 60)
        resposta = input("🔧 Deseja executar correções automáticas? (s/n): ").lower().strip()
        
        if resposta in ['s', 'sim', 'y', 'yes']:
            self.corrigir_problemas()
        else:
            print("ℹ️ Correções não executadas. Execute manualmente se necessário.")
        
        print("\n" + "=" * 60)
        print("✅ Diagnóstico concluído!")
        print("=" * 60)

def main():
    """Função principal"""
    try:
        diagnostico = PlankaDiagnostico()
        diagnostico.executar_diagnostico_completo()
    except KeyboardInterrupt:
        print("\n\n❌ Operação cancelada pelo usuário.")
    except Exception as e:
        print(f"\n❌ Erro inesperado: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 