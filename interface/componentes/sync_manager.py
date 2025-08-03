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
            command=self._sincronizar_producao,
            style="Accent.TButton"
        )
        self.btn_sincronizar.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        
        # Botão configurar sempre desenvolvimento
        self.btn_configurar_sempre = ttk.Button(
            self.frame_botoes,
            text="⚙️ Configurar Sempre Dev",
            command=self._configurar_sempre_desenvolvimento,
            style="Accent.TButton"
        )
        self.btn_configurar_sempre.grid(row=0, column=1, sticky="ew", padx=(5, 0))
        
        # Botão restaurar
        self.btn_restaurar = ttk.Button(
            self.frame_botoes,
            text="↩️ Restaurar Original",
            command=self._restaurar_original
        )
        self.btn_restaurar.grid(row=1, column=0, sticky="ew", padx=(0, 5))
        
        # Botão verificar
        self.btn_verificar = ttk.Button(
            self.frame_botoes,
            text="🔍 Verificar Status",
            command=self._verificar_status
        )
        self.btn_verificar.grid(row=1, column=1, sticky="ew", padx=(5, 0))
        
        # Frame de botões de produção avançada
        self.frame_producao_avancada = ttk.Frame(self)
        self.frame_producao_avancada.grid(row=3, column=0, sticky="ew", padx=10, pady=(5, 10))
        self.frame_producao_avancada.columnconfigure(0, weight=1)
        self.frame_producao_avancada.columnconfigure(1, weight=1)
        
        # Separador visual
        separator = ttk.Separator(self.frame_producao_avancada, orient='horizontal')
        separator.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        
        # Label para seção de produção avançada
        label_producao = ttk.Label(self.frame_producao_avancada, text="🔧 Produção Avançada", 
                                  font=("Arial", 9, "bold"))
        label_producao.grid(row=1, column=0, columnspan=2, sticky="w", pady=(0, 5))
        
        # Botão produção com modificações
        self.btn_producao_modificacoes = ttk.Button(
            self.frame_producao_avancada,
            text="🔧 Produção com Modificações",
            command=self._producao_com_modificacoes,
            style="Accent.TButton"
        )
        self.btn_producao_modificacoes.grid(row=2, column=0, sticky="ew", padx=(0, 5))
        
        # Botão diagnóstico produção
        self.btn_diagnostico_producao = ttk.Button(
            self.frame_producao_avancada,
            text="🔍 Diagnóstico Produção",
            command=self._diagnostico_producao
        )
        self.btn_diagnostico_producao.grid(row=2, column=1, sticky="ew", padx=(5, 0))
    
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
    
    def _configurar_sempre_desenvolvimento(self):
        """Configura produção para sempre usar desenvolvimento."""
        try:
            # Confirmar ação
            resposta = messagebox.askyesno(
                "Configurar Produção para Sempre Usar Desenvolvimento",
                "Isso irá configurar a produção para SEMPRE usar o código de desenvolvimento.\n\n"
                "A partir de agora, sempre que você iniciar a produção, ela usará automaticamente "
                "o código mais recente do desenvolvimento.\n\n"
                "Deseja continuar?"
            )
            
            if resposta:
                # Desabilitar botões durante operação
                self._desabilitar_botoes()
                
                # Executar em thread separada
                thread = threading.Thread(target=self._configurar_sempre_thread)
                thread.daemon = True
                thread.start()
                
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao configurar: {str(e)}")
    
    def _configurar_sempre_thread(self):
        """Executa configuração em thread separada."""
        try:
            # Executar configuração
            self.controller.configurar_producao_sempre_desenvolvimento()
            
            # Aguardar um pouco
            import time
            time.sleep(2)
            
            # Verificar novo status
            status_info = self.controller.verificar_sincronizacao_producao()
            
            # Atualizar interface na thread principal
            self.after(0, lambda: self._finalizar_configuracao_sempre(status_info))
            
        except Exception as e:
            self.after(0, lambda: self._erro_configuracao_sempre(str(e)))
    
    def _finalizar_configuracao_sempre(self, status_info: Dict):
        """Finaliza a configuração."""
        try:
            # Reabilitar botões
            self._habilitar_botoes()
            
            # Atualizar status
            self._atualizar_status_from_info(status_info)
            
            # Mostrar mensagem de sucesso
            if status_info.get("sincronizada", False):
                messagebox.showinfo(
                    "Configuração Concluída",
                    "Produção configurada para sempre usar desenvolvimento!\n\n"
                    "A partir de agora:\n"
                    "✅ Produção sempre usa código de desenvolvimento\n"
                    "✅ Build automático a cada reinicialização\n"
                    "✅ Sempre atualizado com suas modificações\n\n"
                    "Reinicie o Planka para aplicar as mudanças."
                )
            else:
                messagebox.showwarning(
                    "Configuração Falhou",
                    "A configuração não foi concluída com sucesso.\n\n"
                    "Verifique os logs para mais detalhes."
                )
                
        except Exception as e:
            self._erro_configuracao_sempre(str(e))
    
    def _erro_configuracao_sempre(self, erro: str):
        """Trata erro na configuração."""
        try:
            # Reabilitar botões
            self._habilitar_botoes()
            
            # Mostrar erro
            messagebox.showerror("Erro na Configuração", f"Erro: {erro}")
            
        except Exception as e:
            print(f"Erro ao tratar erro de configuração: {str(e)}")

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
            # Reabilitar botões
            self._habilitar_botoes()
            
            # Atualizar status
            self._atualizar_status_from_info(status_info)
            
            # Mostrar mensagem de sucesso
            if status_info.get("sincronizada", False):
                messagebox.showinfo(
                    "Sincronização Concluída",
                    "Produção foi sincronizada com desenvolvimento!\n\n"
                    "Reinicie o Planka para aplicar as mudanças."
                )
            else:
                messagebox.showwarning(
                    "Sincronização Falhou",
                    "A sincronização não foi concluída com sucesso.\n\n"
                    "Verifique os logs para mais detalhes."
                )
                
        except Exception as e:
            self._erro_sincronizacao(str(e))
    
    def _erro_sincronizacao(self, erro: str):
        """Trata erro na sincronização."""
        try:
            # Reabilitar botões
            self._habilitar_botoes()
            
            # Mostrar erro
            messagebox.showerror("Erro na Sincronização", f"Erro: {erro}")
            
        except Exception as e:
            print(f"Erro ao tratar erro de sincronização: {str(e)}")
    
    def _restaurar_original(self):
        """Restaura a versão original."""
        try:
            # Confirmar ação
            resposta = messagebox.askyesno(
                "Confirmar Restauração",
                "Isso irá restaurar o docker-compose.yml original (imagem oficial).\n\n"
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
            # Reabilitar botões
            self._habilitar_botoes()
            
            # Atualizar status
            self._atualizar_status_from_info(status_info)
            
            # Mostrar mensagem de sucesso
            if not status_info.get("sincronizada", True):
                messagebox.showinfo(
                    "Restauração Concluída",
                    "Produção foi restaurada para versão original!\n\n"
                    "Reinicie o Planka para aplicar as mudanças."
                )
            else:
                messagebox.showwarning(
                    "Restauração Falhou",
                    "A restauração não foi concluída com sucesso.\n\n"
                    "Verifique os logs para mais detalhes."
                )
                
        except Exception as e:
            self._erro_restauracao(str(e))
    
    def _erro_restauracao(self, erro: str):
        """Trata erro na restauração."""
        try:
            # Reabilitar botões
            self._habilitar_botoes()
            
            # Mostrar erro
            messagebox.showerror("Erro na Restauração", f"Erro: {erro}")
            
        except Exception as e:
            print(f"Erro ao tratar erro de restauração: {str(e)}")
    
    def _verificar_status(self):
        """Verifica o status atual."""
        try:
            # Desabilitar botão temporariamente
            self.btn_verificar.config(state="disabled")
            
            # Executar em thread separada
            thread = threading.Thread(target=self._verificar_status_thread)
            thread.daemon = True
            thread.start()
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao verificar status: {str(e)}")
            self.btn_verificar.config(state="normal")
    
    def _desabilitar_botoes(self):
        """Desabilita os botões durante operações."""
        try:
            self.btn_sincronizar.config(state="disabled")
            self.btn_restaurar.config(state="disabled")
            self.btn_verificar.config(state="disabled")
            self.btn_configurar_sempre.config(state="disabled")
            self.btn_producao_modificacoes.config(state="disabled")
            self.btn_diagnostico_producao.config(state="disabled")
        except Exception as e:
            print(f"Erro ao desabilitar botões: {str(e)}")
    
    def _habilitar_botoes(self):
        """Habilita os botões após operações."""
        try:
            self.btn_sincronizar.config(state="normal")
            self.btn_restaurar.config(state="normal")
            self.btn_verificar.config(state="normal")
            self.btn_configurar_sempre.config(state="normal")
            self.btn_producao_modificacoes.config(state="normal")
            self.btn_diagnostico_producao.config(state="normal")
        except Exception as e:
            print(f"Erro ao habilitar botões: {str(e)}")
    
    def atualizar_status(self):
        """Atualiza o status da sincronização."""
        try:
            self._verificar_status_inicial()
        except Exception as e:
            print(f"Erro ao atualizar status: {str(e)}")
    
    def _producao_com_modificacoes(self):
        """Executa produção com modificações locais."""
        if not messagebox.askyesno("Produção com Modificações", 
                                  "Deseja executar produção com modificações locais?\n\n"
                                  "• Gera secret key segura automaticamente\n"
                                  "• Configura admin user automaticamente\n"
                                  "• Aplica melhores práticas da documentação\n"
                                  "• Acesso: http://localhost:3000"):
            return
        
        try:
            self._desabilitar_botoes()
            self._atualizar_status("Executando produção com modificações...", "Executando...", "blue")
            
            # Executar em thread separada
            thread = threading.Thread(target=self._executar_producao_modificacoes, daemon=True)
            thread.start()
            
        except Exception as e:
            self._erro_producao_modificacoes(str(e))
    
    def _executar_producao_modificacoes(self):
        """Executa produção com modificações em thread separada."""
        try:
            # Importar o PlankaManager
            from core.planka import PlankaManager
            
            # Criar instância do PlankaManager
            planka_manager = PlankaManager(self.controller.settings)
            
            # Executar produção com modificações
            sucesso, mensagem = planka_manager.executar_producao_com_modificacoes_locais()
            
            if sucesso:
                self._finalizar_producao_modificacoes({"status": "sucesso", "mensagem": mensagem})
            else:
                self._erro_producao_modificacoes(mensagem)
            
        except Exception as e:
            self._erro_producao_modificacoes(str(e))
    
    def _finalizar_producao_modificacoes(self, resultado: Dict):
        """Finaliza execução de produção com modificações."""
        try:
            self._habilitar_botoes()
            self._atualizar_status("Produção com modificações ativa", "Sucesso!", "green")
            
            # Mostrar mensagem de sucesso
            messagebox.showinfo("Sucesso", 
                              f"Produção com modificações iniciada com sucesso!\n\n"
                              f"🌐 Acesso: http://localhost:3000\n"
                              f"👤 Admin user configurado automaticamente\n\n"
                              f"{resultado.get('mensagem', '')}")
            
        except Exception as e:
            self._erro_producao_modificacoes(str(e))
    
    def _erro_producao_modificacoes(self, erro: str):
        """Trata erro na produção com modificações."""
        try:
            self._habilitar_botoes()
            self._atualizar_status("Erro na produção", f"Erro: {erro}", "red")
            
            # Mostrar mensagem de erro
            messagebox.showerror("Erro", f"Erro ao executar produção com modificações:\n\n{erro}")
            
        except Exception as e:
            print(f"Erro ao tratar erro de produção: {str(e)}")
    
    def _diagnostico_producao(self):
        """Executa diagnóstico da configuração de produção."""
        if not messagebox.askyesno("Diagnóstico de Produção", 
                                  "Deseja executar diagnóstico completo da configuração de produção?\n\n"
                                  "• Verifica containers e configurações\n"
                                  "• Analisa logs detalhados\n"
                                  "• Verifica admin user e secret key\n"
                                  "• Testa conectividade"):
            return
        
        try:
            self._desabilitar_botoes()
            self._atualizar_status("Executando diagnóstico...", "Analisando...", "blue")
            
            # Executar em thread separada
            thread = threading.Thread(target=self._executar_diagnostico_producao, daemon=True)
            thread.start()
            
        except Exception as e:
            self._erro_diagnostico_producao(str(e))
    
    def _executar_diagnostico_producao(self):
        """Executa diagnóstico de produção em thread separada."""
        try:
            # Importar o PlankaManager
            from core.planka import PlankaManager
            
            # Criar instância do PlankaManager
            planka_manager = PlankaManager(self.controller.settings)
            
            # Executar diagnóstico
            resultado = planka_manager.diagnosticar_producao()
            
            self._finalizar_diagnostico_producao(resultado)
            
        except Exception as e:
            self._erro_diagnostico_producao(str(e))
    
    def _finalizar_diagnostico_producao(self, resultado: Dict):
        """Finaliza diagnóstico de produção."""
        try:
            self._habilitar_botoes()
            
            # Preparar mensagem de resultado
            status_geral = resultado.get('status_geral', 'N/A')
            containers_ativos = resultado.get('containers_ativos', 0)
            secret_key_valida = resultado.get('secret_key_valida', False)
            admin_user_existe = resultado.get('admin_user_existe', False)
            porta_acessivel = resultado.get('porta_acessivel', False)
            
            problemas = resultado.get('problemas', [])
            
            # Determinar cor do status
            if problemas:
                cor = "red"
                status_texto = "Problemas encontrados"
            else:
                cor = "green"
                status_texto = "Diagnóstico OK"
            
            self._atualizar_status(status_texto, f"Status: {status_geral}", cor)
            
            # Preparar mensagem detalhada
            mensagem = f"📊 Resultados do Diagnóstico:\n\n"
            mensagem += f"• Status geral: {status_geral}\n"
            mensagem += f"• Containers ativos: {containers_ativos}\n"
            mensagem += f"• Secret key válida: {'✅' if secret_key_valida else '❌'}\n"
            mensagem += f"• Admin user existe: {'✅' if admin_user_existe else '❌'}\n"
            mensagem += f"• Porta acessível: {'✅' if porta_acessivel else '❌'}\n\n"
            
            if problemas:
                mensagem += "⚠️ Problemas encontrados:\n"
                for problema in problemas:
                    mensagem += f"• {problema}\n"
            else:
                mensagem += "✅ Nenhum problema encontrado!"
            
            # Mostrar resultado
            messagebox.showinfo("Diagnóstico de Produção", mensagem)
            
        except Exception as e:
            self._erro_diagnostico_producao(str(e))
    
    def _erro_diagnostico_producao(self, erro: str):
        """Trata erro no diagnóstico de produção."""
        try:
            self._habilitar_botoes()
            self._atualizar_status("Erro no diagnóstico", f"Erro: {erro}", "red")
            
            # Mostrar mensagem de erro
            messagebox.showerror("Erro", f"Erro ao executar diagnóstico de produção:\n\n{erro}")
            
        except Exception as e:
            print(f"Erro ao tratar erro de diagnóstico: {str(e)}") 