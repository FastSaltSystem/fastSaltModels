"""Locate the sibling hub's shared engineering package; never silently use stale copies."""
import os
from pathlib import Path
import sys
HUB=Path(os.environ.get('FAST_SALT_HUB', str(Path(__file__).resolve().parents[3]/'fastSalt'))).resolve()
PACKAGE=HUB/'design/engineering'
if not (PACKAGE/'fast_salt_engineering/coolant.py').is_file():
    raise FileNotFoundError('Shared coolant model missing. Place fastSalt beside fastSaltModels or set FAST_SALT_HUB.')
sys.path.insert(0,str(PACKAGE))
from fast_salt_engineering import coolant
ENGINEERING=coolant.read()
