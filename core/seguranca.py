# -*- coding: utf-8 -*-
"""
Módulo de Segurança - Dashboard de Tarefas
Responsável por validar e gerenciar credenciais de forma segura.
"""

import os
import re
import hashlib
import secrets
from typing import Dict, List, Tuple, Optional


class SegurancaManager:
    """
    Gerenciador de segurança para o Dashboard de Tarefas.
    """
    
    def __init__(self):
        """Inicializa o gerenciador de segurança."""
        self.credenciais_sensiveis = [
            "password", "senha", "token", "secret", "key", "credential"
        ]
        
        self.padroes_proibidos = [
            r"admin123",
            r"postgres",
            r"planka",
            r"password\s*=\s*['\"][^'\"]+['\"]",
            r"senha\s*=\s*['\"][^'\"]+['\"]",
            r"token\s*=\s*['\"][^'\"]+['\"]",
            r"secret\s*=\s*['\"][^'\"]+['\"]"
        ]
    
    def validar_arquivo(self, caminho_arquivo: str) -> Dict:
        """
        Valida um arquivo em busca de credenciais sensíveis.
        
        Args:
            caminho_arquivo: Caminho do arquivo a validar
            
        Returns:
            Dict com resultado da validação
        """
        try:
            with open(caminho_arquivo, 'r', encoding='utf-8') as f:
                conteudo = f.read()
            
            problemas = []
            avisos = []
            
            # Verificar padrões proibidos
            for padrao in self.padroes_proibidos:
                matches = re.findall(padrao, conteudo, re.IGNORECASE)
                if matches:
                    problemas.append(f"Padrão proibido encontrado: {padrao}")
            
            # Verificar credenciais hardcoded
            linhas = conteudo.split('\n')
            for i, linha in enumerate(linhas, 1):
                for credencial in self.credenciais_sensiveis:
                    if credencial in linha.lower() and '=' in linha:
                        # Verificar se não é uma variável de ambiente
                        if not linha.strip().startswith('#') and 'os.getenv' not in linha:
                            avisos.append(f"Linha {i}: Possível credencial hardcoded")
                            break
            
            return {
                "arquivo": caminho_arquivo,
                "valido": len(problemas) == 0,
                "problemas": problemas,
                "avisos": avisos
            }
            
        except Exception as e:
            return {
                "arquivo": caminho_arquivo,
                "valido": False,
                "problemas": [f"Erro ao ler arquivo: {str(e)}"],
                "avisos": []
            }
    
    def validar_diretorio(self, caminho_diretorio: str, extensoes: List[str] = None) -> List[Dict]:
        """
        Valida todos os arquivos de um diretório.
        
        Args:
            caminho_diretorio: Caminho do diretório
            extensoes: Lista de extensões a verificar (ex: ['.py', '.js'])
            
        Returns:
            Lista com resultados da validação
        """
        if extensoes is None:
            extensoes = ['.py', '.js', '.jsx', '.json', '.yml', '.yaml']
        
        resultados = []
        
        for root, dirs, files in os.walk(caminho_diretorio):
            # Ignorar diretórios do Git
            if '.git' in dirs:
                dirs.remove('.git')
            
            for arquivo in files:
                if any(arquivo.endswith(ext) for ext in extensoes):
                    caminho_completo = os.path.join(root, arquivo)
                    resultado = self.validar_arquivo(caminho_completo)
                    if not resultado["valido"] or resultado["avisos"]:
                        resultados.append(resultado)
        
        return resultados
    
    def gerar_chave_secreta(self, tamanho: int = 32) -> str:
        """
        Gera uma chave secreta aleatória.
        
        Args:
            tamanho: Tamanho da chave em caracteres
            
        Returns:
            Chave secreta gerada
        """
        return secrets.token_urlsafe(tamanho)
    
    def hash_senha(self, senha: str) -> str:
        """
        Gera hash de uma senha usando SHA-256.
        
        Args:
            senha: Senha em texto plano
            
        Returns:
            Hash da senha
        """
        return hashlib.sha256(senha.encode()).hexdigest()
    
    def validar_senha(self, senha: str) -> Dict:
        """
        Valida a força de uma senha.
        
        Args:
            senha: Senha a validar
            
        Returns:
            Dict com resultado da validação
        """
        problemas = []
        avisos = []
        
        if len(senha) < 8:
            problemas.append("Senha muito curta (mínimo 8 caracteres)")
        
        if not re.search(r'[A-Z]', senha):
            avisos.append("Considere usar letras maiúsculas")
        
        if not re.search(r'[a-z]', senha):
            avisos.append("Considere usar letras minúsculas")
        
        if not re.search(r'\d', senha):
            avisos.append("Considere usar números")
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', senha):
            avisos.append("Considere usar caracteres especiais")
        
        return {
            "valida": len(problemas) == 0,
            "problemas": problemas,
            "avisos": avisos,
            "forca": self._calcular_forca_senha(senha)
        }
    
    def _calcular_forca_senha(self, senha: str) -> str:
        """
        Calcula a força de uma senha.
        
        Args:
            senha: Senha a avaliar
            
        Returns:
            Nível de força da senha
        """
        pontuacao = 0
        
        # Comprimento
        if len(senha) >= 8:
            pontuacao += 1
        if len(senha) >= 12:
            pontuacao += 1
        
        # Complexidade
        if re.search(r'[A-Z]', senha):
            pontuacao += 1
        if re.search(r'[a-z]', senha):
            pontuacao += 1
        if re.search(r'\d', senha):
            pontuacao += 1
        if re.search(r'[!@#$%^&*(),.?":{}|<>]', senha):
            pontuacao += 1
        
        if pontuacao <= 2:
            return "Fraca"
        elif pontuacao <= 4:
            return "Média"
        elif pontuacao <= 5:
            return "Forte"
        else:
            return "Muito Forte"
    
    def verificar_variaveis_ambiente(self) -> Dict:
        """
        Verifica se as variáveis de ambiente necessárias estão configuradas.
        
        Returns:
            Dict com status das variáveis de ambiente
        """
        variaveis_obrigatorias = [
            "PLANKA_DB_PASSWORD",
            "PLANKA_ADMIN_PASSWORD"
        ]
        
        variaveis_opcionais = [
            "PLANKA_SSH_USERNAME",
            "GITHUB_TOKEN",
            "PLANKA_SECRET_KEY"
        ]
        
        resultado = {
            "obrigatorias": {},
            "opcionais": {},
            "faltando_obrigatorias": [],
            "recomendadas": []
        }
        
        # Verificar obrigatórias
        for var in variaveis_obrigatorias:
            valor = os.getenv(var)
            if valor:
                resultado["obrigatorias"][var] = "✅ Configurada"
            else:
                resultado["obrigatorias"][var] = "❌ Não configurada"
                resultado["faltando_obrigatorias"].append(var)
        
        # Verificar opcionais
        for var in variaveis_opcionais:
            valor = os.getenv(var)
            if valor:
                resultado["opcionais"][var] = "✅ Configurada"
            else:
                resultado["opcionais"][var] = "⚠️ Não configurada"
                resultado["recomendadas"].append(var)
        
        return resultado
    
    def gerar_relatorio_seguranca(self, caminho_projeto: str) -> str:
        """
        Gera um relatório completo de segurança do projeto.
        
        Args:
            caminho_projeto: Caminho do projeto
            
        Returns:
            Relatório de segurança em formato texto
        """
        relatorio = []
        relatorio.append("🔒 RELATÓRIO DE SEGURANÇA")
        relatorio.append("=" * 50)
        relatorio.append("")
        
        # Verificar variáveis de ambiente
        relatorio.append("📋 VARIÁVEIS DE AMBIENTE")
        relatorio.append("-" * 30)
        vars_env = self.verificar_variaveis_ambiente()
        
        relatorio.append("Obrigatórias:")
        for var, status in vars_env["obrigatorias"].items():
            relatorio.append(f"  {var}: {status}")
        
        relatorio.append("")
        relatorio.append("Opcionais:")
        for var, status in vars_env["opcionais"].items():
            relatorio.append(f"  {var}: {status}")
        
        relatorio.append("")
        
        # Validar arquivos
        relatorio.append("📁 VALIDAÇÃO DE ARQUIVOS")
        relatorio.append("-" * 30)
        resultados = self.validar_diretorio(caminho_projeto)
        
        if resultados:
            for resultado in resultados:
                relatorio.append(f"Arquivo: {resultado['arquivo']}")
                if resultado["problemas"]:
                    relatorio.append("  ❌ Problemas:")
                    for problema in resultado["problemas"]:
                        relatorio.append(f"    - {problema}")
                if resultado["avisos"]:
                    relatorio.append("  ⚠️ Avisos:")
                    for aviso in resultado["avisos"]:
                        relatorio.append(f"    - {aviso}")
                relatorio.append("")
        else:
            relatorio.append("✅ Nenhum problema de segurança encontrado nos arquivos")
        
        relatorio.append("")
        relatorio.append("🔧 RECOMENDAÇÕES")
        relatorio.append("-" * 30)
        
        if vars_env["faltando_obrigatorias"]:
            relatorio.append("❌ Configure as variáveis obrigatórias:")
            for var in vars_env["faltando_obrigatorias"]:
                relatorio.append(f"  - {var}")
            relatorio.append("")
        
        if vars_env["recomendadas"]:
            relatorio.append("⚠️ Considere configurar:")
            for var in vars_env["recomendadas"]:
                relatorio.append(f"  - {var}")
            relatorio.append("")
        
        relatorio.append("✅ Boas práticas implementadas:")
        relatorio.append("  - Uso de variáveis de ambiente")
        relatorio.append("  - Validação automática de segurança")
        relatorio.append("  - Documentação de segurança")
        
        return "\n".join(relatorio)


# Instância global do gerenciador de segurança
seguranca_manager = SegurancaManager() 