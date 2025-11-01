"""
Configuración de pytest para el proyecto.
"""
import os
import sys
from pathlib import Path

# Agregar el directorio raíz del proyecto al PYTHONPATH
ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))