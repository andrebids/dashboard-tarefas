# -*- coding: utf-8 -*-
"""
Sistema de Cache para Verificação de Dependências.
Evita verificações constantes das dependências do sistema.
"""

import time
import json
import os
from typing import Dict, Optional
from datetime import datetime, timedelta

class DependencyCache:
    """
    Sistema de cache para dependências do sistema.
    Armazena resultados de verificações para evitar re-execuções desnecessárias.
    """
    
    def __init__(self, cache_file: str = "dependency_cache.json", cache_duration: int = 300):
        """
        Inicializa o sistema de cache.
        
        Args:
            cache_file: Arquivo para armazenar o cache
            cache_duration: Duração do cache em segundos (padrão: 5 minutos)
        """
        self.cache_file = cache_file
        self.cache_duration = cache_duration
        self.cache_data = self._carregar_cache()
    
    def _carregar_cache(self) -> Dict:
        """Carrega o cache do arquivo."""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Erro ao carregar cache: {e}")
        return {}
    
    def _salvar_cache(self):
        """Salva o cache no arquivo."""
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Erro ao salvar cache: {e}")
    
    def _is_cache_valido(self, timestamp: float) -> bool:
        """Verifica se o cache ainda é válido."""
        agora = time.time()
        return (agora - timestamp) < self.cache_duration
    
    def obter_dependencias_cache(self) -> Optional[Dict[str, bool]]:
        """
        Obtém as dependências do cache se ainda forem válidas.
        
        Returns:
            Dict com status das dependências ou None se cache expirado
        """
        if "dependencias" not in self.cache_data:
            return None
        
        cache_info = self.cache_data["dependencias"]
        timestamp = cache_info.get("timestamp", 0)
        
        if self._is_cache_valido(timestamp):
            return cache_info.get("resultado", {})
        
        return None
    
    def salvar_dependencias_cache(self, dependencias: Dict[str, bool]):
        """
        Salva as dependências no cache.
        
        Args:
            dependencias: Dict com status das dependências
        """
        self.cache_data["dependencias"] = {
            "resultado": dependencias,
            "timestamp": time.time(),
            "data_verificacao": datetime.now().isoformat()
        }
        self._salvar_cache()
    
    def limpar_cache(self):
        """Limpa todo o cache."""
        self.cache_data = {}
        try:
            if os.path.exists(self.cache_file):
                os.remove(self.cache_file)
        except Exception as e:
            print(f"Erro ao limpar cache: {e}")
    
    def forcar_verificacao(self):
        """Força uma nova verificação ignorando o cache."""
        self.cache_data.pop("dependencias", None)
        self._salvar_cache()
    
    def obter_info_cache(self) -> Dict:
        """Obtém informações sobre o cache atual."""
        if "dependencias" not in self.cache_data:
            return {
                "cache_existe": False,
                "ultima_verificacao": None,
                "proxima_verificacao": None
            }
        
        cache_info = self.cache_data["dependencias"]
        timestamp = cache_info.get("timestamp", 0)
        ultima_verificacao = datetime.fromtimestamp(timestamp)
        proxima_verificacao = ultima_verificacao + timedelta(seconds=self.cache_duration)
        
        return {
            "cache_existe": True,
            "ultima_verificacao": ultima_verificacao.isoformat(),
            "proxima_verificacao": proxima_verificacao.isoformat(),
            "cache_valido": self._is_cache_valido(timestamp)
        } 