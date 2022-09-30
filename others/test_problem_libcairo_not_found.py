"""Attempt to check where libcairo is install because that caused bugs.

see
https://stackoverflow.com/questions/46265677/get-cairosvg-working-in-windows
"""

import ctypes.util
path = ctypes.util.find_library('libcairo-2')
print(path)
path = ctypes.util.find_library('cairo-2')
print(path)
path = ctypes.util.find_library('cairo')
print(path)
path = ctypes.util.find_library('libcairo.2.dylib')
print(path)
