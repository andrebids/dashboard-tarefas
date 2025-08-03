# -*- coding: utf-8 -*-
"""
Configurações de Performance para o Dashboard de Tarefas.
Define timeouts, intervalos e otimizações de performance.
"""

# Configurações de Timeout (em segundos)
TIMEOUTS = {
    # Verificações de dependências
    "dependencias": {
        "docker": 3,
        "docker_compose": 3,
        "nodejs": 3,
        "git": 3
    },
    
    # Verificações de conectividade
    "conectividade": {
        "planka_url": 3,
        "database": 5,
        "servidores": 10
    },
    
    # Operações Docker
    "docker": {
        "status": 5,
        "start": 30,
        "stop": 15,
        "logs": 10
    },
    
    # Operações de repositório
    "repository": {
        "clone": 300,  # 5 minutos
        "pull": 120,   # 2 minutos
        "status": 10
    }
}

# Configurações de Intervalos (em segundos)
INTERVALOS = {
    # Atualizações automáticas
    "atualizacoes": {
        "status_sistema": 5,      # Reduzido de 2 para 5
        "notificacoes": 5,
        "logs": 10
    },
    
    # Cache
    "cache": {
        "status_planka": 30,      # 30 segundos
        "dependencias": 300,      # 5 minutos
        "conectividade": 60,      # 1 minuto
        "processos_docker": 15,   # 15 segundos
        "logs_recentes": 10       # 10 segundos
    }
}

# Configurações de Inicialização
INICIALIZACAO = {
    # Delays para inicialização em background
    "delays": {
        "verificacao_inicial": 1,     # 1 segundo
        "abas_background": 0.5,       # 0.5 segundos
        "entre_abas": 0.2             # 0.2 segundos
    },
    
    # Componentes para inicialização lazy
    "lazy_components": [
        "status_checker",
        "diagnostic_manager",
        "repository_manager"
    ]
}

# Configurações de Performance
PERFORMANCE = {
    # Limites de recursos
    "limites": {
        "max_threads_background": 5,
        "max_cache_items": 100,
        "max_log_lines": 1000
    },
    
    # Otimizações
    "otimizacoes": {
        "usar_cache": True,
        "inicializacao_lazy": True,
        "verificacoes_background": True,
        "timeouts_reduzidos": True
    }
}

# Configurações de Debug
DEBUG = {
    "log_performance": True,
    "medir_tempos": True,
    "mostrar_cache_stats": False
}

def obter_timeout(categoria: str, operacao: str) -> int:
    """
    Obtém o timeout para uma operação específica.
    
    Args:
        categoria: Categoria da operação
        operacao: Nome da operação
        
    Returns:
        Timeout em segundos
    """
    return TIMEOUTS.get(categoria, {}).get(operacao, 10)

def obter_intervalo(categoria: str, operacao: str) -> int:
    """
    Obtém o intervalo para uma operação específica.
    
    Args:
        categoria: Categoria da operação
        operacao: Nome da operação
        
    Returns:
        Intervalo em segundos
    """
    return INTERVALOS.get(categoria, {}).get(operacao, 60)

def obter_delay_inicializacao(operacao: str) -> float:
    """
    Obtém o delay para uma operação de inicialização.
    
    Args:
        operacao: Nome da operação
        
    Returns:
        Delay em segundos
    """
    return INICIALIZACAO["delays"].get(operacao, 0.5)

def is_otimizacao_ativa(otimizacao: str) -> bool:
    """
    Verifica se uma otimização está ativa.
    
    Args:
        otimizacao: Nome da otimização
        
    Returns:
        True se a otimização está ativa
    """
    return PERFORMANCE["otimizacoes"].get(otimizacao, False)

def obter_limite_recurso(recurso: str) -> int:
    """
    Obtém o limite para um recurso específico.
    
    Args:
        recurso: Nome do recurso
        
    Returns:
        Limite do recurso
    """
    return PERFORMANCE["limites"].get(recurso, 100) 