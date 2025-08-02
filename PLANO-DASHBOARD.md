# 🐍 PLANO DASHBOARD PYTHON - SISTEMA SIMPLIFICADO
## Automação Windows + Linux Remoto com Python e Tkinter

---

## 📋 **VISÃO GERAL DO PROJETO**

### **Objetivo Principal**
Dashboard desktop Python simples para Windows que permite executar comandos automatizados tanto localmente (Windows) quanto em servidores Linux remotos, com **interface Tkinter nativa** e **arquitetura simplificada** que facilita a manutenção e expansão do sistema.

### **Por que Python + Tkinter?**
- ✅ **Simplicidade**: Uma linguagem só, sem dependências complexas
- ✅ **Interface Nativa**: Tkinter já vem com Python, sem necessidade de navegador
- ✅ **Bibliotecas Nativas**: SSH, banco de dados, agendamento com bibliotecas Python
- ✅ **Execução Direta**: `python main.py` - sem servidores web
- ✅ **Menos Dependências**: Não precisa Node.js, npm, Docker para o dashboard
- ✅ **Mais Estável**: Menos camadas de abstração = menos problemas

### **Princípios de Organização**
- **Simplicidade**: Código limpo e direto
- **Interface Nativa**: Tkinter desktop, não web
- **Modularidade**: Cada funcionalidade em seu próprio módulo Python
- **Armazenamento Local**: SQLite para configurações e histórico
- **Execução Direta**: Comandos executados diretamente pelo Python

---

## 🏗️ **ESTRUTURA TÉCNICA**

### **Tecnologias Escolhidas**
- **Linguagem**: Python 3.8+
- **Interface**: Tkinter (nativo)
- **SSH**: paramiko
- **Banco**: sqlite3 (nativo)
- **Agendamento**: schedule
- **Criptografia**: cryptography
- **Execução**: subprocess (nativo)

### **Estrutura de Pastas Simplificada**
```
dashboard-tarefas-python/
├── main.py                    # Aplicação principal
├── interface/                 # Interface Tkinter
│   ├── dashboard.py          # Janela principal
│   ├── abas/                 # Abas do dashboard
│   │   ├── principal.py      # Aba principal (Planka)
│   │   ├── servidores.py     # Aba de servidores SSH
│   │   └── logs.py           # Aba de logs
│   └── componentes/          # Componentes reutilizáveis
│       ├── console.py        # Console de logs
│       ├── modal.py          # Janelas modais
│       └── widgets.py        # Widgets customizados
├── core/                     # Lógica de negócio
│   ├── planka.py            # Controle do Planka
│   ├── servidores.py        # Conexões SSH
│   ├── agendamento.py       # Sistema de agendamento
│   └── comandos.py          # Execução de comandos
├── database/                 # Banco de dados
│   ├── database.py          # Configuração SQLite
│   ├── models.py            # Modelos de dados
│   └── migrations.py        # Migrações do banco
├── config/                   # Configurações
│   ├── settings.py          # Configurações gerais
│   └── credentials.py       # Credenciais (criptografadas)
├── logs/                     # Logs do sistema
│   ├── sistema/             # Logs do sistema
│   └── servidores/          # Logs de servidores
├── executaveis/              # Scripts .bat
│   ├── iniciar.bat          # Iniciar dashboard
│   ├── parar.bat            # Parar dashboard
│   └── atalho.bat           # Atalho inteligente
├── tests/                    # Testes automatizados
│   ├── test_planka.py       # Testes do módulo Planka
│   ├── test_servidores.py   # Testes do módulo Servidores
│   └── test_interface.py    # Testes da interface
├── requirements.txt          # Dependências Python
├── README.md                 # Documentação
└── .gitignore               # Arquivos ignorados pelo Git
```

---

## 🎨 **INTERFACE DO USUÁRIO - TKINTER**

### **Janela Principal**
- **Título**: "Dashboard de Tarefas - Python"
- **Tamanho**: 1200x800 pixels
- **Posição**: Centralizada na tela
- **Ícone**: Ícone personalizado do dashboard

### **Sistema de Abas (Notebook)**
- **Aba 1**: 🏠 Principal (Controle do Planka)
- **Aba 2**: 🖥️ Servidores (Conexões SSH)
- **Aba 3**: 📋 Logs (Histórico de logs)

### **Console Global (Fixada na parte inferior)**
- **Altura**: 200 pixels
- **Cores**: Verde (sucesso), Vermelho (erro), Amarelo (aviso), Azul (info)
- **Auto-scroll**: Sempre mostra as mensagens mais recentes
- **Botões**: Limpar, Exportar, Filtros

---

## 📋 **TAREFAS DE DESENVOLVIMENTO**

### **FASE 1: FUNDAÇÃO E ESTRUTURA BÁSICA**
**Duração**: 3-4 dias
**Objetivo**: Criar a estrutura básica e interface principal

#### **Tarefa 1.1: Configuração do Ambiente**
- [ ] **Criar estrutura de pastas** conforme definido
- [ ] **Criar arquivo requirements.txt** com dependências
- [ ] **Configurar .gitignore** para Python
- [ ] **Criar README.md** com instruções de instalação
- [ ] **Testar instalação**: `pip install -r requirements.txt`

#### **Tarefa 1.2: Interface Principal**
- [ ] **Criar main.py** - ponto de entrada da aplicação
- [ ] **Criar dashboard.py** - janela principal com Tkinter
- [ ] **Implementar sistema de abas** (Notebook)
- [ ] **Criar console global** na parte inferior
- [ ] **Implementar menu principal** (Arquivo, Editar, Ajuda)

#### **Tarefa 1.3: Componentes Base**
- [ ] **Criar console.py** - componente de logs reutilizável
- [ ] **Criar modal.py** - sistema de janelas modais
- [ ] **Criar widgets.py** - widgets customizados (botões, labels, etc.)
- [ ] **Implementar tema visual** consistente

#### **Tarefa 1.4: Sistema de Logs Básico**
- [ ] **Criar sistema de logs** em arquivos
- [ ] **Implementar níveis de log** (INFO, WARNING, ERROR, SUCCESS)
- [ ] **Criar função de registro de logs** reutilizável
- [ ] **Conectar console com sistema de logs**

**Testes Fase 1:**
- [ ] **Testar execução**: `python main.py`
- [ ] **Testar interface**: Todas as abas abrem corretamente
- [ ] **Testar console**: Logs aparecem na console
- [ ] **Testar responsividade**: Interface se adapta ao redimensionamento

---

### **FASE 2: CONTROLE DO PLANKA**
**Duração**: 3-4 dias
**Objetivo**: Implementar controle completo do Planka

#### **Tarefa 2.1: Módulo Planka**
- [ ] **Criar planka.py** - módulo de controle do Planka
- [ ] **Implementar verificação de Docker** instalado
- [ ] **Implementar verificação de Node.js** instalado
- [ ] **Implementar verificação de Git** instalado
- [ ] **Criar função de verificação de dependências**

#### **Tarefa 2.2: Controle de Inicialização**
- [ ] **Implementar função iniciar_planka()**
- [ ] **Implementar função parar_planka()**
- [ ] **Implementar função reiniciar_planka()**
- [ ] **Implementar verificação de status** (online/offline)
- [ ] **Implementar abertura automática no navegador**

#### **Tarefa 2.3: Modo Desenvolvimento**
- [ ] **Implementar modo desenvolvimento** (npm run dev)
- [ ] **Implementar hot reload** (monitoramento de arquivos)
- [ ] **Implementar build automático**
- [ ] **Implementar logs de desenvolvimento**

#### **Tarefa 2.4: Aba Principal**
- [ ] **Criar aba principal** com botões grandes
- [ ] **Implementar botão "Iniciar Planka"**
- [ ] **Implementar botão "Parar Planka"**
- [ ] **Implementar botão "Modo Desenvolvimento"**
- [ ] **Implementar indicador de status** (online/offline)
- [ ] **Implementar logs em tempo real** do Planka

**Testes Fase 2:**
- [ ] **Testar verificação de dependências**: Docker, Node.js, Git
- [ ] **Testar inicialização do Planka**: docker-compose up -d
- [ ] **Testar parada do Planka**: docker-compose down
- [ ] **Testar modo desenvolvimento**: npm run dev
- [ ] **Testar logs em tempo real**: Console mostra logs do Planka

---

### **FASE 2.5: GESTÃO DA BASE DE DADOS DO PLANKA**
**Duração**: 2-3 dias
**Objetivo**: Implementar controle completo da base de dados PostgreSQL do Planka

#### **Tarefa 2.5.1: Módulo de Gestão de Base de Dados**
- [ ] **Criar planka_database.py** - módulo de gestão da base de dados
- [ ] **Implementar verificação de status da base** (conectividade, tabelas)
- [ ] **Implementar análise da estrutura** (listar tabelas, colunas, relacionamentos)
- [ ] **Implementar verificação de dados** (contagem de registros por tabela)
- [ ] **Implementar diagnóstico de saúde** da base de dados

#### **Tarefa 2.5.2: Criação e Inicialização de Base de Dados**
- [ ] **Implementar criar_base_dados()** - criar nova base de dados PostgreSQL
- [ ] **Implementar inicializar_base_dados()** - executar migrações e seeders
- [ ] **Implementar verificar_estrutura()** - validar se todas as tabelas existem
- [ ] **Implementar configurar_permissoes()** - configurar permissões de acesso

#### **Tarefa 2.5.3: Editor de Base de Dados**
- [ ] **Implementar conectar_editor()** - abrir pgAdmin ou DBeaver
- [ ] **Implementar interface_sql()** - interface SQL integrada
- [ ] **Implementar visualizador_tabelas()** - visualizar estrutura das tabelas
- [ ] **Implementar editor_dados()** - editar dados diretamente
- [ ] **Implementar executar_query()** - executar consultas SQL customizadas

#### **Tarefa 2.5.4: Sistema de Backup**
- [ ] **Implementar backup_completo()** - backup completo da base de dados
- [ ] **Implementar backup_incremental()** - backup apenas de mudanças
- [ ] **Implementar backup_automatico()** - agendamento de backups
- [ ] **Implementar compressao_backup()** - compactar arquivos de backup
- [ ] **Implementar rotacao_backups()** - manter apenas backups recentes

#### **Tarefa 2.5.5: Sistema de Restauração**
- [ ] **Implementar restaurar_backup()** - restaurar de arquivo de backup
- [ ] **Implementar validar_backup()** - verificar integridade do backup
- [ ] **Implementar preview_backup()** - visualizar conteúdo do backup
- [ ] **Implementar restaurar_seletivo()** - restaurar apenas tabelas específicas
- [ ] **Implementar modo_teste()** - restaurar em ambiente de teste

#### **Tarefa 2.5.6: Upload e Substituição**
- [ ] **Implementar upload_backup()** - fazer upload de arquivo de backup
- [ ] **Implementar substituir_base()** - substituir base atual por backup
- [ ] **Implementar backup_atual()** - fazer backup antes da substituição
- [ ] **Implementar validar_upload()** - verificar arquivo de upload
- [ ] **Implementar rollback()** - reverter substituição se necessário

#### **Tarefa 2.5.7: Interface de Gestão de Base de Dados**
- [ ] **Criar aba "Base de Dados"** na interface principal
- [ ] **Implementar painel de status** (conectividade, tamanho, tabelas)
- [ ] **Implementar botões de ação** (Criar, Backup, Restaurar, Editor)
- [ ] **Implementar lista de backups** com informações detalhadas
- [ ] **Implementar upload de arquivos** com drag & drop
- [ ] **Implementar logs de operações** de base de dados

#### **Tarefa 2.5.8: Funcionalidades Avançadas**
- [ ] **Implementar migracao_dados()** - migrar dados entre versões
- [ ] **Implementar limpeza_dados()** - limpar dados antigos/desnecessários
- [ ] **Implementar otimizacao_base()** - otimizar performance
- [ ] **Implementar monitoramento()** - monitorar uso e performance
- [ ] **Implementar alertas()** - alertas de problemas na base

**Testes Fase 2.5:**
- [ ] **Testar criação de base**: Nova base de dados criada corretamente
- [ ] **Testar backup**: Backup completo e incremental funcionam
- [ ] **Testar restauração**: Restauração de backup funciona
- [ ] **Testar upload**: Upload e substituição funcionam
- [ ] **Testar editor**: Interface de edição funciona
- [ ] **Testar interface**: Todas as operações funcionam na interface

---

### **FASE 4: CONEXÕES SSH**
**Duração**: 3-4 dias
**Objetivo**: Implementar gerenciamento de servidores SSH

#### **Tarefa 4.1: Módulo Servidores**
- [ ] **Criar servidores.py** - módulo de conexões SSH
- [ ] **Implementar conectar_ssh()** - conexão SSH básica
- [ ] **Implementar executar_comando_ssh()** - executar comandos via SSH
- [ ] **Implementar testar_conexao()** - testar conectividade
- [ ] **Implementar desconectar_ssh()** - fechar conexão
- [ ] **Implementar pool de conexões** - reutilizar conexões

#### **Tarefa 4.2: Gerenciamento de Credenciais**
- [ ] **Criar credentials.py** - módulo de credenciais
- [ ] **Implementar criptografia** de senhas (AES-256)
- [ ] **Implementar armazenamento seguro** em arquivo local
- [ ] **Implementar chaves SSH** (arquivos .pem, .ppk)
- [ ] **Implementar backup automático** de credenciais

#### **Tarefa 4.3: Banco de Dados Servidores**
- [ ] **Implementar tabela servidores** (id, nome, host, porta, usuario, etc.)
- [ ] **Implementar tabela conexoes** (id, servidor_id, timestamp, status, etc.)
- [ ] **Implementar relacionamentos** entre tabelas

#### **Tarefa 4.4: Aba Servidores**
- [ ] **Criar aba servidores** com interface completa
- [ ] **Implementar lista de servidores** (TreeView)
- [ ] **Implementar formulário** para adicionar/editar servidores
- [ ] **Implementar botão "Testar Conexão"**
- [ ] **Implementar indicador de status** (online/offline)
- [ ] **Implementar histórico de conexões**

**Testes Fase 4:**
- [ ] **Testar conexão SSH**: Conectar a servidor Linux
- [ ] **Testar execução de comandos**: Comandos via SSH
- [ ] **Testar criptografia**: Senhas criptografadas corretamente
- [ ] **Testar interface**: Adicionar, editar, testar servidores
- [ ] **Testar pool de conexões**: Múltiplas conexões simultâneas

---

### **FASE 5: SISTEMA DE LOGS AVANÇADO**
**Duração**: 2-3 dias
**Objetivo**: Implementar sistema completo de logs

#### **Tarefa 5.1: Módulo Logs**
- [ ] **Criar logs.py** - módulo de logs avançado
- [ ] **Implementar níveis de log** (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- [ ] **Implementar rotação de logs** (por data/tamanho)
- [ ] **Implementar filtros** (por tipo, data, origem)
- [ ] **Implementar busca** em logs
- [ ] **Implementar exportação** (CSV, JSON, TXT)

#### **Tarefa 5.2: Banco de Dados Logs**
- [ ] **Implementar tabela logs_detalhados** (logs estruturados)
- [ ] **Implementar índices** para busca rápida
- [ ] **Implementar limpeza automática** de logs antigos
- [ ] **Implementar backup** de logs importantes

#### **Tarefa 5.3: Aba Logs**
- [ ] **Criar aba logs** com interface avançada
- [ ] **Implementar visualização de logs** (TreeView com colunas)
- [ ] **Implementar filtros** (por tipo, data, origem)
- [ ] **Implementar busca** em tempo real
- [ ] **Implementar botões de ação** (Exportar, Limpar, Atualizar)
- [ ] **Implementar gráficos** simples (estatísticas)

**Testes Fase 5:**
- [ ] **Testar registro de logs**: Todos os níveis funcionam
- [ ] **Testar rotação**: Logs são rotacionados corretamente
- [ ] **Testar filtros**: Filtros funcionam corretamente
- [ ] **Testar busca**: Busca encontra resultados
- [ ] **Testar exportação**: Logs são exportados corretamente

---

### **FASE 6: INTEGRAÇÃO E POLIMENTO**
**Duração**: 2-3 dias
**Objetivo**: Integrar todos os módulos e polir a interface

#### **Tarefa 6.1: Integração de Módulos**
- [ ] **Integrar todos os módulos** no main.py
- [ ] **Implementar comunicação** entre abas
- [ ] **Implementar sincronização** de dados
- [ ] **Implementar tratamento de erros** global
- [ ] **Implementar sistema de notificações**

#### **Tarefa 6.2: Scripts de Inicialização**
- [ ] **Criar iniciar.bat** - iniciar dashboard
- [ ] **Criar parar.bat** - parar dashboard
- [ ] **Criar atalho.bat** - atalho inteligente
- [ ] **Implementar verificação de processo** já rodando
- [ ] **Implementar inicialização automática** com Windows

#### **Tarefa 6.3: Polimento da Interface**
- [ ] **Refinar design visual** (cores, fontes, espaçamentos)
- [ ] **Implementar tooltips** explicativos
- [ ] **Implementar atalhos de teclado**
- [ ] **Implementar menu de contexto** (clique direito)
- [ ] **Implementar barra de status** com informações

#### **Tarefa 6.4: Documentação**
- [ ] **Atualizar README.md** com instruções completas
- [ ] **Criar manual do usuário** (PDF ou HTML)
- [ ] **Documentar código** (docstrings)
- [ ] **Criar guia de instalação** passo a passo

**Testes Fase 6:**
- [ ] **Teste de integração**: Todos os módulos funcionam juntos
- [ ] **Teste de interface**: Interface polida e responsiva
- [ ] **Teste de scripts**: Scripts .bat funcionam corretamente
- [ ] **Teste de documentação**: Instruções claras e completas

---

## 🧪 **TESTES AUTOMATIZADOS**

### **Estrutura de Testes**
```
tests/
├── test_planka.py          # Testes do módulo Planka
├── test_servidores.py      # Testes do módulo Servidores
├── test_logs.py            # Testes do módulo Logs
├── test_database.py        # Testes do banco de dados
├── test_interface.py       # Testes da interface
└── test_integration.py     # Testes de integração
```

### **Tarefas de Teste por Fase**

#### **Testes Fase 1:**
- [ ] **test_interface.py**: Testar criação da janela principal
- [ ] **test_console.py**: Testar sistema de logs básico
- [ ] **test_widgets.py**: Testar widgets customizados

#### **Testes Fase 2:**
- [ ] **test_planka.py**: Testar verificação de dependências
- [ ] **test_planka.py**: Testar controle de inicialização
- [ ] **test_planka.py**: Testar modo desenvolvimento

#### **Testes Fase 2.5:**
- [ ] **test_planka_database.py**: Testar gestão da base de dados
- [ ] **test_planka_database.py**: Testar backup e restauração
- [ ] **test_planka_database.py**: Testar upload e substituição
- [ ] **test_planka_database.py**: Testar editor de base de dados

#### **Testes Fase 4:**
- [ ] **test_servidores.py**: Testar conexões SSH
- [ ] **test_credentials.py**: Testar criptografia
- [ ] **test_servidores.py**: Testar pool de conexões

#### **Testes Fase 5:**
- [ ] **test_logs.py**: Testar sistema de logs
- [ ] **test_logs.py**: Testar filtros e busca
- [ ] **test_logs.py**: Testar exportação

#### **Testes Fase 6:**
- [ ] **test_integration.py**: Testar integração completa
- [ ] **test_interface.py**: Testar interface polida
- [ ] **test_scripts.py**: Testar scripts .bat

### **Execução de Testes**
```bash
# Executar todos os testes
python -m pytest tests/

# Executar testes específicos
python -m pytest tests/test_planka.py

# Executar com cobertura
python -m pytest --cov=. tests/
```

---

## 📦 **DEPENDÊNCIAS E INSTALAÇÃO**

### **requirements.txt**
```txt
# Interface
tkinter (já vem com Python)

# SSH
paramiko==3.4.0

# Requisições HTTP
requests==2.31.0

# Agendamento
schedule==1.2.0

# Criptografia
cryptography==41.0.0

# PostgreSQL (para gestão da base de dados do Planka)
psycopg2-binary==2.9.7

# Testes
pytest==7.4.0
pytest-cov==4.1.0

# Desenvolvimento
black==23.7.0
flake8==6.0.0
```

### **Instalação**
```bash
# 1. Instalar Python 3.8+
# Baixar de: https://python.org

# 2. Clonar repositório
git clone [url-do-repositorio]
cd dashboard-tarefas-python

# 3. Instalar dependências
pip install -r requirements.txt

# 4. Executar
python main.py
```

---

## 🚀 **SCRIPT DE INICIALIZAÇÃO**

### **iniciar.bat**
```batch
@echo off
echo Iniciando Dashboard Python...
cd /d "%~dp0"
python main.py
pause
```

### **parar.bat**
```batch
@echo off
echo Parando Dashboard Python...
taskkill /f /im python.exe /fi "WINDOWTITLE eq Dashboard*"
echo Dashboard parado com sucesso!
pause
```

### **atalho.bat**
```batch
@echo off
cd /d "%~dp0"
echo Verificando status do Dashboard...
tasklist /fi "IMAGENAME eq python.exe" /fi "WINDOWTITLE eq Dashboard*" | find "python.exe" >nul
if %errorlevel% equ 0 (
    echo Dashboard ja esta rodando!
) else (
    echo Iniciando Dashboard...
    start /min python main.py
)
```

---

## 📊 **CRONOGRAMA DE DESENVOLVIMENTO**

### **Semana 1: Fundação**
- **Dias 1-2**: Tarefas 1.1, 1.2 (Estrutura e Interface Principal)
- **Dias 3-4**: Tarefas 1.3, 1.4 (Componentes e Logs Básicos)
- **Dia 5**: Testes Fase 1

### **Semana 2: Planka**
- **Dias 1-2**: Tarefas 2.1, 2.2 (Módulo e Controle)
- **Dias 3-4**: Tarefas 2.3, 2.4 (Desenvolvimento e Interface)
- **Dia 5**: Testes Fase 2

### **Semana 2.5: Base de Dados do Planka**
- **Dias 1-2**: Tarefas 2.5.1, 2.5.2, 2.5.3 (Gestão, Criação e Editor)
- **Dias 3-4**: Tarefas 2.5.4, 2.5.5, 2.5.6 (Backup, Restauração e Upload)
- **Dia 5**: Tarefas 2.5.7, 2.5.8 + Testes Fase 2.5

### **Semana 3: Servidores**
- **Dias 1-2**: Tarefas 4.1, 4.2 (Módulo e Credenciais)
- **Dias 3-4**: Tarefas 4.3, 4.4 (Banco e Interface)
- **Dia 5**: Testes Fase 4

### **Semana 4: Logs e Integração**
- **Dias 1-2**: Tarefas 5.1, 5.2, 5.3 (Logs Avançados)
- **Dias 3-4**: Tarefas 6.1, 6.2 (Integração e Scripts)
- **Dia 5**: Tarefas 6.3, 6.4 + Testes Finais

---

## 🎯 **CRITÉRIOS DE ACEITAÇÃO**

### **Funcionalidades Core**
- [ ] Dashboard inicia com `python main.py`
- [ ] Interface Tkinter funciona corretamente
- [ ] Todas as abas abrem e funcionam
- [ ] Console mostra logs em tempo real
- [ ] Controle do Planka funciona (iniciar/parar/desenvolvimento)
- [ ] Gestão da base de dados funciona (criar/backup/restaurar/upload)
- [ ] Conexões SSH funcionam (conectar/testar/executar comandos)
- [ ] Sistema de logs funciona (registrar/filtrar/exportar)

### **Qualidade**
- [ ] Código documentado com docstrings
- [ ] Testes automatizados passam (cobertura > 80%)
- [ ] Interface responsiva e intuitiva
- [ ] Tratamento de erros robusto
- [ ] Logs detalhados para debug

### **Usabilidade**
- [ ] Instalação simples (pip install -r requirements.txt)
- [ ] Execução direta (python main.py)
- [ ] Scripts .bat funcionam
- [ ] Documentação clara e completa
- [ ] Interface intuitiva para usuários finais

---

## 📝 **NOTAS IMPORTANTES**

### **Vantagens da Abordagem Python**
- ✅ **Mais simples**: Uma linguagem só
- ✅ **Mais rápido**: Desenvolvimento mais direto
- ✅ **Mais estável**: Menos dependências
- ✅ **Interface nativa**: Não precisa de navegador
- ✅ **Execução direta**: Sem servidores web

### **Considerações Técnicas**
- **Python 3.8+**: Versão mínima necessária
- **Tkinter**: Interface nativa, já vem com Python
- **SQLite**: Banco local, não precisa instalação
- **PostgreSQL**: Para gestão da base do Planka
- **paramiko**: Biblioteca SSH robusta e testada
- **schedule**: Agendamento simples e eficiente

### **Limitações Conhecidas**
- Interface desktop apenas (não web)
- Execução sequencial de tarefas (não paralela)
- Dependência de conectividade SSH para servidores remotos
- Logs limitados por espaço em disco

---

**Status do Plano**: ✅ Completo e Organizado
**Próximo Passo**: Iniciar Fase 2.5 - Gestão da Base de Dados do Planka
**Tecnologia**: Python + Tkinter
**Duração Total**: 4 semanas
**Responsável**: Equipe de Desenvolvimento
**Data de Criação**: 02/08/2025 