import os

# Base de datos SQLite
DB_NAME = "pos_v7.db"

# PIN de Administrador (se lee prioritariamente de variable de entorno por seguridad)
PIN_ADMIN = os.getenv("PIN_ADMIN", "200423")
