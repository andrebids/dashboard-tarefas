# -*- coding: utf-8 -*-
"""
Aba Base de Dados - Gestão da Base de Dados do Planka.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
from pathlib import Path
import sys

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
            config_dir = Path(settings.obter("config", "diretorio"))
            if not config_dir:
                # Fallback para diretório padrão
                config_dir = Path(__file__).parent.parent.parent / "config"
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
        
        # Primeira linha de botões
        linha1 = ttk.Frame(botoes_frame)
        linha1.pack(fill=tk.X, pady=(0, 10))
        
        # Botão Criar Base de Dados
        self.btn_criar = ttk.Button(linha1, text="🆕 Criar Base de Dados", 
                                    command=self._criar_base_dados)
        self.btn_criar.pack(side=tk.LEFT, padx=(0, 10))
        
        # Botão Inicializar Base
        self.btn_inicializar = ttk.Button(linha1, text="⚙️ Inicializar Base", 
                                          command=self._inicializar_base_dados)
        self.btn_inicializar.pack(side=tk.LEFT, padx=(0, 10))
        
        # Botão Criar Usuário Admin
        self.btn_admin = ttk.Button(linha1, text="👤 Criar Admin", 
                                    command=self._criar_usuario_admin)
        self.btn_admin.pack(side=tk.LEFT, padx=(0, 10))
        
        # Botão Editor
        self.btn_editor = ttk.Button(linha1, text="✏️ Abrir Editor", 
                                     command=self._abrir_editor)
        self.btn_editor.pack(side=tk.LEFT, padx=(0, 10))
        
        # Segunda linha de botões
        linha2 = ttk.Frame(botoes_frame)
        linha2.pack(fill=tk.X, pady=(0, 10))
        
        # Botão Backup
        self.btn_backup = ttk.Button(linha2, text="💾 Fazer Backup", 
                                     command=self._fazer_backup)
        self.btn_backup.pack(side=tk.LEFT, padx=(0, 10))
        
        # Botão Upload
        self.btn_upload = ttk.Button(linha2, text="📤 Upload Backup", 
                                     command=self._upload_backup)
        self.btn_upload.pack(side=tk.LEFT, padx=(0, 10))
        
        # Botão Restaurar
        self.btn_restaurar = ttk.Button(linha2, text="🔄 Restaurar", 
                                        command=self._restaurar_backup)
        self.btn_restaurar.pack(side=tk.LEFT, padx=(0, 10))
        
        # Botão Substituir
        self.btn_substituir = ttk.Button(linha2, text="🔄 Substituir Base", 
                                         command=self._substituir_base)
        self.btn_substituir.pack(side=tk.LEFT, padx=(0, 10))
        
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
            
            # Botões que precisam de PostgreSQL rodando
            self.btn_criar.config(state="normal" if conectividade["postgres_running"] else "disabled")
            
            # Botões que precisam de base existente
            base_existe = conectividade["database_exists"]
            self.btn_inicializar.config(state="normal" if base_existe else "disabled")
            self.btn_backup.config(state="normal" if base_existe else "disabled")
            self.btn_editor.config(state="normal" if base_existe else "disabled")
            
            # Botões que precisam de tabelas existentes
            tabelas_existem = conectividade["tables_exist"]
            self.btn_admin.config(state="normal" if tabelas_existem else "disabled")
            
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
            self.log_manager.log_sistema("INFO", "Criando base de dados...")
            
            sucesso, mensagem = self.db_manager.criar_base_dados()
            
            if sucesso:
                self.log_manager.log_sistema("SUCCESS", mensagem)
                messagebox.showinfo("Sucesso", mensagem)
                self._verificar_status_inicial()
            else:
                self.log_manager.log_sistema("ERROR", mensagem)
                messagebox.showerror("Erro", mensagem)
                
        except Exception as e:
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
            self.log_manager.log_sistema("INFO", "Inicializando base de dados...")
            
            sucesso, mensagem = self.db_manager.inicializar_base_dados()
            
            if sucesso:
                self.log_manager.log_sistema("SUCCESS", mensagem)
                messagebox.showinfo("Sucesso", mensagem)
                self._verificar_status_inicial()
            else:
                self.log_manager.log_sistema("ERROR", mensagem)
                messagebox.showerror("Erro", mensagem)
                
        except Exception as e:
            self.log_manager.log_sistema("ERROR", f"Erro inesperado: {e}")
            messagebox.showerror("Erro", f"Erro inesperado: {e}")
    
    def _criar_usuario_admin(self):
        """Cria um usuário administrador."""
        # Diálogo para obter dados do usuário
        dialog = tk.Toplevel(self)
        dialog.title("Criar Usuário Administrador")
        dialog.geometry("400x200")
        dialog.transient(self)
        dialog.grab_set()
        
        # Centralizar diálogo
        dialog.geometry("+%d+%d" % (self.winfo_rootx() + 50, self.winfo_rooty() + 50))
        
        # Frame principal
        frame = ttk.Frame(dialog, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Campos
        ttk.Label(frame, text="Email:").grid(row=0, column=0, sticky="w", pady=5)
        email_var = tk.StringVar()
        email_entry = ttk.Entry(frame, textvariable=email_var, width=30)
        email_entry.grid(row=0, column=1, sticky="ew", padx=(10, 0), pady=5)
        
        ttk.Label(frame, text="Senha:").grid(row=1, column=0, sticky="w", pady=5)
        password_var = tk.StringVar()
        password_entry = ttk.Entry(frame, textvariable=password_var, show="*", width=30)
        password_entry.grid(row=1, column=1, sticky="ew", padx=(10, 0), pady=5)
        
        # Botões
        botoes_frame = ttk.Frame(frame)
        botoes_frame.grid(row=2, column=0, columnspan=2, pady=20)
        
        def criar():
            email = email_var.get().strip()
            password = password_var.get().strip()
            
            if not email or not password:
                messagebox.showerror("Erro", "Preencha todos os campos")
                return
            
            dialog.destroy()
            
            # Executar criação em thread
            def executar_criacao():
                try:
                    self.log_manager.log_sistema("INFO", f"Criando usuário admin: {email}")
                    
                    sucesso, mensagem = self.db_manager.criar_usuario_admin(email, password)
                    
                    if sucesso:
                        self.log_manager.log_sistema("SUCCESS", mensagem)
                        messagebox.showinfo("Sucesso", mensagem)
                        self._verificar_status_inicial()
                    else:
                        self.log_manager.log_sistema("ERROR", mensagem)
                        messagebox.showerror("Erro", mensagem)
                        
                except Exception as e:
                    self.log_manager.log_sistema("ERROR", f"Erro inesperado: {e}")
                    messagebox.showerror("Erro", f"Erro inesperado: {e}")
            
            thread = threading.Thread(target=executar_criacao)
            thread.daemon = True
            thread.start()
        
        ttk.Button(botoes_frame, text="Criar", command=criar).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(botoes_frame, text="Cancelar", command=dialog.destroy).pack(side=tk.LEFT)
        
        # Configurar grid
        frame.columnconfigure(1, weight=1)
        
        # Focar no primeiro campo
        email_entry.focus()
    
    def _abrir_editor(self):
        """Abre o editor de base de dados."""
        try:
            # Diálogo para escolher editor
            editor = messagebox.askyesno("Editor", 
                                       "Deseja abrir o pgAdmin no navegador?\n\n"
                                       "Sim = pgAdmin (navegador)\n"
                                       "Não = DBeaver (aplicação)")
            
            editor_nome = "pgadmin" if editor else "dbeaver"
            
            sucesso, mensagem = self.db_manager.conectar_editor(editor_nome)
            
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
            self.log_manager.log_sistema("INFO", "Fazendo backup da base de dados...")
            
            sucesso, mensagem = self.db_manager.backup_completo()
            
            if sucesso:
                self.log_manager.log_sistema("SUCCESS", mensagem)
                messagebox.showinfo("Sucesso", mensagem)
                self._atualizar_lista_backups()
            else:
                self.log_manager.log_sistema("ERROR", mensagem)
                messagebox.showerror("Erro", mensagem)
                
        except Exception as e:
            self.log_manager.log_sistema("ERROR", f"Erro inesperado: {e}")
            messagebox.showerror("Erro", f"Erro inesperado: {e}")
    
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
    
    def _restaurar_backup(self):
        """Restaura um backup."""
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
    
    def _executar_restaurar_backup(self, nome_backup):
        """Executa a restauração em thread separada."""
        try:
            self.log_manager.log_sistema("INFO", f"Restaurando backup: {nome_backup}")
            
            sucesso, mensagem = self.db_manager.restaurar_backup(nome_backup)
            
            if sucesso:
                self.log_manager.log_sistema("SUCCESS", mensagem)
                messagebox.showinfo("Sucesso", mensagem)
                self._verificar_status_inicial()
            else:
                self.log_manager.log_sistema("ERROR", mensagem)
                messagebox.showerror("Erro", mensagem)
                
        except Exception as e:
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
            self.log_manager.log_sistema("INFO", f"Substituindo base por: {nome_backup}")
            
            sucesso, mensagem = self.db_manager.substituir_base(nome_backup)
            
            if sucesso:
                self.log_manager.log_sistema("SUCCESS", mensagem)
                messagebox.showinfo("Sucesso", mensagem)
                self._verificar_status_inicial()
            else:
                self.log_manager.log_sistema("ERROR", mensagem)
                messagebox.showerror("Erro", mensagem)
                
        except Exception as e:
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
    
    def atualizar(self):
        """Atualiza a aba base de dados."""
        self._verificar_status_inicial() 