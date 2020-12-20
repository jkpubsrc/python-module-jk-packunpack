
import os
import typing

import jk_simpleexec
import jk_logging
import jk_utils

from .SpoolInfo import SpoolInfo






class Spooler(object):

	################################################################################################################################
	## Static Helper Methods
	################################################################################################################################

	@staticmethod
	def _copy(inFilePath:str, outFilePath:str, chModValueI:int = None):
		assert inFilePath != outFilePath

		with open(inFilePath, "rb") as fin:
			if chModValueI is None:
				with open(outFilePath, "wb") as fout:
					Spooler._spool(fin, fout)
			else:
				fdesc = os.open(outFilePath, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, chModValueI)
				with open(fdesc, "wb") as fout:
					Spooler._spool(fin, fout)
	#

	@staticmethod
	def _spool(fin, fout):
		assert fin
		assert fout

		lastBlockSize = 65536
		totalLength = 0

		for dataChunk in iter(lambda: fin.read(65536), b""):
			assert lastBlockSize == 65536
			lastBlockSize = len(dataChunk)
			assert lastBlockSize > 0
			totalLength += len(dataChunk)
			fout.write(dataChunk)
	#

	################################################################################################################################
	## Static Public Methods
	################################################################################################################################

	@staticmethod
	def spoolFile(fromFilePath:str, toFilePath:str, bDeleteOriginal:bool, chModValue:typing.Union[int,jk_utils.ChModValue,None], log:jk_logging.AbstractLogger) -> SpoolInfo:
		assert isinstance(fromFilePath, str)
		assert isinstance(toFilePath, str)
		assert isinstance(bDeleteOriginal, bool)
		if chModValue is not None:
			if isinstance(chModValue, int):
				chModValueI = chModValue
			else:
				assert isinstance(chModValue, jk_utils.ChModValue)
				chModValueI = int(chModValue)
		assert isinstance(log, jk_logging.AbstractLogger)

		# ----

		with log.descend("Copying " + repr(fromFilePath) + " ...") as log2:
			fromFilePath = os.path.abspath(fromFilePath)
			assert os.path.isfile(fromFilePath)

			orgFileSize = os.path.getsize(fromFilePath)

			# TODO: check if target file already exists

			Spooler._copy(fromFilePath, toFilePath, chModValueI)

			resultFileSize = os.path.getsize(toFilePath)

			if bDeleteOriginal:
				if os.path.isfile(fromFilePath):
					os.unlink(fromFilePath)
			else:
				if not os.path.isfile(fromFilePath):
					raise Exception("Implementation error!")

			return SpoolInfo(fromFilePath, toFilePath, None, None, orgFileSize, resultFileSize)
	#

#






















