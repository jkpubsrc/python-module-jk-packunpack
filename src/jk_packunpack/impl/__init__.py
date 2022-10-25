


import os


#if os.name == "posix":
#	from .PosixExternalTar import PosixExternalTar
#	TARER = PosixExternalTar()
#else:
#	from .PythonNativeTar import PythonNativeTar
#	TARER = PythonNativeTar()

from .PythonNativeTar import PythonNativeTar
TARER = PythonNativeTar()