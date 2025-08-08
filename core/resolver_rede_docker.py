# -*- coding: utf-8 -*-
"""
Script para resolver problemas de rede Docker que impedem a ligação dos containers.
"""

import subprocess
import time
import json
from pathlib import Path
from typing import Dict, List, Tuple


class ResolvedorRedeDocker:
    """
    Classe para resolver problemas de rede Docker.
    """
    
    def __init__(self):
        """Inicializa o resolvedor de rede Docker."""
        pass
    
    def executar_comando(self, comando: List[str], descricao: str = "") -> Tuple[bool, str]:
        """
        Executa um comando e retorna o resultado.
        
        Args:
            comando: Lista com o comando e argumentos
            descricao: Descrição do comando para logging
            
        Returns:
            Tuple com (sucesso, mensagem)
        """
        try:
            print(f"[{time.strftime('%H:%M:%S')}] {descricao}")
            resultado = subprocess.run(
                comando,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace'
            )
            
            if resultado.returncode == 0:
                return True, resultado.stdout.strip()
            else:
                return False, resultado.stderr.strip()
                
        except Exception as e:
            return False, f"Erro ao executar comando: {str(e)}"
    
    def resolver_problema_rede(self) -> Dict:
        """
        Resolve problemas de rede Docker identificados no log.
        
        Returns:
            Dict com resultados da resolução
        """
        resultado = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "passos": [],
            "sucesso": False,
            "erro": None
        }
        
        try:
            # Passo 1: Parar todos os containers do Planka
            sucesso, msg = self.executar_comando(
                ["docker-compose", "-f", "docker-compose-dev.yml", "down"],
                "Parando containers de desenvolvimento"
            )
            resultado["passos"].append({"acao": "parar_dev", "sucesso": sucesso, "mensagem": msg})
            
            sucesso, msg = self.executar_comando(
                ["docker-compose", "-f", "docker-compose-local.yml", "down"],
                "Parando containers de produção"
            )
            resultado["passos"].append({"acao": "parar_prod", "sucesso": sucesso, "mensagem": msg})
            
            # Passo 2: Verificar se existe rede com labels incorretos
            sucesso, msg = self.executar_comando(
                ["docker", "network", "ls"],
                "Verificando redes existentes"
            )
            resultado["passos"].append({"acao": "verificar_redes", "sucesso": sucesso, "mensagem": msg})
            
            # Passo 3: Remover rede problemática se existir
            if "planka-personalizado_default" in msg:
                sucesso, msg = self.executar_comando(
                    ["docker", "network", "rm", "planka-personalizado_default"],
                    "Removendo rede com labels incorretos"
                )
                resultado["passos"].append({"acao": "remover_rede_problematica", "sucesso": sucesso, "mensagem": msg})
            
            # Passo 4: Limpar redes órfãs
            sucesso, msg = self.executar_comando(
                ["docker", "network", "prune", "-f"],
                "Limpando redes não utilizadas"
            )
            resultado["passos"].append({"acao": "limpar_redes", "sucesso": sucesso, "mensagem": msg})
            
            # Passo 5: Limpar containers órfãos
            sucesso, msg = self.executar_comando(
                ["docker", "container", "prune", "-f"],
                "Limpando containers não utilizados"
            )
            resultado["passos"].append({"acao": "limpar_containers", "sucesso": sucesso, "mensagem": msg})
            
            # Passo 6: Aguardar um pouco
            print(f"[{time.strftime('%H:%M:%S')}] Aguardando 3 segundos...")
            time.sleep(3)
            
            # Passo 7: Tentar iniciar os containers novamente (Docker Compose criará a rede automaticamente)
            sucesso, msg = self.executar_comando(
                ["docker-compose", "-f", "docker-compose-dev.yml", "up", "-d"],
                "Iniciando containers de desenvolvimento"
            )
            resultado["passos"].append({"acao": "iniciar_dev", "sucesso": sucesso, "mensagem": msg})
            
            if sucesso:
                resultado["sucesso"] = True
                print(f"[{time.strftime('%H:%M:%S')}] ✅ Resolução concluída com sucesso")
            else:
                resultado["erro"] = "Falha ao iniciar containers após limpeza"
                print(f"[{time.strftime('%H:%M:%S')}] ❌ Erro na resolução: {resultado['erro']}")
            
        except Exception as e:
            resultado["erro"] = f"Erro durante resolução: {str(e)}"
            print(f"[{time.strftime('%H:%M:%S')}] ❌ Erro crítico: {resultado['erro']}")
        
        return resultado
    
    def verificar_status_containers(self) -> Dict:
        """
        Verifica o status atual dos containers.
        
        Returns:
            Dict com status dos containers
        """
        resultado = {
            "containers": [],
            "redes": [],
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Verificar containers
        sucesso, msg = self.executar_comando(
            ["docker", "ps", "-a"],
            "Verificando status dos containers"
        )
        if sucesso:
            resultado["containers"] = msg.split('\n')[1:]  # Remover cabeçalho
        
        # Verificar redes
        sucesso, msg = self.executar_comando(
            ["docker", "network", "ls"],
            "Verificando redes disponíveis"
        )
        if sucesso:
            resultado["redes"] = msg.split('\n')[1:]  # Remover cabeçalho
        
        return resultado
    
    def gerar_relatorio(self, resultado: Dict) -> str:
        """
        Gera um relatório detalhado da resolução.
        
        Args:
            resultado: Resultado da resolução
            
        Returns:
            String com o relatório formatado
        """
        relatorio = f"""
=== RELATÓRIO DE RESOLUÇÃO DE REDE DOCKER ===
Timestamp: {resultado['timestamp']}
Status: {'✅ SUCESSO' if resultado['sucesso'] else '❌ FALHA'}

PASSOS EXECUTADOS:
"""
        
        for i, passo in enumerate(resultado["passos"], 1):
            status = "✅" if passo["sucesso"] else "❌"
            relatorio += f"{i}. {status} {passo['acao']}: {passo['mensagem'][:100]}...\n"
        
        if resultado["erro"]:
            relatorio += f"\nERRO: {resultado['erro']}\n"
        
        relatorio += "\n" + "="*50 + "\n"
        
        return relatorio


def main():
    """Função principal para executar a resolução."""
    print("🔧 Iniciando resolução de problemas de rede Docker...")
    
    resolvedor = ResolvedorRedeDocker()
    
    # Verificar status inicial
    print("\n📊 Status inicial:")
    status_inicial = resolvedor.verificar_status_containers()
    print(f"Containers: {len(status_inicial['containers'])}")
    print(f"Redes: {len(status_inicial['redes'])}")
    
    # Executar resolução
    print("\n🔧 Executando resolução...")
    resultado = resolvedor.resolver_problema_rede()
    
    # Verificar status final
    print("\n📊 Status final:")
    status_final = resolvedor.verificar_status_containers()
    print(f"Containers: {len(status_final['containers'])}")
    print(f"Redes: {len(status_final['redes'])}")
    
    # Gerar relatório
    relatorio = resolvedor.gerar_relatorio(resultado)
    print(relatorio)
    
    # Salvar relatório
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    arquivo_relatorio = f"relatorio_rede_docker_{timestamp}.txt"
    
    try:
        with open(arquivo_relatorio, 'w', encoding='utf-8') as f:
            f.write(relatorio)
        print(f"📄 Relatório salvo em: {arquivo_relatorio}")
    except Exception as e:
        print(f"❌ Erro ao salvar relatório: {e}")
    
    return resultado["sucesso"]


if __name__ == "__main__":
    main()
