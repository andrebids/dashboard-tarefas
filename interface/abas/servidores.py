# -*- coding: utf-8 -*-
"""
Interface da aba de servidores SSH.
Gerencia servidores, conexões e execução de comandos remotos.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
from typing import Optional
from datetime import datetime

from core.servidores import ServidorSSH, ServidoresManager


class AbaServidores(ttk.Frame):
    """
    Aba de gerenciamento de servidores SSH.
    """
    
    def __init__(self, parent, log_manager, settings):
        """
        Inicializa a aba de servidores.
        
        Args:
            parent: Widget pai
            log_manager: Gerenciador de logs
            settings: Configurações do sistema
        """
        super().__init__(parent)
        self.log_manager = log_manager
        self.settings = settings
        
        # Inicializar gerenciador de servidores
        self.servidores_manager = ServidoresManager(settings)
        
        # Variáveis de controle
        self.servidor_selecionado = None
        self.modo_edicao = False
        
        # Inicializar interface
        self._criar_interface()
        self._carregar_servidores()
    
    def _criar_interface(self):
        """Cria a interface da aba de servidores."""
        # Frame principal
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Frame superior - Formulário
        self._criar_frame_formulario(main_frame)
        
        # Separador
        ttk.Separator(main_frame, orient="horizontal").pack(fill=tk.X, pady=10)
        
        # Frame inferior - Lista de servidores
        self._criar_frame_lista(main_frame)
        
        # Frame inferior - Comandos
        self._criar_frame_comandos(main_frame)
    
    def _criar_frame_formulario(self, parent):
        """Cria o frame do formulário de servidor."""
        # Frame do formulário
        form_frame = ttk.LabelFrame(parent, text="📝 Adicionar/Editar Servidor", padding=10)
        form_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Grid do formulário
        form_frame.columnconfigure(1, weight=1)
        form_frame.columnconfigure(3, weight=1)
        
        # Nome do servidor
        ttk.Label(form_frame, text="Nome:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5), pady=2)
        self.entry_nome = ttk.Entry(form_frame, width=30)
        self.entry_nome.grid(row=0, column=1, sticky=tk.EW, padx=(0, 10), pady=2)
        
        # Host
        ttk.Label(form_frame, text="Host:").grid(row=0, column=2, sticky=tk.W, padx=(0, 5), pady=2)
        self.entry_host = ttk.Entry(form_frame, width=30)
        self.entry_host.grid(row=0, column=3, sticky=tk.EW, pady=2)
        
        # Porta
        ttk.Label(form_frame, text="Porta:").grid(row=1, column=0, sticky=tk.W, padx=(0, 5), pady=2)
        self.entry_porta = ttk.Entry(form_frame, width=10)
        self.entry_porta.insert(0, "22")
        self.entry_porta.grid(row=1, column=1, sticky=tk.W, padx=(0, 10), pady=2)
        
        # Usuário
        ttk.Label(form_frame, text="Usuário:").grid(row=1, column=2, sticky=tk.W, padx=(0, 5), pady=2)
        self.entry_usuario = ttk.Entry(form_frame, width=30)
        self.entry_usuario.grid(row=1, column=3, sticky=tk.EW, pady=2)
        
        # Senha
        ttk.Label(form_frame, text="Senha:").grid(row=2, column=0, sticky=tk.W, padx=(0, 5), pady=2)
        self.entry_senha = ttk.Entry(form_frame, width=30, show="*")
        self.entry_senha.grid(row=2, column=1, sticky=tk.EW, padx=(0, 10), pady=2)
        
        # Chave privada
        ttk.Label(form_frame, text="Chave Privada:").grid(row=2, column=2, sticky=tk.W, padx=(0, 5), pady=2)
        self.entry_chave = ttk.Entry(form_frame, width=30)
        self.entry_chave.grid(row=2, column=3, sticky=tk.EW, pady=2)
        
        # Botão para selecionar chave
        btn_chave = ttk.Button(form_frame, text="📁", width=3, command=self._selecionar_chave)
        btn_chave.grid(row=2, column=4, padx=(5, 0), pady=2)
        
        # Timeout
        ttk.Label(form_frame, text="Timeout (s):").grid(row=3, column=0, sticky=tk.W, padx=(0, 5), pady=2)
        self.entry_timeout = ttk.Entry(form_frame, width=10)
        self.entry_timeout.insert(0, "30")
        self.entry_timeout.grid(row=3, column=1, sticky=tk.W, padx=(0, 10), pady=2)
        
        # Ativo
        self.var_ativo = tk.BooleanVar(value=True)
        self.check_ativo = ttk.Checkbutton(form_frame, text="Ativo", variable=self.var_ativo)
        self.check_ativo.grid(row=3, column=2, sticky=tk.W, padx=(0, 10), pady=2)
        
        # Descrição
        ttk.Label(form_frame, text="Descrição:").grid(row=4, column=0, sticky=tk.W, padx=(0, 5), pady=2)
        self.entry_descricao = ttk.Entry(form_frame, width=70)
        self.entry_descricao.grid(row=4, column=1, columnspan=3, sticky=tk.EW, pady=2)
        
        # Frame de botões
        btn_frame = ttk.Frame(form_frame)
        btn_frame.grid(row=5, column=0, columnspan=4, pady=(10, 0))
        
        # Botões
        self.btn_adicionar = ttk.Button(btn_frame, text="➕ Adicionar", command=self._adicionar_servidor)
        self.btn_adicionar.pack(side=tk.LEFT, padx=(0, 5))
        
        self.btn_atualizar = ttk.Button(btn_frame, text="✏️ Atualizar", command=self._atualizar_servidor, state=tk.DISABLED)
        self.btn_atualizar.pack(side=tk.LEFT, padx=(0, 5))
        
        self.btn_cancelar = ttk.Button(btn_frame, text="❌ Cancelar", command=self._cancelar_edicao, state=tk.DISABLED)
        self.btn_cancelar.pack(side=tk.LEFT, padx=(0, 5))
        
        self.btn_limpar = ttk.Button(btn_frame, text="🧹 Limpar", command=self._limpar_formulario)
        self.btn_limpar.pack(side=tk.LEFT)
    
    def _criar_frame_lista(self, parent):
        """Cria o frame da lista de servidores."""
        # Frame da lista
        lista_frame = ttk.LabelFrame(parent, text="🖥️ Servidores SSH", padding=10)
        lista_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Frame superior - Estatísticas
        stats_frame = ttk.Frame(lista_frame)
        stats_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.lbl_stats = ttk.Label(stats_frame, text="Carregando estatísticas...")
        self.lbl_stats.pack(side=tk.LEFT)
        
        # Botões de ação
        btn_frame = ttk.Frame(lista_frame)
        btn_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(btn_frame, text="🔄 Atualizar", command=self._carregar_servidores).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_frame, text="🗑️ Remover", command=self._remover_servidor).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_frame, text="🔌 Testar Conexão", command=self._testar_conexao).pack(side=tk.LEFT)
        
        # TreeView para lista de servidores
        columns = ("ID", "Nome", "Host", "Porta", "Usuário", "Status", "Descrição")
        self.tree_servidores = ttk.Treeview(lista_frame, columns=columns, show="headings", height=8)
        
        # Configurar colunas
        self.tree_servidores.heading("ID", text="ID")
        self.tree_servidores.heading("Nome", text="Nome")
        self.tree_servidores.heading("Host", text="Host")
        self.tree_servidores.heading("Porta", text="Porta")
        self.tree_servidores.heading("Usuário", text="Usuário")
        self.tree_servidores.heading("Status", text="Status")
        self.tree_servidores.heading("Descrição", text="Descrição")
        
        # Configurar larguras
        self.tree_servidores.column("ID", width=50)
        self.tree_servidores.column("Nome", width=150)
        self.tree_servidores.column("Host", width=120)
        self.tree_servidores.column("Porta", width=60)
        self.tree_servidores.column("Usuário", width=100)
        self.tree_servidores.column("Status", width=80)
        self.tree_servidores.column("Descrição", width=200)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(lista_frame, orient=tk.VERTICAL, command=self.tree_servidores.yview)
        self.tree_servidores.configure(yscrollcommand=scrollbar.set)
        
        # Pack
        self.tree_servidores.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind para seleção
        self.tree_servidores.bind("<<TreeviewSelect>>", self._on_servidor_selecionado)
        self.tree_servidores.bind("<Double-1>", self._on_servidor_double_click)
    
    def _criar_frame_comandos(self, parent):
        """Cria o frame de execução de comandos."""
        # Frame de comandos
        cmd_frame = ttk.LabelFrame(parent, text="⚡ Executar Comando", padding=10)
        cmd_frame.pack(fill=tk.X)
        
        # Frame do comando
        cmd_input_frame = ttk.Frame(cmd_frame)
        cmd_input_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(cmd_input_frame, text="Comando:").pack(side=tk.LEFT, padx=(0, 5))
        self.entry_comando = ttk.Entry(cmd_input_frame, width=60)
        self.entry_comando.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        self.btn_executar = ttk.Button(cmd_input_frame, text="▶️ Executar", command=self._executar_comando, state=tk.DISABLED)
        self.btn_executar.pack(side=tk.RIGHT)
        
        # Frame de resultado
        resultado_frame = ttk.Frame(cmd_frame)
        resultado_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(resultado_frame, text="Resultado:").pack(anchor=tk.W)
        
        # Text widget para resultado
        self.text_resultado = tk.Text(resultado_frame, height=8, wrap=tk.WORD)
        scrollbar_resultado = ttk.Scrollbar(resultado_frame, orient=tk.VERTICAL, command=self.text_resultado.yview)
        self.text_resultado.configure(yscrollcommand=scrollbar_resultado.set)
        
        self.text_resultado.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_resultado.pack(side=tk.RIGHT, fill=tk.Y)
    
    def _selecionar_chave(self):
        """Abre diálogo para selecionar chave privada."""
        arquivo = filedialog.askopenfilename(
            title="Selecionar Chave Privada SSH",
            filetypes=[
                ("Chaves SSH", "*.pem *.ppk *.key"),
                ("Todos os arquivos", "*.*")
            ]
        )
        
        if arquivo:
            self.entry_chave.delete(0, tk.END)
            self.entry_chave.insert(0, arquivo)
    
    def _adicionar_servidor(self):
        """Adiciona um novo servidor."""
        try:
            # Validar campos obrigatórios
            nome = self.entry_nome.get().strip()
            host = self.entry_host.get().strip()
            usuario = self.entry_usuario.get().strip()
            
            if not nome or not host or not usuario:
                messagebox.showerror("Erro", "Nome, Host e Usuário são obrigatórios")
                return
            
            # Criar servidor
            servidor = ServidorSSH(
                nome=nome,
                host=host,
                porta=int(self.entry_porta.get() or "22"),
                usuario=usuario,
                senha=self.entry_senha.get(),
                chave_privada=self.entry_chave.get().strip(),
                timeout=int(self.entry_timeout.get() or "30"),
                descricao=self.entry_descricao.get().strip(),
                ativo=self.var_ativo.get()
            )
            
            # Adicionar ao banco
            sucesso, mensagem = self.servidores_manager.adicionar_servidor(servidor)
            
            if sucesso:
                self.log_manager.log_sistema("SUCCESS", f"Servidor adicionado: {nome}")
                messagebox.showinfo("Sucesso", mensagem)
                self._limpar_formulario()
                self._carregar_servidores()
            else:
                self.log_manager.log_sistema("ERROR", f"Erro ao adicionar servidor: {mensagem}")
                messagebox.showerror("Erro", mensagem)
                
        except ValueError as e:
            messagebox.showerror("Erro", f"Valor inválido: {e}")
        except Exception as e:
            self.log_manager.log_sistema("ERROR", f"Erro inesperado: {e}")
            messagebox.showerror("Erro", f"Erro inesperado: {e}")
    
    def _atualizar_servidor(self):
        """Atualiza o servidor selecionado."""
        if not self.servidor_selecionado:
            return
        
        try:
            # Validar campos obrigatórios
            nome = self.entry_nome.get().strip()
            host = self.entry_host.get().strip()
            usuario = self.entry_usuario.get().strip()
            
            if not nome or not host or not usuario:
                messagebox.showerror("Erro", "Nome, Host e Usuário são obrigatórios")
                return
            
            # Atualizar servidor
            self.servidor_selecionado.nome = nome
            self.servidor_selecionado.host = host
            self.servidor_selecionado.porta = int(self.entry_porta.get() or "22")
            self.servidor_selecionado.usuario = usuario
            self.servidor_selecionado.senha = self.entry_senha.get()
            self.servidor_selecionado.chave_privada = self.entry_chave.get().strip()
            self.servidor_selecionado.timeout = int(self.entry_timeout.get() or "30")
            self.servidor_selecionado.descricao = self.entry_descricao.get().strip()
            self.servidor_selecionado.ativo = self.var_ativo.get()
            
            # Salvar no banco
            sucesso, mensagem = self.servidores_manager.atualizar_servidor(self.servidor_selecionado)
            
            if sucesso:
                self.log_manager.log_sistema("SUCCESS", f"Servidor atualizado: {nome}")
                messagebox.showinfo("Sucesso", mensagem)
                self._cancelar_edicao()
                self._carregar_servidores()
            else:
                self.log_manager.log_sistema("ERROR", f"Erro ao atualizar servidor: {mensagem}")
                messagebox.showerror("Erro", mensagem)
                
        except ValueError as e:
            messagebox.showerror("Erro", f"Valor inválido: {e}")
        except Exception as e:
            self.log_manager.log_sistema("ERROR", f"Erro inesperado: {e}")
            messagebox.showerror("Erro", f"Erro inesperado: {e}")
    
    def _cancelar_edicao(self):
        """Cancela a edição e volta ao modo de adição."""
        self.modo_edicao = False
        self.servidor_selecionado = None
        
        self.btn_adicionar.config(state=tk.NORMAL)
        self.btn_atualizar.config(state=tk.DISABLED)
        self.btn_cancelar.config(state=tk.DISABLED)
        
        self._limpar_formulario()
    
    def _limpar_formulario(self):
        """Limpa todos os campos do formulário."""
        self.entry_nome.delete(0, tk.END)
        self.entry_host.delete(0, tk.END)
        self.entry_porta.delete(0, tk.END)
        self.entry_porta.insert(0, "22")
        self.entry_usuario.delete(0, tk.END)
        self.entry_senha.delete(0, tk.END)
        self.entry_chave.delete(0, tk.END)
        self.entry_timeout.delete(0, tk.END)
        self.entry_timeout.insert(0, "30")
        self.entry_descricao.delete(0, tk.END)
        self.var_ativo.set(True)
    
    def _carregar_servidores(self):
        """Carrega a lista de servidores."""
        try:
            # Limpar lista atual
            for item in self.tree_servidores.get_children():
                self.tree_servidores.delete(item)
            
            # Carregar servidores
            servidores = self.servidores_manager.listar_servidores()
            
            for servidor in servidores:
                status = "🟢 Ativo" if servidor.ativo else "🔴 Inativo"
                
                self.tree_servidores.insert("", tk.END, values=(
                    servidor.id,
                    servidor.nome,
                    servidor.host,
                    servidor.porta,
                    servidor.usuario,
                    status,
                    servidor.descricao
                ))
            
            # Atualizar estatísticas
            self._atualizar_estatisticas()
            
        except Exception as e:
            self.log_manager.log_sistema("ERROR", f"Erro ao carregar servidores: {e}")
            messagebox.showerror("Erro", f"Erro ao carregar servidores: {e}")
    
    def _atualizar_estatisticas(self):
        """Atualiza as estatísticas dos servidores."""
        try:
            stats = self.servidores_manager.obter_estatisticas()
            
            texto = (f"📊 Total: {stats.get('total_servidores', 0)} | "
                    f"🟢 Ativos: {stats.get('servidores_ativos', 0)} | "
                    f"🔌 Conexões: {stats.get('conexoes_ativas', 0)} | "
                    f"📈 Hoje: {stats.get('conexoes_hoje', 0)}")
            
            self.lbl_stats.config(text=texto)
            
        except Exception as e:
            self.lbl_stats.config(text="Erro ao carregar estatísticas")
    
    def _on_servidor_selecionado(self, event):
        """Evento de seleção de servidor."""
        selection = self.tree_servidores.selection()
        if selection:
            item = self.tree_servidores.item(selection[0])
            servidor_id = item['values'][0]
            
            # Habilitar botão de executar comando
            self.btn_executar.config(state=tk.NORMAL)
    
    def _on_servidor_double_click(self, event):
        """Evento de duplo clique no servidor."""
        selection = self.tree_servidores.selection()
        if selection:
            item = self.tree_servidores.item(selection[0])
            servidor_id = item['values'][0]
            
            # Carregar servidor para edição
            servidor = self.servidores_manager.obter_servidor(servidor_id)
            if servidor:
                self._carregar_servidor_para_edicao(servidor)
    
    def _carregar_servidor_para_edicao(self, servidor: ServidorSSH):
        """Carrega um servidor no formulário para edição."""
        self.servidor_selecionado = servidor
        self.modo_edicao = True
        
        # Preencher formulário
        self.entry_nome.delete(0, tk.END)
        self.entry_nome.insert(0, servidor.nome)
        
        self.entry_host.delete(0, tk.END)
        self.entry_host.insert(0, servidor.host)
        
        self.entry_porta.delete(0, tk.END)
        self.entry_porta.insert(0, str(servidor.porta))
        
        self.entry_usuario.delete(0, tk.END)
        self.entry_usuario.insert(0, servidor.usuario)
        
        self.entry_senha.delete(0, tk.END)
        self.entry_senha.insert(0, servidor.senha)
        
        self.entry_chave.delete(0, tk.END)
        self.entry_chave.insert(0, servidor.chave_privada)
        
        self.entry_timeout.delete(0, tk.END)
        self.entry_timeout.insert(0, str(servidor.timeout))
        
        self.entry_descricao.delete(0, tk.END)
        self.entry_descricao.insert(0, servidor.descricao)
        
        self.var_ativo.set(servidor.ativo)
        
        # Atualizar botões
        self.btn_adicionar.config(state=tk.DISABLED)
        self.btn_atualizar.config(state=tk.NORMAL)
        self.btn_cancelar.config(state=tk.NORMAL)
    
    def _remover_servidor(self):
        """Remove o servidor selecionado."""
        selection = self.tree_servidores.selection()
        if not selection:
            messagebox.showwarning("Aviso", "Selecione um servidor para remover")
            return
        
        item = self.tree_servidores.item(selection[0])
        servidor_id = item['values'][0]
        nome_servidor = item['values'][1]
        
        # Confirmar remoção
        if not messagebox.askyesno("Confirmar", f"Deseja remover o servidor '{nome_servidor}'?"):
            return
        
        try:
            sucesso, mensagem = self.servidores_manager.remover_servidor(servidor_id)
            
            if sucesso:
                self.log_manager.log_sistema("SUCCESS", f"Servidor removido: {nome_servidor}")
                messagebox.showinfo("Sucesso", mensagem)
                self._carregar_servidores()
                
                # Se estava editando este servidor, cancelar edição
                if self.servidor_selecionado and self.servidor_selecionado.id == servidor_id:
                    self._cancelar_edicao()
            else:
                self.log_manager.log_sistema("ERROR", f"Erro ao remover servidor: {mensagem}")
                messagebox.showerror("Erro", mensagem)
                
        except Exception as e:
            self.log_manager.log_sistema("ERROR", f"Erro inesperado: {e}")
            messagebox.showerror("Erro", f"Erro inesperado: {e}")
    
    def _testar_conexao(self):
        """Testa a conexão com o servidor selecionado."""
        selection = self.tree_servidores.selection()
        if not selection:
            messagebox.showwarning("Aviso", "Selecione um servidor para testar")
            return
        
        item = self.tree_servidores.item(selection[0])
        servidor_id = item['values'][0]
        nome_servidor = item['values'][1]
        
        # Executar teste em thread separada
        def executar_teste():
            try:
                self.log_manager.log_sistema("INFO", f"Testando conexão: {nome_servidor}")
                
                sucesso, mensagem = self.servidores_manager.testar_conexao(servidor_id)
                
                if sucesso:
                    self.log_manager.log_sistema("SUCCESS", f"Conexão OK: {nome_servidor}")
                    messagebox.showinfo("Teste de Conexão", f"✅ {mensagem}")
                else:
                    self.log_manager.log_sistema("ERROR", f"Falha na conexão: {nome_servidor} - {mensagem}")
                    messagebox.showerror("Teste de Conexão", f"❌ {mensagem}")
                    
            except Exception as e:
                self.log_manager.log_sistema("ERROR", f"Erro no teste: {e}")
                messagebox.showerror("Erro", f"Erro no teste: {e}")
        
        thread = threading.Thread(target=executar_teste, daemon=True)
        thread.start()
    
    def _executar_comando(self):
        """Executa um comando no servidor selecionado."""
        selection = self.tree_servidores.selection()
        if not selection:
            messagebox.showwarning("Aviso", "Selecione um servidor para executar comando")
            return
        
        comando = self.entry_comando.get().strip()
        if not comando:
            messagebox.showwarning("Aviso", "Digite um comando para executar")
            return
        
        item = self.tree_servidores.item(selection[0])
        servidor_id = item['values'][0]
        nome_servidor = item['values'][1]
        
        # Limpar resultado anterior
        self.text_resultado.delete(1.0, tk.END)
        self.text_resultado.insert(tk.END, f"Executando comando em {nome_servidor}...\n")
        self.text_resultado.see(tk.END)
        
        # Executar comando em thread separada
        def executar_comando():
            try:
                self.log_manager.log_sistema("INFO", f"Executando comando em {nome_servidor}: {comando}")
                
                sucesso, stdout, stderr, mensagem = self.servidores_manager.executar_comando(servidor_id, comando)
                
                # Atualizar resultado na interface principal
                self.after(0, lambda: self._mostrar_resultado_comando(sucesso, stdout, stderr, mensagem))
                
            except Exception as e:
                self.log_manager.log_sistema("ERROR", f"Erro ao executar comando: {e}")
                self.after(0, lambda: self._mostrar_resultado_comando(False, "", "", f"Erro: {e}"))
        
        thread = threading.Thread(target=executar_comando, daemon=True)
        thread.start()
    
    def _mostrar_resultado_comando(self, sucesso: bool, stdout: str, stderr: str, mensagem: str):
        """Mostra o resultado do comando executado."""
        self.text_resultado.delete(1.0, tk.END)
        
        if sucesso:
            self.text_resultado.insert(tk.END, f"✅ {mensagem}\n\n")
            self.log_manager.log_sistema("SUCCESS", f"Comando executado com sucesso")
        else:
            self.text_resultado.insert(tk.END, f"❌ {mensagem}\n\n")
            self.log_manager.log_sistema("ERROR", f"Comando falhou: {mensagem}")
        
        if stdout:
            self.text_resultado.insert(tk.END, "=== STDOUT ===\n")
            self.text_resultado.insert(tk.END, stdout)
            self.text_resultado.insert(tk.END, "\n")
        
        if stderr:
            self.text_resultado.insert(tk.END, "=== STDERR ===\n")
            self.text_resultado.insert(tk.END, stderr)
            self.text_resultado.insert(tk.END, "\n")
        
        self.text_resultado.see(tk.END)
    
    def atualizar(self):
        """Atualiza a aba de servidores."""
        self._carregar_servidores() 