import os
import sys

# Locate the active execution directory
sys.path.insert(0, os.path.dirname(__file__))

# Point directly to the virtual environment path we will create on Hostinger
# (We use the standard relative tracking path format)
venv_path = os.path.join(os.path.dirname(__file__), 'venv', 'lib', 'python3.10', 'site-packages')
sys.path.insert(1, venv_path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'kaanuro_project.settings'

from kaanuro_project.wsgi import application
