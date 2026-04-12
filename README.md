# My Personal Finances

Flask app for tracking personal finances. Import bank statements (XLS) and credit card summaries, visualize monthly budgets and credit card debt. Deployed on Vercel + Neon PostgreSQL.

## Stack

- **Backend:** Python 3, Flask, SQLAlchemy, pandas, pdfplumber
- **Frontend:** Jinja2 templates, DaisyUI (Aqua theme), Tailwind CSS
- **DB:** PostgreSQL (Neon) in production, SQLite locally
- **Deploy:** Vercel (Python serverless)

## Setup local

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Crear `.env` en la raíz:

```env
DATABASE_URL=sqlite:///local.db   # o tu conexión PostgreSQL
SECRET_KEY=una-clave-secreta
APP_PIN=1234
```

Correr el servidor:

```bash
python src/main.py
```

App disponible en `http://localhost:5000`.

## Deploy en Vercel

1. Crear proyecto en [Neon](https://neon.tech) y copiar el connection string.
2. En Vercel → Settings → Environment Variables, configurar:
   - `DATABASE_URL` — connection string de Neon
   - `SECRET_KEY` — clave secreta para sesiones Flask
   - `APP_PIN` — PIN de 4 dígitos para acceso
3. Conectar el repo en Vercel y deployar.
