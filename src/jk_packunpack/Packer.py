
import os

import tarfile
import gzip
import bz2
import lzma

import jk_simpleexec
import jk_logging






class Packer(object):

	_TAR_PATH = "/bin/tar"

	@staticmethod
	def tarDir(srcDirPath:str, destTarFile:str, log:jk_logging.AbstractLogger):
		assert isinstance(srcDirPath, str)
		assert isinstance(destTarFile, str)
		assert isinstance(log, jk_logging.AbstractLogger)

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
	def compressFile(filePath:str, compression:str, bDeleteOriginal:bool, log:jk_logging.AbstractLogger) -> str:
		assert isinstance(filePath, str)
		assert isinstance(compression, str)
		assert isinstance(bDeleteOriginal, bool)
		assert isinstance(log, jk_logging.AbstractLogger)

		with log.descend("Compressing " + repr(filePath) + " ...") as log2:
			filePath = os.path.abspath(filePath)
			assert os.path.isfile(filePath)

			if compression in [ "gz", "gzip" ]:
				name = "gzip"
				ext = ".gz"
				m = Packer._compressGZip
			elif compression in [ "bz2", "bzip2" ]:
				name = "bzip2"
				ext = ".bz2"
				m = Packer._compressBZip2
			elif compression in [ "xz" ]:
				name = "xz"
				ext = ".xz"
				m = Packer._compressXZ
			else:
				raise Exception("Unknown compression: " + repr(compression))

			log.notice("Packing with " + name + " ...")

			orgFileSize = os.path.getsize(filePath)

			toFilePath = filePath + ext

			# TODO: check if target file already exists

			m(filePath, toFilePath)

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
	def _compressGZip(inFilePath:str, outFilePath:str):
		assert inFilePath != outFilePath

		with open(inFilePath, "rb") as fin:
			with gzip.open(outFilePath, "wb") as fout:
				Packer._spool(fin, fout)
	#

	@staticmethod
	def _compressBZip2(inFilePath:str, outFilePath:str):
		assert inFilePath != outFilePath

		with open(inFilePath, "rb") as fin:
			with bz2.open(outFilePath, "wb") as fout:
				Packer._spool(fin, fout)
	#

	@staticmethod
	def _compressXZ(inFilePath:str, outFilePath:str):
		assert inFilePath != outFilePath

		with open(inFilePath, "rb") as fin:
			with lzma.open(outFilePath, "wb") as fout:
				Packer._spool(fin, fout)
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

#






















