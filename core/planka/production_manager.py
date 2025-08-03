# -*- coding: utf-8 -*-
"""
Módulo para gerenciamento específico de produção do Planka.
Gerenciamento de produção com modificações locais e sincronização.
"""

import subprocess
import time
import shutil
import secrets
from typing import Tuple, Dict
from pathlib import Path


class ProductionManager:
    """
    Gerenciador específico de produção do sistema Planka.
    """
    
    def __init__(self, settings):
        """
        Inicializa o gerenciador de produção.
        
        Args:
            settings: Instância das configurações do sistema
        """
        self.settings = settings
        self.planka_dir = Path(settings.obter("planka", "diretorio"))
    
    def executar_producao_com_modificacoes_locais(self) -> Tuple[bool, str]:
        """
        Executa o Planka em produção com modificações locais.
        Implementa as melhores práticas da documentação oficial.
        
        Returns:
            (sucesso, mensagem)
        """
        try:
            self._adicionar_log("🚀 INICIANDO PRODUÇÃO COM MODIFICAÇÕES LOCAIS")
            self._adicionar_log("=" * 60)
            
            # Verificar dependências com detalhes
            self._adicionar_log("📋 VERIFICANDO DEPENDÊNCIAS...")
            from .dependency_checker import DependencyChecker
            dependency_checker = DependencyChecker(self.settings)
            dependencias = dependency_checker.verificar_dependencias()
            
            self._adicionar_log(f"  • Docker instalado: {'✅ Sim' if dependencias['docker'] else '❌ Não'}")
            self._adicionar_log(f"  • Docker rodando: {'✅ Sim' if dependencias['docker_rodando'] else '❌ Não'}")
            self._adicionar_log(f"  • Docker Compose: {'✅ Sim' if dependencias['docker_compose'] else '❌ Não'}")
            self._adicionar_log(f"  • Node.js: {'✅ Sim' if dependencias['nodejs'] else '❌ Não'}")
            self._adicionar_log(f"  • Git: {'✅ Sim' if dependencias['git'] else '❌ Não'}")
            
            if not dependencias["docker"]:
                return False, "Docker não está instalado. Instale o Docker Desktop."
            if not dependencias["docker_rodando"]:
                return False, "Docker não está rodando. Inicie o Docker Desktop e aguarde até estar completamente carregado."
            if not dependencias["docker_compose"]:
                return False, "Docker Compose não encontrado"
            
            # Verificar diretório com detalhes
            self._adicionar_log("📁 VERIFICANDO DIRETÓRIO DO PLANKA...")
            from .utils import PlankaUtils
            utils = PlankaUtils(self.settings)
            if not utils.verificar_diretorio_planka():
                return False, "Diretório do Planka não encontrado"
            
            # Verificar arquivos importantes
            arquivos_importantes = ["docker-compose.yml", "docker-compose-local.yml", "package.json"]
            for arquivo in arquivos_importantes:
                caminho_arquivo = self.planka_dir / arquivo
                self._adicionar_log(f"  • {arquivo}: {'✅ Existe' if caminho_arquivo.exists() else '❌ Não encontrado'}")
            
            # Verificar status atual
            self._adicionar_log("🔍 VERIFICANDO STATUS ATUAL...")
            from .status_monitor import StatusMonitor
            status_monitor = StatusMonitor(self.settings)
            status_atual = status_monitor.verificar_status()
            modo_atual = status_monitor.verificar_modo_ativo()
            self._adicionar_log(f"  • Status atual: {status_atual}")
            self._adicionar_log(f"  • Modo atual: {modo_atual}")
            
            # Verificar containers ativos
            containers_ativos = status_monitor.verificar_containers_ativos()
            self._adicionar_log("  • Containers ativos:")
            for container, ativo in containers_ativos.items():
                self._adicionar_log(f"    - {container}: {'🟢 Ativo' if ativo else '🔴 Parado'}")
            
            # Parar containers existentes
            self._adicionar_log("⏹️ PARANDO CONTAINERS EXISTENTES...")
            from .container_manager import ContainerManager
            container_manager = ContainerManager(self.settings)
            container_manager.parar_planka()
            self._adicionar_log("  • Aguardando 5 segundos para garantir parada...")
            time.sleep(5)
            
            # Verificar se containers pararam
            containers_apos_parar = status_monitor.verificar_containers_ativos()
            self._adicionar_log("  • Status após parar:")
            for container, ativo in containers_apos_parar.items():
                self._adicionar_log(f"    - {container}: {'🟢 Ainda ativo' if ativo else '🔴 Parado'}")
            
            # Gerar secret key adequado
            self._adicionar_log("🔑 GERANDO SECRET KEY...")
            self._adicionar_log("  • Tentando gerar com openssl...")
            secret_key = self._gerar_secret_key()
            if not secret_key:
                return False, "Erro ao gerar secret key"
            
            self._adicionar_log(f"  • Secret key gerado: {secret_key[:20]}...{secret_key[-20:]}")
            
            # Criar docker-compose otimizado para produção local
            self._adicionar_log("📝 CRIANDO CONFIGURAÇÃO DE PRODUÇÃO...")
            self._adicionar_log("  • Modificando docker-compose-local.yml...")
            sucesso_config = self._criar_configuracao_producao_local(secret_key)
            if not sucesso_config:
                return False, "Erro ao criar configuração de produção"
            
            self._adicionar_log("  • Configuração criada com sucesso")
            
            # Fazer build da imagem
            self._adicionar_log("🔨 FAZENDO BUILD DA IMAGEM...")
            self._adicionar_log("  • Comando: docker-compose -f docker-compose-local.yml build --no-cache")
            self._adicionar_log("  • Timeout: 5 minutos")
            sucesso_build = self._fazer_build_producao()
            if not sucesso_build:
                return False, "Erro no build da imagem"
            
            # Iniciar containers
            self._adicionar_log("🚀 INICIANDO CONTAINERS...")
            self._adicionar_log("  • Comando: docker-compose -f docker-compose-local.yml up -d")
            self._adicionar_log("  • Timeout: 1 minuto")
            sucesso_inicio = self._iniciar_containers_producao()
            if not sucesso_inicio:
                return False, "Erro ao iniciar containers"
            
            # Aguardar inicialização
            self._adicionar_log("⏳ AGUARDANDO INICIALIZAÇÃO...")
            self._adicionar_log("  • Aguardando 15 segundos para inicialização completa...")
            time.sleep(15)
            
            # Verificar containers após inicialização
            containers_apos_inicio = status_monitor.verificar_containers_ativos()
            self._adicionar_log("  • Status após inicialização:")
            for container, ativo in containers_apos_inicio.items():
                self._adicionar_log(f"    - {container}: {'🟢 Ativo' if ativo else '🔴 Parado'}")
            
            # Criar admin user se necessário
            self._adicionar_log("👤 VERIFICANDO ADMIN USER...")
            self._adicionar_log("  • Comando: npm run db:create-admin-user")
            sucesso_admin = self._criar_admin_user_se_necessario()
            if not sucesso_admin:
                self._adicionar_log("⚠️ Aviso: Erro ao criar admin user, mas continuando...")
            
            # Verificar se está funcionando
            self._adicionar_log("🔍 VERIFICANDO FUNCIONAMENTO...")
            status_final = status_monitor.verificar_status()
            self._adicionar_log(f"  • Status final: {status_final}")
            
            if status_final == "online":
                self._adicionar_log("✅ PLANKA EM PRODUÇÃO INICIADO COM SUCESSO!")
                self._adicionar_log("🌐 Acesso: http://localhost:3000")
                self._adicionar_log("=" * 60)
                return True, "Planka em produção iniciado com sucesso"
            else:
                self._adicionar_log("❌ PLANKA INICIADO MAS NÃO ESTÁ RESPONDENDO")
                self._adicionar_log("  • Verifique os logs do container para mais detalhes")
                self._adicionar_log("=" * 60)
                return False, "Planka iniciado mas não está respondendo"
                
        except Exception as e:
            self._adicionar_log(f"❌ ERRO CRÍTICO: {str(e)}")
            self._adicionar_log("=" * 60)
            return False, f"Erro ao executar produção: {str(e)}"
    
    def sincronizar_producao_com_desenvolvimento(self) -> Tuple[bool, str]:
        """
        Sincroniza a versão de produção com a de desenvolvimento.
        Cria um novo docker-compose que usa o build local em vez da imagem oficial.
        
        Returns:
            (sucesso, mensagem)
        """
        try:
            # Verificar se o diretório existe
            from .utils import PlankaUtils
            utils = PlankaUtils(self.settings)
            if not utils.verificar_diretorio_planka():
                return False, "Diretório do Planka não encontrado"
            
            # Verificar se docker-compose-dev.yml existe
            dev_compose_file = self.planka_dir / "docker-compose-dev.yml"
            if not dev_compose_file.exists():
                return False, "docker-compose-dev.yml não encontrado"
            
            # Verificar se docker-compose.yml existe (original)
            prod_compose_file = self.planka_dir / "docker-compose.yml"
            if not prod_compose_file.exists():
                return False, "docker-compose.yml não encontrado"
            
            # Fazer backup do arquivo original
            backup_file = self.planka_dir / "docker-compose.yml.backup"
            if not backup_file.exists():
                shutil.copy2(prod_compose_file, backup_file)
            
            # Criar novo docker-compose baseado no dev mas para produção
            novo_compose_content = self._criar_docker_compose_producao()
            
            # Salvar novo arquivo
            with open(prod_compose_file, 'w', encoding='utf-8') as f:
                f.write(novo_compose_content)
            
            return True, "Versão de produção sincronizada com desenvolvimento"
            
        except Exception as e:
            return False, f"Erro ao sincronizar produção com desenvolvimento: {str(e)}"
    
    def restaurar_producao_original(self) -> Tuple[bool, str]:
        """
        Restaura a versão de produção original (usando imagem oficial).
        
        Returns:
            (sucesso, mensagem)
        """
        try:
            # Verificar se o diretório existe
            from .utils import PlankaUtils
            utils = PlankaUtils(self.settings)
            if not utils.verificar_diretorio_planka():
                return False, "Diretório do Planka não encontrado"
            
            # Verificar se backup existe
            backup_file = self.planka_dir / "docker-compose.yml.backup"
            if not backup_file.exists():
                return False, "Backup do docker-compose.yml não encontrado"
            
            # Restaurar backup
            prod_compose_file = self.planka_dir / "docker-compose.yml"
            shutil.copy2(backup_file, prod_compose_file)
            
            return True, "Versão de produção original restaurada"
            
        except Exception as e:
            return False, f"Erro ao restaurar produção original: {str(e)}"
    
    def verificar_sincronizacao_producao(self) -> Dict:
        """
        Verifica se a produção está sincronizada com desenvolvimento.
        
        Returns:
            Dict com informações sobre a sincronização
        """
        try:
            # Verificar se o diretório existe
            from .utils import PlankaUtils
            utils = PlankaUtils(self.settings)
            if not utils.verificar_diretorio_planka():
                return {
                    "sincronizada": False,
                    "motivo": "Diretório do Planka não encontrado",
                    "backup_existe": False,
                    "modo_atual": "desconhecido"
                }
            
            prod_compose_file = self.planka_dir / "docker-compose.yml"
            backup_file = self.planka_dir / "docker-compose.yml.backup"
            
            # Verificar se arquivo atual usa build local
            if prod_compose_file.exists():
                with open(prod_compose_file, 'r', encoding='utf-8') as f:
                    conteudo = f.read()
                    usa_build_local = "build:" in conteudo and "dockerfile: Dockerfile.dev" in conteudo
            else:
                usa_build_local = False
            
            # Verificar modo atual
            from .status_monitor import StatusMonitor
            status_monitor = StatusMonitor(self.settings)
            modo_atual = status_monitor.verificar_modo_ativo()
            
            return {
                "sincronizada": usa_build_local,
                "motivo": "Usa build local" if usa_build_local else "Usa imagem oficial",
                "backup_existe": backup_file.exists(),
                "modo_atual": modo_atual,
                "arquivo_existe": prod_compose_file.exists()
            }
            
        except Exception as e:
            return {
                "sincronizada": False,
                "motivo": f"Erro ao verificar: {str(e)}",
                "backup_existe": False,
                "modo_atual": "erro"
            }
    
    def configurar_producao_sempre_desenvolvimento(self) -> Tuple[bool, str]:
        """
        Configura produção para sempre usar o código de desenvolvimento.
        Isso modifica permanentemente o docker-compose.yml.
        
        Returns:
            (sucesso, mensagem)
        """
        try:
            # Verificar se o diretório existe
            from .utils import PlankaUtils
            utils = PlankaUtils(self.settings)
            if not utils.verificar_diretorio_planka():
                return False, "Diretório do Planka não encontrado"
            
            # Verificar se docker-compose-dev.yml existe
            dev_compose_file = self.planka_dir / "docker-compose-dev.yml"
            if not dev_compose_file.exists():
                return False, "docker-compose-dev.yml não encontrado"
            
            # Verificar se docker-compose.yml existe (original)
            prod_compose_file = self.planka_dir / "docker-compose.yml"
            if not prod_compose_file.exists():
                return False, "docker-compose.yml não encontrado"
            
            # Fazer backup do arquivo original (apenas se não existir)
            backup_file = self.planka_dir / "docker-compose.yml.backup"
            if not backup_file.exists():
                shutil.copy2(prod_compose_file, backup_file)
            
            # Criar novo docker-compose que sempre usa desenvolvimento
            novo_compose_content = self._criar_docker_compose_sempre_desenvolvimento()
            
            # Salvar novo arquivo
            with open(prod_compose_file, 'w', encoding='utf-8') as f:
                f.write(novo_compose_content)
            
            return True, "Produção configurada para sempre usar código de desenvolvimento"
            
        except Exception as e:
            return False, f"Erro ao configurar produção: {str(e)}"
    
    def _gerar_secret_key(self) -> str:
        """
        Gera um secret key adequado usando openssl.
        
        Returns:
            Secret key gerado ou string vazia se erro
        """
        try:
            self._adicionar_log("  • Tentando gerar secret key com openssl...")
            
            comando = ["openssl", "rand", "-hex", "64"]
            self._adicionar_log(f"  • Comando: {' '.join(comando)}")
            self._adicionar_log(f"  • Tamanho da chave: 64 bytes (128 caracteres hex)")
            
            result = subprocess.run(
                comando,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            self._adicionar_log(f"  • Código de retorno: {result.returncode}")
            
            if result.returncode == 0:
                secret_key = result.stdout.strip()
                self._adicionar_log(f"  ✅ Secret key gerado com sucesso via openssl")
                self._adicionar_log(f"  • Tamanho da chave gerada: {len(secret_key)} caracteres")
                self._adicionar_log(f"  • Primeiros 20 caracteres: {secret_key[:20]}...")
                self._adicionar_log(f"  • Últimos 20 caracteres: ...{secret_key[-20:]}")
                return secret_key
            else:
                self._adicionar_log(f"  ⚠️ Erro ao gerar com openssl: {result.stderr}")
                self._adicionar_log(f"  • Tentando fallback com Python secrets...")
                
                # Fallback: gerar secret key simples
                secret_key = secrets.token_hex(64)
                self._adicionar_log(f"  ✅ Secret key gerado com fallback (Python secrets)")
                self._adicionar_log(f"  • Tamanho da chave gerada: {len(secret_key)} caracteres")
                self._adicionar_log(f"  • Primeiros 20 caracteres: {secret_key[:20]}...")
                self._adicionar_log(f"  • Últimos 20 caracteres: ...{secret_key[-20:]}")
                return secret_key
                
        except subprocess.TimeoutExpired:
            self._adicionar_log(f"  ⏰ Timeout ao gerar secret key com openssl")
            self._adicionar_log(f"  • Tentando fallback com Python secrets...")
            
            try:
                secret_key = secrets.token_hex(64)
                self._adicionar_log(f"  ✅ Secret key gerado com fallback (Python secrets)")
                self._adicionar_log(f"  • Tamanho da chave gerada: {len(secret_key)} caracteres")
                return secret_key
            except Exception as e2:
                self._adicionar_log(f"  ❌ Erro no fallback: {e2}")
                return ""
                
        except Exception as e:
            self._adicionar_log(f"  ❌ Erro ao gerar secret key: {e}")
            self._adicionar_log(f"  • Tipo de erro: {type(e).__name__}")
            self._adicionar_log(f"  • Usando secret key padrão...")
            
            # Fallback: secret key padrão
            secret_key = "planka_secret_key_local_development_" + str(int(time.time()))
            self._adicionar_log(f"  ⚠️ Usando secret key padrão (não seguro para produção)")
            self._adicionar_log(f"  • Secret key padrão: {secret_key}")
            return secret_key
    
    def _criar_configuracao_producao_local(self, secret_key: str) -> bool:
        """
        Cria configuração de produção otimizada para modificações locais.
        
        Args:
            secret_key: Secret key gerado
            
        Returns:
            True se sucesso, False caso contrário
        """
        try:
            # Verificar se docker-compose-local.yml existe
            local_compose_file = self.planka_dir / "docker-compose-local.yml"
            if not local_compose_file.exists():
                return False
            
            # Ler arquivo atual
            with open(local_compose_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Substituir secret key
            content = content.replace(
                'SECRET_KEY=your-secret-key-change-this',
                f'SECRET_KEY={secret_key}'
            )
            
            # Adicionar configurações de admin se não existirem
            if 'DEFAULT_ADMIN_EMAIL' not in content:
                admin_config = '''
      - DEFAULT_ADMIN_EMAIL=admin@planka.local
      - DEFAULT_ADMIN_PASSWORD=admin123
      - DEFAULT_ADMIN_NAME=Admin User
      - DEFAULT_ADMIN_USERNAME=admin'''
                
                # Inserir após SECRET_KEY
                content = content.replace(
                    f'- SECRET_KEY={secret_key}',
                    f'- SECRET_KEY={secret_key}{admin_config}'
                )
            
            # Salvar arquivo atualizado
            with open(local_compose_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return True
            
        except Exception as e:
            self._adicionar_log(f"❌ Erro ao criar configuração: {e}")
            return False
    
    def _fazer_build_producao(self) -> bool:
        """
        Faz build da imagem de produção.
        
        Returns:
            True se sucesso, False caso contrário
        """
        try:
            self._adicionar_log("  • Iniciando processo de build...")
            
            comando = ["docker-compose", "-f", "docker-compose-local.yml", "build", "--no-cache"]
            self._adicionar_log(f"  • Comando completo: {' '.join(comando)}")
            self._adicionar_log(f"  • Diretório de trabalho: {self.planka_dir}")
            self._adicionar_log(f"  • Timeout configurado: 300 segundos (5 minutos)")
            
            # Verificar se o arquivo docker-compose-local.yml existe
            arquivo_compose = self.planka_dir / "docker-compose-local.yml"
            if not arquivo_compose.exists():
                self._adicionar_log(f"  ❌ Arquivo docker-compose-local.yml não encontrado em {arquivo_compose}")
                return False
            
            self._adicionar_log(f"  ✅ Arquivo docker-compose-local.yml encontrado")
            
            # Verificar espaço em disco antes do build
            try:
                total, usado, livre = shutil.disk_usage(self.planka_dir)
                livre_gb = livre / (1024**3)
                self._adicionar_log(f"  • Espaço livre em disco: {livre_gb:.2f} GB")
                if livre_gb < 2:
                    self._adicionar_log(f"  ⚠️ Aviso: Pouco espaço em disco ({livre_gb:.2f} GB)")
            except Exception as e:
                self._adicionar_log(f"  ⚠️ Não foi possível verificar espaço em disco: {e}")
            
            self._adicionar_log("  • Executando comando de build...")
            result = subprocess.run(
                comando,
                cwd=self.planka_dir,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minutos
                encoding='utf-8', errors='replace'
            )
            
            self._adicionar_log(f"  • Código de retorno: {result.returncode}")
            self._adicionar_log(f"  • Tamanho da saída stdout: {len(result.stdout)} caracteres")
            self._adicionar_log(f"  • Tamanho da saída stderr: {len(result.stderr)} caracteres")
            
            if result.returncode == 0:
                self._adicionar_log("  ✅ Build concluído com sucesso")
                return True
            else:
                self._adicionar_log("  ❌ Erro no build")
                return False
                
        except subprocess.TimeoutExpired:
            self._adicionar_log("  ⏰ Timeout no build após 5 minutos")
            return False
        except Exception as e:
            self._adicionar_log(f"  ❌ Erro inesperado no build: {e}")
            return False
    
    def _iniciar_containers_producao(self) -> bool:
        """
        Inicia os containers de produção.
        
        Returns:
            True se sucesso, False caso contrário
        """
        try:
            self._adicionar_log("  • Iniciando processo de inicialização dos containers...")
            
            comando = ["docker-compose", "-f", "docker-compose-local.yml", "up", "-d"]
            self._adicionar_log(f"  • Comando completo: {' '.join(comando)}")
            self._adicionar_log(f"  • Diretório de trabalho: {self.planka_dir}")
            self._adicionar_log(f"  • Timeout configurado: 60 segundos")
            
            # Verificar status dos containers antes de iniciar
            self._adicionar_log("  • Verificando status dos containers antes da inicialização...")
            from .status_monitor import StatusMonitor
            status_monitor = StatusMonitor(self.settings)
            containers_antes = status_monitor.verificar_containers_ativos()
            for container, ativo in containers_antes.items():
                self._adicionar_log(f"    - {container}: {'🟢 Ativo' if ativo else '🔴 Parado'}")
            
            # Verificar se há containers rodando que possam conflitar
            containers_rodando = sum(1 for ativo in containers_antes.values() if ativo)
            if containers_rodando > 0:
                self._adicionar_log(f"  ⚠️ Aviso: {containers_rodando} container(s) já está(ão) rodando")
            
            self._adicionar_log("  • Executando comando de inicialização...")
            result = subprocess.run(
                comando,
                cwd=self.planka_dir,
                capture_output=True,
                text=True,
                timeout=60,
                encoding='utf-8', errors='replace'
            )
            
            self._adicionar_log(f"  • Código de retorno: {result.returncode}")
            self._adicionar_log(f"  • Tamanho da saída stdout: {len(result.stdout)} caracteres")
            self._adicionar_log(f"  • Tamanho da saída stderr: {len(result.stderr)} caracteres")
            
            if result.returncode == 0:
                self._adicionar_log("  ✅ Comando de inicialização executado com sucesso")
                
                # Aguardar um pouco para os containers inicializarem
                self._adicionar_log("  • Aguardando 3 segundos para containers inicializarem...")
                time.sleep(3)
                
                # Verificar status dos containers após inicialização
                self._adicionar_log("  • Verificando status dos containers após inicialização...")
                containers_depois = status_monitor.verificar_containers_ativos()
                for container, ativo in containers_depois.items():
                    self._adicionar_log(f"    - {container}: {'🟢 Ativo' if ativo else '🔴 Parado'}")
                
                # Verificar se pelo menos um container está ativo
                containers_ativos = sum(1 for ativo in containers_depois.values() if ativo)
                if containers_ativos > 0:
                    self._adicionar_log(f"  ✅ {containers_ativos} container(s) ativo(s) após inicialização")
                else:
                    self._adicionar_log("  ⚠️ Nenhum container está ativo após inicialização")
                
                return True
            else:
                self._adicionar_log("  ❌ Erro ao executar comando de inicialização")
                return False
                
        except subprocess.TimeoutExpired:
            self._adicionar_log("  ⏰ Timeout ao iniciar containers após 60 segundos")
            return False
        except Exception as e:
            self._adicionar_log(f"  ❌ Erro inesperado ao iniciar containers: {e}")
            return False
    
    def _criar_admin_user_se_necessario(self) -> bool:
        """
        Cria admin user se não existir.
        
        Returns:
            True se sucesso, False caso contrário
        """
        try:
            self._adicionar_log("  • Iniciando verificação/criação do admin user...")
            
            comando = ["docker-compose", "-f", "docker-compose-local.yml", "exec", "-T", "planka", "npm", "run", "db:create-admin-user"]
            self._adicionar_log(f"  • Comando completo: {' '.join(comando)}")
            self._adicionar_log(f"  • Diretório de trabalho: {self.planka_dir}")
            self._adicionar_log(f"  • Timeout configurado: 30 segundos")
            
            # Verificar se o container planka está rodando antes de executar o comando
            self._adicionar_log("  • Verificando se o container planka está rodando...")
            from .status_monitor import StatusMonitor
            status_monitor = StatusMonitor(self.settings)
            containers_ativos = status_monitor.verificar_containers_ativos()
            if not containers_ativos.get("planka", False):
                self._adicionar_log("  ⚠️ Container planka não está rodando")
                self._adicionar_log("  • Não é possível criar admin user sem o container ativo")
                return False
            
            self._adicionar_log("  ✅ Container planka está rodando")
            self._adicionar_log("  • Executando comando para criar/verificar admin user...")
            
            result = subprocess.run(
                comando,
                cwd=self.planka_dir,
                capture_output=True,
                text=True,
                timeout=30,
                encoding='utf-8', errors='replace'
            )
            
            self._adicionar_log(f"  • Código de retorno: {result.returncode}")
            self._adicionar_log(f"  • Tamanho da saída stdout: {len(result.stdout)} caracteres")
            self._adicionar_log(f"  • Tamanho da saída stderr: {len(result.stderr)} caracteres")
            
            # Se retornou 0, admin user foi criado ou já existe
            if result.returncode == 0:
                self._adicionar_log("  ✅ Admin user verificado/criado com sucesso")
                return True
            else:
                self._adicionar_log("  ⚠️ Erro ao verificar/criar admin user")
                
                # Verificar se é um erro comum
                if "already exists" in result.stderr.lower() or "already exists" in result.stdout.lower():
                    self._adicionar_log("  ℹ️ Admin user já existe (não é um erro)")
                    return True
                
                return False
                
        except subprocess.TimeoutExpired:
            self._adicionar_log("  ⏰ Timeout ao verificar/criar admin user após 30 segundos")
            return False
        except Exception as e:
            self._adicionar_log(f"  ❌ Erro inesperado ao verificar/criar admin user: {e}")
            return False
    
    def _criar_docker_compose_producao(self) -> str:
        """
        Cria conteúdo do docker-compose para produção baseado no desenvolvimento.
        
        Returns:
            Conteúdo do arquivo docker-compose
        """
        return '''services:
  planka:
    build:
      context: .
      dockerfile: Dockerfile.dev
    image: planka-producao
    pull_policy: never
    restart: on-failure
    volumes:
      - favicons:/app/public/favicons
      - user-avatars:/app/public/user-avatars
      - background-images:/app/public/background-images
      - attachments:/app/private/attachments
    ports:
      - 3000:1337
    environment:
      - BASE_URL=http://localhost:3000
      - DATABASE_URL=postgresql://postgres@postgres/planka
      - SECRET_KEY=notsecretkey
    depends_on:
      postgres:
        condition: service_healthy

  postgres:
    image: postgres:15-alpine
    restart: on-failure
    volumes:
      - postgres:/var/lib/postgresql/data
    environment:
      - POSTGRES_DB=planka
      - POSTGRES_USER=postgres
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  favicons:
  user-avatars:
  background-images:
  attachments:
  postgres:
'''
    
    def _criar_docker_compose_sempre_desenvolvimento(self) -> str:
        """
        Cria conteúdo do docker-compose que sempre usa desenvolvimento.
        
        Returns:
            Conteúdo do arquivo docker-compose
        """
        return '''services:
  planka:
    build:
      context: .
      dockerfile: Dockerfile.dev
    image: planka-producao-desenvolvimento
    pull_policy: never
    restart: on-failure
    volumes:
      - favicons:/app/public/favicons
      - user-avatars:/app/public/user-avatars
      - background-images:/app/public/background-images
      - attachments:/app/private/attachments
    ports:
      - 3000:1337
    environment:
      - BASE_URL=http://localhost:3000
      - DATABASE_URL=postgresql://postgres@postgres/planka
      - SECRET_KEY=notsecretkey
    depends_on:
      postgres:
        condition: service_healthy

  postgres:
    image: postgres:15-alpine
    restart: on-failure
    volumes:
      - postgres:/var/lib/postgresql/data
    environment:
      - POSTGRES_DB=planka
      - POSTGRES_USER=postgres
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  favicons:
  user-avatars:
  background-images:
  attachments:
  postgres:
'''
    
    def _adicionar_log(self, mensagem: str):
        """
        Adiciona mensagem de log para acompanhamento.
        
        Args:
            mensagem: Mensagem a ser logada
        """
        timestamp = time.strftime("%H:%M:%S")
        print(f"[{timestamp}] {mensagem}")
        
        # Também logar no sistema se disponível
        try:
            from .utils import PlankaUtils
            utils = PlankaUtils(self.settings)
            utils.adicionar_log(mensagem)
        except:
            pass 