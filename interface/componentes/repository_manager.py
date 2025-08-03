# -*- coding: utf-8 -*-
"""
Componente de Gestão de Repositório - Controle do repositório Git do Planka.
"""
import tkinter as tk
from tkinter import ttk, messagebox
import threading
from typing import Dict, Callable, Optional

class RepositoryManager:
    """
    Componente de gestão de repositório.
    Responsável pelos botões e ações relacionadas ao Git.
    """
    def __init__(self, parent, repository_manager, log_manager, callback_adicionar_log: Optional[Callable] = None):
        self.parent = parent
        self.repository_manager = repository_manager
        self.log_manager = log_manager
        self.callback_adicionar_log = callback_adicionar_log
        self.thread_operacao = None
        self._criar_interface()
    
    def _criar_interface(self):
        """Cria a interface do componente."""
        # Frame principal
        self.frame = ttk.LabelFrame(self.parent, text="Gestão de Repositório", padding=20)
        
        # Grid de botões
        self.frame_botoes = ttk.Frame(self.frame)
        self.frame_botoes.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        
        # Botões
        self.btn_verificar_dependencias = ttk.Button(
            self.frame_botoes,
            text="Verificar Dependências",
            command=self._verificar_dependencias,
            style="TButton"
        )
        self.btn_verificar_dependencias.grid(row=0, column=0, padx=(0, 10), pady=5)
        
        self.btn_forcar_verificacao = ttk.Button(
            self.frame_botoes,
            text="Forçar Verificação",
            command=self._forcar_verificacao_dependencias,
            style="TButton"
        )
        self.btn_forcar_verificacao.grid(row=0, column=1, padx=(0, 10), pady=5)
        
        self.btn_clone_repositorio = ttk.Button(
            self.frame_botoes,
            text="Clone Repositório",
            command=self._clone_repositorio,
            style="TButton"
        )
        self.btn_clone_repositorio.grid(row=0, column=2, padx=(0, 10), pady=5)
        
        self.btn_pull_repositorio = ttk.Button(
            self.frame_botoes,
            text="Pull Repositório",
            command=self._pull_repositorio,
            style="TButton"
        )
        self.btn_pull_repositorio.grid(row=0, column=3, padx=(0, 10), pady=5)
        
        self.btn_limpar_repositorio = ttk.Button(
            self.frame_botoes,
            text="Limpar Repositório",
            command=self._limpar_repositorio,
            style="TButton"
        )
        self.btn_limpar_repositorio.grid(row=0, column=4, pady=5)
        
        # Frame de informações
        self.frame_info = ttk.LabelFrame(self.frame, text="Informações do Repositório", padding=10)
        self.frame_info.grid(row=1, column=0, sticky="ew", pady=(10, 0))
        
        # Labels de informação
        self.label_diretorio = ttk.Label(self.frame_info, text="Diretório: Verificando...")
        self.label_diretorio.grid(row=0, column=0, sticky="w", pady=2)
        
        self.label_tamanho = ttk.Label(self.frame_info, text="Tamanho: Verificando...")
        self.label_tamanho.grid(row=1, column=0, sticky="w", pady=2)
        
        self.label_estado = ttk.Label(self.frame_info, text="Estado: Verificando...")
        self.label_estado.grid(row=2, column=0, sticky="w", pady=2)
        
        # Atualizar informações iniciais
        self._atualizar_informacoes()
    
    def _verificar_dependencias(self):
        """Verifica as dependências do sistema."""
        if self.thread_operacao and self.thread_operacao.is_alive():
            messagebox.showwarning("Aviso", "Operação em andamento. Aguarde...")
            return
        
        self.thread_operacao = threading.Thread(target=self._executar_verificar_dependencias)
        self.thread_operacao.daemon = True
        self.thread_operacao.start()
    
    def _forcar_verificacao_dependencias(self):
        """Força uma nova verificação de dependências, ignorando o cache."""
        if self.thread_operacao and self.thread_operacao.is_alive():
            messagebox.showwarning("Aviso", "Operação em andamento. Aguarde...")
            return
        
        self.thread_operacao = threading.Thread(target=self._executar_forcar_verificacao_dependencias)
        self.thread_operacao.daemon = True
        self.thread_operacao.start()
    
    def _executar_forcar_verificacao_dependencias(self):
        """Executa a verificação forçada de dependências em thread separada."""
        try:
            self._adicionar_log("Forçando verificação completa das dependências...", "info")
            self._adicionar_log("Cache será ignorado - verificação completa em andamento", "warning")
            
            # Usar o método de forçar verificação do PlankaManager
            try:
                from core.planka import PlankaManager
                planka_manager = PlankaManager(self.repository_manager.settings)
                dependencias = planka_manager.forcar_verificacao_dependencias()
            except:
                # Fallback para o método normal se não conseguir usar o PlankaManager
                dependencias = self.repository_manager.verificar_dependencias()
            
            self._adicionar_log("=== VERIFICAÇÃO FORÇADA DE DEPENDÊNCIAS ===", "info")
            for dependencia, disponivel in dependencias.items():
                status = "✓ Disponível" if disponivel else "✗ Não encontrado"
                self._adicionar_log(f"{dependencia}: {status}", "info" if disponivel else "error")
            
            # Verificar se todas as dependências estão disponíveis
            todas_disponiveis = all(dependencias.values())
            if todas_disponiveis:
                self._adicionar_log("Todas as dependências estão disponíveis!", "success")
            else:
                self._adicionar_log("Algumas dependências estão em falta. Verifique a instalação.", "warning")
            
            self._adicionar_log("Verificação forçada de dependências concluída.", "info")
            
        except Exception as e:
            self._adicionar_log(f"Erro ao forçar verificação de dependências: {str(e)}", "error")
    
    def _executar_verificar_dependencias(self):
        """Executa a verificação de dependências em thread separada."""
        try:
            self._adicionar_log("Verificando dependências do sistema...", "info")
            
            # Verificar se há cache disponível
            try:
                from core.planka import PlankaManager
                planka_manager = PlankaManager(self.repository_manager.settings)
                info_cache = planka_manager.obter_info_cache_dependencias()
                
                if info_cache.get("cache_existe") and info_cache.get("cache_valido"):
                    self._adicionar_log("Usando cache de dependências (verificação otimizada)", "info")
                    self._adicionar_log(f"Última verificação: {info_cache.get('ultima_verificacao', 'N/A')}", "info")
                else:
                    self._adicionar_log("Fazendo verificação completa das dependências", "info")
            except:
                pass
            
            dependencias = self.repository_manager.verificar_dependencias()
            
            self._adicionar_log("=== VERIFICAÇÃO DE DEPENDÊNCIAS ===", "info")
            for dependencia, disponivel in dependencias.items():
                status = "✓ Disponível" if disponivel else "✗ Não encontrado"
                self._adicionar_log(f"{dependencia}: {status}", "info" if disponivel else "error")
            
            # Verificar se todas as dependências estão disponíveis
            todas_disponiveis = all(dependencias.values())
            if todas_disponiveis:
                self._adicionar_log("Todas as dependências estão disponíveis!", "success")
            else:
                self._adicionar_log("Algumas dependências estão em falta. Verifique a instalação.", "warning")
            
            self._adicionar_log("Verificação de dependências concluída.", "info")
            
        except Exception as e:
            self._adicionar_log(f"Erro ao verificar dependências: {str(e)}", "error")
    
    def _clone_repositorio(self):
        """Clona o repositório do Planka."""
        if self.thread_operacao and self.thread_operacao.is_alive():
            messagebox.showwarning("Aviso", "Operação em andamento. Aguarde...")
            return
        
        self.thread_operacao = threading.Thread(target=self._executar_clone_repositorio)
        self.thread_operacao.daemon = True
        self.thread_operacao.start()
    
    def _executar_clone_repositorio(self):
        """Executa o clone do repositório em thread separada."""
        try:
            self._adicionar_log("Iniciando clone do repositório Planka...", "info")
            
            sucesso, mensagem = self.repository_manager.clone_repositorio()
            
            if sucesso:
                self._adicionar_log("Repositório clonado com sucesso!", "success")
                self._adicionar_log(f"Detalhes: {mensagem}", "info")
            else:
                self._adicionar_log(f"Erro ao clonar repositório: {mensagem}", "error")
            
            # Atualizar informações após clone
            self._atualizar_informacoes()
            
        except Exception as e:
            self._adicionar_log(f"Erro inesperado ao clonar repositório: {str(e)}", "error")
    
    def _pull_repositorio(self):
        """Atualiza o repositório do Planka."""
        if self.thread_operacao and self.thread_operacao.is_alive():
            messagebox.showwarning("Aviso", "Operação em andamento. Aguarde...")
            return
        
        self.thread_operacao = threading.Thread(target=self._executar_pull_repositorio)
        self.thread_operacao.daemon = True
        self.thread_operacao.start()
    
    def _executar_pull_repositorio(self):
        """Executa o pull do repositório em thread separada."""
        try:
            self._adicionar_log("Atualizando repositório Planka...", "info")
            
            sucesso, mensagem = self.repository_manager.pull_repositorio()
            
            if sucesso:
                self._adicionar_log("Repositório atualizado com sucesso!", "success")
                self._adicionar_log(f"Detalhes: {mensagem}", "info")
            else:
                self._adicionar_log(f"Erro ao atualizar repositório: {mensagem}", "error")
            
            # Atualizar informações após pull
            self._atualizar_informacoes()
            
        except Exception as e:
            self._adicionar_log(f"Erro inesperado ao atualizar repositório: {str(e)}", "error")
    
    def _limpar_repositorio(self):
        """Limpa o repositório do Planka."""
        if self.thread_operacao and self.thread_operacao.is_alive():
            messagebox.showwarning("Aviso", "Operação em andamento. Aguarde...")
            return
        
        # Confirmar ação
        resposta = messagebox.askyesno(
            "Confirmar Limpeza",
            "Tem certeza que deseja limpar o repositório?\n\nEsta ação irá remover todos os arquivos do diretório Planka."
        )
        
        if not resposta:
            return
        
        self.thread_operacao = threading.Thread(target=self._executar_limpar_repositorio)
        self.thread_operacao.daemon = True
        self.thread_operacao.start()
    
    def _executar_limpar_repositorio(self):
        """Executa a limpeza do repositório em thread separada."""
        try:
            self._adicionar_log("Iniciando limpeza do repositório...", "warning")
            
            sucesso, mensagem = self.repository_manager.limpar_repositorio()
            
            if sucesso:
                self._adicionar_log("Repositório limpo com sucesso!", "success")
                self._adicionar_log(f"Detalhes: {mensagem}", "info")
            else:
                self._adicionar_log(f"Erro ao limpar repositório: {mensagem}", "error")
            
            # Atualizar informações após limpeza
            self._atualizar_informacoes()
            
        except Exception as e:
            self._adicionar_log(f"Erro inesperado ao limpar repositório: {str(e)}", "error")
    
    def _atualizar_informacoes(self):
        """Atualiza as informações do repositório."""
        try:
            info = self.repository_manager.obter_informacoes_repositorio()
            
            # Atualizar labels
            self.label_diretorio.config(text=f"Diretório: {info.get('diretorio', 'N/A')}")
            self.label_tamanho.config(text=f"Tamanho: {info.get('tamanho', 'N/A')}")
            self.label_estado.config(text=f"Estado: {info.get('estado', 'N/A')}")
            
        except Exception as e:
            self.label_diretorio.config(text="Diretório: Erro ao verificar")
            self.label_tamanho.config(text="Tamanho: Erro ao verificar")
            self.label_estado.config(text="Estado: Erro ao verificar")
    
    def _adicionar_log(self, mensagem: str, nivel: str = "info"):
        """Adiciona log à área de logs."""
        if self.callback_adicionar_log:
            self.callback_adicionar_log(mensagem, nivel)
        else:
            self.log_manager.adicionar_log(mensagem, nivel)
    
    def definir_callback_adicionar_log(self, callback: Callable):
        """Define callback para adicionar logs."""
        self.callback_adicionar_log = callback
    
    def obter_widget(self) -> ttk.Frame:
        """Retorna o widget principal do componente."""
        return self.frame
    
    def atualizar_informacoes(self):
        """Atualiza as informações do repositório."""
        self._atualizar_informacoes() 