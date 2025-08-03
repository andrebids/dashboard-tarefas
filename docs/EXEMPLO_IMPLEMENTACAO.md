# 🔧 Exemplos de Implementação - Refatoração PlankaManager

## 📁 Estrutura de Diretórios Proposta

```
core/
├── planka/
│   ├── __init__.py
│   ├── manager.py
│   ├── dependency_checker.py
│   ├── status_monitor.py
│   ├── container_manager.py
│   ├── production_manager.py
│   ├── docker_compose_generator.py
│   ├── logs_manager.py
│   ├── diagnostic_manager.py
│   ├── backup_manager.py
│   └── utils.py
```

## 🔍 Exemplo 1: Módulo DependencyChecker

### core/planka/dependency_checker.py
```python
# -*- coding: utf-8 -*-
"""
Módulo para verificação de dependências do Planka.
Gerencia cache e verificação de Docker, Node.js, Git, etc.
"""

import subprocess
import time
from typing import Dict
from pathlib import Path

# Importar sistema de cache
try:
    from config.dependency_cache import DependencyCache
except ImportError:
    DependencyCache = None


class DependencyChecker:
    """
    Verificador de dependências do sistema Planka.
    """
    
    def __init__(self, settings):
        """
        Inicializa o verificador de dependências.
        
        Args:
            settings: Instância das configurações do sistema
        """
        self.settings = settings
        
        # Inicializar sistema de cache para dependências
        self.dependency_cache = None
        if DependencyCache:
            cache_duration = settings.obter("performance", "cache_dependencias", 300)
            self.dependency_cache = DependencyCache(cache_duration=cache_duration)
    
    def verificar_dependencias(self, forcar_verificacao: bool = False) -> Dict[str, bool]:
        """
        Verifica se as dependências necessárias estão instaladas.
        Usa cache para evitar verificações constantes.
        
        Args:
            forcar_verificacao: Se True, ignora o cache e força nova verificação
            
        Returns:
            Dict com status de cada dependência
        """
        # Verificar cache primeiro (se disponível e não forçar verificação)
        if self.dependency_cache and not forcar_verificacao:
            dependencias_cache = self.dependency_cache.obter_dependencias_cache()
            if dependencias_cache:
                return dependencias_cache
        
        # Se não há cache válido, fazer verificação completa
        dependencias = {
            "docker": False,
            "docker_rodando": False,
            "nodejs": False,
            "git": False,
            "docker_compose": False
        }
        
        try:
            # Verificar Docker
            dependencias["docker"] = self._verificar_docker()
            
            # Verificar se Docker está rodando
            if dependencias["docker"]:
                dependencias["docker_rodando"] = self._verificar_docker_rodando()
            
            # Verificar Docker Compose
            dependencias["docker_compose"] = self._verificar_docker_compose()
            
            # Verificar Node.js
            dependencias["nodejs"] = self._verificar_nodejs()
            
            # Verificar Git
            dependencias["git"] = self._verificar_git()
            
            # Salvar no cache (se disponível)
            if self.dependency_cache:
                self.dependency_cache.salvar_dependencias_cache(dependencias)
            
        except Exception as e:
            print(f"Erro ao verificar dependências: {e}")
            
        return dependencias
    
    def forcar_verificacao_dependencias(self) -> Dict[str, bool]:
        """
        Força uma nova verificação de dependências, ignorando o cache.
        
        Returns:
            Dict com status de cada dependência
        """
        # Limpar cache se disponível
        if self.dependency_cache:
            self.dependency_cache.forcar_verificacao()
        
        # Fazer verificação completa
        return self.verificar_dependencias(forcar_verificacao=True)
    
    def obter_info_cache_dependencias(self) -> Dict:
        """
        Obtém informações sobre o cache de dependências.
        
        Returns:
            Dict com informações do cache
        """
        if self.dependency_cache:
            return self.dependency_cache.obter_info_cache()
        return {"cache_disponivel": False}
    
    def _verificar_docker(self) -> bool:
        """Verifica se Docker está instalado."""
        try:
            result = subprocess.run(
                ["docker", "--version"], 
                capture_output=True, 
                text=True, 
                timeout=3,
                encoding='utf-8', errors='replace'
            )
            return result.returncode == 0
        except Exception:
            return False
    
    def _verificar_docker_rodando(self) -> bool:
        """Verifica se Docker está rodando."""
        try:
            result = subprocess.run(
                ["docker", "info"], 
                capture_output=True, 
                text=True, 
                timeout=3,
                encoding='utf-8', errors='replace'
            )
            return result.returncode == 0
        except Exception:
            return False
    
    def _verificar_docker_compose(self) -> bool:
        """Verifica se Docker Compose está disponível."""
        try:
            result = subprocess.run(
                ["docker-compose", "--version"], 
                capture_output=True, 
                text=True, 
                timeout=3,
                encoding='utf-8', errors='replace'
            )
            return result.returncode == 0
        except Exception:
            return False
    
    def _verificar_nodejs(self) -> bool:
        """Verifica se Node.js está instalado."""
        try:
            result = subprocess.run(
                ["node", "--version"], 
                capture_output=True, 
                text=True, 
                timeout=3,
                encoding='utf-8', errors='replace'
            )
            return result.returncode == 0
        except Exception:
            return False
    
    def _verificar_git(self) -> bool:
        """Verifica se Git está instalado."""
        try:
            result = subprocess.run(
                ["git", "--version"], 
                capture_output=True, 
                text=True, 
                timeout=3,
                encoding='utf-8', errors='replace'
            )
            return result.returncode == 0
        except Exception:
            return False
```

## 🔍 Exemplo 2: Módulo Utils

### core/planka/utils.py
```python
# -*- coding: utf-8 -*-
"""
Utilitários compartilhados para o sistema Planka.
Funções auxiliares e logging.
"""

import time
from datetime import datetime
from typing import Dict
from pathlib import Path


class PlankaUtils:
    """
    Utilitários compartilhados do sistema Planka.
    """
    
    def __init__(self, settings):
        """
        Inicializa os utilitários.
        
        Args:
            settings: Instância das configurações do sistema
        """
        self.settings = settings
        self.planka_dir = Path(settings.obter("planka", "diretorio"))
        self.planka_url = settings.obter("planka", "url")
        self.planka_porta = settings.obter("planka", "porta")
    
    def adicionar_log(self, mensagem: str):
        """
        Adiciona mensagem de log para acompanhamento.
        
        Args:
            mensagem: Mensagem a ser logada
        """
        timestamp = time.strftime("%H:%M:%S")
        print(f"[{timestamp}] {mensagem}")
        
        # Também logar no sistema se disponível
        try:
            if hasattr(self, 'log_manager'):
                self.log_manager.log_sistema("INFO", mensagem)
        except:
            pass
    
    def obter_informacoes(self) -> Dict:
        """
        Obtém informações básicas do sistema Planka.
        
        Returns:
            Dict com informações do sistema
        """
        info = {
            "diretorio": str(self.planka_dir),
            "url": self.planka_url,
            "porta": self.planka_porta,
            "timestamp": datetime.now().isoformat()
        }
        
        return info
    
    def verificar_diretorio_planka(self) -> bool:
        """
        Verifica se o diretório do Planka existe e tem a estrutura correta.
        
        Returns:
            True se o diretório existe e é válido
        """
        if not self.planka_dir.exists():
            return False
            
        # Verificar arquivos essenciais
        arquivos_essenciais = [
            "docker-compose.yml",
            "package.json",
            "README.md"
        ]
        
        for arquivo in arquivos_essenciais:
            if not (self.planka_dir / arquivo).exists():
                return False
                
        return True
```

## 🔍 Exemplo 3: Módulo Manager Principal

### core/planka/manager.py
```python
# -*- coding: utf-8 -*-
"""
Classe principal do PlankaManager.
Coordena todos os módulos especializados.
"""

from .dependency_checker import DependencyChecker
from .status_monitor import StatusMonitor
from .container_manager import ContainerManager
from .production_manager import ProductionManager
from .logs_manager import LogsManager
from .diagnostic_manager import DiagnosticManager
from .backup_manager import BackupManager
from .utils import PlankaUtils


class PlankaManager:
    """
    Gerenciador principal do Planka personalizado.
    Coordena todos os módulos especializados.
    """
    
    def __init__(self, settings):
        """
        Inicializa o gerenciador do Planka.
        
        Args:
            settings: Instância das configurações do sistema
        """
        self.settings = settings
        
        # Inicializar todos os módulos especializados
        self.utils = PlankaUtils(settings)
        self.dependency_checker = DependencyChecker(settings)
        self.status_monitor = StatusMonitor(settings)
        self.container_manager = ContainerManager(settings)
        self.production_manager = ProductionManager(settings)
        self.logs_manager = LogsManager(settings)
        self.diagnostic_manager = DiagnosticManager(settings)
        self.backup_manager = BackupManager(settings)
        
        # Status interno
        self.status = "desconhecido"
    
    # Métodos públicos que delegam para módulos especializados
    
    def verificar_dependencias(self, forcar_verificacao: bool = False):
        """Delega para DependencyChecker."""
        return self.dependency_checker.verificar_dependencias(forcar_verificacao)
    
    def forcar_verificacao_dependencias(self):
        """Delega para DependencyChecker."""
        return self.dependency_checker.forcar_verificacao_dependencias()
    
    def obter_info_cache_dependencias(self):
        """Delega para DependencyChecker."""
        return self.dependency_checker.obter_info_cache_dependencias()
    
    def verificar_status(self):
        """Delega para StatusMonitor."""
        return self.status_monitor.verificar_status()
    
    def verificar_modo_ativo(self):
        """Delega para StatusMonitor."""
        return self.status_monitor.verificar_modo_ativo()
    
    def verificar_processos_docker(self):
        """Delega para StatusMonitor."""
        return self.status_monitor.verificar_processos_docker()
    
    def verificar_containers_ativos(self):
        """Delega para StatusMonitor."""
        return self.status_monitor.verificar_containers_ativos()
    
    def verificar_diretorio_planka(self):
        """Delega para Utils."""
        return self.utils.verificar_diretorio_planka()
    
    def iniciar_planka(self):
        """Delega para ContainerManager."""
        return self.container_manager.iniciar_planka()
    
    def parar_planka(self):
        """Delega para ContainerManager."""
        return self.container_manager.parar_planka()
    
    def reiniciar_planka(self):
        """Delega para ContainerManager."""
        return self.container_manager.reiniciar_planka()
    
    def modo_desenvolvimento(self):
        """Delega para ContainerManager."""
        return self.container_manager.modo_desenvolvimento()
    
    def parar_modo_desenvolvimento(self):
        """Delega para ContainerManager."""
        return self.container_manager.parar_modo_desenvolvimento()
    
    def obter_logs(self, linhas: int = 50):
        """Delega para LogsManager."""
        return self.logs_manager.obter_logs(linhas)
    
    def backup_database(self):
        """Delega para BackupManager."""
        return self.backup_manager.backup_database()
    
    def obter_informacoes(self):
        """Delega para Utils."""
        return self.utils.obter_informacoes()
    
    def diagnostico_detalhado(self):
        """Delega para DiagnosticManager."""
        return self.diagnostic_manager.diagnostico_detalhado()
    
    def sincronizar_producao_com_desenvolvimento(self):
        """Delega para ProductionManager."""
        return self.production_manager.sincronizar_producao_com_desenvolvimento()
    
    def restaurar_producao_original(self):
        """Delega para ProductionManager."""
        return self.production_manager.restaurar_producao_original()
    
    def verificar_sincronizacao_producao(self):
        """Delega para ProductionManager."""
        return self.production_manager.verificar_sincronizacao_producao()
    
    def configurar_producao_sempre_desenvolvimento(self):
        """Delega para ProductionManager."""
        return self.production_manager.configurar_producao_sempre_desenvolvimento()
    
    def executar_producao_com_modificacoes_locais(self):
        """Delega para ProductionManager."""
        return self.production_manager.executar_producao_com_modificacoes_locais()
    
    def diagnosticar_producao(self):
        """Delega para DiagnosticManager."""
        return self.diagnostic_manager.diagnosticar_producao()
    
    def obter_logs_producao_detalhados(self, linhas: int = 100):
        """Delega para LogsManager."""
        return self.logs_manager.obter_logs_producao_detalhados(linhas)
    
    # Método de compatibilidade para logging
    def _adicionar_log(self, mensagem: str):
        """Delega para Utils."""
        self.utils.adicionar_log(mensagem)
```

## 🔍 Exemplo 4: Arquivo __init__.py

### core/planka/__init__.py
```python
# -*- coding: utf-8 -*-
"""
Módulo Planka - Sistema de gerenciamento do Planka personalizado.
"""

from .manager import PlankaManager

__all__ = ['PlankaManager']
__version__ = '2.0.0'
```

## 🔄 Migração Gradual

### Passo 1: Criar estrutura de diretórios
```bash
mkdir -p core/planka
touch core/planka/__init__.py
```

### Passo 2: Migrar módulo por módulo
1. Criar cada módulo individualmente
2. Testar isoladamente
3. Integrar no manager principal
4. Remover código do arquivo original

### Passo 3: Atualizar imports existentes
```python
# Antes
from core.planka import PlankaManager

# Depois (mantém compatibilidade)
from core.planka import PlankaManager
```

## 🧪 Exemplo de Teste

### tests/test_dependency_checker.py
```python
# -*- coding: utf-8 -*-
"""
Testes para o módulo DependencyChecker.
"""

import unittest
from unittest.mock import patch, MagicMock
from core.planka.dependency_checker import DependencyChecker


class TestDependencyChecker(unittest.TestCase):
    
    def setUp(self):
        """Configuração inicial para cada teste."""
        self.settings = MagicMock()
        self.settings.obter.return_value = 300
        self.checker = DependencyChecker(self.settings)
    
    @patch('subprocess.run')
    def test_verificar_docker_instalado(self, mock_run):
        """Testa verificação de Docker instalado."""
        # Configurar mock
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Docker version 20.10.0"
        mock_run.return_value = mock_result
        
        # Executar teste
        result = self.checker._verificar_docker()
        
        # Verificar resultado
        self.assertTrue(result)
        mock_run.assert_called_once()
    
    @patch('subprocess.run')
    def test_verificar_docker_nao_instalado(self, mock_run):
        """Testa verificação de Docker não instalado."""
        # Configurar mock para simular erro
        mock_run.side_effect = FileNotFoundError()
        
        # Executar teste
        result = self.checker._verificar_docker()
        
        # Verificar resultado
        self.assertFalse(result)
    
    def test_verificar_dependencias_com_cache(self):
        """Testa verificação de dependências com cache."""
        # Configurar cache mock
        self.checker.dependency_cache = MagicMock()
        self.checker.dependency_cache.obter_dependencias_cache.return_value = {
            "docker": True,
            "docker_rodando": True,
            "nodejs": True,
            "git": True,
            "docker_compose": True
        }
        
        # Executar teste
        result = self.checker.verificar_dependencias()
        
        # Verificar resultado
        self.assertEqual(result["docker"], True)
        self.assertEqual(result["nodejs"], True)


if __name__ == '__main__':
    unittest.main()
```

## 📊 Benefícios da Refatoração

### Antes (arquivo único)
- 1906 linhas em um arquivo
- Múltiplas responsabilidades misturadas
- Difícil de manter e debugar
- Testes complexos

### Depois (módulos separados)
- ~200 linhas por módulo
- Responsabilidades bem definidas
- Fácil manutenção e debugging
- Testes unitários simples

## 🎯 Próximos Passos

1. **Implementar módulo por módulo** seguindo os exemplos
2. **Criar testes unitários** para cada módulo
3. **Integrar gradualmente** no manager principal
4. **Validar funcionalidade** completa
5. **Remover arquivo original** após validação

---

**Nota**: Este é um exemplo de implementação. A implementação real deve seguir as especificações exatas do código original, mantendo todas as funcionalidades existentes. 