# 🔧 Correções Aplicadas - Build do Planka

## 📋 Resumo do Problema

O build do Planka estava falhando com o erro:
```
failed to solve: invalid file request server/.venv/bin/python
```

## 🔍 Análise do Problema

### Causa Raiz
O problema estava relacionado ao arquivo `.dockerignore` que estava excluindo o diretório `.venv/`, mas o Docker estava tentando acessar arquivos dentro desse diretório durante o build.

### Problemas Identificados
1. **Exclusão do `.venv/`**: O `.dockerignore` estava excluindo o ambiente virtual
2. **Arquivo `.env.sample` ausente**: O Dockerfile tentava copiar um arquivo que não existia
3. **Permissões do `start.sh`**: O arquivo não tinha permissões de execução
4. **Diretórios `node_modules`**: Existiam localmente e causavam conflitos

## 🛠️ Correções Aplicadas

### 1. Correção do `.dockerignore`

**Problema**: O arquivo estava excluindo `.venv/` que é necessário para o build.

**Solução**: Remover a exclusão do `.venv/` do `.dockerignore`.

```diff
# .dockerignore
env/
venv/
- .venv/
pip-log.txt
```

### 2. Criação do Arquivo `env.sample`

**Problema**: O Dockerfile tentava copiar `.env.sample` que não existia.

**Solução**: Criar o arquivo `server/env.sample` com as configurações padrão.

```bash
# Configurações do Planka
BASE_URL=http://localhost:3000
DATABASE_URL=postgresql://postgres@postgres/planka
SECRET_KEY=your-secret-key-change-this

# Configurações do Admin (opcional)
# DEFAULT_ADMIN_EMAIL=admin@example.com
# DEFAULT_ADMIN_PASSWORD=admin123
# DEFAULT_ADMIN_NAME=Admin User
# DEFAULT_ADMIN_USERNAME=admin

# Configurações de Log
LOG_LEVEL=info

# ... outras configurações ...
```

### 3. Atualização do Dockerfile

**Problema**: O Dockerfile tentava copiar `.env.sample` mas o arquivo se chamava `env.sample`.

**Solução**: Atualizar o comando para usar o nome correto do arquivo.

```diff
RUN python3 -m venv .venv \
  && .venv/bin/pip install -r requirements.txt --no-cache-dir \
- && mv .env.sample .env \
+ && mv env.sample .env \
  && npm config set update-notifier false
```

### 4. Adição de Permissões de Execução

**Problema**: O arquivo `start.sh` não tinha permissões de execução.

**Solução**: Adicionar comando `chmod` no Dockerfile.

```diff
RUN python3 -m venv .venv \
  && .venv/bin/pip install -r requirements.txt --no-cache-dir \
  && mv env.sample .env \
+ && chmod +x start.sh \
  && npm config set update-notifier false
```

### 5. Remoção de Diretórios Locais

**Problema**: Diretórios `node_modules` e `.venv` existiam localmente e causavam conflitos.

**Solução**: Remover esses diretórios antes do build.

```powershell
# Remover diretórios que causam conflito
Remove-Item -Recurse -Force server\.venv
Remove-Item -Recurse -Force server\node_modules
Remove-Item -Recurse -Force node_modules -ErrorAction SilentlyContinue
```

## 📁 Arquivos Modificados

### 1. `planka-personalizado/.dockerignore`
```diff
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*
.git/
.gitignore
README.md
.env
.nyc_output
coverage/
.nyc_output
.coverage
.pytest_cache/
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
env/
venv/
- .venv/
pip-log.txt
pip-delete-this-directory.txt
.tox/
.cache
nosetests.xml
coverage.xml
*.cover
.hypothesis/
.mypy_cache/
.dmypy.json
dmypy.json
```

### 2. `planka-personalizado/server/env.sample` (Novo arquivo)
```bash
# Configurações do Planka
BASE_URL=http://localhost:3000
DATABASE_URL=postgresql://postgres@postgres/planka
SECRET_KEY=your-secret-key-change-this

# Configurações do Admin (opcional)
# DEFAULT_ADMIN_EMAIL=admin@example.com
# DEFAULT_ADMIN_PASSWORD=admin123
# DEFAULT_ADMIN_NAME=Admin User
# DEFAULT_ADMIN_USERNAME=admin

# Configurações de Log
LOG_LEVEL=info

# Configurações de Proxy (se necessário)
# TRUST_PROXY=true

# Configurações de Token
# TOKEN_EXPIRES_IN=365

# Configurações de Idioma
# DEFAULT_LANGUAGE=pt-BR

# Configurações de Limite de Usuários
# ACTIVE_USERS_LIMIT=

# Configurações de Segurança
# SHOW_DETAILED_AUTH_ERRORS=false

# Configurações do S3 (opcional)
# S3_ENDPOINT=
# S3_REGION=
# S3_ACCESS_KEY_ID=
# S3_SECRET_ACCESS_KEY=
# S3_BUCKET=
# S3_FORCE_PATH_STYLE=true

# Configurações OIDC (opcional)
# OIDC_ISSUER=
```

### 3. `planka-personalizado/Dockerfile`
```diff
RUN python3 -m venv .venv \
  && .venv/bin/pip install -r requirements.txt --no-cache-dir \
- && mv .env.sample .env \
+ && mv env.sample .env \
+ && chmod +x start.sh \
  && npm config set update-notifier false
```

## 🧪 Testes Realizados

### 1. Build Local
```bash
cd planka-personalizado
docker-compose -f docker-compose-local.yml build --no-cache
```

**Resultado**: ✅ Build concluído com sucesso

### 2. Execução dos Containers
```bash
docker-compose -f docker-compose-local.yml up -d
```

**Resultado**: ✅ Containers iniciados com sucesso

### 3. Verificação de Status
```bash
docker-compose -f docker-compose-local.yml ps
```

**Resultado**: ✅ Containers rodando corretamente

## 📊 Métricas de Melhoria

### Antes das Correções
- ❌ Build falhava com erro de arquivo não encontrado
- ❌ Container reiniciava constantemente
- ❌ Arquivo `start.sh` não executável

### Depois das Correções
- ✅ Build concluído com sucesso
- ✅ Containers rodando estáveis
- ✅ Arquivo `start.sh` executável
- ✅ Ambiente virtual criado corretamente
- ✅ Configurações de ambiente aplicadas

## 🔄 Comandos para Reproduzir

### Limpeza Prévia (se necessário)
```powershell
# Remover diretórios que podem causar conflito
Remove-Item -Recurse -Force server\.venv -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force server\node_modules -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force node_modules -ErrorAction SilentlyContinue
```

### Build e Execução
```bash
# Navegar para o diretório
cd planka-personalizado

# Fazer build
docker-compose -f docker-compose-local.yml build --no-cache

# Executar containers
docker-compose -f docker-compose-local.yml up -d

# Verificar status
docker-compose -f docker-compose-local.yml ps

# Ver logs (se necessário)
docker-compose -f docker-compose-local.yml logs planka
```

## 🚨 Problemas Conhecidos

### 1. Container Reiniciando
**Sintoma**: Container reinicia constantemente
**Causa**: Arquivo `start.sh` não encontrado ou não executável
**Solução**: Verificar permissões e existência do arquivo

### 2. Erro de Arquivo Não Encontrado
**Sintoma**: `invalid file request server/.venv/bin/python`
**Causa**: `.dockerignore` excluindo arquivos necessários
**Solução**: Remover exclusões desnecessárias do `.dockerignore`

### 3. Erro de Build Context
**Sintoma**: `invalid file request server/node_modules/.bin/_mocha`
**Causa**: Diretórios `node_modules` existem localmente
**Solução**: Remover diretórios `node_modules` antes do build

## 📋 Checklist de Verificação

### Antes do Build
- [ ] Verificar se `.dockerignore` não exclui arquivos necessários
- [ ] Confirmar existência do arquivo `env.sample`
- [ ] Remover diretórios `node_modules` e `.venv` locais
- [ ] Verificar permissões do arquivo `start.sh`

### Durante o Build
- [ ] Monitorar logs de build
- [ ] Verificar se todas as etapas são executadas
- [ ] Confirmar criação do ambiente virtual
- [ ] Validar cópia de arquivos

### Após o Build
- [ ] Verificar status dos containers
- [ ] Testar conectividade da aplicação
- [ ] Validar logs de execução
- [ ] Confirmar funcionamento do Planka

## 🔮 Melhorias Futuras

### 1. Otimização do Build
- Implementar multi-stage builds mais eficientes
- Reduzir tamanho da imagem final
- Otimizar camadas do Docker

### 2. Scripts de Automação
- Criar script de limpeza automática
- Implementar build com validações
- Adicionar testes automatizados

### 3. Documentação
- Criar guia de troubleshooting
- Documentar configurações avançadas
- Adicionar exemplos de uso

---

**Versão**: 1.0  
**Data**: Agosto 2025  
**Autor**: Equipe de Desenvolvimento  
**Status**: Concluído 