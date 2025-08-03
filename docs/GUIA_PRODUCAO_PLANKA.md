# 🚀 Guia Completo - Planka em Produção com Modificações Locais

## 📋 Visão Geral

Este guia explica como executar o Planka em modo produção mantendo as modificações locais, seguindo as melhores práticas da [documentação oficial do Planka](https://docs.planka.cloud/docs/installation/docker/production-version).

## 🎯 Objetivo

Executar o Planka em produção com:
- ✅ Modificações locais aplicadas
- ✅ Configurações de segurança adequadas
- ✅ Usuário administrador criado
- ✅ Build otimizado para produção
- ✅ Diagnóstico automático de problemas

## 🛠️ Funcionalidades Implementadas

### 1. **Execução Automática de Produção**
```python
# Executa produção com modificações locais
sucesso, mensagem = planka_manager.executar_producao_com_modificacoes_locais()
```

**O que faz:**
- 🔑 Gera secret key adequado com `openssl rand -hex 64`
- 📝 Atualiza configurações do `docker-compose-local.yml`
- 🔨 Faz build da imagem com `--no-cache`
- 🚀 Inicia containers de produção
- 👤 Cria usuário administrador
- ✅ Verifica se está funcionando

### 2. **Diagnóstico Automático**
```python
# Diagnostica problemas específicos
diagnostico = planka_manager.diagnosticar_producao()
```

**Verifica:**
- 🐳 Status dos containers
- ⚙️ Configurações do docker-compose
- 🔑 Secret key adequado
- 👤 Usuário administrador
- 🌐 Acessibilidade da porta 3000
- 📋 Logs de erro

### 3. **Logs Detalhados**
```python
# Obtém logs completos
logs = planka_manager.obter_logs_producao_detalhados(100)
```

## 🚀 Como Usar

### Método 1: Script de Teste Interativo

```bash
# Navegar para o diretório
cd dashboard-tarefas

# Executar script de teste
python teste_producao_planka.py
```

**Opções disponíveis:**
1. **Executar produção com modificações locais**
2. **Diagnosticar problemas de produção**
3. **Ver logs detalhados de produção**
4. **Verificar status atual**
5. **Parar produção**

### Método 2: Uso Direto no Código

```python
from core.planka import PlankaManager
from config.database_config import DatabaseConfig

# Configurar
config = DatabaseConfig()
planka_manager = PlankaManager(config)

# Executar produção
sucesso, mensagem = planka_manager.executar_producao_com_modificacoes_locais()

if sucesso:
    print("✅ Planka em produção iniciado!")
    print("🌐 Acesso: http://localhost:3000")
    print("👤 Admin: admin@planka.local / admin123")
else:
    print(f"❌ Erro: {mensagem}")
    
    # Diagnosticar problemas
    diagnostico = planka_manager.diagnosticar_producao()
    print("🔍 Problemas encontrados:", diagnostico['problemas'])
```

## 📋 Processo de Execução

### 1. **Preparação**
- ✅ Verifica dependências (Docker, Docker Compose)
- ✅ Verifica diretório do Planka
- ⏹️ Para containers existentes

### 2. **Configuração**
- 🔑 Gera secret key com `openssl rand -hex 64`
- 📝 Atualiza `docker-compose-local.yml`
- 👤 Adiciona configurações de admin

### 3. **Build**
- 🔨 Executa `docker-compose -f docker-compose-local.yml build --no-cache`
- ⏰ Timeout de 5 minutos
- 📋 Logs detalhados do processo

### 4. **Inicialização**
- 🚀 Executa `docker-compose -f docker-compose-local.yml up -d`
- ⏳ Aguarda 15 segundos para inicialização
- 👤 Cria admin user se necessário

### 5. **Verificação**
- ✅ Testa conectividade na porta 3000
- 📊 Verifica status dos containers
- 🔍 Executa diagnóstico completo

## 🔧 Configurações Aplicadas

### Secret Key
```yaml
# Gerado automaticamente com openssl
SECRET_KEY=abc123def456...  # 64 caracteres hex
```

### Admin User
```yaml
DEFAULT_ADMIN_EMAIL=admin@planka.local
DEFAULT_ADMIN_PASSWORD=admin123
DEFAULT_ADMIN_NAME=Admin User
DEFAULT_ADMIN_USERNAME=admin
```

### Docker Compose
```yaml
services:
  planka:
    build:
      context: .
      dockerfile: Dockerfile  # Usa build local
    image: planka-producao-local
    ports:
      - 3000:1337
    environment:
      - BASE_URL=http://localhost:3000
      - DATABASE_URL=postgresql://postgres@postgres/planka
      - SECRET_KEY=${SECRET_KEY_GERADO}
      - DEFAULT_ADMIN_EMAIL=admin@planka.local
      - DEFAULT_ADMIN_PASSWORD=admin123
```

## 🔍 Diagnóstico de Problemas

### Problemas Comuns e Soluções

#### 1. **Container não inicia**
```bash
# Verificar logs
docker-compose -f docker-compose-local.yml logs planka

# Verificar se a porta está livre
netstat -tulpn | grep :3000
```

#### 2. **Secret Key inválido**
```bash
# Gerar novo secret key
openssl rand -hex 64

# Atualizar no docker-compose-local.yml
```

#### 3. **Admin user não criado**
```bash
# Criar manualmente
docker-compose -f docker-compose-local.yml exec planka npm run db:create-admin-user
```

#### 4. **Build falha**
```bash
# Limpar cache
docker system prune -f

# Verificar espaço em disco
df -h

# Verificar Dockerfile
cat Dockerfile
```

### Diagnóstico Automático

O sistema detecta automaticamente:

- ❌ Container não rodando
- 🔄 Container reiniciando constantemente
- 🔑 Secret key inválido
- 👤 Admin user não criado
- 🌐 Porta não acessível

## 📊 Monitoramento

### Status dos Containers
```python
containers = planka_manager.verificar_containers_ativos()
# Retorna: {'planka': True, 'postgres': True}
```

### Logs em Tempo Real
```python
# Logs dos últimos 100 linhas
logs = planka_manager.obter_logs_producao_detalhados(100)

# Logs específicos do Planka
diagnostico = planka_manager.diagnosticar_producao()
logs_planka = diagnostico['logs']['planka']
```

### Health Check
```python
status = planka_manager.verificar_status()
# Retorna: 'online', 'offline', 'error'
```

## 🚨 Troubleshooting

### Erro: "Container reiniciando"
1. Verificar logs: `docker-compose -f docker-compose-local.yml logs planka`
2. Verificar configurações: `docker-compose -f docker-compose-local.yml config`
3. Verificar recursos: `docker stats`

### Erro: "Porta já em uso"
1. Verificar processos: `netstat -tulpn | grep :3000`
2. Parar outros containers: `docker-compose down`
3. Alterar porta no docker-compose-local.yml

### Erro: "Build falha"
1. Limpar cache: `docker system prune -f`
2. Verificar Dockerfile
3. Verificar espaço em disco
4. Verificar permissões

### Erro: "Admin user não criado"
1. Executar manualmente: `docker-compose -f docker-compose-local.yml exec planka npm run db:create-admin-user`
2. Verificar logs do banco: `docker-compose -f docker-compose-local.yml logs postgres`

## 📈 Melhorias Futuras

### 1. **Backup Automático**
- Backup do banco antes de atualizações
- Backup das configurações

### 2. **Rollback Automático**
- Reverter para versão anterior em caso de erro
- Restaurar configurações de backup

### 3. **Monitoramento Avançado**
- Métricas de performance
- Alertas automáticos
- Dashboard de status

### 4. **Deploy Automatizado**
- CI/CD pipeline
- Testes automatizados
- Deploy em múltiplos ambientes

## 📝 Comandos Úteis

### Verificar Status
```bash
# Status geral
docker-compose -f docker-compose-local.yml ps

# Logs em tempo real
docker-compose -f docker-compose-local.yml logs -f

# Logs específicos
docker-compose -f docker-compose-local.yml logs planka
```

### Manutenção
```bash
# Parar todos os containers
docker-compose -f docker-compose-local.yml down

# Rebuild sem cache
docker-compose -f docker-compose-local.yml build --no-cache

# Limpar volumes (CUIDADO!)
docker-compose -f docker-compose-local.yml down -v
```

### Backup
```bash
# Backup do banco
docker-compose -f docker-compose-local.yml exec postgres pg_dump -U postgres planka > backup.sql

# Restaurar backup
docker-compose -f docker-compose-local.yml exec -T postgres psql -U postgres planka < backup.sql
```

---

**Versão**: 1.0  
**Data**: Agosto 2025  
**Autor**: Equipe de Desenvolvimento  
**Status**: Ativo 