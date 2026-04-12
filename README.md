# My Personal Finances

Flask app para tracking de finanzas personales/familiares. Se puede importar el extracto del resumen de la cuenta de banco (XLS) y los resumenes de las tarjetas de crédito (texto plano), se visualizan datos con budget mensual y deuda. Deploy en Vercel + Neon PostgreSQL.

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
