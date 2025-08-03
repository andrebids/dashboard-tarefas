# -*- coding: utf-8 -*-
"""
Otimizador de Performance para o Dashboard de Tarefas.
Implementa inicialização lazy, cache e otimizações de performance.
"""

import time
import threading
from typing import Dict, Any, Optional, Callable
from datetime import datetime, timedelta


class PerformanceOptimizer:
    """
    Otimizador de performance para o dashboard.
    Implementa cache, inicialização lazy e otimizações.
    """
    
    def __init__(self):
        """Inicializa o otimizador de performance."""
        self.cache = {}
        self.cache_timestamps = {}
        self.cache_duration = {
            "status_planka": 30,  # 30 segundos
            "dependencias": 300,  # 5 minutos
            "conectividade": 60,  # 1 minuto
            "processos_docker": 15,  # 15 segundos
            "logs_recentes": 10,  # 10 segundos
        }
        self.lazy_initialized = {}
        self.background_tasks = []
        self.lock = threading.Lock()
    
    def get_cached(self, key: str, default=None):
        """
        Obtém um valor do cache se ainda for válido.
        
        Args:
            key: Chave do cache
            default: Valor padrão se não encontrado ou expirado
            
        Returns:
            Valor do cache ou default
        """
        with self.lock:
            if key in self.cache:
                timestamp = self.cache_timestamps.get(key, 0)
                duration = self.cache_duration.get(key, 60)
                
                if time.time() - timestamp < duration:
                    return self.cache[key]
                else:
                    # Cache expirado, remover
                    del self.cache[key]
                    if key in self.cache_timestamps:
                        del self.cache_timestamps[key]
            
            return default
    
    def set_cached(self, key: str, value: Any, duration: Optional[int] = None):
        """
        Armazena um valor no cache.
        
        Args:
            key: Chave do cache
            value: Valor a armazenar
            duration: Duração em segundos (usa padrão se None)
        """
        with self.lock:
            self.cache[key] = value
            self.cache_timestamps[key] = time.time()
            if duration:
                self.cache_duration[key] = duration
    
    def is_lazy_initialized(self, component: str) -> bool:
        """
        Verifica se um componente foi inicializado de forma lazy.
        
        Args:
            component: Nome do componente
            
        Returns:
            True se já foi inicializado
        """
        return self.lazy_initialized.get(component, False)
    
    def mark_lazy_initialized(self, component: str):
        """
        Marca um componente como inicializado de forma lazy.
        
        Args:
            component: Nome do componente
        """
        self.lazy_initialized[component] = True
    
    def run_background_task(self, task: Callable, *args, **kwargs):
        """
        Executa uma tarefa em background.
        
        Args:
            task: Função a executar
            *args: Argumentos posicionais
            **kwargs: Argumentos nomeados
        """
        def background_wrapper():
            try:
                task(*args, **kwargs)
            except Exception as e:
                print(f"Erro em tarefa background: {e}")
        
        thread = threading.Thread(target=background_wrapper, daemon=True)
        thread.start()
        self.background_tasks.append(thread)
    
    def clear_cache(self, key: Optional[str] = None):
        """
        Limpa o cache.
        
        Args:
            key: Chave específica para limpar (None para limpar tudo)
        """
        with self.lock:
            if key:
                if key in self.cache:
                    del self.cache[key]
                if key in self.cache_timestamps:
                    del self.cache_timestamps[key]
            else:
                self.cache.clear()
                self.cache_timestamps.clear()
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Obtém estatísticas do cache.
        
        Returns:
            Dicionário com estatísticas do cache
        """
        with self.lock:
            return {
                "total_items": len(self.cache),
                "cache_keys": list(self.cache.keys()),
                "lazy_initialized": list(self.lazy_initialized.keys()),
                "background_tasks": len(self.background_tasks)
            }


class LazyInitializer:
    """
    Inicializador lazy para componentes do dashboard.
    """
    
    def __init__(self, optimizer: PerformanceOptimizer):
        """
        Inicializa o inicializador lazy.
        
        Args:
            optimizer: Instância do otimizador de performance
        """
        self.optimizer = optimizer
        self.initialization_callbacks = {}
    
    def register_component(self, name: str, init_callback: Callable):
        """
        Registra um componente para inicialização lazy.
        
        Args:
            name: Nome do componente
            init_callback: Função de inicialização
        """
        self.initialization_callbacks[name] = init_callback
    
    def initialize_component(self, name: str, *args, **kwargs):
        """
        Inicializa um componente se ainda não foi inicializado.
        
        Args:
            name: Nome do componente
            *args: Argumentos para a função de inicialização
            **kwargs: Argumentos nomeados para a função de inicialização
            
        Returns:
            Resultado da inicialização
        """
        if not self.optimizer.is_lazy_initialized(name):
            if name in self.initialization_callbacks:
                # Executar em background para não bloquear a UI
                self.optimizer.run_background_task(
                    self._initialize_component_safe,
                    name, *args, **kwargs
                )
                self.optimizer.mark_lazy_initialized(name)
                return None  # Retorna None para indicar que está sendo inicializado
            else:
                raise ValueError(f"Componente '{name}' não registrado para inicialização lazy")
        
        return True  # Já foi inicializado
    
    def _initialize_component_safe(self, name: str, *args, **kwargs):
        """
        Inicializa um componente de forma segura.
        
        Args:
            name: Nome do componente
            *args: Argumentos posicionais
            **kwargs: Argumentos nomeados
        """
        try:
            callback = self.initialization_callbacks[name]
            callback(*args, **kwargs)
        except Exception as e:
            print(f"Erro ao inicializar componente '{name}': {e}")


class DashboardPerformanceOptimizer:
    """
    Otimizador específico para o dashboard.
    """
    
    def __init__(self):
        """Inicializa o otimizador do dashboard."""
        self.optimizer = PerformanceOptimizer()
        self.lazy_initializer = LazyInitializer(self.optimizer)
        self.startup_time = time.time()
    
    def optimize_startup(self, dashboard_instance):
        """
        Otimiza o processo de inicialização do dashboard.
        
        Args:
            dashboard_instance: Instância do dashboard
        """
        # Registrar componentes para inicialização lazy
        self.lazy_initializer.register_component(
            "status_checker",
            dashboard_instance._initialize_status_checker
        )
        
        self.lazy_initializer.register_component(
            "diagnostic_manager",
            dashboard_instance._initialize_diagnostic_manager
        )
        
        # Configurar verificações em background
        self._setup_background_checks(dashboard_instance)
    
    def _setup_background_checks(self, dashboard_instance):
        """
        Configura verificações em background.
        
        Args:
            dashboard_instance: Instância do dashboard
        """
        # Verificação inicial em background
        self.optimizer.run_background_task(
            self._background_initial_check,
            dashboard_instance
        )
    
    def _background_initial_check(self, dashboard_instance):
        """
        Executa verificação inicial em background.
        
        Args:
            dashboard_instance: Instância do dashboard
        """
        try:
            # Aguardar um pouco para não interferir na inicialização da UI
            time.sleep(1)
            
            # Verificações básicas em background
            self._check_dependencies_cached()
            self._check_planka_status_cached()
            
        except Exception as e:
            print(f"Erro na verificação inicial em background: {e}")
    
    def _check_dependencies_cached(self):
        """Verifica dependências usando cache."""
        cached = self.optimizer.get_cached("dependencias")
        if cached is None:
            # Implementar verificação de dependências aqui
            # Por enquanto, apenas simular
            self.optimizer.set_cached("dependencias", {"docker": True, "nodejs": True})
    
    def _check_planka_status_cached(self):
        """Verifica status do Planka usando cache."""
        cached = self.optimizer.get_cached("status_planka")
        if cached is None:
            # Implementar verificação de status aqui
            # Por enquanto, apenas simular
            self.optimizer.set_cached("status_planka", "offline")
    
    def get_startup_time(self) -> float:
        """
        Obtém o tempo de inicialização.
        
        Returns:
            Tempo de inicialização em segundos
        """
        return time.time() - self.startup_time
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """
        Obtém estatísticas de performance.
        
        Returns:
            Dicionário com estatísticas de performance
        """
        return {
            "startup_time": self.get_startup_time(),
            "cache_stats": self.optimizer.get_cache_stats(),
            "lazy_initialized": list(self.lazy_initializer.initialization_callbacks.keys())
        } 