
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





class Unpacker(object):

	_TAR_PATH = "/bin/tar"

	################################################################################################################################
	## Static Helper Methods
	################################################################################################################################

	@staticmethod
	def _uncompressGZip(
			inFilePath:str,
			outFilePath:str,
			terminationFlag:typing.Union[jk_utils.TerminationFlag,None]
		):
		assert inFilePath != outFilePath

		with gzip.open(inFilePath, "rb") as fin:
			with open(outFilePath, "wb") as fout:
				Spooler.spoolStream(fin, fout, terminationFlag)
	#

	@staticmethod
	def _uncompressBZip2(
			inFilePath:str,
			outFilePath:str,
			terminationFlag:typing.Union[jk_utils.TerminationFlag,None]
		):

		assert inFilePath != outFilePath

		with bz2.open(inFilePath, "rb") as fin:
			with open(outFilePath, "wb") as fout:
				Spooler.spoolStream(fin, fout, terminationFlag)
	#

	@staticmethod
	def _uncompressXZ(
			inFilePath:str,
			outFilePath:str,
			terminationFlag:typing.Union[jk_utils.TerminationFlag,None]
		):

		assert inFilePath != outFilePath

		with lzma.open(inFilePath, "rb") as fin:
			with open(outFilePath, "wb") as fout:
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
			srcTarFilePath:str,
			destDirPath:str,
			log:jk_logging.AbstractLogger
		) -> None:

		assert isinstance(srcTarFilePath, str)
		assert os.path.isfile(srcTarFilePath)
		assert isinstance(destDirPath, str)
		assert isinstance(log, jk_logging.AbstractLogger)

		# ----

		with log.descend("Unpacking " + repr(srcTarFilePath) + " ...") as log2:
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
			log2.notice("Invoking /bin/tar with: " + str(tarArgs))
			cmdResult = jk_simpleexec.invokeCmd(Unpacker._TAR_PATH, tarArgs, workingDirectory=destDirPath)

			if cmdResult.returnCode != 0:
				cmdResult.dump(writeFunction=log2.error)
				raise Exception("Failed to run 'tar'!")
	#

	@staticmethod
	def guessCompressionFromFilePath(
			filePath:str
		) -> typing.Union[str,str]:

		assert isinstance(filePath, str)

		if filePath.endswith(".gz"):
			return "gz", filePath[:-3]
		elif filePath.endswith(".bz2"):
			return "bz2", filePath[:-4]
		elif filePath.endswith(".xz"):
			return "xz", filePath[:-3]
		elif filePath.endswith(".tgz"):
			return "gz", filePath[:-2] + "ar"
		elif filePath.endswith(".tbz2"):
			return "bz2", filePath[:-3] + "ar"
		elif filePath.endswith(".txz"):
			return "xz", filePath[:-2] + "ar"
		else:
			raise Exception("Can't guess compression!")
	#

	@staticmethod
	def uncompressFile(
			filePath:str,
			toFilePath:typing.Union[str,None],
			bDeleteOriginal:bool,
			terminationFlag:typing.Union[jk_utils.TerminationFlag,None],
			log:jk_logging.AbstractLogger
		) -> str:

		assert isinstance(filePath, str)
		if toFilePath is not None:
			assert isinstance(toFilePath, str)
		assert isinstance(bDeleteOriginal, bool)
		assert isinstance(log, jk_logging.AbstractLogger)

		# ----

		with log.descend("Uncompressing " + repr(filePath) + " ...") as log2:
			filePath = os.path.abspath(filePath)
			assert os.path.isfile(filePath)

			compression, toFilePath2 = Unpacker.guessCompressionFromFilePath(filePath)
			if toFilePath is None:
				toFilePath = toFilePath2

			if compression in [ "gz", "gzip" ]:
				name = "gzip"
				m = Unpacker._uncompressGZip
			elif compression in [ "bz2", "bzip2" ]:
				name = "bzip2"
				m = Unpacker._uncompressBZip2
			elif compression in [ "xz" ]:
				name = "xz"
				m = Unpacker._uncompressXZ
			else:
				raise Exception("Unknown compression: " + repr(compression))

			log.notice("Unpacking with " + name + " ...")

			orgFileSize = os.path.getsize(filePath)

			# TODO: check if target file already exists

			m(filePath, toFilePath, terminationFlag)

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






















