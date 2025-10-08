# StreamEvents

# ✨ Objectius
StreamEvents és una plataforma web que permet als usuaris crear i visualitzar esdeveniments en directe, similar a Twitch però més simple. Inclou un assistent virtual intel·ligent que ajuda en la moderació i recomanacions.

# 🧱 Stack Principal
- Python 3.11+
- Django 4.1.13
- Djongo (MongoDB connector)
- MongoDB
- Pillow (per imatges d’avatars)

# 📂 Estructura Simplificada

streamevents/
├── config/
├── users/
│ ├── fixtures/
│ │ ├── 01_groups.json
│ │ └── 02_users.json
│ ├── management/
│ │ ├── init.py
│ │ └── commands/
│ │ ├── init.py
│ │ └── seed_users.py
│ ├── models.py
│ └── admin.py
├── templates/
├── media/
├── static/
├── venv/
└── manage.py

# ✅ Requisits previs

- Python 3.11+
- MongoDB en funcionament
- Llibreries instal·lades:
    asgiref==3.8.1
    attrs==25.3.0
    Django==4.1.13
    djongo==1.3.6
    pymongo==3.12.3
    Pillow==10.1.0

# 🚀 Instal·lació ràpida

1. **Clonar i preparar entorn**:
```bash
git clone (repositori)
cd streamevents
python -m venv venv
```

2.**Activar entorn virtual**:
```bash
venv\Scripts\activate
```

3.**Instalar dependecies**
```bash
pip install django==5.0.0
pip install djongo==1.3.6
pip install pymongo==3.12.3
pip install python-dotenv==1.0.0
pip install pillow==10.1.0
```

4.**Aplicar migracions**
```bash
python manage.py makemigrations
python manage.py migrate
```

# 🔐 Variables d'entorn (env.example)

SECRET_KEY=your_secret_key
DEBUG=True
DB_NAME=streamevents
DB_HOST=localhost
DB_PORT=27017

# 👤 Superusuari

python manage.py createsuperuser

# 🗃️ Migrar a MongoDB

DATABASES = {
    "default": {  # MOD
        "ENGINE": "djongo",  # MOD: Motor djongo
        "NAME": "streamevents_db",  # MOD: Nom BBDD
        "ENFORCE_SCHEMA": True,  # MOD: Validació d'esquema
        "CLIENT": {  # MOD
            "host": "mongodb://localhost:27017"  # MOD: Connexió Mongo
        },  # MOD
    }  # MOD
}

# 🛠️ Comandes útils

## Executar servidor
python manage.py runserver

## Crear nova app
python manage.py startapp app_name

# 💾 Fixtures (exemple)

## Els grups
python manage.py loaddata 01_groups.json

## Els usuaris
python manage.py loaddata 02_users.json


# 🌱 Seeds (exemple d'script)

## Crear 10 usuaris per defecte
python manage.py seed_users

## Crear 25 usuaris eliminant els existents
python manage.py seed_users --users 25 --clear

## Crear usuaris amb relacions de seguiment
python manage.py seed_users --users 15 --with-follows

## Veure ajuda del command
python manage.py seed_users --help
