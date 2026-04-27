# API Flask — Guia para rodar o projeto

## Fluxo de desenvolvimento (Git)

- Sempre crie uma branch a partir da `main`
- Desenvolva na sua branch
- Abra um PR (Pull Request) para `main`

Exemplo:

```bash
git checkout main
git pull
git checkout -b minha-feature
```

Depois de finalizar:

```bash
git add .
git commit -m "Minha feature"
git push origin minha-feature
```

Abra o PR no GitHub.

---

# Como rodar o projeto

Após clonar o repositório:

```bash
git clone <repo>
cd <repo>
```

---

# Windows

Cada linha é um comando:

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
set FLASK_APP=run.py
flask run
```

Servidor iniciará em:

```
http://localhost:5000
```

---

# Linux / Mac

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
export FLASK_APP=run.py
flask run
```

Servidor:

```
http://localhost:5000
```

---

# Variáveis de ambiente (.env)

Criar arquivo `.env` na raiz:

```
DATABASE_URL=sua_connection_string
```

Exemplo:

```
DATABASE_URL=postgresql://user:password@host:6543/postgres
```

---

# Estrutura do projeto

```
app/
 ├── routes/
 ├── services/
 ├── repositories/
 ├── database.py
 └── __init__.py

run.py
requirements.txt
.env
```

---

# Instalar novas dependências

Sempre que instalar algo:

```bash
pip install nome-pacote
```

Atualize:

```bash
pip freeze > requirements.txt
```

---

# Rodar em modo debug (opcional)

Windows:

```bash
set FLASK_ENV=development
```

Linux:

```bash
export FLASK_ENV=development
```

---

# Endpoints

Exemplo:

```
GET /produtos
GET /produtos/{id}
```
