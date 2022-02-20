
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
from .FileUncompressionGuess import FileUncompressionGuess






class Unpacker(object):

	_TAR_PATH = "/bin/tar"

	################################################################################################################################
	## Static Helper Methods
	################################################################################################################################

	@staticmethod
	def _uncompressGZip(
			inFilePath:str,
			outFilePath:str,
			chModValueI:int = None,
			terminationFlag:jk_utils.TerminationFlag = None,
		):
		assert inFilePath != outFilePath

		with gzip.open(inFilePath, "rb") as fin:
			if chModValueI is None:
				with open(outFilePath, "wb") as fout:
					Spooler.spoolStream(fin, fout, terminationFlag)
			else:
				fdesc = os.open(outFilePath, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, chModValueI)
				with open(fdesc, "wb") as fout:
					Spooler.spoolStream(fin, fout, terminationFlag)
	#

	@staticmethod
	def _uncompressBZip2(
			inFilePath:str,
			outFilePath:str,
			chModValueI:int = None,
			terminationFlag:jk_utils.TerminationFlag = None,
		):

		assert inFilePath != outFilePath

		with bz2.open(inFilePath, "rb") as fin:
			if chModValueI is None:
				with open(outFilePath, "wb") as fout:
					Spooler.spoolStream(fin, fout, terminationFlag)
			else:
				fdesc = os.open(outFilePath, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, chModValueI)
				with open(fdesc, "wb") as fout:
					Spooler.spoolStream(fin, fout, terminationFlag)
	#

	@staticmethod
	def _uncompressXZ(
			inFilePath:str,
			outFilePath:str,
			chModValueI:int = None,
			terminationFlag:jk_utils.TerminationFlag = None,
		):

		assert inFilePath != outFilePath

		with lzma.open(inFilePath, "rb") as fin:
			if chModValueI is None:
				with open(outFilePath, "wb") as fout:
					Spooler.spoolStream(fin, fout, terminationFlag)
			else:
				fdesc = os.open(outFilePath, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, chModValueI)
				with open(fdesc, "wb") as fout:
					Spooler.spoolStream(fin, fout, terminationFlag)
	#

	################################################################################################################################
	## Static Public Methods
	################################################################################################################################

	#
	# Untar the specified <c>tar</c> archive and write the contents to the specified directory.
	#
	# @param	str srcTarFilePath					(required) The tar archive to read
	# @param	str destDirFilePath					(required) The target directory to unpack all data to
	# @param	AbstractLogger log					(required) A logger to write log information to
	#
	@staticmethod
	def untarToDir(
			*args,
			srcTarFilePath:str,
			destDirPath:str,
			log:jk_logging.AbstractLogger,
		) -> None:

		if args:
			raise Exception("Invoke this method with named arguments only!")

		assert isinstance(srcTarFilePath, str)
		assert os.path.isfile(srcTarFilePath)
		assert isinstance(destDirPath, str)
		assert isinstance(log, jk_logging.AbstractLogger)

		# ----

		with log.descend("Unpacking " + repr(srcTarFilePath) + " ...", logLevel=jk_logging.EnumLogLevel.NOTICE) as log2:
			srcTarFilePath = os.path.abspath(srcTarFilePath)
			assert os.path.isfile(srcTarFilePath)
			destDirPath = os.path.abspath(destDirPath)
			if not os.path.isdir(destDirPath):
				os.makedirs(destDirPath)

			if not os.path.isfile(Unpacker._TAR_PATH):
				raise Exception("'tar' not found!")

			tarArgs = [
				"-xf", srcTarFilePath, "-C", destDirPath
			]
			log2.notice("Invoking {} with: {}".format(Unpacker._TAR_PATH, str(tarArgs)))
			cmdResult = jk_simpleexec.invokeCmd(Unpacker._TAR_PATH, tarArgs, workingDirectory=destDirPath)

			if cmdResult.returnCode != 0:
				cmdResult.dump(writeFunction=log2.error)
				raise Exception("Failed to run 'tar'!")
	#

	#
	# Guess the type of uncompression and calculate the uncompression file path
	# An exception is raised on error.
	#
	@staticmethod
	def guessCompressionFromFilePathE(
			filePath:str
		) -> FileUncompressionGuess:

		assert isinstance(filePath, str)

		if filePath.endswith(".gz"):
			return FileUncompressionGuess("gz", filePath[:-3])
		elif filePath.endswith(".bz2"):
			return FileUncompressionGuess("bz2", filePath[:-4])
		elif filePath.endswith(".xz"):
			return FileUncompressionGuess("xz", filePath[:-3])
		elif filePath.endswith(".tgz"):
			return FileUncompressionGuess("gz", filePath[:-2] + "ar")
		elif filePath.endswith(".tbz2"):
			return FileUncompressionGuess("bz2", filePath[:-3] + "ar")
		elif filePath.endswith(".txz"):
			return FileUncompressionGuess("xz", filePath[:-2] + "ar")
		else:
			raise Exception("Can't guess compression!")
	#

	#
	# Guess the type of uncompression and calculate the uncompression file path
	#
	@staticmethod
	def guessCompressionFromFilePathN(
			filePath:str
		) -> typing.Union[FileUncompressionGuess,None]:

		assert isinstance(filePath, str)

		if filePath.endswith(".gz"):
			return FileUncompressionGuess("gz", filePath[:-3])
		elif filePath.endswith(".bz2"):
			return FileUncompressionGuess("bz2", filePath[:-4])
		elif filePath.endswith(".xz"):
			return FileUncompressionGuess("xz", filePath[:-3])
		elif filePath.endswith(".tgz"):
			return FileUncompressionGuess("gz", filePath[:-2] + "ar")
		elif filePath.endswith(".tbz2"):
			return FileUncompressionGuess("bz2", filePath[:-3] + "ar")
		elif filePath.endswith(".txz"):
			return FileUncompressionGuess("xz", filePath[:-2] + "ar")
		else:
			return None
	#

	#
	# Decompress the specified file.
	#
	# @param	str filePath						(required) The path of the file to uncompress.
	# @param	str toFilePath						(optional) The path of the file to write the uncompressed data to.
	# @param	str toDirPath						(optional) A directory to write the data to. If specified this overrides the
	#												regular directory the resulting file will be created in.
	# @param	bool bDeleteOriginal				(required) If <c>True</c> the source file will be deleted after successfull decompression.
	# @param	int|str|ChModValue chModValue		(optional) If specified this change-mode value will be used to set the permissions of
	#												the created file.
	# @param	TerminationFlag terminationFlag		(optional) A termination flag for graceful asynchroneous termination.
	# @param	AbstractLogger log					(required) A logger to write log information to
	# @return	str									Returns the path of the result file.
	#
	@staticmethod
	def uncompressFile(
			*args,
			filePath:str,
			toFilePath:str = None,
			toDirPath:str = None,
			bDeleteOriginal:bool = False,
			chModValue:typing.Union[int,str,jk_utils.ChModValue,None] = None,
			terminationFlag:jk_utils.TerminationFlag = None,
			log:jk_logging.AbstractLogger,
		) -> str:

		if args:
			raise Exception("Invoke this method with named arguments only!")

		assert isinstance(filePath, str)
		if toFilePath is not None:
			assert isinstance(toFilePath, str)
		if toDirPath is not None:
			assert isinstance(toDirPath, str)
			assert os.path.isdir(toDirPath)
		assert isinstance(bDeleteOriginal, bool)
		chModValue = jk_utils.ChModValue.createN(chModValue)
		chModValueI = None if chModValue is None else chModValue.toInt()
		assert isinstance(log, jk_logging.AbstractLogger)

		# ----

		with log.descend("Uncompressing " + repr(filePath) + " ...", logLevel=jk_logging.EnumLogLevel.NOTICE) as log2:
			filePath = os.path.abspath(filePath)
			assert os.path.isfile(filePath)

			guess = Unpacker.guessCompressionFromFilePathE(filePath)
			if toFilePath is None:
				toFilePath = guess.toFilePath
			if toDirPath is not None:
				# override already existing directory
				_fileName = os.path.basename(toFilePath)
				toFilePath = os.path.join(toDirPath, _fileName)

			if guess.compression in [ "gz", "gzip" ]:
				name = "gzip"
				m = Unpacker._uncompressGZip
			elif guess.compression in [ "bz2", "bzip2" ]:
				name = "bzip2"
				m = Unpacker._uncompressBZip2
			elif guess.compression in [ "xz" ]:
				name = "xz"
				m = Unpacker._uncompressXZ
			else:
				raise Exception("Unknown compression: " + repr(guess.compression))

			log.notice("Unpacking with " + name + " ...")

			orgFileSize = os.path.getsize(filePath)

			# TODO: check if target file already exists

			m(filePath, toFilePath, chModValueI, terminationFlag)

			resultFileSize = os.path.getsize(toFilePath)
			uncompressionFactor = round(100 * orgFileSize / resultFileSize, 2)
			log.notice("Uncompression factor: {}%".format(uncompressionFactor))

			if bDeleteOriginal:
				if os.path.isfile(filePath):
					os.unlink(filePath)
			else:
				if not os.path.isfile(filePath):
					raise Exception("Implementation error!")

			return toFilePath
	#

#






















