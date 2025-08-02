# 🐍 Dashboard de Tarefas - Python
## Sistema de Automação Windows + Linux Remoto

---

## 📋 **VISÃO GERAL**

Dashboard desktop Python simples para Windows que permite executar comandos automatizados tanto localmente (Windows) quanto em servidores Linux remotos, com **interface Tkinter nativa** e **arquitetura simplificada**.

### **Por que Python + Tkinter?**
- ✅ **Simplicidade**: Uma linguagem só, sem dependências complexas
- ✅ **Interface Nativa**: Tkinter já vem com Python, sem necessidade de navegador
- ✅ **Execução Direta**: `python main.py` - sem servidores web
- ✅ **Menos Dependências**: Não precisa Node.js, npm, Docker para o dashboard
- ✅ **Mais Estável**: Menos camadas de abstração = menos problemas

---

## ✨ **FUNCIONALIDADES**

### **Fase 1: Fundação e Estrutura Básica** ✅ **CONCLUÍDA**
- 🏠 **Interface Principal** - Dashboard com sistema de abas
- 📊 **Console Global** - Logs em tempo real com cores
- 🔧 **Sistema de Configurações** - Configurações JSON
- 📝 **Sistema de Logs** - Logs organizados por tipo
- 🎨 **Interface Tkinter** - Interface desktop nativa

### **Próximas Fases (Em Desenvolvimento)**
- 🐳 **Controle do Planka** - Inicialização e gerenciamento (Fase 2)
- ⚙️ **Sistema de Tarefas** - Criação, agendamento e execução (Fase 3)
- 🖥️ **Conexões SSH** - Gerenciamento de servidores remotos (Fase 4)
- 📋 **Logs Avançados** - Sistema completo de logs (Fase 5)
- 🔧 **Integração Completa** - Polimento e finalização (Fase 6)

---

## 🛠️ **INSTALAÇÃO E USO**

### **Requisitos**
- ✅ **Python 3.8+** - [Baixar Python](https://python.org)
- ✅ **Windows 10/11** - Sistema operacional
- ✅ **4GB RAM** - Mínimo recomendado
- ✅ **2GB espaço livre** - Para instalação

### **Método 1: Instalação Automática (Recomendado)**

1. **Execute como Administrador:**
   ```bash
   # Duplo clique no arquivo:
   dashboard.bat
   ```

2. **O script irá automaticamente:**
   - ✅ Verificar se o dashboard já está rodando
   - ✅ Verificar se o Python está instalado
   - ✅ Instalar dependências (py -m pip install -r requirements.txt)
   - ✅ Iniciar o dashboard
   - ✅ Abrir a interface Tkinter

### **Método 2: Instalação Manual**

1. **Instalar Python 3.8+:**
   ```bash
   # Baixar de: https://python.org
   # Ou usar o script automático
   ```

2. **Clonar o projeto:**
   ```bash
   git clone [url-do-repositorio]
   cd dashboard-tarefas
   ```

3. **Instalar dependências:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Executar:**
   ```bash
   py main.py
   ```

---

## 🎨 **INTERFACE**

### **Janela Principal**
- **Título**: "Dashboard de Tarefas - Python"
- **Tamanho**: 1200x800 pixels
- **Interface**: Tkinter nativa (não web)

### **Sistema de Abas**
1. **🏠 Principal** - Controle do Planka
2. **⚙️ Tarefas** - Gerenciamento de tarefas
3. **🖥️ Servidores** - Conexões SSH
4. **📋 Logs** - Sistema de logs

### **Console Global**
- **Posição**: Fixa na parte inferior
- **Cores**: Verde (sucesso), Vermelho (erro), Amarelo (aviso), Azul (info)
- **Filtros**: Por tipo, origem e busca
- **Auto-scroll**: Sempre mostra mensagens recentes

---

## 📁 **ESTRUTURA DO PROJETO**

```
dashboard-tarefas/
├── main.py                    # Aplicação principal
├── interface/                 # Interface Tkinter
│   ├── dashboard.py          # Janela principal
│   ├── abas/                 # Abas do dashboard
│   │   ├── principal.py      # Aba principal (Planka)
│   │   ├── tarefas.py        # Aba de tarefas
│   │   ├── servidores.py     # Aba de servidores SSH
│   │   └── logs.py           # Aba de logs
│   └── componentes/          # Componentes reutilizáveis
│       └── console.py        # Console de logs
├── core/                     # Lógica de negócio
│   └── logs.py              # Sistema de logs
├── config/                   # Configurações
│   └── settings.py          # Configurações gerais
├── logs/                     # Logs do sistema
├── executaveis/              # Scripts .bat
│   ├── iniciar.bat          # Iniciar dashboard
│   └── atalho.bat           # Atalho inteligente
├── requirements.txt          # Dependências Python
└── README.md                # Documentação
```

---

## 🔧 **DEPENDÊNCIAS**

### **requirements.txt**
```txt
# SSH
paramiko==3.4.0

# Agendamento
schedule==1.2.0

# Criptografia
cryptography==41.0.0

# Testes
pytest==7.4.0
pytest-cov==4.1.0

# Desenvolvimento
black==23.7.0
flake8==6.0.0
```

---

## 🚀 **EXECUÇÃO**

### **Scripts Disponíveis**
- **`dashboard.bat`** - Inicializador unificado (recomendado)
- **`py main.py`** - Execução direta

### **Primeira Execução**
1. Duplo clique em `executaveis/atalho.bat`
2. Aguarde a instalação das dependências
3. Interface Tkinter abrirá automaticamente

---

## 📊 **STATUS DO DESENVOLVIMENTO**

### **Fase 1: Fundação e Estrutura Básica** ✅ **CONCLUÍDA**
- ✅ Estrutura de pastas organizada
- ✅ Interface Tkinter básica funcionando
- ✅ Sistema de abas implementado
- ✅ Console global em tempo real
- ✅ Sistema de configurações
- ✅ Sistema de logs básico
- ✅ Scripts .bat para inicialização

### **Próximas Fases**
- **Fase 2**: Controle do Planka (3-4 dias)
- **Fase 3**: Sistema de Tarefas (4-5 dias)
- **Fase 4**: Conexões SSH (3-4 dias)
- **Fase 5**: Logs Avançados (2-3 dias)
- **Fase 6**: Integração e Polimento (2-3 dias)

---

## 🚨 **SOLUÇÃO DE PROBLEMAS**

### **Python não encontrado:**
```bash
# Execute como administrador:
executaveis/atalho.bat
```

### **Erro de dependências:**
```bash
# Limpar cache e reinstalar:
pip cache purge
pip install -r requirements.txt
```

### **Erro de permissões:**
```bash
# Clique direito no atalho.bat
# "Executar como administrador"
```

### **Interface não abre:**
```bash
# Verificar se Tkinter está disponível:
py -c "import tkinter; print('Tkinter OK')"
```

---

## 📈 **ROADMAP**

### **Versão 1.0 (Atual)**
- Interface Tkinter básica
- Sistema de abas
- Console de logs
- Configurações básicas

### **Versão 2.0 (Próxima)**
- Controle completo do Planka
- Verificação de dependências
- Modo desenvolvimento

### **Versão 3.0 (Futura)**
- Sistema de tarefas completo
- Agendamento automático
- Execução de comandos

---

## 📝 **NOTAS IMPORTANTES**

### **Vantagens da Abordagem Python**
- ✅ **Mais simples**: Uma linguagem só
- ✅ **Mais rápido**: Desenvolvimento mais direto
- ✅ **Mais estável**: Menos dependências
- ✅ **Interface nativa**: Não precisa de navegador
- ✅ **Execução direta**: Sem servidores web

### **Limitações Conhecidas**
- Interface desktop apenas (não web)
- Execução sequencial de tarefas (não paralela)
- Dependência de conectividade SSH para servidores remotos

---

## 🤝 **CONTRIBUIÇÃO**

1. Fork o projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

---

## 📄 **LICENÇA**

Este projeto está sob a licença MIT. Veja o arquivo LICENSE para mais detalhes.

---

**Status do Projeto**: ✅ Fase 1 Concluída
**Próximo Passo**: Iniciar Fase 2 - Controle do Planka
**Tecnologia**: Python + Tkinter
**Versão**: 1.0.0
**Data**: 02/08/2025 