# 🔒 Segurança - Dashboard de Tarefas

## ⚠️ Informações Sensíveis

Este projeto contém informações sensíveis que **NUNCA** devem ser enviadas em commits.

### Arquivos Sensíveis (NÃO COMMITAR)

- `config/database_config.json` - Configuração da base de dados com senhas
- `config/database_key.key` - Chave de encriptação
- `config/credentials.json` - Credenciais gerais
- `config/passwords.json` - Senhas
- `config/secrets.json` - Segredos
- `*.key`, `*.pem`, `*.ppk` - Chaves SSH/SSL
- `test_*.py` - Arquivos de teste com credenciais hardcoded

### Arquivos Seguros (PODE COMMITAR)

- `config/database_config.example.json` - Exemplo de configuração
- `config/settings.json` - Configurações gerais (sem senhas)
- `config/settings.py` - Código de configuração

## 🛡️ Configuração Segura com Variáveis de Ambiente

### 1. Variáveis de Ambiente Obrigatórias

```bash
# Base de Dados
export PLANKA_DB_PASSWORD="sua_senha_segura_aqui"
export PLANKA_DB_USER="postgres"
export PLANKA_DB_HOST="localhost"
export PLANKA_DB_PORT="5432"

# Administrador
export PLANKA_ADMIN_EMAIL="admin@seudominio.com"
export PLANKA_ADMIN_PASSWORD="senha_admin_segura"
export PLANKA_ADMIN_USERNAME="admin"

# SSH
export PLANKA_SSH_USERNAME="seu_usuario_ssh"
export PLANKA_SSH_KEY_PATH="/caminho/para/sua/chave.pem"
export PLANKA_SSH_HOST="seu_host_ssh"
export PLANKA_SSH_PORT="22"

# GitHub
export GITHUB_TOKEN="seu_token_github"
export GITHUB_USERNAME="seu_usuario_github"

# Docker
export PLANKA_SECRET_KEY="chave_secreta_aleatoria_32_chars"
export POSTGRES_PASSWORD="senha_postgres_segura"
export POSTGRES_USER="postgres"
```

### 2. Arquivo .env (Recomendado)

Crie um ficheiro `.env` na raiz do projeto:

```bash
# Copiar template
cp .env.example .env

# Editar com suas credenciais
nano .env
```

**NUNCA commitar o ficheiro .env!**

### 3. Configuração da Base de Dados

```bash
# Copiar o arquivo de exemplo
cp config/database_config.example.json config/database_config.json

# O sistema usará automaticamente as variáveis de ambiente
# NUNCA commitar este arquivo com credenciais reais
```

## 🔍 Verificação de Segurança

### Antes de fazer commit, verifique:

1. **Arquivos sensíveis não estão no staging:**
   ```bash
   git status
   ```

2. **Nenhuma senha hardcoded:**
   ```bash
   grep -r "password\|senha\|admin123\|postgres" . --exclude-dir=.git
   ```

3. **Variáveis de ambiente configuradas:**
   ```bash
   python -c "from config.settings import Settings; s = Settings(); print(s.validar_configuracoes_seguranca())"
   ```

4. **Arquivos de configuração estão no .gitignore:**
   ```bash
   git check-ignore config/database_config.json
   git check-ignore .env
   ```

## 🚨 Validação Automática

O sistema agora inclui validação automática de segurança:

```python
from config.settings import Settings

settings = Settings()
resultado = settings.validar_configuracoes_seguranca()

if not resultado["valido"]:
    print("❌ Problemas de segurança encontrados:")
    for problema in resultado["problemas"]:
        print(f"   - {problema}")
    
if resultado["avisos"]:
    print("⚠️ Avisos de segurança:")
    for aviso in resultado["avisos"]:
        print(f"   - {aviso}")
```

## 🚨 Em Caso de Exposição

Se credenciais foram expostas:

1. **Imediatamente:**
   - Alterar todas as senhas expostas
   - Revogar tokens/chaves
   - Notificar administradores

2. **Limpar histórico:**
   ```bash
   git filter-branch --force --index-filter \
   'git rm --cached --ignore-unmatch config/database_config.json .env' \
   --prune-empty --tag-name-filter cat -- --all
   ```

3. **Forçar push:**
   ```bash
   git push origin --force --all
   ```

## 📋 Checklist de Segurança

- [ ] Nenhum arquivo com credenciais no staging
- [ ] Variáveis de ambiente configuradas
- [ ] Arquivos de exemplo criados
- [ ] .gitignore atualizado
- [ ] Testes não contêm credenciais reais
- [ ] Documentação de segurança atualizada
- [ ] Validação de segurança passa sem erros
- [ ] Ficheiro .env não está no repositório

## 🔐 Configuração Segura

### Para Desenvolvedores

1. Clone o repositório
2. Configure as variáveis de ambiente
3. Copie `config/database_config.example.json` para `config/database_config.json`
4. Execute validação de segurança
5. NUNCA commite credenciais reais

### Para Produção

1. Use variáveis de ambiente do sistema
2. Configure chaves de encriptação
3. Use secrets management
4. Implemente rotação de credenciais
5. Monitore logs de segurança

## 🛠️ Scripts de Segurança

### Validar Configurações
```bash
python -c "from config.settings import Settings; s = Settings(); print('✅ Configurações válidas' if s.validar_configuracoes_seguranca()['valido'] else '❌ Problemas encontrados')"
```

### Limpar Credenciais Hardcoded
```bash
# Procurar por passwords hardcoded
grep -r "admin123\|postgres\|password" . --exclude-dir=.git --exclude=*.md
```

---

**Lembre-se: Segurança é responsabilidade de todos!** 🔒 