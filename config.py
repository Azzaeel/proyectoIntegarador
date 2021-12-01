from app import app
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import secrets


# Configuración de la BD
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database/genesisSystem.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


# Llave secreta para archivo cookies
app.secret_key = secrets.token_hex()

db = SQLAlchemy(app)

# Configuración Flask Migrate
migrate = Migrate()
migrate.init_app(app, db)