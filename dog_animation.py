# dog_animation.py
import glob
from PyQt5.QtGui import QPixmap

def load_frames(folder_pattern, size=(100, 100)):
    paths = sorted(glob.glob(folder_pattern))
    return [QPixmap(path).scaled(*size, aspectRatioMode=1, transformMode=1) for path in paths]