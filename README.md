# 🔒 Dashboard de Tarefas - Sistema Seguro

Sistema de automação e gestão de tarefas com foco em segurança e boas práticas.

## 🚀 Instalação Rápida

### 1. Pré-requisitos

- Python 3.8+
- Git
- Acesso ao repositório

### 2. Configuração Inicial

```bash
# Clone o repositório
git clone <url-do-repositorio>
cd dashboard-tarefas

# Instalar dependências
pip install -r requirements.txt

# Configurar variáveis de ambiente
cp env.example .env
# Editar .env com suas credenciais
nano .env

# Validar configurações de segurança
python scripts/validar_seguranca.py
```

### 3. Configuração de Segurança

**IMPORTANTE:** Configure as variáveis de ambiente obrigatórias:

```bash
# Base de Dados
export PLANKA_DB_PASSWORD="sua_senha_segura_aqui"
export PLANKA_ADMIN_PASSWORD="senha_admin_segura"

# SSH (se necessário)
export PLANKA_SSH_USERNAME="seu_usuario_ssh"
export PLANKA_SSH_KEY_PATH="/caminho/para/sua/chave.pem"

# GitHub (se necessário)
export GITHUB_TOKEN="seu_token_github"
export GITHUB_USERNAME="seu_usuario_github"
```

### 4. Executar

```bash
# Iniciar dashboard
python main.py

# Ou usar o script de inicialização
./dashboard.bat  # Windows
./dashboard.sh   # Linux/Mac
```

## 🔒 Segurança

### Validação Automática

O sistema inclui validação automática de segurança:

```bash
# Validar configurações
python scripts/validar_seguranca.py

# Verificar variáveis de ambiente
python -c "from config.settings import Settings; s = Settings(); print(s.validar_configuracoes_seguranca())"
```

### Boas Práticas Implementadas

- ✅ Uso de variáveis de ambiente para credenciais
- ✅ Validação automática de segurança
- ✅ Documentação de segurança completa
- ✅ Scripts de validação
- ✅ Configurações separadas (exemplo vs. real)
- ✅ .gitignore configurado para ficheiros sensíveis

### Checklist de Segurança

- [ ] Variáveis de ambiente configuradas
- [ ] Ficheiro .env criado e configurado
- [ ] Validação de segurança passa sem erros
- [ ] Nenhuma credencial hardcoded no código
- [ ] Ficheiros sensíveis no .gitignore

## 📁 Estrutura do Projeto

```
dashboard-tarefas/
├── config/                 # Configurações
│   ├── database_config.example.json
│   ├── settings.py
│   └── settings.json
├── core/                   # Módulos principais
│   ├── seguranca.py       # Gestão de segurança
│   ├── logs.py
│   └── database.py
├── scripts/               # Scripts utilitários
│   └── validar_seguranca.py
├── interface/             # Interface gráfica
├── logs/                  # Logs do sistema
├── database/              # Base de dados
├── .env.example          # Template de variáveis
├── SECURITY.md           # Documentação de segurança
└── README.md
```

## 🛠️ Desenvolvimento

### Adicionar Novas Funcionalidades

1. **Seguir padrões de segurança:**
   ```python
   # ✅ CORRETO - Usar variáveis de ambiente
   password = os.getenv("PLANKA_DB_PASSWORD")
   
   # ❌ ERRADO - Hardcoded
   password = "minha_senha"
   ```

2. **Validar antes de commitar:**
   ```bash
   python scripts/validar_seguranca.py
   ```

3. **Documentar mudanças de segurança**

### Testes

```bash
# Executar validação de segurança
python scripts/validar_seguranca.py

# Verificar configurações
python -c "from config.settings import Settings; print(Settings().config)"
```

## 🔧 Configuração Avançada

### Variáveis de Ambiente Completas

Veja `env.example` para todas as variáveis disponíveis:

- **Base de Dados:** Configurações PostgreSQL
- **Administrador:** Credenciais de admin
- **SSH:** Configurações de acesso remoto
- **GitHub:** Tokens e usernames
- **Docker:** Configurações de containers

### Personalização

1. **Configurações de Interface:** `config/settings.json`
2. **Base de Dados:** `config/database_config.json`
3. **Logs:** Configuráveis via interface

## 🚨 Troubleshooting

### Problemas Comuns

1. **"Variáveis de ambiente não configuradas"**
   ```bash
   # Configurar variáveis obrigatórias
   export PLANKA_DB_PASSWORD="sua_senha"
   export PLANKA_ADMIN_PASSWORD="senha_admin"
   ```

2. **"Erro de conexão com base de dados"**
   ```bash
   # Verificar configurações
   python -c "from config.settings import Settings; s = Settings(); print(s.obter_seguranca('database'))"
   ```

3. **"Problemas de segurança encontrados"**
   ```bash
   # Executar validação completa
   python scripts/validar_seguranca.py
   ```

### Logs

- **Sistema:** `logs/sistema/`
- **Tarefas:** `logs/tarefas/`
- **Servidores:** `logs/servidores/`

## 📚 Documentação

- [SECURITY.md](SECURITY.md) - Guia completo de segurança
- [PLANO-DASHBOARD.md](PLANO-DASHBOARD.md) - Plano de desenvolvimento
- [env.example](env.example) - Template de variáveis de ambiente

## 🤝 Contribuição

1. Fork o projeto
2. Configure ambiente de desenvolvimento
3. Execute validação de segurança
4. Faça suas alterações
5. Teste com `python scripts/validar_seguranca.py`
6. Submit pull request

## 📄 Licença

Este projeto segue as melhores práticas de segurança e é destinado para uso interno.

---

**🔒 Segurança é prioridade!** Execute sempre a validação antes de commitar. 