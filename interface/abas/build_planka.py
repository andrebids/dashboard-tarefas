# -*- coding: utf-8 -*-
"""
Aba para gerenciar o build do Planka com modificações personalizadas.
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import subprocess
import os
import time
from typing import Optional


class AbaBuildPlanka(ttk.Frame):
    """
    Aba para gerenciar o build do Planka.
    """
    
    def __init__(self, parent, log_manager, settings, **kwargs):
        """
        Inicializa a aba de build do Planka.
        
        Args:
            parent: Widget pai (notebook)
            log_manager: Gerenciador de logs
            settings: Configurações do sistema
            **kwargs: Argumentos adicionais para ttk.Frame
        """
        super().__init__(parent, **kwargs)
        
        self.parent = parent
        self.log_manager = log_manager
        self.settings = settings
        
        # Status do build
        self.build_em_andamento = False
        self.thread_build = None
        
        # Caminho do projeto Planka
        self.caminho_planka = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "planka-personalizado")
        
        self._criar_interface()
        self._configurar_eventos()
        
        # Registrar log de inicialização
        self.log_manager.log_sistema("SUCCESS", "Aba Build Planka inicializada")
    
    def _criar_interface(self):
        """Cria a interface da aba de build."""
        # Configurar peso das linhas e colunas
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Frame principal
        main_frame = ttk.Frame(self)
        main_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        main_frame.grid_rowconfigure(1, weight=1)
        main_frame.grid_columnconfigure(1, weight=1)
        
        # Título
        titulo = ttk.Label(main_frame, text="🔨 Build do Planka Personalizado", 
                          font=("Arial", 14, "bold"))
        titulo.grid(row=0, column=0, columnspan=2, pady=(0, 20), sticky="w")
        
        # Frame de controles (lado esquerdo)
        frame_controles = ttk.LabelFrame(main_frame, text="Controles de Build", padding=10)
        frame_controles.grid(row=1, column=0, sticky="nsew", padx=(0, 10))
        frame_controles.grid_columnconfigure(0, weight=1)
        
        # Informações do projeto
        self.lbl_caminho = ttk.Label(frame_controles, text=f"Caminho: {self.caminho_planka}")
        self.lbl_caminho.grid(row=0, column=0, sticky="w", pady=(0, 10))
        
        # Status atual
        self.lbl_status = ttk.Label(frame_controles, text="Status: Pronto", 
                                   font=("Arial", 10, "bold"))
        self.lbl_status.grid(row=1, column=0, sticky="w", pady=(0, 20))
        
        # Botões principais (organizados verticalmente)
        frame_botoes_principais = ttk.LabelFrame(frame_controles, text="Ações Principais", padding=10)
        frame_botoes_principais.grid(row=2, column=0, sticky="ew", pady=(0, 20))
        frame_botoes_principais.grid_columnconfigure(0, weight=1)
        
        self.btn_verificar = ttk.Button(frame_botoes_principais, text="🔍 Verificar Status", 
                                       command=self._verificar_status)
        self.btn_verificar.grid(row=0, column=0, sticky="ew", pady=(0, 5))
        
        self.btn_build = ttk.Button(frame_botoes_principais, text="🔨 Fazer Build", 
                                   command=self._iniciar_build)
        self.btn_build.grid(row=1, column=0, sticky="ew", pady=(0, 5))
        
        self.btn_parar = ttk.Button(frame_botoes_principais, text="⏹️ Parar Build", 
                                   command=self._parar_build, state="disabled")
        self.btn_parar.grid(row=2, column=0, sticky="ew", pady=(0, 5))
        
        self.btn_reiniciar = ttk.Button(frame_botoes_principais, text="🔄 Reiniciar Planka", 
                                       command=self._reiniciar_planka)
        self.btn_reiniciar.grid(row=3, column=0, sticky="ew")
        
        # Botões de modo (organizados verticalmente)
        frame_botoes_modo = ttk.LabelFrame(frame_controles, text="Modos de Execução", padding=10)
        frame_botoes_modo.grid(row=3, column=0, sticky="ew", pady=(0, 20))
        frame_botoes_modo.grid_columnconfigure(0, weight=1)
        
        self.btn_desenvolvimento = ttk.Button(frame_botoes_modo, text="🚀 Modo Desenvolvimento", 
                                             command=self._iniciar_desenvolvimento)
        self.btn_desenvolvimento.grid(row=0, column=0, sticky="ew", pady=(0, 5))
        
        self.btn_producao = ttk.Button(frame_botoes_modo, text="🏭 Modo Produção", 
                                      command=self._iniciar_producao)
        self.btn_producao.grid(row=1, column=0, sticky="ew", pady=(0, 5))
        
        self.btn_producao_modificacoes = ttk.Button(frame_botoes_modo, text="🔧 Produção com Modificações", 
                                                   command=self._iniciar_producao_modificacoes)
        self.btn_producao_modificacoes.grid(row=2, column=0, sticky="ew", pady=(0, 5))
        
        self.btn_diagnostico_producao = ttk.Button(frame_botoes_modo, text="🔍 Diagnóstico Produção", 
                                                  command=self._diagnostico_producao)
        self.btn_diagnostico_producao.grid(row=3, column=0, sticky="ew", pady=(0, 5))
        
        self.btn_parar_todos = ttk.Button(frame_botoes_modo, text="⏹️ Parar Todos", 
                                         command=self._parar_todos)
        self.btn_parar_todos.grid(row=4, column=0, sticky="ew")
        
        # Opções de build
        frame_opcoes = ttk.LabelFrame(frame_controles, text="Opções de Build", padding=10)
        frame_opcoes.grid(row=4, column=0, sticky="ew", pady=(0, 20))
        frame_opcoes.grid_columnconfigure(0, weight=1)
        
        self.var_no_cache = tk.BooleanVar(value=True)
        self.chk_no_cache = ttk.Checkbutton(frame_opcoes, text="Forçar rebuild (--no-cache)", 
                                           variable=self.var_no_cache)
        self.chk_no_cache.grid(row=0, column=0, sticky="w", pady=(0, 5))
        
        self.var_parar_antes = tk.BooleanVar(value=True)
        self.chk_parar_antes = ttk.Checkbutton(frame_opcoes, text="Parar containers antes do build", 
                                              variable=self.var_parar_antes)
        self.chk_parar_antes.grid(row=1, column=0, sticky="w", pady=(0, 5))
        
        self.var_iniciar_depois = tk.BooleanVar(value=True)
        self.chk_iniciar_depois = ttk.Checkbutton(frame_opcoes, text="Iniciar Planka após build", 
                                                 variable=self.var_iniciar_depois)
        self.chk_iniciar_depois.grid(row=2, column=0, sticky="w")
        
        # Frame de logs (lado direito)
        frame_logs = ttk.LabelFrame(main_frame, text="Logs do Build", padding=10)
        frame_logs.grid(row=1, column=1, sticky="nsew")
        frame_logs.grid_rowconfigure(0, weight=1)
        frame_logs.grid_columnconfigure(0, weight=1)
        
        # Área de logs
        self.txt_logs = scrolledtext.ScrolledText(frame_logs, width=60, height=20, 
                                                 font=("Consolas", 9))
        self.txt_logs.grid(row=0, column=0, sticky="nsew")
        
        # Botões de log
        frame_botoes_log = ttk.Frame(frame_logs)
        frame_botoes_log.grid(row=1, column=0, sticky="ew", pady=(10, 0))
        frame_botoes_log.grid_columnconfigure(0, weight=1)
        frame_botoes_log.grid_columnconfigure(1, weight=1)
        
        self.btn_limpar_logs = ttk.Button(frame_botoes_log, text="🧹 Limpar Logs", 
                                         command=self._limpar_logs)
        self.btn_limpar_logs.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        
        self.btn_salvar_logs = ttk.Button(frame_botoes_log, text="💾 Salvar Logs", 
                                         command=self._salvar_logs)
        self.btn_salvar_logs.grid(row=0, column=1, sticky="ew", padx=(5, 0))
        
        # Progress bar (na parte inferior)
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(10, 0))
        
        # Inicialmente esconder progress bar
        self.progress.grid_remove()
        
        # Adicionar tooltips para melhor usabilidade
        self._adicionar_tooltips()
    
    def _adicionar_tooltips(self):
        """Adiciona tooltips aos botões para melhor usabilidade."""
        try:
            # Tooltips para botões principais
            self._criar_tooltip(self.btn_verificar, "Verifica o status atual do Planka e containers Docker")
            self._criar_tooltip(self.btn_build, "Executa o build completo do Planka com as opções selecionadas")
            self._criar_tooltip(self.btn_parar, "Para o processo de build em andamento")
            self._criar_tooltip(self.btn_reiniciar, "Reinicia todos os containers do Planka")
            
            # Tooltips para botões de modo
            self._criar_tooltip(self.btn_desenvolvimento, "Inicia o Planka em modo desenvolvimento (hot reload ativo)")
            self._criar_tooltip(self.btn_producao, "Inicia o Planka em modo produção (otimizado)")
            self._criar_tooltip(self.btn_producao_modificacoes, "Executa produção com modificações locais (secret key, admin user, etc.)")
            self._criar_tooltip(self.btn_diagnostico_producao, "Executa diagnóstico completo da configuração de produção")
            self._criar_tooltip(self.btn_parar_todos, "Para todos os containers Docker do Planka")
            
            # Tooltips para opções
            self._criar_tooltip(self.chk_no_cache, "Força rebuild completo ignorando cache do Docker")
            self._criar_tooltip(self.chk_parar_antes, "Para containers antes de iniciar o build")
            self._criar_tooltip(self.chk_iniciar_depois, "Inicia automaticamente o Planka após o build")
            
            # Tooltips para botões de log
            self._criar_tooltip(self.btn_limpar_logs, "Limpa todos os logs da área de texto")
            self._criar_tooltip(self.btn_salvar_logs, "Salva os logs em um arquivo de texto")
            
        except Exception as e:
            self.log_manager.log_sistema("WARNING", f"Erro ao adicionar tooltips: {e}")
    
    def _criar_tooltip(self, widget, texto):
        """Cria um tooltip simples para um widget."""
        try:
            def mostrar_tooltip(event):
                tooltip = tk.Toplevel()
                tooltip.wm_overrideredirect(True)
                tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
                
                label = tk.Label(tooltip, text=texto, justify=tk.LEFT,
                               background="#ffffe0", relief=tk.SOLID, borderwidth=1,
                               font=("Arial", 8))
                label.pack()
                
                def esconder_tooltip(event):
                    tooltip.destroy()
                
                widget.bind('<Leave>', esconder_tooltip)
                tooltip.bind('<Leave>', esconder_tooltip)
            
            widget.bind('<Enter>', mostrar_tooltip)
            
        except Exception as e:
            pass  # Ignorar erros de tooltip
    
    def _configurar_eventos(self):
        """Configura eventos da interface."""
        try:
            # Verificar status inicial
            self._verificar_status()
            
        except Exception as e:
            self.log_manager.log_sistema("ERROR", f"Erro ao configurar eventos: {e}")
    
    def _verificar_status(self):
        """Verifica o status atual do Planka."""
        try:
            self._adicionar_log("Verificando status do Planka...")
            
            # Verificar se o diretório existe
            if not os.path.exists(self.caminho_planka):
                self._atualizar_status("Erro: Diretório do Planka não encontrado", "error")
                self._adicionar_log("❌ Diretório do Planka não encontrado")
                return
            
            # Verificar se o docker-compose está disponível
            try:
                resultado = subprocess.run(["docker-compose", "--version"], 
                                         capture_output=True, text=True, timeout=10,
                                         encoding='utf-8', errors='replace')
                if resultado.returncode != 0:
                    self._atualizar_status("Erro: Docker Compose não disponível", "error")
                    self._adicionar_log("❌ Docker Compose não disponível")
                    return
            except Exception as e:
                self._atualizar_status("Erro: Docker não disponível", "error")
                self._adicionar_log(f"❌ Docker não disponível: {e}")
                return
            
            # Verificar containers em execução
            try:
                # Verificar modo desenvolvimento primeiro (mais específico)
                resultado_dev = subprocess.run(["docker-compose", "-f", "docker-compose-dev.yml", "ps"], 
                                             cwd=self.caminho_planka, capture_output=True, text=True, timeout=10,
                                             encoding='utf-8', errors='replace')
                
                # Se modo desenvolvimento está ativo, verificar se os containers específicos estão rodando
                if resultado_dev.returncode == 0 and "Up" in resultado_dev.stdout:
                    linhas_dev = resultado_dev.stdout.strip().split('\n')
                    server_rodando = False
                    client_rodando = False
                    
                    for linha in linhas_dev:
                        if "planka-personalizado-planka-server-1" in linha and "Up" in linha:
                            server_rodando = True
                        elif "planka-personalizado-planka-client-1" in linha and "Up" in linha:
                            client_rodando = True
                    
                    if server_rodando and client_rodando:
                        self._atualizar_status("Modo Desenvolvimento ativo", "success")
                        self._adicionar_log("🚀 Planka em modo desenvolvimento")
                        self._adicionar_log("📱 Frontend: http://localhost:3000")
                        self._adicionar_log("🔧 Backend: http://localhost:1337")
                        return
                
                # Verificar modo produção
                resultado_prod = subprocess.run(["docker-compose", "-f", "docker-compose-local.yml", "ps"], 
                                              cwd=self.caminho_planka, capture_output=True, text=True, timeout=10,
                                              encoding='utf-8', errors='replace')
                
                # Se modo produção está ativo, verificar se o container planka está rodando
                if resultado_prod.returncode == 0 and "Up" in resultado_prod.stdout:
                    linhas_prod = resultado_prod.stdout.strip().split('\n')
                    for linha in linhas_prod:
                        if "planka-personalizado-planka-1" in linha and "Up" in linha:
                            self._atualizar_status("Modo Produção ativo", "success")
                            self._adicionar_log("🏭 Planka em modo produção")
                            self._adicionar_log("🌐 Acesso: http://localhost:3000")
                            return
                
                # Se nenhum modo específico está ativo
                self._atualizar_status("Planka parado", "warning")
                self._adicionar_log("⚠️ Planka está parado")
                    
            except Exception as e:
                self._atualizar_status("Erro ao verificar containers", "error")
                self._adicionar_log(f"❌ Erro ao verificar containers: {e}")
                
        except Exception as e:
            self.log_manager.log_sistema("ERROR", f"Erro ao verificar status: {e}")
            self._atualizar_status("Erro na verificação", "error")
    
    def _iniciar_build(self):
        """Inicia o processo de build."""
        if self.build_em_andamento:
            messagebox.showwarning("Aviso", "Build já está em andamento!")
            return
        
        if not messagebox.askyesno("Confirmar Build", 
                                  "Deseja iniciar o build do Planka?\n\n"
                                  "Isso pode demorar vários minutos."):
            return
        
        try:
            self.build_em_andamento = True
            self._atualizar_interface_build(True)
            
            # Iniciar thread de build
            self.thread_build = threading.Thread(target=self._executar_build, daemon=True)
            self.thread_build.start()
            
        except Exception as e:
            self.log_manager.log_sistema("ERROR", f"Erro ao iniciar build: {e}")
            self._atualizar_status("Erro ao iniciar build", "error")
            self.build_em_andamento = False
            self._atualizar_interface_build(False)
    
    def _executar_build(self):
        """Executa o build em thread separada."""
        try:
            self._adicionar_log("🚀 Iniciando build do Planka...")
            self._atualizar_status("Build em andamento...", "building")
            
            # Parar containers se solicitado
            if self.var_parar_antes.get():
                self._adicionar_log("⏹️ Parando containers...")
                self._executar_comando(["docker-compose", "-f", "docker-compose-local.yml", "down"], 
                                     "Parando containers")
            
            # Fazer build
            self._adicionar_log("🔨 Executando build...")
            args = ["docker-compose", "-f", "docker-compose-local.yml", "build"]
            if self.var_no_cache.get():
                args.append("--no-cache")
            
            self._executar_comando(args, "Fazendo build")
            
            # Iniciar containers se solicitado
            if self.var_iniciar_depois.get():
                self._adicionar_log("🚀 Iniciando Planka...")
                self._executar_comando(["docker-compose", "-f", "docker-compose-local.yml", "up", "-d"], 
                                     "Iniciando Planka")
            
            self._adicionar_log("✅ Build concluído com sucesso!")
            self._atualizar_status("Build concluído", "success")
            
        except Exception as e:
            self.log_manager.log_sistema("ERROR", f"Erro no build: {e}")
            self._adicionar_log(f"❌ Erro no build: {e}")
            self._atualizar_status("Erro no build", "error")
        
        finally:
            self.build_em_andamento = False
            self._atualizar_interface_build(False)
    
    def _executar_comando(self, comando, descricao):
        """Executa um comando e mostra o output."""
        try:
            self._adicionar_log(f"📋 {descricao}: {' '.join(comando)}")
            
            processo = subprocess.Popen(comando, cwd=self.caminho_planka, 
                                      stdout=subprocess.PIPE, stderr=subprocess.STDOUT, 
                                      text=True, bufsize=1, universal_newlines=True,
                                      encoding='utf-8', errors='replace')
            
            # Ler output em tempo real
            for linha in processo.stdout:
                self._adicionar_log(linha.rstrip())
            
            processo.wait()
            
            if processo.returncode == 0:
                self._adicionar_log(f"✅ {descricao} concluído")
            else:
                self._adicionar_log(f"❌ {descricao} falhou (código: {processo.returncode})")
                raise Exception(f"Comando falhou com código {processo.returncode}")
                
        except Exception as e:
            self.log_manager.log_sistema("ERROR", f"Erro ao executar comando {descricao}: {e}")
            raise
    
    def _parar_build(self):
        """Para o build em andamento."""
        if not self.build_em_andamento:
            return
        
        if messagebox.askyesno("Parar Build", "Deseja realmente parar o build?"):
            self._adicionar_log("⏹️ Parando build...")
            self.build_em_andamento = False
            self._atualizar_interface_build(False)
            self._atualizar_status("Build interrompido", "warning")
    
    def _reiniciar_planka(self):
        """Reinicia o Planka."""
        if not messagebox.askyesno("Reiniciar Planka", "Deseja reiniciar o Planka?"):
            return
        
        try:
            self._adicionar_log("🔄 Reiniciando Planka...")
            self._atualizar_status("Reiniciando...", "building")
            
            # Executar em thread separada
            thread = threading.Thread(target=self._executar_reinicio, daemon=True)
            thread.start()
            
        except Exception as e:
            self.log_manager.log_sistema("ERROR", f"Erro ao reiniciar Planka: {e}")
            self._adicionar_log(f"❌ Erro ao reiniciar: {e}")
    
    def _executar_reinicio(self):
        """Executa o reinício em thread separada."""
        try:
            self._executar_comando(["docker-compose", "-f", "docker-compose-local.yml", "restart"], 
                                 "Reiniciando Planka")
            self._adicionar_log("✅ Planka reiniciado com sucesso!")
            self._atualizar_status("Planka reiniciado", "success")
            
        except Exception as e:
            self.log_manager.log_sistema("ERROR", f"Erro no reinício: {e}")
            self._adicionar_log(f"❌ Erro no reinício: {e}")
            self._atualizar_status("Erro no reinício", "error")
    
    def _iniciar_desenvolvimento(self):
        """Inicia o modo de desenvolvimento."""
        if not messagebox.askyesno("Modo Desenvolvimento", 
                                  "Deseja iniciar o modo de desenvolvimento?\n\n"
                                  "• Frontend: http://localhost:3000\n"
                                  "• Backend: http://localhost:1337\n"
                                  "• Hot reload automático\n"
                                  "• Alterações vistas instantaneamente"):
            return
        
        try:
            self._adicionar_log("🚀 Iniciando modo de desenvolvimento...")
            self._atualizar_status("Iniciando desenvolvimento...", "building")
            
            # Executar em thread separada
            thread = threading.Thread(target=self._executar_desenvolvimento, daemon=True)
            thread.start()
            
        except Exception as e:
            self.log_manager.log_sistema("ERROR", f"Erro ao iniciar desenvolvimento: {e}")
            self._adicionar_log(f"❌ Erro ao iniciar desenvolvimento: {e}")
    
    def _executar_desenvolvimento(self):
        """Executa o modo de desenvolvimento em thread separada."""
        try:
            # Parar containers de produção se estiverem rodando
            self._adicionar_log("⏹️ Parando containers de produção...")
            self._executar_comando(["docker-compose", "-f", "docker-compose-local.yml", "down"], 
                                 "Parando produção")
            
            # Iniciar modo desenvolvimento
            self._adicionar_log("🚀 Iniciando containers de desenvolvimento...")
            self._executar_comando(["docker-compose", "-f", "docker-compose-dev.yml", "up", "-d"], 
                                 "Iniciando desenvolvimento")
            
            self._adicionar_log("✅ Modo de desenvolvimento iniciado!")
            self._adicionar_log("📱 Frontend: http://localhost:3000")
            self._adicionar_log("🔧 Backend: http://localhost:1337")
            self._adicionar_log("💡 Hot reload ativo - alterações são vistas instantaneamente")
            self._atualizar_status("Modo desenvolvimento ativo", "success")
            
        except Exception as e:
            self.log_manager.log_sistema("ERROR", f"Erro no desenvolvimento: {e}")
            self._adicionar_log(f"❌ Erro no desenvolvimento: {e}")
            self._atualizar_status("Erro no desenvolvimento", "error")
    
    def _iniciar_producao(self):
        """Inicia o modo de produção."""
        if not messagebox.askyesno("Modo Produção", 
                                  "Deseja iniciar o modo de produção?\n\n"
                                  "• Versão otimizada\n"
                                  "• Acesso: http://localhost:3000\n"
                                  "• Requer build completo"):
            return
        
        try:
            self._adicionar_log("🏭 Iniciando modo de produção...")
            self._atualizar_status("Iniciando produção...", "building")
            
            # Executar em thread separada
            thread = threading.Thread(target=self._executar_producao, daemon=True)
            thread.start()
            
        except Exception as e:
            self.log_manager.log_sistema("ERROR", f"Erro ao iniciar produção: {e}")
            self._adicionar_log(f"❌ Erro ao iniciar produção: {e}")
    
    def _executar_producao(self):
        """Executa o modo de produção em thread separada."""
        try:
            # Parar containers de desenvolvimento se estiverem rodando
            self._adicionar_log("⏹️ Parando containers de desenvolvimento...")
            self._executar_comando(["docker-compose", "-f", "docker-compose-dev.yml", "down"], 
                                 "Parando desenvolvimento")
            
            # Fazer build completo
            self._adicionar_log("🔨 Fazendo build completo...")
            args = ["docker-compose", "-f", "docker-compose-local.yml", "build"]
            if self.var_no_cache.get():
                args.append("--no-cache")
            
            self._executar_comando(args, "Build completo")
            
            # Iniciar produção
            self._adicionar_log("🏭 Iniciando containers de produção...")
            self._executar_comando(["docker-compose", "-f", "docker-compose-local.yml", "up", "-d"], 
                                 "Iniciando produção")
            
            self._adicionar_log("✅ Modo de produção iniciado!")
            self._adicionar_log("🌐 Acesso: http://localhost:3000")
            self._adicionar_log("📦 Versão otimizada e compilada")
            self._atualizar_status("Modo produção ativo", "success")
            
        except Exception as e:
            self.log_manager.log_sistema("ERROR", f"Erro na produção: {e}")
            self._adicionar_log(f"❌ Erro na produção: {e}")
            self._atualizar_status("Erro na produção", "error")
    
    def _parar_todos(self):
        """Para todos os containers do Planka."""
        if not messagebox.askyesno("Parar Todos", "Deseja parar todos os containers do Planka?"):
            return
        
        try:
            self._adicionar_log("⏹️ Parando todos os containers...")
            self._atualizar_status("Parando containers...", "building")
            
            # Executar em thread separada
            thread = threading.Thread(target=self._executar_parar_todos, daemon=True)
            thread.start()
            
        except Exception as e:
            self.log_manager.log_sistema("ERROR", f"Erro ao parar containers: {e}")
            self._adicionar_log(f"❌ Erro ao parar containers: {e}")
    
    def _executar_parar_todos(self):
        """Executa a parada de todos os containers em thread separada."""
        try:
            # Parar containers de produção
            self._adicionar_log("⏹️ Parando containers de produção...")
            self._executar_comando(["docker-compose", "-f", "docker-compose-local.yml", "down"], 
                                 "Parando produção")
            
            # Parar containers de desenvolvimento
            self._adicionar_log("⏹️ Parando containers de desenvolvimento...")
            self._executar_comando(["docker-compose", "-f", "docker-compose-dev.yml", "down"], 
                                 "Parando desenvolvimento")
            
            self._adicionar_log("✅ Todos os containers parados!")
            self._atualizar_status("Todos os containers parados", "warning")
            
        except Exception as e:
            self.log_manager.log_sistema("ERROR", f"Erro ao parar containers: {e}")
            self._adicionar_log(f"❌ Erro ao parar containers: {e}")
            self._atualizar_status("Erro ao parar containers", "error")
    
    def _iniciar_producao_modificacoes(self):
        """Inicia o modo de produção com modificações locais."""
        if not messagebox.askyesno("Produção com Modificações", 
                                  "Deseja iniciar o modo de produção com modificações locais?\n\n"
                                  "• Gera secret key segura automaticamente\n"
                                  "• Configura admin user automaticamente\n"
                                  "• Aplica melhores práticas da documentação\n"
                                  "• Acesso: http://localhost:3000"):
            return
        
        try:
            self._adicionar_log("🔧 Iniciando produção com modificações locais...")
            self._atualizar_status("Iniciando produção com modificações...", "building")
            
            # Executar em thread separada
            thread = threading.Thread(target=self._executar_producao_modificacoes, daemon=True)
            thread.start()
            
        except Exception as e:
            self.log_manager.log_sistema("ERROR", f"Erro ao iniciar produção com modificações: {e}")
            self._adicionar_log(f"❌ Erro ao iniciar produção com modificações: {e}")
    
    def _executar_producao_modificacoes(self):
        """Executa o modo de produção com modificações locais em thread separada."""
        try:
            # Importar o PlankaManager
            from core.planka import PlankaManager
            
            # Criar instância do PlankaManager
            planka_manager = PlankaManager(self.settings)
            
            # Executar produção com modificações
            self._adicionar_log("🔧 Executando produção com modificações locais...")
            sucesso, mensagem = planka_manager.executar_producao_com_modificacoes_locais()
            
            if sucesso:
                self._adicionar_log("✅ Produção com modificações iniciada com sucesso!")
                self._adicionar_log("🌐 Acesso: http://localhost:3000")
                self._adicionar_log("👤 Admin user configurado automaticamente")
                self._atualizar_status("Produção com modificações ativa", "success")
            else:
                self._adicionar_log(f"❌ Erro na produção com modificações: {mensagem}")
                self._atualizar_status("Erro na produção com modificações", "error")
            
        except Exception as e:
            self.log_manager.log_sistema("ERROR", f"Erro na produção com modificações: {e}")
            self._adicionar_log(f"❌ Erro na produção com modificações: {e}")
            self._atualizar_status("Erro na produção com modificações", "error")
    
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
            self._adicionar_log("🔍 Iniciando diagnóstico de produção...")
            self._atualizar_status("Executando diagnóstico...", "building")
            
            # Executar em thread separada
            thread = threading.Thread(target=self._executar_diagnostico_producao, daemon=True)
            thread.start()
            
        except Exception as e:
            self.log_manager.log_sistema("ERROR", f"Erro ao iniciar diagnóstico: {e}")
            self._adicionar_log(f"❌ Erro ao iniciar diagnóstico: {e}")
    
    def _executar_diagnostico_producao(self):
        """Executa diagnóstico da configuração de produção em thread separada."""
        try:
            # Importar o PlankaManager
            from core.planka import PlankaManager
            
            # Criar instância do PlankaManager
            planka_manager = PlankaManager(self.settings)
            
            # Executar diagnóstico
            self._adicionar_log("🔍 Executando diagnóstico de produção...")
            resultado = planka_manager.diagnosticar_producao()
            
            # Exibir resultados
            self._adicionar_log("📊 Resultados do diagnóstico:")
            self._adicionar_log(f"   • Status geral: {resultado.get('status_geral', 'N/A')}")
            self._adicionar_log(f"   • Containers ativos: {resultado.get('containers_ativos', 0)}")
            self._adicionar_log(f"   • Secret key válida: {resultado.get('secret_key_valida', False)}")
            self._adicionar_log(f"   • Admin user existe: {resultado.get('admin_user_existe', False)}")
            self._adicionar_log(f"   • Porta acessível: {resultado.get('porta_acessivel', False)}")
            
            # Verificar problemas
            problemas = resultado.get('problemas', [])
            if problemas:
                self._adicionar_log("⚠️ Problemas encontrados:")
                for problema in problemas:
                    self._adicionar_log(f"   • {problema}")
            else:
                self._adicionar_log("✅ Nenhum problema encontrado!")
            
            # Logs detalhados se houver
            logs_detalhados = resultado.get('logs_detalhados', {})
            if logs_detalhados:
                self._adicionar_log("📋 Logs detalhados:")
                for container, log in logs_detalhados.items():
                    self._adicionar_log(f"   • {container}: {log[:100]}...")
            
            self._atualizar_status("Diagnóstico concluído", "success")
            
        except Exception as e:
            self.log_manager.log_sistema("ERROR", f"Erro no diagnóstico: {e}")
            self._adicionar_log(f"❌ Erro no diagnóstico: {e}")
            self._atualizar_status("Erro no diagnóstico", "error")
    
    def _atualizar_interface_build(self, em_andamento: bool):
        """Atualiza a interface durante o build."""
        try:
            if em_andamento:
                self.btn_build.config(state="disabled")
                self.btn_parar.config(state="normal")
                self.btn_verificar.config(state="disabled")
                self.btn_reiniciar.config(state="disabled")
                self.progress.grid()
                self.progress.start()
            else:
                self.btn_build.config(state="normal")
                self.btn_parar.config(state="disabled")
                self.btn_verificar.config(state="normal")
                self.btn_reiniciar.config(state="normal")
                self.progress.stop()
                self.progress.grid_remove()
                
        except Exception as e:
            self.log_manager.log_sistema("ERROR", f"Erro ao atualizar interface: {e}")
    
    def _atualizar_status(self, status: str, tipo: str = "info"):
        """Atualiza o status na interface."""
        try:
            cores = {
                "success": "green",
                "error": "red", 
                "warning": "orange",
                "building": "blue",
                "info": "black"
            }
            
            cor = cores.get(tipo, "black")
            self.lbl_status.config(text=f"Status: {status}", foreground=cor)
            
        except Exception as e:
            self.log_manager.log_sistema("ERROR", f"Erro ao atualizar status: {e}")
    
    def _adicionar_log(self, mensagem: str):
        """Adiciona uma mensagem ao log."""
        try:
            timestamp = time.strftime("%H:%M:%S")
            log_entry = f"[{timestamp}] {mensagem}\n"
            
            # Adicionar na thread principal
            self.after(0, lambda: self._adicionar_log_ui(log_entry))
            
        except Exception as e:
            self.log_manager.log_sistema("ERROR", f"Erro ao adicionar log: {e}")
    
    def _adicionar_log_ui(self, log_entry: str):
        """Adiciona log na interface (deve ser chamado na thread principal)."""
        try:
            self.txt_logs.insert(tk.END, log_entry)
            self.txt_logs.see(tk.END)
            
            # Limitar tamanho do log (manter apenas últimas 1000 linhas)
            linhas = self.txt_logs.get("1.0", tk.END).split('\n')
            if len(linhas) > 1000:
                self.txt_logs.delete("1.0", f"{len(linhas) - 1000}.0")
                
        except Exception as e:
            self.log_manager.log_sistema("ERROR", f"Erro ao adicionar log na UI: {e}")
    
    def _limpar_logs(self):
        """Limpa os logs da interface."""
        try:
            self.txt_logs.delete("1.0", tk.END)
            self._adicionar_log("🧹 Logs limpos")
            
        except Exception as e:
            self.log_manager.log_sistema("ERROR", f"Erro ao limpar logs: {e}")
    
    def _salvar_logs(self):
        """Salva os logs para arquivo."""
        try:
            from tkinter import filedialog
            
            arquivo = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Arquivos de texto", "*.txt"), ("Todos os arquivos", "*.*")],
                title="Salvar logs do build"
            )
            
            if arquivo:
                conteudo = self.txt_logs.get("1.0", tk.END)
                with open(arquivo, 'w', encoding='utf-8') as f:
                    f.write(conteudo)
                
                self._adicionar_log(f"💾 Logs salvos em: {arquivo}")
                messagebox.showinfo("Sucesso", f"Logs salvos em:\n{arquivo}")
                
        except Exception as e:
            self.log_manager.log_sistema("ERROR", f"Erro ao salvar logs: {e}")
            messagebox.showerror("Erro", f"Erro ao salvar logs: {e}")
    
    def atualizar(self):
        """Atualiza a aba."""
        try:
            self._verificar_status()
        except Exception as e:
            self.log_manager.log_sistema("ERROR", f"Erro ao atualizar aba build: {e}") 