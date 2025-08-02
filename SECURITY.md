# 🔐 GUIA DE SEGURANÇA - CONFIGURAÇÃO DE CREDENCIAIS

## ⚠️ **IMPORTANTE: CREDENCIAIS REMOVIDAS DO CÓDIGO**

As credenciais da base de dados foram **removidas do código** por questões de segurança. Agora é necessário configurá-las de forma segura.

## 🚨 **PROBLEMA RESOLVIDO**

**Antes (INSECURO):**
```python
# ❌ CREDENCIAIS HARDCODED NO CÓDIGO
self.db_host = "localhost"
self.db_port = 5432
self.db_name = "planka"
self.db_user = "postgres"
self.db_password = "planka"  # ❌ SENHA EXPOSTA
```

**Agora (SEGURO):**
```python
# ✅ CONFIGURAÇÃO SEGURA
from config.database_config import DatabaseConfig
self.db_config = DatabaseConfig(config_dir)
config = self.db_config.get_database_config()  # ✅ SENHA SEGURA
```

## 🔧 **COMO CONFIGURAR AS CREDENCIAIS**

### **Opção 1: Script Automático (RECOMENDADO)**

Execute o script de configuração:

```bash
python configurar_credenciais.py
```

O script irá:
1. ✅ Verificar a configuração atual
2. ✅ Guiar você através do processo de configuração
3. ✅ Configurar as credenciais de forma segura

### **Opção 2: Configuração Manual**

#### **2.1 Variáveis de Ambiente (MAIS SEGURO)**

**Windows (PowerShell):**
```powershell
$env:PLANKA_DB_PASSWORD = "sua_senha_aqui"
```

**Windows (CMD):**
```cmd
set PLANKA_DB_PASSWORD=sua_senha_aqui
```

**Linux/Mac:**
```bash
export PLANKA_DB_PASSWORD='sua_senha_aqui'
```

#### **2.2 Arquivo de Configuração Criptografado**

O sistema também suporta salvar a senha em um arquivo criptografado:

1. Execute: `python configurar_credenciais.py`
2. Escolha a opção 2 (Arquivo de configuração)
3. Digite a senha quando solicitado
4. A senha será criptografada e salva automaticamente

## 📁 **ARQUIVOS DE CONFIGURAÇÃO**

### **Arquivos Criados Automaticamente:**
- `config/database_config.json` - Configuração da base de dados
- `config/database_key.key` - Chave de criptografia (NÃO COMMITAR)

### **Arquivos Protegidos (.gitignore):**
```
# Configuração da base de dados (SENSÍVEL - NÃO COMMITAR)
config/database_config.json
config/database_key.key
config/credentials.json
config/passwords.json
```

## 🔒 **NÍVEIS DE SEGURANÇA**

### **Nível 1: Variáveis de Ambiente (MAIS SEGURO)**
- ✅ Senha nunca salva em arquivo
- ✅ Senha não aparece em logs
- ✅ Senha não é commitada no Git
- ⚠️ Precisa definir a variável toda vez

### **Nível 2: Arquivo Criptografado (SEGURO)**
- ✅ Senha criptografada com Fernet (AES-256)
- ✅ Chave de criptografia separada
- ✅ Arquivos protegidos no .gitignore
- ⚠️ Arquivo existe no sistema

## 🛠️ **CONFIGURAÇÃO PADRÃO**

A configuração padrão é:
- **Host**: localhost
- **Porta**: 5432
- **Base de Dados**: planka
- **Usuário**: postgres
- **Senha**: (deve ser configurada)

## 🔍 **VERIFICAR CONFIGURAÇÃO**

Para verificar se a configuração está correta:

```python
from config.database_config import DatabaseConfig
from pathlib import Path

config_dir = Path("config")
db_config = DatabaseConfig(config_dir)
config_info = db_config.get_config_info()

print(f"Configuração válida: {config_info['valid']}")
print(f"Senha configurada: {config_info['password_set']}")
```

## 🚀 **PRÓXIMOS PASSOS**

1. **Execute o script de configuração:**
   ```bash
   python configurar_credenciais.py
   ```

2. **Configure a senha** seguindo as instruções

3. **Execute o dashboard:**
   ```bash
   python main.py
   ```

4. **Acesse a aba "Base de Dados"** para gerenciar a base

## ⚡ **SOLUÇÃO RÁPIDA**

Se precisar configurar rapidamente:

```bash
# 1. Configurar variável de ambiente
$env:PLANKA_DB_PASSWORD = "planka"

# 2. Executar dashboard
python main.py
```

## 🔧 **TROUBLESHOOTING**

### **Erro: "Configuração da base de dados inválida"**
- Execute: `python configurar_credenciais.py`
- Configure a senha seguindo as instruções

### **Erro: "Senha não configurada"**
- Defina a variável de ambiente: `$env:PLANKA_DB_PASSWORD = "sua_senha"`
- Ou execute o script de configuração

### **Erro: "Arquivo de configuração não encontrado"**
- Execute: `python configurar_credenciais.py`
- O script criará os arquivos necessários

## 📞 **SUPORTE**

Se tiver problemas:
1. Execute: `python configurar_credenciais.py`
2. Siga as instruções na tela
3. Verifique se a variável de ambiente está definida
4. Consulte este guia de segurança

---

**✅ SEGURANÇA GARANTIDA: As credenciais não estão mais no código!** 