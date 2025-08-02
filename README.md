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

### **Fase 2: Controle do Planka** ✅ **CONCLUÍDA**
- 🐳 **Controle do Planka** - Inicialização e gerenciamento
- 🔄 **Modo Desenvolvimento** - Ambiente de desenvolvimento
- 📊 **Status em Tempo Real** - Monitoramento do Planka

### **Fase 2.5: Gestão da Base de Dados do Planka** ✅ **CONCLUÍDA**
- 🗄️ **Gestão da Base de Dados** - Criação, backup e restauração
- 📤 **Upload de Base de Dados** - Substituição de dados
- 🔍 **Editor de Base de Dados** - Visualização e edição
- 📊 **Progresso Visual** - Barras de progresso e tooltips

### **Fase 4: Conexões SSH** ✅ **CONCLUÍDA**
- 🖥️ **Gerenciamento de Servidores** - Adicionar, editar e remover servidores
- 🔐 **Credenciais Criptografadas** - Armazenamento seguro com AES-256
- 🔗 **Pool de Conexões** - Conexões SSH reutilizáveis
- ⚡ **Teste de Conexão** - Verificação rápida de conectividade
- 📝 **Execução de Comandos** - Comandos remotos via SSH

### **Fase 5: Sistema de Logs Avançado** ✅ **CONCLUÍDA**
- 📋 **Logs Estruturados** - Metadados completos (usuário, sessão, IP)
- 🔍 **Filtros Avançados** - Por nível, origem, usuário, data
- 📊 **Estatísticas Detalhadas** - Análise de logs em tempo real
- 📤 **Exportação Múltipla** - CSV, JSON, TXT, ZIP
- ⚡ **Cache em Memória** - Performance otimizada
- 🧹 **Limpeza Automática** - Logs antigos removidos automaticamente

### **Fase 6: Integração e Polimento** ✅ **CONCLUÍDA**
- 🔗 **Comunicação entre Módulos** - Eventos e callbacks
- 🔔 **Sistema de Notificações** - Alertas visuais
- 🎨 **Interface Polida** - Tooltips e design melhorado
- 📜 **Scripts de Inicialização** - iniciar.bat, parar.bat, atalho.bat
- 📚 **Documentação Completa** - Manual do usuário e guias

---

## 🛠️ **INSTALAÇÃO E USO**

### **Requisitos**
- ✅ **Python 3.8+** - [Baixar Python](https://python.org)
- ✅ **Windows 10/11** - Sistema operacional
- ✅ **4GB RAM** - Mínimo recomendado
- ✅ **2GB espaço livre** - Para instalação

### **Método 1: Scripts Automáticos (Recomendado)**

#### **Iniciar Dashboard:**
```bash
# Duplo clique no arquivo:
iniciar.bat
```

#### **Parar Dashboard:**
```bash
# Duplo clique no arquivo:
parar.bat
```

#### **Atalho Inteligente:**
```bash
# Duplo clique no arquivo:
atalho.bat
# Detecta automaticamente se está rodando e oferece opções
```

### **Método 2: Instalação Manual**

1. **Instalar Python 3.8+:**
   ```bash
   # Baixar de: https://python.org
   ```

2. **Clonar o projeto:**
   ```bash
   git clone https://github.com/andrebids/dashboard-tarefas.git
   cd dashboard-tarefas
   ```

3. **Instalar dependências:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Executar:**
   ```bash
   python main.py
   ```

---

## 🎨 **INTERFACE**

### **Janela Principal**
- **Título**: "Dashboard de Tarefas - Python"
- **Tamanho**: 1200x800 pixels (redimensionável)
- **Interface**: Tkinter nativa (não web)

### **Sistema de Abas**
1. **🏠 Principal** - Controle do Planka e status geral
2. **🗄️ Base de Dados** - Gestão da base de dados do Planka
3. **🖥️ Servidores** - Conexões SSH e servidores remotos
4. **📋 Logs** - Sistema de logs avançado

### **Barra de Status**
- **Sistema**: Status geral da aplicação
- **Planka**: Status atual do Planka
- **Conexões**: Número de conexões SSH ativas
- **Base de Dados**: Status da base de dados
- **Logs**: Número total de logs registrados

### **Sistema de Notificações**
- **Alertas Visuais**: Notificações temporárias na interface
- **Cores**: Verde (sucesso), Azul (info), Laranja (aviso), Vermelho (erro)
- **Duração**: Configurável (padrão: 5 segundos)

### **Console Global**
- **Posição**: Fixa na parte inferior
- **Funcionalidades**: 
  - Logs em tempo real com cores
  - Botão para limpar console
  - Botão para exportar logs
  - Filtros por nível e origem

---

## 🔧 **CONFIGURAÇÃO**

### **Arquivo de Configuração**
```json
{
  "planka": {
    "docker_compose_path": "C:/planka-personalizado",
    "port": 3000
  },
  "database": {
    "host": "localhost",
    "port": 5432,
    "name": "planka",
    "user": "postgres",
    "password": "password"
  },
  "logs": {
    "max_files": 30,
    "max_size_mb": 10
  }
}
```

### **Diretórios Criados Automaticamente**
```
dashboard-tarefas/
├── logs/           # Arquivos de log
├── config/         # Configurações
├── database/       # Bases de dados locais
└── executaveis/    # Scripts e executáveis
```

---

## 📚 **MANUAL DO USUÁRIO**

### **Aba Principal (Planka)**
1. **Iniciar Planka**: Clique em "▶️ Iniciar" para iniciar o Planka
2. **Parar Planka**: Clique em "⏹️ Parar" para parar o Planka
3. **Modo Desenvolvimento**: Ative para desenvolvimento local
4. **Status**: Visualize o status atual do Planka

### **Aba Base de Dados**
1. **Criar Base**: Crie uma nova base de dados do Planka
2. **Backup**: Faça backup da base de dados atual
3. **Restaurar**: Restaure um backup existente
4. **Upload**: Faça upload de um arquivo SQL
5. **Editor**: Visualize e edite dados diretamente

### **Aba Servidores**
1. **Adicionar Servidor**: Configure um novo servidor SSH
2. **Testar Conexão**: Verifique se a conexão SSH funciona
3. **Executar Comando**: Execute comandos no servidor remoto
4. **Gerenciar Credenciais**: Visualize e edite credenciais salvas

### **Aba Logs**
1. **Visualizar Logs**: Veja todos os logs registrados
2. **Filtros**: Use filtros avançados para encontrar logs específicos
3. **Estatísticas**: Visualize estatísticas de logs
4. **Exportar**: Exporte logs em diferentes formatos

### **Atalhos de Teclado**
- **Ctrl+Q**: Sair da aplicação
- **Ctrl+L**: Limpar console
- **Ctrl+E**: Exportar logs
- **F1**: Abrir documentação
- **F5**: Atualizar aba atual

---

## 🐛 **RESOLUÇÃO DE PROBLEMAS**

### **Problema: Python não encontrado**
**Solução**: Instale o Python 3.8+ de https://python.org

### **Problema: Dependências não instaladas**
**Solução**: Execute `pip install -r requirements.txt`

### **Problema: Dashboard não inicia**
**Solução**: 
1. Verifique se está no diretório correto
2. Execute `python main.py` para ver erros detalhados
3. Verifique se todas as dependências estão instaladas

### **Problema: Conexão SSH falha**
**Solução**:
1. Verifique se o servidor está acessível
2. Confirme usuário e senha
3. Verifique se a porta SSH está correta (padrão: 22)

### **Problema: Base de dados não conecta**
**Solução**:
1. Verifique se o PostgreSQL está rodando
2. Confirme credenciais no arquivo de configuração
3. Verifique se a base de dados existe

---

## 📊 **ESTATÍSTICAS DO PROJETO**

### **Código**
- **Linhas de Código**: ~5,000+
- **Arquivos Python**: 25+
- **Módulos**: 8 principais
- **Testes**: 10+ scripts de teste

### **Funcionalidades**
- **Abas**: 4 abas principais
- **Scripts**: 3 scripts .bat
- **Formatos de Exportação**: 4 formatos
- **Tipos de Log**: 5 níveis
- **Criptografia**: AES-256

### **Compatibilidade**
- **Sistemas**: Windows 10/11
- **Python**: 3.8+
- **Bancos**: PostgreSQL, SQLite
- **Protocolos**: SSH, HTTP

---

## 🤝 **CONTRIBUIÇÃO**

### **Como Contribuir**
1. Faça um fork do projeto
2. Crie uma branch para sua feature
3. Implemente suas mudanças
4. Teste suas mudanças
5. Envie um pull request

### **Padrões de Código**
- **Linguagem**: Python 3.8+
- **Interface**: Tkinter
- **Documentação**: Docstrings em português
- **Logs**: Sistema de logs estruturado
- **Tratamento de Erros**: Try/catch em todas as operações

---

## 📄 **LICENÇA**

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

---

## 📞 **SUPORTE**

### **Canais de Suporte**
- **Issues**: [GitHub Issues](https://github.com/andrebids/dashboard-tarefas/issues)
- **Documentação**: [Wiki do Projeto](https://github.com/andrebids/dashboard-tarefas/wiki)
- **Email**: [contato@exemplo.com]

### **Informações do Projeto**
- **Versão**: 2.0.0
- **Última Atualização**: Janeiro 2025
- **Status**: ✅ Completo e Funcional
- **Próxima Versão**: 2.1.0 (Melhorias e correções)

---

**🎉 Projeto Completo e Funcional!** 