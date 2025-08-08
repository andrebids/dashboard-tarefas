# Solução para Problemas de Rede Docker

## Problema Identificado

O erro que estava a impedir a ligação do Docker era:

```
Error response from daemon: failed to set up container networking: network 8f366c53bd8c174998be572c443f64e39d6e394e4ebb559faa888fdfda820dec not found
```

## Causa Raiz

O problema ocorreu porque:

1. **Rede com labels incorretos**: A rede `planka-personalizado_default` existia mas não foi criada pelo Docker Compose
2. **Labels incompatíveis**: A rede tinha `com.docker.compose.network` vazio quando deveria ter o valor "default"
3. **Referência a rede inexistente**: O container tentava conectar-se a uma rede que foi removida ou corrompida

## Solução Implementada

### Passos da Resolução:

1. **Parar todos os containers** do Planka (dev e prod)
2. **Verificar redes existentes** para identificar problemas
3. **Remover rede problemática** se existir com labels incorretos
4. **Limpar redes órfãs** com `docker network prune -f`
5. **Limpar containers órfãos** com `docker container prune -f`
6. **Aguardar 3 segundos** para estabilização
7. **Iniciar containers novamente** - Docker Compose criará a rede automaticamente

### Comandos Manuais:

```bash
# Parar containers
docker-compose -f docker-compose-dev.yml down
docker-compose -f docker-compose-local.yml down

# Remover rede problemática
docker network rm planka-personalizado_default

# Limpar recursos órfãos
docker network prune -f
docker container prune -f

# Iniciar novamente
docker-compose -f docker-compose-dev.yml up -d
```

## Script Automatizado

Foi criado o script `resolver_rede_docker.py` que automatiza todo o processo:

```bash
python resolver_rede_docker.py
```

### Funcionalidades do Script:

- ✅ Verificação automática de status
- ✅ Limpeza de redes problemáticas
- ✅ Reinicialização completa dos containers
- ✅ Geração de relatório detalhado
- ✅ Logging de todos os passos

## Verificação de Sucesso

Após a resolução, verificar:

```bash
# Status dos containers
docker ps

# Status das redes
docker network ls

# Logs dos containers
docker logs planka-personalizado-planka-server-1
docker logs planka-personalizado-planka-client-1
```

## Prevenção

Para evitar este problema no futuro:

1. **Sempre usar Docker Compose** para gerir redes
2. **Não criar redes manualmente** com nomes que o Compose usa
3. **Limpar recursos órfãos** periodicamente
4. **Usar o script de resolução** quando necessário

## Resultado

✅ **Problema resolvido**: Todos os containers estão a funcionar
✅ **Rede criada corretamente**: `planka-personalizado_default` com labels corretos
✅ **Acesso disponível**: Planka acessível em `http://localhost:3001`

## Arquivos Relacionados

- `resolver_rede_docker.py` - Script de resolução automática
- `docker-compose-dev.yml` - Configuração de desenvolvimento
- `docker-compose-local.yml` - Configuração de produção local
