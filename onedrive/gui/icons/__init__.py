import os.path
from PySide6.QtGui import QIcon

icons = {
    'alert': QIcon(os.path.join(os.path.dirname(__file__), 'alert.svg')),
    'cloud': QIcon(os.path.join(os.path.dirname(__file__), 'cloud.svg')),
    'off': QIcon(os.path.join(os.path.dirname(__file__), 'off.svg')),
    'refresh': QIcon(os.path.join(os.path.dirname(__file__), 'refresh.svg'))
}
