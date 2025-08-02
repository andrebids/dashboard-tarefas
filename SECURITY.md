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

## 🛡️ Boas Práticas

### 1. Configuração da Base de Dados

```bash
# Copiar o arquivo de exemplo
cp config/database_config.example.json config/database_config.json

# Editar com suas credenciais reais
# NUNCA commitar este arquivo
```

### 2. Variáveis de Ambiente

Use variáveis de ambiente para credenciais:

```bash
export PLANKA_DB_PASSWORD="sua_senha_aqui"
export PLANKA_SECRET_KEY="sua_chave_secreta"
```

### 3. Arquivos de Teste

Nunca inclua credenciais reais em arquivos de teste:

```python
# ❌ ERRADO
password = "admin123"

# ✅ CORRETO
password = os.getenv("TEST_PASSWORD", "test_password")
```

## 🔍 Verificação de Segurança

Antes de fazer commit, verifique:

1. **Arquivos sensíveis não estão no staging:**
   ```bash
   git status
   ```

2. **Nenhuma senha hardcoded:**
   ```bash
   grep -r "password\|senha\|admin123" . --exclude-dir=.git
   ```

3. **Arquivos de configuração estão no .gitignore:**
   ```bash
   git check-ignore config/database_config.json
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
   'git rm --cached --ignore-unmatch config/database_config.json' \
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

## 🔐 Configuração Segura

### Para Desenvolvedores

1. Clone o repositório
2. Copie `config/database_config.example.json` para `config/database_config.json`
3. Configure suas credenciais locais
4. NUNCA commite o arquivo com credenciais reais

### Para Produção

1. Use variáveis de ambiente
2. Configure chaves de encriptação
3. Use secrets management
4. Implemente rotação de credenciais

---

**Lembre-se: Segurança é responsabilidade de todos!** 🔒 