# -*- coding: utf-8 -*-
"""
Componente de Sincronização - Gerencia sincronização entre produção e desenvolvimento.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
from typing import Dict, Callable


class SyncManager(ttk.LabelFrame):
    """
    Componente para gerenciar sincronização entre produção e desenvolvimento.
    """
    
    def __init__(self, parent, controller, **kwargs):
        """
        Inicializa o componente de sincronização.
        
        Args:
            parent: Widget pai
            controller: Controlador principal
            **kwargs: Argumentos adicionais para ttk.LabelFrame
        """
        super().__init__(parent, text="🔄 Sincronização Produção ↔ Desenvolvimento", **kwargs)
        
        self.parent = parent
        self.controller = controller
        
        # Configurar grid
        self.columnconfigure(0, weight=1)
        
        # Inicializar componentes
        self._criar_componentes()
        
        # Verificar status inicial
        self._verificar_status_inicial()
    
    def _criar_componentes(self):
        """Cria os componentes da interface."""
        # Frame de status
        self.frame_status = ttk.Frame(self)
        self.frame_status.grid(row=0, column=0, sticky="ew", padx=10, pady=5)
        self.frame_status.columnconfigure(1, weight=1)
        
        # Label de status
        self.label_status = ttk.Label(self.frame_status, text="Status:", font=("Arial", 9, "bold"))
        self.label_status.grid(row=0, column=0, sticky="w", padx=(0, 10))
        
        # Label de valor do status
        self.label_status_valor = ttk.Label(self.frame_status, text="Verificando...", foreground="gray")
        self.label_status_valor.grid(row=0, column=1, sticky="w")
        
        # Frame de informações
        self.frame_info = ttk.Frame(self)
        self.frame_info.grid(row=1, column=0, sticky="ew", padx=10, pady=5)
        self.frame_info.columnconfigure(0, weight=1)
        
        # Label de informações
        self.label_info = ttk.Label(self.frame_info, text="", foreground="gray", wraplength=400)
        self.label_info.grid(row=0, column=0, sticky="w")
        
        # Frame de botões
        self.frame_botoes = ttk.Frame(self)
        self.frame_botoes.grid(row=2, column=0, sticky="ew", padx=10, pady=10)
        self.frame_botoes.columnconfigure(0, weight=1)
        self.frame_botoes.columnconfigure(1, weight=1)
        
        # Botão sincronizar
        self.btn_sincronizar = ttk.Button(
            self.frame_botoes,
            text="🔄 Sincronizar Produção",
            command=self._sincronizar_producao
        )
        self.btn_sincronizar.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        
        # Botão restaurar
        self.btn_restaurar = ttk.Button(
            self.frame_botoes,
            text="↩️ Restaurar Original",
            command=self._restaurar_original
        )
        self.btn_restaurar.grid(row=0, column=1, sticky="ew", padx=(5, 0))
        
        # Botão verificar
        self.btn_verificar = ttk.Button(
            self.frame_botoes,
            text="🔍 Verificar Status",
            command=self._verificar_status
        )
        self.btn_verificar.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(5, 0))
    
    def _verificar_status_inicial(self):
        """Verifica o status inicial da sincronização."""
        try:
            # Executar em thread separada para não bloquear a interface
            thread = threading.Thread(target=self._verificar_status_thread)
            thread.daemon = True
            thread.start()
        except Exception as e:
            self._atualizar_status("Erro", f"Erro ao verificar status: {str(e)}", "error")
    
    def _verificar_status_thread(self):
        """Verifica o status em thread separada."""
        try:
            status_info = self.controller.verificar_sincronizacao_producao()
            self._atualizar_status_thread(status_info)
        except Exception as e:
            self._atualizar_status("Erro", f"Erro ao verificar status: {str(e)}", "error")
    
    def _atualizar_status_thread(self, status_info: Dict):
        """Atualiza o status na thread principal."""
        try:
            self.after(0, lambda: self._atualizar_status_from_info(status_info))
        except Exception as e:
            print(f"Erro ao atualizar status: {str(e)}")
    
    def _atualizar_status_from_info(self, status_info: Dict):
        """Atualiza o status baseado nas informações recebidas."""
        try:
            sincronizada = status_info.get("sincronizada", False)
            motivo = status_info.get("motivo", "Desconhecido")
            backup_existe = status_info.get("backup_existe", False)
            modo_atual = status_info.get("modo_atual", "desconhecido")
            
            if sincronizada:
                status_text = "✅ Sincronizada"
                status_color = "green"
                info_text = f"Produção usa código de desenvolvimento\nModo atual: {modo_atual}"
            else:
                status_text = "❌ Não Sincronizada"
                status_color = "red"
                info_text = f"Produção usa imagem oficial\nModo atual: {modo_atual}\nBackup: {'Sim' if backup_existe else 'Não'}"
            
            self._atualizar_status(status_text, info_text, status_color)
            
        except Exception as e:
            self._atualizar_status("Erro", f"Erro ao processar status: {str(e)}", "error")
    
    def _atualizar_status(self, status: str, info: str, cor: str = "black"):
        """Atualiza o status na interface."""
        try:
            self.label_status_valor.config(text=status, foreground=cor)
            self.label_info.config(text=info)
        except Exception as e:
            print(f"Erro ao atualizar status: {str(e)}")
    
    def _sincronizar_producao(self):
        """Sincroniza produção com desenvolvimento."""
        try:
            # Confirmar ação
            resposta = messagebox.askyesno(
                "Confirmar Sincronização",
                "Isso irá modificar o docker-compose.yml para usar o código de desenvolvimento em produção.\n\n"
                "Deseja continuar?"
            )
            
            if resposta:
                # Desabilitar botões durante operação
                self._desabilitar_botoes()
                
                # Executar em thread separada
                thread = threading.Thread(target=self._sincronizar_thread)
                thread.daemon = True
                thread.start()
                
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao sincronizar: {str(e)}")
    
    def _sincronizar_thread(self):
        """Executa sincronização em thread separada."""
        try:
            # Executar sincronização
            self.controller.sincronizar_producao_com_desenvolvimento()
            
            # Aguardar um pouco
            import time
            time.sleep(2)
            
            # Verificar novo status
            status_info = self.controller.verificar_sincronizacao_producao()
            
            # Atualizar interface na thread principal
            self.after(0, lambda: self._finalizar_sincronizacao(status_info))
            
        except Exception as e:
            self.after(0, lambda: self._erro_sincronizacao(str(e)))
    
    def _finalizar_sincronizacao(self, status_info: Dict):
        """Finaliza a sincronização."""
        try:
            self._habilitar_botoes()
            
            if status_info.get("sincronizada", False):
                messagebox.showinfo("Sucesso", "Produção sincronizada com desenvolvimento!")
            else:
                messagebox.showwarning("Aviso", "Sincronização pode não ter sido bem-sucedida.")
            
            # Atualizar status
            self._atualizar_status_from_info(status_info)
            
        except Exception as e:
            print(f"Erro ao finalizar sincronização: {str(e)}")
    
    def _erro_sincronizacao(self, erro: str):
        """Trata erro na sincronização."""
        try:
            self._habilitar_botoes()
            messagebox.showerror("Erro", f"Erro na sincronização: {erro}")
            self._atualizar_status("Erro", f"Erro na sincronização: {erro}", "error")
        except Exception as e:
            print(f"Erro ao tratar erro de sincronização: {str(e)}")
    
    def _restaurar_original(self):
        """Restaura a versão original de produção."""
        try:
            # Confirmar ação
            resposta = messagebox.askyesno(
                "Confirmar Restauração",
                "Isso irá restaurar o docker-compose.yml para usar a imagem oficial.\n\n"
                "Deseja continuar?"
            )
            
            if resposta:
                # Desabilitar botões durante operação
                self._desabilitar_botoes()
                
                # Executar em thread separada
                thread = threading.Thread(target=self._restaurar_thread)
                thread.daemon = True
                thread.start()
                
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao restaurar: {str(e)}")
    
    def _restaurar_thread(self):
        """Executa restauração em thread separada."""
        try:
            # Executar restauração
            self.controller.restaurar_producao_original()
            
            # Aguardar um pouco
            import time
            time.sleep(2)
            
            # Verificar novo status
            status_info = self.controller.verificar_sincronizacao_producao()
            
            # Atualizar interface na thread principal
            self.after(0, lambda: self._finalizar_restauracao(status_info))
            
        except Exception as e:
            self.after(0, lambda: self._erro_restauracao(str(e)))
    
    def _finalizar_restauracao(self, status_info: Dict):
        """Finaliza a restauração."""
        try:
            self._habilitar_botoes()
            
            if not status_info.get("sincronizada", True):
                messagebox.showinfo("Sucesso", "Produção restaurada para versão original!")
            else:
                messagebox.showwarning("Aviso", "Restauração pode não ter sido bem-sucedida.")
            
            # Atualizar status
            self._atualizar_status_from_info(status_info)
            
        except Exception as e:
            print(f"Erro ao finalizar restauração: {str(e)}")
    
    def _erro_restauracao(self, erro: str):
        """Trata erro na restauração."""
        try:
            self._habilitar_botoes()
            messagebox.showerror("Erro", f"Erro na restauração: {erro}")
            self._atualizar_status("Erro", f"Erro na restauração: {erro}", "error")
        except Exception as e:
            print(f"Erro ao tratar erro de restauração: {str(e)}")
    
    def _verificar_status(self):
        """Verifica o status atual."""
        try:
            # Desabilitar botões durante verificação
            self._desabilitar_botoes()
            
            # Executar em thread separada
            thread = threading.Thread(target=self._verificar_status_thread)
            thread.daemon = True
            thread.start()
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao verificar status: {str(e)}")
            self._habilitar_botoes()
    
    def _desabilitar_botoes(self):
        """Desabilita os botões durante operações."""
        try:
            self.btn_sincronizar.config(state="disabled")
            self.btn_restaurar.config(state="disabled")
            self.btn_verificar.config(state="disabled")
        except Exception as e:
            print(f"Erro ao desabilitar botões: {str(e)}")
    
    def _habilitar_botoes(self):
        """Habilita os botões após operações."""
        try:
            self.btn_sincronizar.config(state="normal")
            self.btn_restaurar.config(state="normal")
            self.btn_verificar.config(state="normal")
        except Exception as e:
            print(f"Erro ao habilitar botões: {str(e)}")
    
    def atualizar_status(self):
        """Atualiza o status."""
        self._verificar_status() 