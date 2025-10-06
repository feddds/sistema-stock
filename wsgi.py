import sys
import os

# Agregar el path de tu aplicación al sistema
path = os.path.dirname(os.path.abspath(__file__))
if path not in sys.path:
    sys.path.insert(0, path)

# Configurar para producción
os.environ['FLASK_ENV'] = 'production'

# Importar la aplicación
from app import app as application

if __name__ == '__main__':
    application.run()