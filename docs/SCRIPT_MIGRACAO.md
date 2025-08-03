# 🔄 Script de Migração Automatizada

## 📋 Script Python para Migração

### migrate_planka.py
```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de migração automatizada para refatoração do PlankaManager.
Separa o arquivo planka.py em múltiplos módulos especializados.
"""

import os
import shutil
import re
from pathlib import Path
from typing import List, Dict, Tuple


class PlankaMigrator:
    """
    Migrador automatizado para refatoração do PlankaManager.
    """
    
    def __init__(self, base_path: str = "dashboard-tarefas"):
        """
        Inicializa o migrador.
        
        Args:
            base_path: Caminho base do projeto
        """
        self.base_path = Path(base_path)
        self.core_path = self.base_path / "core"
        self.planka_path = self.core_path / "planka"
        self.original_file = self.core_path / "planka.py"
        
        # Mapeamento de métodos para módulos
        self.method_mapping = {
            "dependency_checker": [
                "verificar_dependencias",
                "forcar_verificacao_dependencias", 
                "obter_info_cache_dependencias"
            ],
            "status_monitor": [
                "verificar_status",
                "verificar_modo_ativo",
                "verificar_processos_docker",
                "verificar_containers_ativos"
            ],
            "container_manager": [
                "iniciar_planka",
                "parar_planka", 
                "reiniciar_planka",
                "modo_desenvolvimento",
                "parar_modo_desenvolvimento"
            ],
            "production_manager": [
                "executar_producao_com_modificacoes_locais",
                "sincronizar_producao_com_desenvolvimento",
                "restaurar_producao_original",
                "verificar_sincronizacao_producao",
                "configurar_producao_sempre_desenvolvimento",
                "_gerar_secret_key",
                "_criar_configuracao_producao_local",
                "_fazer_build_producao",
                "_iniciar_containers_producao",
                "_criar_admin_user_se_necessario"
            ],
            "docker_compose_generator": [
                "_criar_docker_compose_producao",
                "_criar_docker_compose_sempre_desenvolvimento"
            ],
            "logs_manager": [
                "obter_logs",
                "obter_logs_producao_detalhados",
                "_obter_logs_producao"
            ],
            "diagnostic_manager": [
                "diagnostico_detalhado",
                "diagnosticar_producao",
                "_verificar_configuracoes_producao",
                "_verificar_container_reiniciando",
                "_verificar_admin_user",
                "_verificar_porta_acessivel"
            ],
            "backup_manager": [
                "backup_database"
            ],
            "utils": [
                "_adicionar_log",
                "obter_informacoes",
                "verificar_diretorio_planka"
            ]
        }
    
    def criar_estrutura_diretorios(self) -> bool:
        """
        Cria a estrutura de diretórios necessária.
        
        Returns:
            True se sucesso, False caso contrário
        """
        try:
            print("📁 Criando estrutura de diretórios...")
            
            # Criar diretório planka
            self.planka_path.mkdir(exist_ok=True)
            print(f"  ✅ Diretório criado: {self.planka_path}")
            
            # Criar __init__.py
            init_file = self.planka_path / "__init__.py"
            if not init_file.exists():
                init_file.write_text(self._gerar_init_content())
                print(f"  ✅ Arquivo criado: {init_file}")
            
            return True
            
        except Exception as e:
            print(f"  ❌ Erro ao criar estrutura: {e}")
            return False
    
    def ler_arquivo_original(self) -> str:
        """
        Lê o conteúdo do arquivo original.
        
        Returns:
            Conteúdo do arquivo
        """
        try:
            print(f"📖 Lendo arquivo original: {self.original_file}")
            return self.original_file.read_text(encoding='utf-8')
        except Exception as e:
            print(f"  ❌ Erro ao ler arquivo: {e}")
            return ""
    
    def extrair_imports(self, content: str) -> List[str]:
        """
        Extrai imports do arquivo original.
        
        Args:
            content: Conteúdo do arquivo
            
        Returns:
            Lista de imports
        """
        imports = []
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            if line.startswith('import ') or line.startswith('from '):
                imports.append(line)
            elif line == '':
                break
        
        return imports
    
    def extrair_classe(self, content: str) -> Tuple[str, str]:
        """
        Extrai a definição da classe PlankaManager.
        
        Args:
            content: Conteúdo do arquivo
            
        Returns:
            (definição da classe, resto do conteúdo)
        """
        # Encontrar início da classe
        class_pattern = r'class PlankaManager:.*?(?=\n\S|\Z)'
        match = re.search(class_pattern, content, re.DOTALL)
        
        if match:
            class_content = match.group(0)
            remaining_content = content[match.end():]
            return class_content, remaining_content
        
        return "", content
    
    def extrair_metodos(self, class_content: str) -> Dict[str, str]:
        """
        Extrai métodos da classe.
        
        Args:
            class_content: Conteúdo da classe
            
        Returns:
            Dict com nome do método e seu conteúdo
        """
        methods = {}
        
        # Padrão para encontrar métodos
        method_pattern = r'def (\w+)\s*\([^)]*\)\s*->?\s*[^:]*:.*?(?=\n\s*def|\Z)'
        matches = re.finditer(method_pattern, class_content, re.DOTALL)
        
        for match in matches:
            method_name = match.group(1)
            method_content = match.group(0)
            methods[method_name] = method_content
        
        return methods
    
    def criar_modulo(self, module_name: str, methods: Dict[str, str], imports: List[str]) -> bool:
        """
        Cria um módulo específico.
        
        Args:
            module_name: Nome do módulo
            methods: Métodos a incluir
            imports: Imports necessários
            
        Returns:
            True se sucesso, False caso contrário
        """
        try:
            print(f"🔧 Criando módulo: {module_name}")
            
            # Filtrar métodos para este módulo
            module_methods = self.method_mapping.get(module_name, [])
            selected_methods = {name: content for name, content in methods.items() 
                              if name in module_methods}
            
            if not selected_methods:
                print(f"  ⚠️ Nenhum método encontrado para {module_name}")
                return True
            
            # Gerar conteúdo do módulo
            content = self._gerar_modulo_content(module_name, selected_methods, imports)
            
            # Salvar arquivo
            module_file = self.planka_path / f"{module_name}.py"
            module_file.write_text(content, encoding='utf-8')
            
            print(f"  ✅ Módulo criado: {module_file}")
            print(f"  📊 Métodos incluídos: {len(selected_methods)}")
            
            return True
            
        except Exception as e:
            print(f"  ❌ Erro ao criar módulo {module_name}: {e}")
            return False
    
    def criar_manager_principal(self, methods: Dict[str, str]) -> bool:
        """
        Cria o manager principal com delegação.
        
        Args:
            methods: Todos os métodos disponíveis
            
        Returns:
            True se sucesso, False caso contrário
        """
        try:
            print("🔧 Criando manager principal...")
            
            content = self._gerar_manager_content(methods)
            
            # Salvar arquivo
            manager_file = self.planka_path / "manager.py"
            manager_file.write_text(content, encoding='utf-8')
            
            print(f"  ✅ Manager criado: {manager_file}")
            
            return True
            
        except Exception as e:
            print(f"  ❌ Erro ao criar manager: {e}")
            return False
    
    def fazer_backup(self) -> bool:
        """
        Faz backup do arquivo original.
        
        Returns:
            True se sucesso, False caso contrário
        """
        try:
            print("💾 Fazendo backup do arquivo original...")
            
            backup_file = self.core_path / "planka.py.backup"
            shutil.copy2(self.original_file, backup_file)
            
            print(f"  ✅ Backup criado: {backup_file}")
            return True
            
        except Exception as e:
            print(f"  ❌ Erro ao fazer backup: {e}")
            return False
    
    def executar_migracao(self) -> bool:
        """
        Executa a migração completa.
        
        Returns:
            True se sucesso, False caso contrário
        """
        print("🚀 Iniciando migração do PlankaManager...")
        print("=" * 60)
        
        # Verificar se arquivo original existe
        if not self.original_file.exists():
            print(f"❌ Arquivo original não encontrado: {self.original_file}")
            return False
        
        # Fazer backup
        if not self.fazer_backup():
            return False
        
        # Criar estrutura de diretórios
        if not self.criar_estrutura_diretorios():
            return False
        
        # Ler arquivo original
        content = self.ler_arquivo_original()
        if not content:
            return False
        
        # Extrair componentes
        imports = self.extrair_imports(content)
        class_content, remaining = self.extrair_classe(content)
        methods = self.extrair_metodos(class_content)
        
        print(f"📊 Estatísticas:")
        print(f"  • Imports encontrados: {len(imports)}")
        print(f"  • Métodos encontrados: {len(methods)}")
        print(f"  • Módulos a criar: {len(self.method_mapping)}")
        
        # Criar módulos
        success_count = 0
        for module_name in self.method_mapping.keys():
            if self.criar_modulo(module_name, methods, imports):
                success_count += 1
        
        # Criar manager principal
        if self.criar_manager_principal(methods):
            success_count += 1
        
        print("=" * 60)
        print(f"✅ Migração concluída!")
        print(f"📊 Módulos criados com sucesso: {success_count}/{len(self.method_mapping) + 1}")
        print(f"📁 Estrutura criada em: {self.planka_path}")
        print(f"💾 Backup salvo em: {self.core_path / 'planka.py.backup'}")
        
        return success_count == len(self.method_mapping) + 1
    
    def _gerar_init_content(self) -> str:
        """Gera conteúdo do __init__.py."""
        return '''# -*- coding: utf-8 -*-
"""
Módulo Planka - Sistema de gerenciamento do Planka personalizado.
"""

from .manager import PlankaManager

__all__ = ['PlankaManager']
__version__ = '2.0.0'
'''
    
    def _gerar_modulo_content(self, module_name: str, methods: Dict[str, str], imports: List[str]) -> str:
        """Gera conteúdo de um módulo específico."""
        class_name = ''.join(word.capitalize() for word in module_name.split('_'))
        
        content = f'''# -*- coding: utf-8 -*-
"""
Módulo {module_name} do sistema Planka.
{self._get_module_description(module_name)}
"""

{chr(10).join(imports)}

# Importar sistema de cache
try:
    from config.dependency_cache import DependencyCache
except ImportError:
    DependencyCache = None


class {class_name}:
    """
    {self._get_class_description(module_name)}
    """
    
    def __init__(self, settings):
        """
        Inicializa o {module_name}.
        
        Args:
            settings: Instância das configurações do sistema
        """
        self.settings = settings
        self.planka_dir = Path(settings.obter("planka", "diretorio"))
        self.planka_url = settings.obter("planka", "url")
        self.planka_porta = settings.obter("planka", "porta")
        
        # Inicializar sistema de cache se necessário
        self.dependency_cache = None
        if DependencyCache and module_name == "dependency_checker":
            cache_duration = settings.obter("performance", "cache_dependencias", 300)
            self.dependency_cache = DependencyCache(cache_duration=cache_duration)

'''
        
        # Adicionar métodos
        for method_name, method_content in methods.items():
            # Remover indentação da classe original
            lines = method_content.split('\n')
            if lines[0].startswith('    def '):
                # Remover 4 espaços de indentação
                method_content = '\n'.join(line[4:] if line.startswith('    ') else line 
                                         for line in lines)
            
            content += f"\n{method_content}\n"
        
        return content
    
    def _gerar_manager_content(self, methods: Dict[str, str]) -> str:
        """Gera conteúdo do manager principal."""
        content = '''# -*- coding: utf-8 -*-
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
'''
        
        # Adicionar métodos de delegação
        for module_name, method_list in self.method_mapping.items():
            for method_name in method_list:
                if method_name in methods:
                    content += f'''
    def {method_name}(self, *args, **kwargs):
        """Delega para {module_name.replace('_', ' ').title()}."""
        return self.{module_name}.{method_name}(*args, **kwargs)
'''
        
        # Adicionar método de compatibilidade para logging
        content += '''
    # Método de compatibilidade para logging
    def _adicionar_log(self, mensagem: str):
        """Delega para Utils."""
        self.utils.adicionar_log(mensagem)
'''
        
        return content
    
    def _get_module_description(self, module_name: str) -> str:
        """Retorna descrição do módulo."""
        descriptions = {
            "dependency_checker": "Gerencia cache e verificação de Docker, Node.js, Git, etc.",
            "status_monitor": "Monitoramento de status do Planka e verificação de containers ativos.",
            "container_manager": "Gerenciamento de containers Docker e controle de modo desenvolvimento vs produção.",
            "production_manager": "Gerenciamento específico de produção com modificações locais.",
            "docker_compose_generator": "Geração de arquivos docker-compose e templates de configuração.",
            "logs_manager": "Gerenciamento de logs e obtenção de logs detalhados.",
            "diagnostic_manager": "Diagnósticos do sistema e verificação de problemas.",
            "backup_manager": "Backup de banco de dados e gerenciamento de arquivos de backup.",
            "utils": "Utilitários compartilhados e funções auxiliares."
        }
        return descriptions.get(module_name, "Funcionalidades específicas do módulo.")
    
    def _get_class_description(self, module_name: str) -> str:
        """Retorna descrição da classe."""
        descriptions = {
            "dependency_checker": "Verificador de dependências do sistema Planka.",
            "status_monitor": "Monitor de status do sistema Planka.",
            "container_manager": "Gerenciador de containers do sistema Planka.",
            "production_manager": "Gerenciador de produção do sistema Planka.",
            "docker_compose_generator": "Gerador de arquivos docker-compose.",
            "logs_manager": "Gerenciador de logs do sistema Planka.",
            "diagnostic_manager": "Gerenciador de diagnósticos do sistema Planka.",
            "backup_manager": "Gerenciador de backups do sistema Planka.",
            "utils": "Utilitários compartilhados do sistema Planka."
        }
        return descriptions.get(module_name, "Classe especializada do sistema Planka.")


def main():
    """Função principal para execução do script."""
    migrator = PlankaMigrator()
    success = migrator.executar_migracao()
    
    if success:
        print("\n🎉 Migração concluída com sucesso!")
        print("📝 Próximos passos:")
        print("  1. Testar todos os módulos criados")
        print("  2. Verificar se todas as funcionalidades continuam funcionando")
        print("  3. Atualizar imports em outros arquivos se necessário")
        print("  4. Remover arquivo original após validação completa")
    else:
        print("\n❌ Migração falhou!")
        print("📝 Verifique os erros acima e tente novamente.")


if __name__ == "__main__":
    main()
```

## 🔧 Como Usar o Script

### 1. Executar Migração
```bash
cd dashboard-tarefas
python docs/SCRIPT_MIGRACAO.md
```

### 2. Verificar Resultado
```bash
ls -la core/planka/
```

### 3. Testar Funcionalidade
```python
# Testar se a importação ainda funciona
from core.planka import PlankaManager
print("✅ Importação funcionando!")
```

## ⚠️ Avisos Importantes

### Antes da Migração
1. **Fazer commit** de todas as mudanças atuais
2. **Criar branch** específica para refatoração
3. **Testar** o script em ambiente de desenvolvimento

### Após a Migração
1. **Testar** todas as funcionalidades existentes
2. **Verificar** se não há quebras de compatibilidade
3. **Validar** que todos os métodos continuam funcionando
4. **Remover** arquivo original apenas após validação completa

## 🔄 Rollback

Se algo der errado, você pode fazer rollback:

```bash
# Restaurar arquivo original
cp core/planka.py.backup core/planka.py

# Remover estrutura criada
rm -rf core/planka/
```

## 📊 Benefícios do Script

1. **Automatização**: Processo totalmente automatizado
2. **Segurança**: Backup automático do arquivo original
3. **Consistência**: Estrutura padronizada para todos os módulos
4. **Rastreabilidade**: Logs detalhados do processo
5. **Reversibilidade**: Possibilidade de rollback fácil

---

**Nota**: Este script é um exemplo. A implementação real deve ser adaptada às necessidades específicas do projeto e testada cuidadosamente antes de ser executada em produção. 