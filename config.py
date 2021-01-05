# STOCKIE'S CONFIGURATION FILE
from tempfile import mkdtemp

DEBUG=True
# Ensure templates are auto-reloaded
TEMPLATES_AUTO_RELOAD = True
# Configure session to use filesystem (instead of signed cookies)
SESSION_FILE_DIR = mkdtemp()
SESSION_PERMANENT = False
SESSION_TYPE = "filesystem"