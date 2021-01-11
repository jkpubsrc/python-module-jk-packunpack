
import os
import typing
import tarfile
import gzip
import bz2
import lzma

import jk_simpleexec
import jk_logging
import jk_utils

from .Spooler import Spooler
from .SpoolInfo import SpoolInfo






class Packer(object):

	_TAR_PATH = "/bin/tar"

	################################################################################################################################
	## Static Helper Methods
	################################################################################################################################

	@staticmethod
	def _compressGZip(
			inFilePath:str,
			outFilePath:str,
			chModValueI:int = None,
			terminationFlag:jk_utils.TerminationFlag = None
		):

		assert inFilePath != outFilePath

		with open(inFilePath, "rb") as fin:
			if chModValueI is None:
				with gzip.open(outFilePath, "wb") as fout:
					Spooler.spoolStream(fin, fout, terminationFlag)
			else:
				fdesc = os.open(outFilePath, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, chModValueI)
				with open(fdesc, "wb") as fout2:
					with gzip.open(fout2, "wb") as fout:
						Spooler.spoolStream(fin, fout, terminationFlag)
	#

	@staticmethod
	def _compressBZip2(
			inFilePath:str,
			outFilePath:str,
			chModValueI:int = None,
			terminationFlag:jk_utils.TerminationFlag = None
		):

		assert inFilePath != outFilePath

		with open(inFilePath, "rb") as fin:
			if chModValueI is None:
				with bz2.open(outFilePath, "wb") as fout:
					Spooler.spoolStream(fin, fout, terminationFlag)
			else:
				fdesc = os.open(outFilePath, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, chModValueI)
				with open(fdesc, "wb") as fout2:
					with bz2.open(fout2, "wb") as fout:
						Spooler.spoolStream(fin, fout, terminationFlag)
	#

	@staticmethod
	def _compressXZ(
			inFilePath:str,
			outFilePath:str,
			chModValueI:int = None,
			terminationFlag:jk_utils.TerminationFlag = None
		):

		assert inFilePath != outFilePath

		with open(inFilePath, "rb") as fin:
			if chModValueI is None:
				with lzma.open(outFilePath, "wb") as fout:
					Spooler.spoolStream(fin, fout, terminationFlag)
			else:
				fdesc = os.open(outFilePath, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, chModValueI)
				with open(fdesc, "wb") as fout2:
					with lzma.open(fout2, "wb") as fout:
						Spooler.spoolStream(fin, fout, terminationFlag)
	#

	#
	# @return		str name
	# @return		str ext
	# @return		callable m
	#
	@staticmethod
	def _getCompressionParams(compression:str):
		assert isinstance(compression, str)

		if compression in [ "gz", "gzip" ]:
			return "gzip", ".gz", Packer._compressGZip
		elif compression in [ "bz2", "bzip2" ]:
			return "bzip2", ".bz2", Packer._compressBZip2
		elif compression in [ "xz" ]:
			return "xz", ".xz", Packer._compressXZ
		else:
			raise Exception("Unknown compression: " + repr(compression))
	#

	################################################################################################################################
	## Static Public Methods
	################################################################################################################################

	@staticmethod
	def tarDir(
			srcDirPath:str,
			destTarFile:str,
			log:jk_logging.AbstractLogger
		):

		assert isinstance(srcDirPath, str)
		assert isinstance(destTarFile, str)
		assert isinstance(log, jk_logging.AbstractLogger)

		# ----

		with log.descend("Packing " + repr(srcDirPath) + " ...") as log2:
			srcDirPath = os.path.abspath(srcDirPath)
			assert os.path.isdir(srcDirPath)
			destTarFile = os.path.abspath(destTarFile)

			if not os.path.isfile(Packer._TAR_PATH):
				raise Exception("'tar' not found!")

			tarArgs = [
				"-cf", destTarFile, "."
			]
			log2.notice("Invoking /bin/tar with: " + str(tarArgs))
			cmdResult = jk_simpleexec.invokeCmd(Packer._TAR_PATH, tarArgs, workingDirectory=srcDirPath)

			if cmdResult.returnCode != 0:
				cmdResult.dump(writeFunction=log2.error)
				raise Exception("Failed to run 'tar'!")
	#

	@staticmethod
	@jk_utils.deprecated
	def compressFile(
			filePath:str,
			compression:str,
			bDeleteOriginal:bool,
			terminationFlag:typing.Union[jk_utils.TerminationFlag,None],
			log:jk_logging.AbstractLogger
		) -> str:

		assert isinstance(filePath, str)
		assert isinstance(compression, str)
		assert isinstance(bDeleteOriginal, bool)
		assert isinstance(log, jk_logging.AbstractLogger)

		# ----

		with log.descend("Compressing " + repr(filePath) + " ...") as log2:
			filePath = os.path.abspath(filePath)
			assert os.path.isfile(filePath)

			name, ext, m = Packer._getCompressionParams(compression)

			log.notice("Packing with " + name + " ...")

			orgFileSize = os.path.getsize(filePath)

			toFilePath = filePath + ext

			# TODO: check if target file already exists

			m(filePath, toFilePath, None, terminationFlag)

			resultFileSize = os.path.getsize(toFilePath)
			compressionFactor = round(100 * resultFileSize / orgFileSize, 2)
			log.notice("Compression factor: {}%".format(compressionFactor))

			if bDeleteOriginal:
				if os.path.isfile(filePath):
					os.unlink(filePath)
			else:
				if not os.path.isfile(filePath):
					raise Exception("Implementation error!")

			return toFilePath
	#

	@staticmethod
	def compressFile2(
			filePath:str,
			toFilePath:typing.Union[str,None],
			compression:str,
			bDeleteOriginal:bool,
			chModValue:typing.Union[int,jk_utils.ChModValue,None],
			terminationFlag:typing.Union[jk_utils.TerminationFlag,None],
			log:jk_logging.AbstractLogger
		) -> SpoolInfo:

		assert isinstance(filePath, str)
		if toFilePath is not None:
			assert isinstance(toFilePath, str)
		assert isinstance(compression, str)
		assert isinstance(bDeleteOriginal, bool)
		if chModValue is not None:
			if isinstance(chModValue, int):
				chModValueI = chModValue
			else:
				assert isinstance(chModValue, jk_utils.ChModValue)
				chModValueI = int(chModValue)
		assert isinstance(log, jk_logging.AbstractLogger)

		# ----

		with log.descend("Compressing " + repr(filePath) + " ...") as log2:
			filePath = os.path.abspath(filePath)
			assert os.path.isfile(filePath)

			compressionName, compressionFileExt, m = Packer._getCompressionParams(compression)

			log.notice("Packing with " + compressionName + " ...")

			orgFileSize = os.path.getsize(filePath)

			if toFilePath is None:
				toFilePath = filePath + compressionFileExt

			# TODO: check if target file already exists

			m(filePath, toFilePath, chModValueI, terminationFlag)

			resultFileSize = os.path.getsize(toFilePath)

			if bDeleteOriginal:
				if os.path.isfile(filePath):
					os.unlink(filePath)
			else:
				if not os.path.isfile(filePath):
					raise Exception("Implementation error!")

			return SpoolInfo(filePath, toFilePath, compressionName, compressionFileExt, orgFileSize, resultFileSize)
	#

#






















