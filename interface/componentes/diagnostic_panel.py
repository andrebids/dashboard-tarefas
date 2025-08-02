# -*- coding: utf-8 -*-
"""
Componente de Painel de Diagnósticos - Diagnósticos do sistema Planka.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
from typing import Dict, Callable, Optional


class DiagnosticPanel:
    """
    Componente de painel de diagnósticos.
    Responsável pelos botões de diagnóstico e área de logs.
    """
    
    def __init__(self, parent, diagnostic_manager, log_manager, 
                 callback_adicionar_log: Optional[Callable] = None):
        """
        Inicializa o componente de painel de diagnósticos.
        
        Args:
            parent: Widget pai
            diagnostic_manager: Instância do DiagnosticManager
            log_manager: Gerenciador de logs
            callback_adicionar_log: Callback para adicionar logs
        """
        self.parent = parent
        self.diagnostic_manager = diagnostic_manager
        self.log_manager = log_manager
        self.callback_adicionar_log = callback_adicionar_log
        
        # Thread para operações longas
        self.thread_operacao = None
        
        # Widgets
        self.btn_diagnostico_completo = None
        self.btn_diagnostico_rapido = None
        self.btn_forcar_reinicio = None
        self.text_logs = None
        
        self._criar_interface()
    
    def _criar_interface(self):
        """Cria a interface do painel de diagnósticos."""
        # Frame principal
        self.frame_diagnosticos = ttk.LabelFrame(self.parent, text="Diagnósticos", padding=20)
        self.frame_diagnosticos.pack(fill=tk.X, pady=(0, 20))
        
        # Frame para botões de diagnóstico
        self.frame_botoes = ttk.Frame(self.frame_diagnosticos)
        self.frame_botoes.pack(fill=tk.X, pady=(0, 10))
        
        # Botão Diagnóstico Completo
        self.btn_diagnostico_completo = ttk.Button(self.frame_botoes, text="🔧 Diagnóstico Completo", 
                                                  command=self._diagnostico_completo)
        self.btn_diagnostico_completo.pack(side=tk.LEFT, padx=(0, 10))
        
        # Botão Diagnóstico Rápido
        self.btn_diagnostico_rapido = ttk.Button(self.frame_botoes, text="⚡ Diagnóstico Rápido", 
                                                command=self._diagnostico_rapido)
        self.btn_diagnostico_rapido.pack(side=tk.LEFT, padx=(0, 10))
        
        # Botão Forçar Reinicialização
        self.btn_forcar_reinicio = ttk.Button(self.frame_botoes, text="🔄 Forçar Reinicialização", 
                                             command=self._forcar_reinicializacao)
        self.btn_forcar_reinicio.pack(side=tk.LEFT, padx=(0, 10))
        
        # Frame para área de logs
        self.frame_logs = ttk.LabelFrame(self.frame_diagnosticos, text="Logs de Diagnóstico", padding=10)
        self.frame_logs.pack(fill=tk.BOTH, expand=True)
        
        # Área de logs
        self.text_logs = tk.Text(self.frame_logs, height=8, font=("Consolas", 9),
                                bg="black", fg="white", wrap=tk.WORD)
        scrollbar = ttk.Scrollbar(self.frame_logs, orient="vertical", command=self.text_logs.yview)
        self.text_logs.configure(yscrollcommand=scrollbar.set)
        
        self.text_logs.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Configurar tags para cores
        self.text_logs.tag_configure("info", foreground="lightblue")
        self.text_logs.tag_configure("warning", foreground="yellow")
        self.text_logs.tag_configure("error", foreground="red")
        self.text_logs.tag_configure("success", foreground="lightgreen")
        
        # Frame de controles dos logs
        self.frame_controles_logs = ttk.Frame(self.frame_logs)
        self.frame_controles_logs.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(self.frame_controles_logs, text="Limpar Logs", 
                  command=self._limpar_logs).pack(side=tk.LEFT)
    
    def _diagnostico_completo(self):
        """Executa um diagnóstico completo do Planka."""
        if self.thread_operacao and self.thread_operacao.is_alive():
            messagebox.showwarning("Aviso", "Operação em andamento. Aguarde...")
            return
        
        self.thread_operacao = threading.Thread(target=self._executar_diagnostico_completo)
        self.thread_operacao.daemon = True
        self.thread_operacao.start()
    
    def _executar_diagnostico_completo(self):
        """Executa o diagnóstico completo em thread separada."""
        try:
            self.log_manager.log_planka("INFO", "Iniciando diagnóstico completo...")
            self._adicionar_log("🔧 Iniciando diagnóstico completo do Planka...", "info")
            
            # Limpar logs anteriores
            self._limpar_logs()
            
            # Executar diagnóstico detalhado
            self._adicionar_log("📋 Executando análise completa do sistema...", "info")
            diagnostico = self.diagnostic_manager.diagnostico_detalhado()
            
            # 1. Mostrar dependências
            self._adicionar_log("\n📦 DEPENDÊNCIAS DO SISTEMA:", "info")
            for dep, status in diagnostico["dependencias"].items():
                icone = "✅" if status else "❌"
                self._adicionar_log(f"  {icone} {dep.upper()}: {'Disponível' if status else 'Não encontrado'}", 
                                  "success" if status else "error")
            
            # 2. Mostrar status do diretório
            self._adicionar_log("\n📁 DIRETÓRIO DO PLANKA:", "info")
            if diagnostico["diretorio"]["valido"]:
                self._adicionar_log(f"  ✅ Diretório válido: {diagnostico['diretorio']['caminho']}", "success")
            else:
                self._adicionar_log(f"  ❌ Diretório inválido: {diagnostico['diretorio']['caminho']}", "error")
            
            # 3. Mostrar processos Docker
            self._adicionar_log("\n🐳 PROCESSOS DOCKER:", "info")
            if diagnostico["docker"]["processos"]:
                for processo in diagnostico["docker"]["processos"]:
                    self._adicionar_log(f"  📦 {processo['nome']}: {processo['status']}", "info")
            else:
                self._adicionar_log("  ⚠️ Nenhum processo Docker encontrado", "warning")
            
            # 4. Mostrar status geral
            self._adicionar_log("\n🌐 STATUS GERAL:", "info")
            status_geral = diagnostico["status_geral"]
            if status_geral["status"] == "online":
                self._adicionar_log("  ✅ Planka está online", "success")
                self._adicionar_log(f"  📊 Modo ativo: {status_geral['modo_ativo']}", "info")
            else:
                self._adicionar_log(f"  ❌ Planka está {status_geral['status']}", "error")
            
            # 5. Mostrar conectividade
            self._adicionar_log("\n🔌 CONECTIVIDADE:", "info")
            conectividade = diagnostico["conectividade"]
            if conectividade.get("acessivel", False):
                self._adicionar_log(f"  ✅ Acessível (HTTP {conectividade['status_code']})", "success")
            else:
                erro = conectividade.get("erro", "Desconhecido")
                self._adicionar_log(f"  ❌ Não acessível: {erro}", "error")
            
            # 6. Mostrar logs
            self._adicionar_log("\n📝 ANÁLISE DE LOGS:", "info")
            logs = diagnostico["logs"]
            if logs.get("disponivel", False):
                self._adicionar_log(f"  📊 Logs disponíveis ({logs['tamanho']} caracteres)", "info")
                
                if logs.get("erros"):
                    self._adicionar_log("  ⚠️ Erros encontrados nos logs:", "warning")
                    for erro in logs["erros"]:
                        self._adicionar_log(f"    • {erro}", "error")
                else:
                    self._adicionar_log("  ✅ Nenhum erro encontrado nos logs", "success")
            else:
                erro = logs.get("erro", "Desconhecido")
                self._adicionar_log(f"  ❌ Não foi possível obter logs: {erro}", "error")
            
            # 7. Mostrar recursos (se disponível)
            if "recursos" in diagnostico:
                self._adicionar_log("\n💻 RECURSOS DO SISTEMA:", "info")
                recursos = diagnostico["recursos"]
                if recursos.get("stats_disponivel", False):
                    self._adicionar_log("  📊 Estatísticas de recursos disponíveis", "info")
                    # Mostrar apenas as primeiras linhas das estatísticas
                    linhas_stats = recursos["output"].split('\n')[:5]
                    for linha in linhas_stats:
                        if linha.strip():
                            self._adicionar_log(f"    {linha}", "info")
                else:
                    erro = recursos.get("erro", "Desconhecido")
                    self._adicionar_log(f"  ⚠️ Estatísticas não disponíveis: {erro}", "warning")
            
            # 8. Relatório final
            self._adicionar_log("\n📊 RELATÓRIO FINAL", "info")
            
            problemas = diagnostico["problemas"]
            sugestoes = diagnostico["sugestoes"]
            
            if problemas:
                self._adicionar_log("  ❌ PROBLEMAS IDENTIFICADOS:", "error")
                for problema in problemas:
                    self._adicionar_log(f"    • {problema}", "error")
                
                self._adicionar_log("\n💡 SUGESTÕES DE CORREÇÃO:", "info")
                for sugestao in sugestoes:
                    self._adicionar_log(f"    • {sugestao}", "info")
                
                # Resumo
                self._adicionar_log(f"\n📈 RESUMO: {len(problemas)} problema(s) encontrado(s)", "warning")
            else:
                self._adicionar_log("  ✅ SISTEMA FUNCIONANDO PERFEITAMENTE!", "success")
                self._adicionar_log("  🎉 Todos os componentes estão operacionais", "success")
            
            # 9. Informações adicionais
            self._adicionar_log(f"\n⏰ Diagnóstico executado em: {diagnostico['timestamp']}", "info")
            self._adicionar_log("🔧 Diagnóstico completo finalizado!", "success")
            
            self.log_manager.log_planka("SUCCESS", "Diagnóstico completo finalizado")
            
        except Exception as e:
            self._adicionar_log(f"❌ Erro durante diagnóstico: {str(e)}", "error")
            self.log_manager.log_planka("ERROR", f"Erro durante diagnóstico: {e}")
    
    def _diagnostico_rapido(self):
        """Executa um diagnóstico rápido do Planka."""
        if self.thread_operacao and self.thread_operacao.is_alive():
            messagebox.showwarning("Aviso", "Operação em andamento. Aguarde...")
            return
        
        self.thread_operacao = threading.Thread(target=self._executar_diagnostico_rapido)
        self.thread_operacao.daemon = True
        self.thread_operacao.start()
    
    def _executar_diagnostico_rapido(self):
        """Executa diagnóstico rápido focado em problemas comuns."""
        try:
            self.log_manager.log_planka("INFO", "Iniciando diagnóstico rápido...")
            self._adicionar_log("⚡ Iniciando diagnóstico rápido...", "info")
            
            # Limpar logs anteriores
            self._limpar_logs()
            
            # Executar diagnóstico rápido
            resultado = self.diagnostic_manager.diagnostico_rapido()
            
            problemas_encontrados = resultado["problemas"]
            sugestoes = resultado["sugestoes"]
            
            # Relatório final
            self._adicionar_log("\n📊 RELATÓRIO RÁPIDO", "info")
            
            if problemas_encontrados:
                self._adicionar_log("  ❌ PROBLEMAS ENCONTRADOS:", "error")
                for problema in problemas_encontrados:
                    self._adicionar_log(f"    • {problema}", "error")
                
                self._adicionar_log("\n💡 SUGESTÕES:", "info")
                for sugestao in sugestoes:
                    self._adicionar_log(f"    • {sugestao}", "info")
                
                self._adicionar_log(f"\n📈 Total: {len(problemas_encontrados)} problema(s)", "warning")
            else:
                self._adicionar_log("  ✅ Nenhum problema crítico encontrado!", "success")
                self._adicionar_log("  💡 Se o Planka ainda não carrega, aguarde alguns minutos", "info")
            
            self._adicionar_log("\n⚡ Diagnóstico rápido finalizado!", "success")
            self.log_manager.log_planka("SUCCESS", "Diagnóstico rápido finalizado")
            
        except Exception as e:
            self._adicionar_log(f"❌ Erro durante diagnóstico rápido: {str(e)}", "error")
            self.log_manager.log_planka("ERROR", f"Erro durante diagnóstico rápido: {e}")
    
    def _forcar_reinicializacao(self):
        """Força uma reinicialização completa do Planka."""
        if self.thread_operacao and self.thread_operacao.is_alive():
            messagebox.showwarning("Aviso", "Operação em andamento. Aguarde...")
            return
        
        # Confirmar ação
        if messagebox.askyesno("Forçar Reinicialização", 
                              "Deseja forçar uma reinicialização completa do Planka?\n\n"
                              "Isso irá:\n"
                              "• Parar todos os containers\n"
                              "• Limpar recursos Docker\n"
                              "• Reiniciar o Planka\n\n"
                              "Esta operação pode demorar alguns minutos."):
            
            self.thread_operacao = threading.Thread(target=self._executar_forcar_reinicializacao)
            self.thread_operacao.daemon = True
            self.thread_operacao.start()
    
    def _executar_forcar_reinicializacao(self):
        """Executa a reinicialização forçada em thread separada."""
        try:
            self.log_manager.log_planka("INFO", "Iniciando reinicialização forçada...")
            self._adicionar_log("🔄 Iniciando reinicialização forçada...", "info")
            
            # Limpar logs anteriores
            self._limpar_logs()
            
            # Executar reinicialização forçada
            sucesso, mensagem = self.diagnostic_manager.forcar_reinicializacao()
            
            if sucesso:
                self._adicionar_log("  ✅ Reinicialização forçada concluída com sucesso!", "success")
                self._adicionar_log("  💡 Aguarde alguns minutos para o Planka estar totalmente disponível", "info")
            else:
                self._adicionar_log(f"  ❌ Erro na reinicialização: {mensagem}", "error")
            
            self._adicionar_log("\n🔄 Reinicialização forçada finalizada!", "success")
            self.log_manager.log_planka("SUCCESS", "Reinicialização forçada finalizada")
            
        except Exception as e:
            self._adicionar_log(f"❌ Erro durante reinicialização forçada: {str(e)}", "error")
            self.log_manager.log_planka("ERROR", f"Erro durante reinicialização forçada: {e}")
    
    def _limpar_logs(self):
        """Limpa os logs do painel de diagnósticos."""
        if self.text_logs:
            self.text_logs.delete(1.0, tk.END)
    
    def _adicionar_log(self, mensagem: str, nivel: str = "info"):
        """
        Adiciona um log à área de texto.
        
        Args:
            mensagem: Mensagem a adicionar
            nivel: Nível do log (info, warning, error, success)
        """
        if self.text_logs:
            try:
                import datetime
                timestamp = datetime.datetime.now().strftime("%H:%M:%S")
                log_entry = f"[{timestamp}] {mensagem}\n"
                
                # Agendar inserção na thread principal
                self.frame_diagnosticos.after(0, lambda: self._inserir_log_ui(log_entry, nivel))
                
            except Exception as e:
                self.log_manager.log_sistema("ERROR", f"Erro ao adicionar log: {e}")
    
    def _inserir_log_ui(self, log_entry: str, nivel: str):
        """Insere log na UI (deve ser chamado na thread principal)."""
        try:
            self.text_logs.insert(tk.END, log_entry, nivel)
            self.text_logs.see(tk.END)
        except Exception as e:
            self.log_manager.log_sistema("ERROR", f"Erro ao inserir log na UI: {e}")
    
    def definir_callback_adicionar_log(self, callback: Callable):
        """
        Define o callback para adicionar logs.
        
        Args:
            callback: Função a ser chamada para adicionar logs
        """
        self.callback_adicionar_log = callback
    
    def obter_widget(self) -> ttk.Frame:
        """
        Retorna o widget principal do componente.
        
        Returns:
            ttk.Frame principal
        """
        return self.frame_diagnosticos 