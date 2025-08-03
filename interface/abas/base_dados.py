# -*- coding: utf-8 -*-
"""
Aba Base de Dados - Gestão da Base de Dados do Planka.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
from pathlib import Path
import sys
import os
import time
from typing import Dict

# Importar o PlankaDatabaseManager
sys.path.append(str(Path(__file__).parent.parent.parent))
from core.planka_database import PlankaDatabaseManager


class AbaBaseDados(ttk.Frame):
    """
    Aba de gestão da base de dados do Planka.
    """
    
    def __init__(self, parent, log_manager, settings, **kwargs):
        """
        Inicializa a aba de base de dados.
        
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
        
        # Inicializar PlankaDatabaseManager
        try:
            config_dir = settings.obter_diretorio_config()
        except:
            # Fallback para diretório padrão
            config_dir = Path(__file__).parent.parent.parent / "config"
        
        self.db_manager = PlankaDatabaseManager(settings)
        
        # Thread para operações longas
        self.thread_operacao = None
        
        self._criar_interface()
        self._verificar_status_inicial()
        
        self.log_manager.log_sistema("SUCCESS", "Aba base de dados inicializada")
    
    def _criar_interface(self):
        """Cria a interface da aba base de dados."""
        # Frame principal
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Título
        titulo_frame = ttk.Frame(main_frame)
        titulo_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(titulo_frame, text="🗄️ Gestão da Base de Dados", 
                  font=("Arial", 16, "bold")).pack(side=tk.LEFT)
        
        # Status da base de dados
        self.lbl_status_db = ttk.Label(titulo_frame, text="Status: Verificando...",
                                       font=("Arial", 10))
        self.lbl_status_db.pack(side=tk.RIGHT)
        
        # Frame de status da base de dados
        status_frame = ttk.LabelFrame(main_frame, text="Status da Base de Dados", padding=20)
        status_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Grid de informações
        info_grid = ttk.Frame(status_frame)
        info_grid.pack(fill=tk.X)
        
        # Informações da base de dados
        ttk.Label(info_grid, text="PostgreSQL:").grid(row=0, column=0, sticky="w", pady=2)
        self.lbl_postgres = ttk.Label(info_grid, text="Verificando...", foreground="blue")
        self.lbl_postgres.grid(row=0, column=1, sticky="w", padx=(10, 0), pady=2)
        
        ttk.Label(info_grid, text="Base de Dados:").grid(row=1, column=0, sticky="w", pady=2)
        self.lbl_database = ttk.Label(info_grid, text="Verificando...", foreground="blue")
        self.lbl_database.grid(row=1, column=1, sticky="w", padx=(10, 0), pady=2)
        
        ttk.Label(info_grid, text="Tabelas:").grid(row=2, column=0, sticky="w", pady=2)
        self.lbl_tabelas = ttk.Label(info_grid, text="Verificando...", foreground="blue")
        self.lbl_tabelas.grid(row=2, column=1, sticky="w", padx=(10, 0), pady=2)
        
        ttk.Label(info_grid, text="Tamanho:").grid(row=3, column=0, sticky="w", pady=2)
        self.lbl_tamanho = ttk.Label(info_grid, text="Verificando...", foreground="blue")
        self.lbl_tamanho.grid(row=3, column=1, sticky="w", padx=(10, 0), pady=2)
        
        # Frame de ações da base de dados
        acoes_frame = ttk.LabelFrame(main_frame, text="Ações da Base de Dados", padding=20)
        acoes_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Grid para botões
        botoes_frame = ttk.Frame(acoes_frame)
        botoes_frame.pack(fill=tk.X)
        
        # Linha de botões principais
        linha_botoes = ttk.Frame(botoes_frame)
        linha_botoes.pack(fill=tk.X, pady=(0, 10))
        
        # Botão Diagnóstico
        self.btn_diagnostico = ttk.Button(linha_botoes, text="🔍 Diagnóstico Completo", 
                                          command=self._executar_diagnostico)
        self.btn_diagnostico.pack(side=tk.LEFT, padx=(0, 10))
        
        # Botão Backup
        self.btn_backup = ttk.Button(linha_botoes, text="💾 Fazer Backup", 
                                     command=self._fazer_backup)
        self.btn_backup.pack(side=tk.LEFT, padx=(0, 10))
        
        # Botão Restaurar (melhorado)
        self.btn_restaurar = ttk.Button(linha_botoes, text="🔄 Restaurar Backup", 
                                        command=self._restaurar_backup_melhorado)
        self.btn_restaurar.pack(side=tk.LEFT, padx=(0, 10))
        
        # Frame de progresso (inicialmente oculto)
        self.progress_frame = ttk.Frame(main_frame)
        self.progress_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.lbl_progress = ttk.Label(self.progress_frame, text="", font=("Arial", 10))
        self.lbl_progress.pack(anchor="w")
        
        self.progress_bar = ttk.Progressbar(self.progress_frame, mode='indeterminate')
        self.progress_bar.pack(fill=tk.X, pady=(5, 0))
        
        # Ocultar progresso inicialmente
        self.progress_frame.pack_forget()
        
        # Frame de backups
        backups_frame = ttk.LabelFrame(main_frame, text="Backups Disponíveis", padding=10)
        backups_frame.pack(fill=tk.BOTH, expand=True)
        
        # TreeView para listar backups
        colunas = ("Nome", "Tamanho", "Data", "Tipo")
        self.tree_backups = ttk.Treeview(backups_frame, columns=colunas, show="headings", height=8)
        
        # Configurar colunas
        for col in colunas:
            self.tree_backups.heading(col, text=col)
            self.tree_backups.column(col, width=150)
        
        # Scrollbar para TreeView
        scrollbar = ttk.Scrollbar(backups_frame, orient="vertical", command=self.tree_backups.yview)
        self.tree_backups.configure(yscrollcommand=scrollbar.set)
        
        self.tree_backups.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Frame de controles dos backups
        backups_controls = ttk.Frame(backups_frame)
        backups_controls.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(backups_controls, text="Atualizar Lista", 
                  command=self._atualizar_lista_backups).pack(side=tk.LEFT)
        
        ttk.Button(backups_controls, text="Validar Selecionado", 
                  command=self._validar_backup_selecionado).pack(side=tk.LEFT, padx=(10, 0))
        
        ttk.Button(backups_controls, text="Comprimir Selecionado", 
                  command=self._comprimir_backup_selecionado).pack(side=tk.LEFT, padx=(10, 0))
        
        # Configurar estado inicial dos botões
        self._atualizar_estado_botoes()
        
        # Adicionar tooltips aos botões
        self._adicionar_tooltips()
    
    def _verificar_status_inicial(self):
        """Verifica o status inicial da base de dados."""
        try:
            # Verificar conectividade
            conectividade = self.db_manager.verificar_conectividade()
            
            # Atualizar labels
            if conectividade["postgres_running"]:
                self.lbl_postgres.config(text="🟢 Rodando", foreground="green")
            else:
                self.lbl_postgres.config(text="🔴 Parado", foreground="red")
            
            if conectividade["database_exists"]:
                self.lbl_database.config(text="🟢 Existe", foreground="green")
            else:
                self.lbl_database.config(text="🔴 Não existe", foreground="red")
            
            if conectividade["tables_exist"]:
                self.lbl_tabelas.config(text="🟢 Existem", foreground="green")
            else:
                self.lbl_tabelas.config(text="🔴 Não existem", foreground="red")
            
            # Obter estrutura da base de dados
            if conectividade["database_exists"]:
                estrutura = self.db_manager.obter_estrutura_base()
                self.lbl_tamanho.config(text=estrutura["tamanho_base"], foreground="blue")
                
                if conectividade["tables_exist"]:
                    self.lbl_status_db.config(text=f"Status: 🟢 {estrutura['total_tabelas']} tabelas, {estrutura['total_registros']} registros", foreground="green")
                else:
                    self.lbl_status_db.config(text="Status: 🟡 Base vazia", foreground="orange")
            else:
                self.lbl_tamanho.config(text="N/A", foreground="gray")
                self.lbl_status_db.config(text="Status: 🔴 Base não existe", foreground="red")
            
            # Atualizar lista de backups
            self._atualizar_lista_backups()
            
            self._atualizar_estado_botoes()
            
        except Exception as e:
            self.log_manager.log_sistema("ERROR", f"Erro ao verificar status inicial: {e}")
    
    def _atualizar_estado_botoes(self):
        """Atualiza o estado dos botões baseado no status da base de dados."""
        try:
            conectividade = self.db_manager.verificar_conectividade()
            
            # Botões que precisam de base existente
            base_existe = conectividade["database_exists"]
            self.btn_backup.config(state="normal" if base_existe else "disabled")
            
            # Botão de diagnóstico sempre disponível
            self.btn_diagnostico.config(state="normal")
            
            # Botão de restaurar sempre disponível (pode restaurar mesmo sem base)
            self.btn_restaurar.config(state="normal")
            
        except Exception as e:
            self.log_manager.log_sistema("ERROR", f"Erro ao atualizar estado dos botões: {e}")
    
    def _criar_base_dados(self):
        """Cria uma nova base de dados."""
        if self.thread_operacao and self.thread_operacao.is_alive():
            messagebox.showwarning("Aviso", "Operação em andamento. Aguarde...")
            return
        
        self.thread_operacao = threading.Thread(target=self._executar_criar_base_dados)
        self.thread_operacao.daemon = True
        self.thread_operacao.start()
    
    def _executar_criar_base_dados(self):
        """Executa a criação da base de dados em thread separada."""
        try:
            self._mostrar_progresso("Criando base de dados...")
            self.log_manager.log_sistema("INFO", "Criando base de dados...")
            
            sucesso, mensagem = self.db_manager.criar_base_dados()
            
            self._ocultar_progresso()
            
            if sucesso:
                self.log_manager.log_sistema("SUCCESS", mensagem)
                messagebox.showinfo("Sucesso", mensagem)
                self._verificar_status_inicial()
            else:
                self.log_manager.log_sistema("ERROR", mensagem)
                messagebox.showerror("Erro", mensagem)
                
        except Exception as e:
            self._ocultar_progresso()
            self.log_manager.log_sistema("ERROR", f"Erro inesperado: {e}")
            messagebox.showerror("Erro", f"Erro inesperado: {e}")
    
    def _inicializar_base_dados(self):
        """Inicializa a base de dados."""
        if self.thread_operacao and self.thread_operacao.is_alive():
            messagebox.showwarning("Aviso", "Operação em andamento. Aguarde...")
            return
        
        self.thread_operacao = threading.Thread(target=self._executar_inicializar_base_dados)
        self.thread_operacao.daemon = True
        self.thread_operacao.start()
    
    def _executar_inicializar_base_dados(self):
        """Executa a inicialização da base de dados em thread separada."""
        try:
            self._mostrar_progresso("Inicializando base de dados...")
            self.log_manager.log_sistema("INFO", "Inicializando base de dados...")
            
            sucesso, mensagem = self.db_manager.inicializar_base_dados()
            
            self._ocultar_progresso()
            
            if sucesso:
                self.log_manager.log_sistema("SUCCESS", mensagem)
                messagebox.showinfo("Sucesso", mensagem)
                self._verificar_status_inicial()
            else:
                self.log_manager.log_sistema("ERROR", mensagem)
                messagebox.showerror("Erro", mensagem)
                
        except Exception as e:
            self._ocultar_progresso()
            self.log_manager.log_sistema("ERROR", f"Erro inesperado: {e}")
            messagebox.showerror("Erro", f"Erro inesperado: {e}")
    

    

    
    def _abrir_editor(self):
        """Abre o editor de base de dados (pgAdmin no navegador)."""
        try:
            sucesso, mensagem = self.db_manager.conectar_editor("pgadmin")
            
            if sucesso:
                self.log_manager.log_sistema("SUCCESS", mensagem)
                messagebox.showinfo("Sucesso", mensagem)
            else:
                self.log_manager.log_sistema("ERROR", mensagem)
                messagebox.showerror("Erro", mensagem)
                
        except Exception as e:
            self.log_manager.log_sistema("ERROR", f"Erro ao abrir editor: {e}")
            messagebox.showerror("Erro", f"Erro ao abrir editor: {e}")
    
    def _fazer_backup(self):
        """Faz backup da base de dados."""
        if self.thread_operacao and self.thread_operacao.is_alive():
            messagebox.showwarning("Aviso", "Operação em andamento. Aguarde...")
            return
        
        self.thread_operacao = threading.Thread(target=self._executar_fazer_backup)
        self.thread_operacao.daemon = True
        self.thread_operacao.start()
    
    def _executar_fazer_backup(self):
        """Executa o backup em thread separada."""
        try:
            self._mostrar_progresso("Fazendo backup da base de dados...")
            self.log_manager.log_sistema("INFO", "Fazendo backup da base de dados...")
            
            sucesso, mensagem = self.db_manager.backup_completo()
            
            self._ocultar_progresso()
            
            if sucesso:
                self.log_manager.log_sistema("SUCCESS", mensagem)
                messagebox.showinfo("Sucesso", mensagem)
                self._atualizar_lista_backups()
            else:
                self.log_manager.log_sistema("ERROR", mensagem)
                messagebox.showerror("Erro", mensagem)
                
        except Exception as e:
            self._ocultar_progresso()
            self.log_manager.log_sistema("ERROR", f"Erro inesperado: {e}")
            messagebox.showerror("Erro", f"Erro inesperado: {e}")
    
    def _executar_diagnostico(self):
        """Executa diagnóstico completo da base de dados."""
        if self.thread_operacao and self.thread_operacao.is_alive():
            messagebox.showwarning("Aviso", "Operação em andamento. Aguarde...")
            return
        
        self.thread_operacao = threading.Thread(target=self._executar_diagnostico_background)
        self.thread_operacao.daemon = True
        self.thread_operacao.start()
    
    def _executar_diagnostico_background(self):
        """Executa diagnóstico em thread separada."""
        try:
            self._mostrar_progresso("Executando diagnóstico completo...")
            self.log_manager.log_sistema("INFO", "Iniciando diagnóstico da base de dados...")
            
            # Importar o módulo de diagnóstico
            from core.diagnostic_database import DatabaseDiagnostic
            
            # Executar diagnóstico
            diagnostic = DatabaseDiagnostic(self.settings)
            resultado = diagnostic.executar_diagnostico_completo()
            
            # Gerar relatório
            relatorio = diagnostic.gerar_relatorio(resultado)
            
            self._ocultar_progresso()
            
            # Salvar relatório em arquivo
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            relatorio_file = Path(self.settings.obter("logs", "diretorio_sistema")) / f"diagnostico_db_{timestamp}.txt"
            
            try:
                relatorio_file.parent.mkdir(parents=True, exist_ok=True)
                with open(relatorio_file, 'w', encoding='utf-8') as f:
                    f.write(relatorio)
                
                self.log_manager.log_sistema("SUCCESS", f"Diagnóstico concluído. Relatório salvo em: {relatorio_file}")
                
                # Mostrar relatório em janela
                self._mostrar_relatorio_diagnostico(relatorio, resultado)
                
            except Exception as e:
                self.log_manager.log_sistema("ERROR", f"Erro ao salvar relatório: {e}")
                messagebox.showerror("Erro", f"Erro ao salvar relatório: {e}")
                
        except Exception as e:
            self._ocultar_progresso()
            self.log_manager.log_sistema("ERROR", f"Erro no diagnóstico: {e}")
            messagebox.showerror("Erro", f"Erro no diagnóstico: {e}")
    
    def _mostrar_relatorio_diagnostico(self, relatorio: str, resultado: Dict):
        """Mostra o relatório de diagnóstico em uma janela."""
        # Criar janela de relatório
        janela_relatorio = tk.Toplevel(self)
        janela_relatorio.title("Diagnóstico da Base de Dados")
        janela_relatorio.geometry("800x600")
        janela_relatorio.resizable(True, True)
        
        # Frame principal
        main_frame = ttk.Frame(janela_relatorio)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Título
        ttk.Label(main_frame, text="🔍 Relatório de Diagnóstico", 
                  font=("Arial", 14, "bold")).pack(pady=(0, 10))
        
        # Text widget para o relatório
        text_frame = ttk.Frame(main_frame)
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        text_widget = tk.Text(text_frame, wrap=tk.WORD, font=("Consolas", 9))
        scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Inserir relatório
        text_widget.insert(tk.END, relatorio)
        text_widget.config(state=tk.DISABLED)  # Tornar somente leitura
        
        # Frame de botões
        botoes_frame = ttk.Frame(main_frame)
        botoes_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Botão para copiar relatório
        ttk.Button(botoes_frame, text="📋 Copiar Relatório", 
                  command=lambda: self._copiar_relatorio(text_widget)).pack(side=tk.LEFT, padx=(0, 10))
        
        # Botão para fechar
        ttk.Button(botoes_frame, text="❌ Fechar", 
                  command=janela_relatorio.destroy).pack(side=tk.RIGHT)
        
        # Mostrar resumo dos problemas se houver
        if resultado["problemas"]:
            self._mostrar_resumo_problemas(janela_relatorio, resultado)
    
    def _copiar_relatorio(self, text_widget):
        """Copia o relatório para a área de transferência."""
        try:
            relatorio = text_widget.get(1.0, tk.END)
            self.clipboard_clear()
            self.clipboard_append(relatorio)
            messagebox.showinfo("Sucesso", "Relatório copiado para a área de transferência!")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao copiar relatório: {e}")
    
    def _mostrar_resumo_problemas(self, parent, resultado: Dict):
        """Mostra um resumo dos problemas encontrados."""
        # Criar janela de resumo
        janela_resumo = tk.Toplevel(parent)
        janela_resumo.title("Resumo dos Problemas")
        janela_resumo.geometry("500x400")
        janela_resumo.resizable(True, True)
        
        # Frame principal
        main_frame = ttk.Frame(janela_resumo)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Título
        ttk.Label(main_frame, text="🚨 Problemas Encontrados", 
                  font=("Arial", 12, "bold")).pack(pady=(0, 10))
        
        # Lista de problemas
        if resultado["problemas"]:
            for i, problema in enumerate(resultado["problemas"], 1):
                ttk.Label(main_frame, text=f"{i}. {problema}", 
                          font=("Arial", 10)).pack(anchor="w", pady=2)
        
        # Recomendações
        if resultado["recomendacoes"]:
            ttk.Label(main_frame, text="", font=("Arial", 10)).pack(pady=10)
            ttk.Label(main_frame, text="💡 Recomendações:", 
                      font=("Arial", 12, "bold")).pack(pady=(0, 10))
            
            for i, recomendacao in enumerate(resultado["recomendacoes"], 1):
                ttk.Label(main_frame, text=f"{i}. {recomendacao}", 
                          font=("Arial", 10)).pack(anchor="w", pady=2)
        
        # Botão fechar
        ttk.Button(main_frame, text="❌ Fechar", 
                  command=janela_resumo.destroy).pack(pady=(20, 0))
    
    def _upload_backup(self):
        """Faz upload de um arquivo de backup."""
        try:
            arquivo = filedialog.askopenfilename(
                title="Selecionar arquivo de backup",
                filetypes=[
                    ("Arquivos SQL", "*.sql"),
                    ("Arquivos ZIP", "*.zip"),
                    ("Todos os arquivos", "*.*")
                ]
            )
            
            if arquivo:
                # Validar arquivo antes do upload
                if not self._validar_arquivo_upload(arquivo):
                    return
                
                self.log_manager.log_sistema("INFO", f"Fazendo upload: {arquivo}")
                
                sucesso, mensagem = self.db_manager.upload_backup(arquivo)
                
                if sucesso:
                    self.log_manager.log_sistema("SUCCESS", mensagem)
                    messagebox.showinfo("Sucesso", mensagem)
                    self._atualizar_lista_backups()
                else:
                    self.log_manager.log_sistema("ERROR", mensagem)
                    messagebox.showerror("Erro", mensagem)
                    
        except Exception as e:
            self.log_manager.log_sistema("ERROR", f"Erro ao fazer upload: {e}")
            messagebox.showerror("Erro", f"Erro ao fazer upload: {e}")
    
    def _validar_arquivo_upload(self, arquivo: str) -> bool:
        """Valida um arquivo de upload."""
        try:
            # Verificar se o arquivo existe
            if not os.path.exists(arquivo):
                messagebox.showerror("Erro", "Arquivo não encontrado")
                return False
            
            # Verificar tamanho do arquivo (máximo 100MB)
            tamanho = os.path.getsize(arquivo)
            tamanho_mb = tamanho / (1024 * 1024)
            
            if tamanho_mb > 100:
                resposta = messagebox.askyesno("Arquivo Grande", 
                                             f"O arquivo tem {tamanho_mb:.1f}MB. "
                                             "Arquivos grandes podem demorar muito. "
                                             "Deseja continuar?")
                if not resposta:
                    return False
            
            # Verificar extensão
            extensao = os.path.splitext(arquivo)[1].lower()
            extensoes_validas = ['.sql', '.zip', '.gz', '.tar']
            
            if extensao not in extensoes_validas:
                resposta = messagebox.askyesno("Extensão Desconhecida", 
                                             f"O arquivo tem extensão '{extensao}' que não é comum. "
                                             "Deseja continuar mesmo assim?")
                if not resposta:
                    return False
            
            return True
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao validar arquivo: {e}")
            return False
    
    def _restaurar_backup_melhorado(self):
        """Restaura um backup com opção de escolher arquivo específico."""
        # Criar janela de diálogo para escolher o arquivo
        arquivo_backup = filedialog.askopenfilename(
            title="Escolher arquivo de backup para restaurar",
            filetypes=[
                ("Arquivos SQL", "*.sql"),
                ("Arquivos de backup", "*.backup"),
                ("Arquivos comprimidos", "*.gz"),
                ("Todos os arquivos", "*.*")
            ],
            initialdir=Path.home() / "Downloads"  # Começar na pasta Downloads
        )
        
        if not arquivo_backup:
            return  # Usuário cancelou
        
        # Verificar se arquivo existe
        if not Path(arquivo_backup).exists():
            messagebox.showerror("Erro", "Arquivo selecionado não existe!")
            return
        
        # Mostrar informações do arquivo
        arquivo_path = Path(arquivo_backup)
        tamanho = arquivo_path.stat().st_size
        tamanho_mb = tamanho / (1024 * 1024)
        
        # Confirmar restauração
        resposta = messagebox.askyesno(
            "Confirmar Restauração", 
            f"Deseja restaurar o backup?\n\n"
            f"Arquivo: {arquivo_path.name}\n"
            f"Tamanho: {tamanho_mb:.2f} MB\n"
            f"Local: {arquivo_path.parent}\n\n"
            "ATENÇÃO: Esta operação pode substituir dados existentes!"
        )
        
        if resposta:
            if self.thread_operacao and self.thread_operacao.is_alive():
                messagebox.showwarning("Aviso", "Operação em andamento. Aguarde...")
                return
            
            self.thread_operacao = threading.Thread(
                target=self._executar_restaurar_backup_arquivo, 
                args=(arquivo_backup,)
            )
            self.thread_operacao.daemon = True
            self.thread_operacao.start()
    
    def _restaurar_backup(self):
        """Restaura um backup da lista."""
        selecao = self.tree_backups.selection()
        if not selecao:
            messagebox.showwarning("Aviso", "Selecione um backup para restaurar")
            return
        
        item = self.tree_backups.item(selecao[0])
        nome_backup = item['values'][0]
        
        # Confirmar restauração
        resposta = messagebox.askyesno("Confirmar Restauração", 
                                      f"Deseja restaurar o backup '{nome_backup}'?\n\n"
                                      "ATENÇÃO: Esta operação pode substituir dados existentes!")
        
        if resposta:
            if self.thread_operacao and self.thread_operacao.is_alive():
                messagebox.showwarning("Aviso", "Operação em andamento. Aguarde...")
                return
            
            self.thread_operacao = threading.Thread(
                target=self._executar_restaurar_backup, 
                args=(nome_backup,)
            )
            self.thread_operacao.daemon = True
            self.thread_operacao.start()
    
    def _executar_restaurar_backup_arquivo(self, arquivo_backup):
        """Executa a restauração de arquivo específico em thread separada."""
        try:
            arquivo_path = Path(arquivo_backup)
            self._mostrar_progresso(f"Restaurando backup: {arquivo_path.name}")
            self.log_manager.log_sistema("INFO", f"Restaurando backup de arquivo: {arquivo_path}")
            
            # Usar o método do db_manager para restaurar arquivo específico
            sucesso, mensagem = self.db_manager.restaurar_backup_arquivo(arquivo_backup)
            
            self._ocultar_progresso()
            
            if sucesso:
                self.log_manager.log_sistema("SUCCESS", mensagem)
                messagebox.showinfo("Sucesso", mensagem)
                self._verificar_status_inicial()
            else:
                self.log_manager.log_sistema("ERROR", mensagem)
                messagebox.showerror("Erro", mensagem)
                
        except Exception as e:
            self._ocultar_progresso()
            self.log_manager.log_sistema("ERROR", f"Erro inesperado: {e}")
            messagebox.showerror("Erro", f"Erro inesperado: {e}")
    
    def _executar_restaurar_backup(self, nome_backup):
        """Executa a restauração em thread separada."""
        try:
            self._mostrar_progresso(f"Restaurando backup: {nome_backup}")
            self.log_manager.log_sistema("INFO", f"Restaurando backup: {nome_backup}")
            
            sucesso, mensagem = self.db_manager.restaurar_backup(nome_backup)
            
            self._ocultar_progresso()
            
            if sucesso:
                self.log_manager.log_sistema("SUCCESS", mensagem)
                messagebox.showinfo("Sucesso", mensagem)
                self._verificar_status_inicial()
            else:
                self.log_manager.log_sistema("ERROR", mensagem)
                messagebox.showerror("Erro", mensagem)
                
        except Exception as e:
            self._ocultar_progresso()
            self.log_manager.log_sistema("ERROR", f"Erro inesperado: {e}")
            messagebox.showerror("Erro", f"Erro inesperado: {e}")
    
    def _substituir_base(self):
        """Substitui a base de dados atual por um backup."""
        selecao = self.tree_backups.selection()
        if not selecao:
            messagebox.showwarning("Aviso", "Selecione um backup para substituir a base")
            return
        
        item = self.tree_backups.item(selecao[0])
        nome_backup = item['values'][0]
        
        # Confirmar substituição
        resposta = messagebox.askyesno("Confirmar Substituição", 
                                      f"Deseja substituir a base de dados atual pelo backup '{nome_backup}'?\n\n"
                                      "ATENÇÃO: Esta operação irá:\n"
                                      "1. Fazer backup da base atual\n"
                                      "2. Substituir completamente pelos dados do backup\n"
                                      "3. Reiniciar o Planka\n\n"
                                      "Tem certeza?")
        
        if resposta:
            if self.thread_operacao and self.thread_operacao.is_alive():
                messagebox.showwarning("Aviso", "Operação em andamento. Aguarde...")
                return
            
            self.thread_operacao = threading.Thread(
                target=self._executar_substituir_base, 
                args=(nome_backup,)
            )
            self.thread_operacao.daemon = True
            self.thread_operacao.start()
    
    def _executar_substituir_base(self, nome_backup):
        """Executa a substituição em thread separada."""
        try:
            self._mostrar_progresso(f"Substituindo base por: {nome_backup}")
            self.log_manager.log_sistema("INFO", f"Substituindo base por: {nome_backup}")
            
            sucesso, mensagem = self.db_manager.substituir_base(nome_backup)
            
            self._ocultar_progresso()
            
            if sucesso:
                self.log_manager.log_sistema("SUCCESS", mensagem)
                messagebox.showinfo("Sucesso", mensagem)
                self._verificar_status_inicial()
            else:
                self.log_manager.log_sistema("ERROR", mensagem)
                messagebox.showerror("Erro", mensagem)
                
        except Exception as e:
            self._ocultar_progresso()
            self.log_manager.log_sistema("ERROR", f"Erro inesperado: {e}")
            messagebox.showerror("Erro", f"Erro inesperado: {e}")
    
    def _atualizar_lista_backups(self):
        """Atualiza a lista de backups."""
        try:
            # Limpar lista atual
            for item in self.tree_backups.get_children():
                self.tree_backups.delete(item)
            
            # Obter lista de backups
            backups = self.db_manager.listar_backups()
            
            # Adicionar backups à lista
            for backup in backups:
                tamanho_mb = backup["tamanho"] / (1024 * 1024)
                data_str = backup["data_criacao"].strftime("%d/%m/%Y %H:%M")
                
                self.tree_backups.insert("", "end", values=(
                    backup["nome"],
                    f"{tamanho_mb:.1f} MB",
                    data_str,
                    backup["tipo"]
                ))
                
        except Exception as e:
            self.log_manager.log_sistema("ERROR", f"Erro ao atualizar lista de backups: {e}")
    
    def _validar_backup_selecionado(self):
        """Valida o backup selecionado."""
        selecao = self.tree_backups.selection()
        if not selecao:
            messagebox.showwarning("Aviso", "Selecione um backup para validar")
            return
        
        item = self.tree_backups.item(selecao[0])
        nome_backup = item['values'][0]
        
        try:
            sucesso, mensagem = self.db_manager.validar_backup(nome_backup)
            
            if sucesso:
                messagebox.showinfo("Validação", f"✅ {mensagem}")
            else:
                messagebox.showerror("Validação", f"❌ {mensagem}")
                
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao validar backup: {e}")
    
    def _comprimir_backup_selecionado(self):
        """Comprime o backup selecionado."""
        selecao = self.tree_backups.selection()
        if not selecao:
            messagebox.showwarning("Aviso", "Selecione um backup para comprimir")
            return
        
        item = self.tree_backups.item(selecao[0])
        nome_backup = item['values'][0]
        
        # Verificar se já é um arquivo ZIP
        if nome_backup.endswith('.zip'):
            messagebox.showinfo("Info", "O backup já está comprimido")
            return
        
        try:
            sucesso, mensagem = self.db_manager.comprimir_backup(nome_backup)
            
            if sucesso:
                messagebox.showinfo("Sucesso", mensagem)
                self._atualizar_lista_backups()
            else:
                messagebox.showerror("Erro", mensagem)
                
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao comprimir backup: {e}")
    
    def _adicionar_tooltips(self):
        """Adiciona tooltips aos botões da interface."""
        try:
            # Tooltips para botões de ação
            self._criar_tooltip(self.btn_diagnostico, 
                               "Executa diagnóstico completo da base de dados, Docker e configuração")
            
            self._criar_tooltip(self.btn_backup, 
                               "Faz um backup completo da base de dados atual")
            
            self._criar_tooltip(self.btn_restaurar, 
                               "Restaura um backup - permite escolher arquivo específico ou da lista")
            
        except Exception as e:
            self.log_manager.log_sistema("WARNING", f"Erro ao criar tooltips: {e}")
    
    def _criar_tooltip(self, widget, texto):
        """Cria um tooltip simples para um widget."""
        def mostrar_tooltip(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
            
            label = tk.Label(tooltip, text=texto, 
                           justify=tk.LEFT,
                           background="#ffffe0", 
                           relief=tk.SOLID, 
                           borderwidth=1,
                           font=("Arial", "8", "normal"))
            label.pack()
            
            def esconder_tooltip(event):
                tooltip.destroy()
            
            widget.tooltip = tooltip
            widget.bind('<Leave>', esconder_tooltip)
        
        widget.bind('<Enter>', mostrar_tooltip)
    
    def _mostrar_progresso(self, mensagem: str):
        """Mostra a barra de progresso com mensagem."""
        self.lbl_progress.config(text=mensagem)
        self.progress_frame.pack(fill=tk.X, pady=(0, 10))
        self.progress_bar.start()
        self.update()
    
    def _ocultar_progresso(self):
        """Oculta a barra de progresso."""
        self.progress_bar.stop()
        self.progress_frame.pack_forget()
        self.update()
    
    def atualizar(self):
        """Atualiza a aba base de dados."""
        self._verificar_status_inicial() 