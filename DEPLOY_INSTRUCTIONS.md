# 🚀 Deploy da Plataforma Mini Dólar no Render

## Passo a Passo para Deploy

### 1. Criar Conta no Render
- Acesse: https://render.com/
- Clique em "Get Started for Free"
- Faça login com GitHub, Google ou email

### 2. Criar Repositório no GitHub
- Acesse: https://github.com/
- Crie um novo repositório público chamado "mini-dollar-trading-platform"
- **NÃO** inicialize com README, .gitignore ou license

### 3. Fazer Upload do Código
Execute os comandos abaixo no terminal (substitua SEU_USUARIO pelo seu usuário do GitHub):

```bash
cd mini_dollar_platform
git remote add origin https://github.com/SEU_USUARIO/mini-dollar-trading-platform.git
git branch -M main
git push -u origin main
```

### 4. Deploy no Render

#### 4.1 Criar Banco de Dados PostgreSQL
1. No dashboard do Render, clique em "New +"
2. Selecione "PostgreSQL"
3. Configure:
   - **Name**: mini-dollar-db
   - **Database**: mini_dollar_trading
   - **User**: mini_dollar_user
   - **Plan**: Free
4. Clique em "Create Database"
5. **Anote a URL de conexão** que será gerada

#### 4.2 Criar Web Service
1. No dashboard do Render, clique em "New +"
2. Selecione "Web Service"
3. Conecte seu repositório GitHub
4. Configure:
   - **Name**: mini-dollar-trading-platform
   - **Environment**: Python 3
   - **Build Command**: `./build.sh`
   - **Start Command**: `gunicorn --bind 0.0.0.0:$PORT src.main:app`
   - **Plan**: Free

#### 4.3 Configurar Variáveis de Ambiente
Na seção "Environment Variables", adicione:
- **DATABASE_URL**: Cole a URL do PostgreSQL criado no passo 4.1

### 5. Finalizar Deploy
1. Clique em "Create Web Service"
2. Aguarde o build e deploy (pode levar 5-10 minutos)
3. Sua aplicação estará disponível em: `https://mini-dollar-trading-platform.onrender.com`

## 🎯 URL Final
Após o deploy, sua plataforma estará acessível em:
**https://mini-dollar-trading-platform.onrender.com**

## 🔧 Funcionalidades Disponíveis
- ✅ Cotação USD/BRL em tempo real
- ✅ Análise técnica avançada
- ✅ Análise de sentimento de notícias
- ✅ Sinais de trading inteligentes
- ✅ Interface web moderna e responsiva
- ✅ Banco de dados PostgreSQL
- ✅ SSL automático

## 📱 Acesso
A plataforma funcionará 24/7 e será acessível de qualquer dispositivo com internet.

## ⚠️ Limitações do Plano Gratuito
- A aplicação pode "dormir" após 15 minutos de inatividade
- Primeiro acesso após inatividade pode demorar 30-60 segundos
- 750 horas de uso por mês (suficiente para uso pessoal)

## 🆘 Suporte
Se tiver problemas no deploy, verifique:
1. Se o repositório GitHub está público
2. Se as variáveis de ambiente estão corretas
3. Se o banco PostgreSQL foi criado corretamente

---

**🎉 Sua plataforma de trading estará online e funcionando!**

