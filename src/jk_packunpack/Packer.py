
import os
import typing
import tarfile
import gzip
import bz2
import lzma
import time
import re
import zipfile

import jk_simpleexec
import jk_logging
import jk_utils
import jk_dirwalker

from .Spooler import Spooler
from .SpoolInfo import SpoolInfo
from .impl import TARER
from ._NameMatcher import _NameMatcher





class Packer(object):

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

	#
	# This method selects files and directories (non-recursively) from the specified source directory.
	#
	# This is a helper method only. It is used by other method(s) such as <c>tarDirContents()</c> for filtering.
	# However, it is quite useful for other purposes not related to compression. This is the reason why it is made
	# public in this module though it is not related to compression in a strict sense.
	#
	@staticmethod
	def selectFilesAndDirs(
			dirPath:str,
			filesAndDirsToInclude:typing.Iterable[typing.Union[str,re.Match]] = None,
			filesAndDirsToExclude:typing.Iterable[typing.Union[str,re.Match]] = None,
			bDebugIncludeExclude:bool = False,
			log:jk_logging.AbstractLogger = None,
		) -> typing.List[str]:

		if bDebugIncludeExclude:
			log.notice(":: filesAndDirsToInclude = " + str(filesAndDirsToInclude))
			log.notice(":: filesAndDirsToExclude = " + str(filesAndDirsToExclude))

		_includeMatcher = _NameMatcher(filesAndDirsToInclude, bDefaultIfNone=True)
		_excludeMatcher = _NameMatcher(filesAndDirsToExclude, bDefaultIfNone=False)

		entries = []
		if bDebugIncludeExclude:
			for fe in os.scandir(dirPath):
				if _includeMatcher.matchDebug(fe.name, "include candidate", "exclude", log) \
						and not _excludeMatcher.matchDebug(fe.name, "exclude", "don't exclude", log):
					log.notice("-> including: " + fe.name)
					entries.append(fe.name)
		else:
			for fe in os.scandir(dirPath):
				if _includeMatcher.match(fe.name) and not _excludeMatcher.match(fe.name):
					entries.append(fe.name)

		return sorted(entries)
	#

	#
	# Pack the contents of the specified directory in a tar file.
	#
	# @param	str srcDirPath						(required) The directory to pack
	# @param	str destTarFilePath					(required) The tar file to create
	# @param	str[] filesAndDirsToInclude			(optional) The file and directorie names (without path!) to include.
	#												If <c>None</c> is specified the source directory is scanned and all
	#												files and directories found there will be included automatically.
	# @param	AbstractLogger log					(required) A logger to write log information to
	#
	@staticmethod
	def tarDirContents(
			*args,
			srcDirPath:str,
			destTarFilePath:str,
			chModValue:typing.Union[int,str,jk_utils.ChModValue,None] = None,
			filesAndDirsToInclude:typing.Iterable[typing.Union[str,re.Match]] = None,
			filesAndDirsToExclude:typing.Iterable[typing.Union[str,re.Match]] = None,
			log:jk_logging.AbstractLogger,
			bDebugIncludeExclude:bool = False,
		) -> typing.Union[str,None]:

		if args:
			raise Exception("Invoke this method with named arguments only!")

		assert isinstance(srcDirPath, str)
		assert isinstance(destTarFilePath, str)
		chModValue = jk_utils.ChModValue.createN(chModValue)
		chModValueI = None if chModValue is None else chModValue.toInt()
		assert isinstance(log, jk_logging.AbstractLogger)
		assert isinstance(bDebugIncludeExclude, bool)

		# ----------------------------------------------------------------

		with log.descend("Tar-Packing " + repr(srcDirPath) + " ...", logLevel=jk_logging.EnumLogLevel.NOTICE) as log2:
			srcDirPath = os.path.abspath(srcDirPath)
			assert os.path.isdir(srcDirPath)
			destTarFilePath = os.path.abspath(destTarFilePath)

			# --------
			# create a flat list of file and directory names that are to include from srcDirPath

			_selectedEntries = Packer.selectFilesAndDirs(srcDirPath, filesAndDirsToInclude, filesAndDirsToExclude, bDebugIncludeExclude, log2)
			if not _selectedEntries:
				log2.notice("No files and directories to include.")
				return None

			# --------
			# do the packing

			_oldmask = os.umask(0o777 ^ chModValueI) if chModValueI is not None else None
			try:
				TARER.tarDirContents(
					destTarFilePath,
					srcDirPath,
					_selectedEntries,
					log2,
				)
			finally:
				if _oldmask is not None:
					os.umask(_oldmask)
					if os.path.isfile(destTarFilePath):
						os.chmod(destTarFilePath, chModValueI)	# required as tar will not set the execute bit

		# ----------------------------------------------------------------

		return destTarFilePath
	#

	#
	# Pack the contents of the specified directory in a zip file.
	#
	# @param	str srcDirPath						(required) The directory to pack
	# @param	str destZipFilePath					(required) The tar file to create
	# @param	str[] filesAndDirsToInclude			(optional) The file and directorie names (without path!) to include.
	#												If <c>None</c> is specified the source directory is scanned and all
	#												files and directories found there will be included automatically.
	# @param	AbstractLogger log					(required) A logger to write log information to
	#
	@staticmethod
	def zipDirContents(
			*args,
			srcDirPath:str,
			destZipFilePath:str,
			chModValue:typing.Union[int,str,jk_utils.ChModValue,None] = None,
			filesAndDirsToInclude:typing.Iterable[typing.Union[str,re.Match]] = None,
			filesAndDirsToExclude:typing.Iterable[typing.Union[str,re.Match]] = None,
			log:jk_logging.AbstractLogger,
			bDebugIncludeExclude:bool = False,
		) -> typing.Union[str,None]:

		if args:
			raise Exception("Invoke this method with named arguments only!")

		assert isinstance(srcDirPath, str)
		assert isinstance(destZipFilePath, str)
		chModValue = jk_utils.ChModValue.createN(chModValue)
		chModValueI = None if chModValue is None else chModValue.toInt()
		assert isinstance(log, jk_logging.AbstractLogger)
		assert isinstance(bDebugIncludeExclude, bool)

		# ----------------------------------------------------------------

		with log.descend("Zip-Packing " + repr(srcDirPath) + " ...", logLevel=jk_logging.EnumLogLevel.NOTICE) as log2:
			srcDirPath = os.path.abspath(srcDirPath)
			assert os.path.isdir(srcDirPath)
			destZipFilePath = os.path.abspath(destZipFilePath)

			# --------
			# create a flat list of file and directory names that are to include from srcDirPath

			_selectedEntries = Packer.selectFilesAndDirs(srcDirPath, filesAndDirsToInclude, filesAndDirsToExclude, bDebugIncludeExclude, log2)
			if not _selectedEntries:
				log2.notice("No files and directories to include.")
				return None

			# --------
			# unfortunately the zipfile module does no recursive descend on its own. therefore we create a list of files to include into the
			# ZIP file manually.

			filesToIncludeRelPaths = []
			w = jk_dirwalker.DirWalker(emitFilter = jk_dirwalker.StdEmitFilter.newFromDisabled(
					emitRegularFiles = True,
				),
				raiseErrors = True,
			)
			for _selectedEntry in _selectedEntries:
				_absPath = os.path.join(srcDirPath, _selectedEntry)
				if os.path.isfile(_absPath):
					# files
					filesToIncludeRelPaths.append(_selectedEntry)
				elif os.path.isdir(_absPath):
					# directories
					for x in w.scandir(_absPath):
						filesToIncludeRelPaths.append(os.path.join(_selectedEntry, x.relFilePath))
				else:
					# ignore
					pass

			# --------
			# do the packing

			_oldmask = os.umask(0o777 ^ chModValueI) if chModValueI is not None else None
			try:
				with zipfile.PyZipFile(destZipFilePath, "w") as zipf:
					for selectedEntry in filesToIncludeRelPaths:
						assert isinstance(selectedEntry, str)
						localFilePath = os.path.join(srcDirPath, selectedEntry.replace("/", os.path.sep))
						log2.debug("Writing: " + localFilePath + " as " + selectedEntry)
						zipf.write(localFilePath, selectedEntry)
			finally:
				if _oldmask is not None:
					os.umask(_oldmask)
					if os.path.isfile(destZipFilePath):
						os.chmod(destZipFilePath, chModValueI)	# required as tar will not set the execute bit

		# ----------------------------------------------------------------

		return destZipFilePath
	#

	@staticmethod
	def isValidCompression(compression:str) -> bool:
		try:
			Packer._getCompressionParams(compression)
			return True
		except:
			return False
	#

	@staticmethod
	def isAlreadyCompressed(filePath:str) -> bool:
		fileName = os.path.basename(filePath)
		_, fileExt = os.path.splitext(fileName)
		if not fileExt:
			return None

		assert fileExt.startswith(".")
		fileExt = fileExt[1:]

		try:
			Packer._getCompressionParams(fileExt)
			return True
		except:
			return False
	#

	#
	# Pack the contents of the specified directory.
	#
	# @param	str srcDirPath						(required) The directory to pack
	# @param	str destTarFilePath					(required) The file to create
	# @param	str packaging						(required) Either specify "tar" or "zip" here.
	# @param	str[] filesAndDirsToInclude			(optional) The file and directorie names (without path!) to include.
	#												If <c>None</c> is specified the source directory is scanned and all
	#												files and directories found there will be included automatically.
	# @param	AbstractLogger log					(required) A logger to write log information to
	#
	@staticmethod
	def packDirContents(
			*args,
			srcDirPath:str,
			destTarFilePath:str,
			packing:str,
			chModValue:typing.Union[int,str,jk_utils.ChModValue,None] = None,
			filesAndDirsToInclude:typing.Iterable[typing.Union[str,re.Match]] = None,
			filesAndDirsToExclude:typing.Iterable[typing.Union[str,re.Match]] = None,
			log:jk_logging.AbstractLogger,
			bDebugIncludeExclude:bool = False,
		) -> typing.Union[str,None]:

		if packing == "tar":
			return Packer.tarDirContents(
				*args,
				srcDirPath=srcDirPath,
				destTarFilePath=destTarFilePath,
				chModValue=chModValue,
				filesAndDirsToInclude=filesAndDirsToInclude,
				filesAndDirsToExclude=filesAndDirsToExclude,
				log=log,
				bDebugIncludeExclude=bDebugIncludeExclude,
			)
		elif packing == "zip":
			return Packer.zipDirContents(
				*args,
				srcDirPath=srcDirPath,
				destZipFilePath=destTarFilePath,
				chModValue=chModValue,
				filesAndDirsToInclude=filesAndDirsToInclude,
				filesAndDirsToExclude=filesAndDirsToExclude,
				log=log,
				bDebugIncludeExclude=bDebugIncludeExclude,
			)
		else:
			raise Exception("Invalid packaging identifier specified: {}".format(packing))
	#


	#
	# Compress the specified file.
	#
	# @param	str filePath						(required) The path of the file to compress.
	# @param	str toFilePath						(optional) The path of the file to write the compressed data to.
	#												If <c>None</c> a new file path is created with suitable exension based on the
	#												compression type.
	# @param	str toDirPath						(optional) A directory to write the data to. If specified this overrides the
	#												regular directory the resulting file will be created in.
	# @param	str compression						(required) The compression. Valid values are: "gz", "gzip", "bz2", "bzip2", "xz"
	# @param	bool bDeleteOriginal				(required) If <c>True</c> the source file will be deleted after successfull compression.
	# @param	int|str|ChModValue chModValue		(optional) If specified this change-mode value will be used to set the permissions of
	#												the created file.
	# @param	TerminationFlag terminationFlag		(optional) A termination flag for graceful asynchroneous termination.
	# @param	AbstractLogger log					(required) A logger to write log information to
	# @return	str									Returns the path of the result file.
	#
	@staticmethod
	def compressFile(
			*args,
			filePath:str,
			toFilePath:str = None,
			toDirPath:str = None,
			compression:str,
			bDeleteOriginal:bool = False,
			chModValue:typing.Union[int,str,jk_utils.ChModValue,None] = None,
			terminationFlag:jk_utils.TerminationFlag = None,
			log:jk_logging.AbstractLogger,
		) -> SpoolInfo:

		if args:
			raise Exception("Invoke this method with named arguments only!")

		assert isinstance(filePath, str)
		if toFilePath is not None:
			assert isinstance(toFilePath, str)
		if toDirPath is not None:
			assert isinstance(toDirPath, str)
			assert os.path.isdir(toDirPath)
		assert isinstance(compression, str)
		assert isinstance(bDeleteOriginal, bool)
		chModValue = jk_utils.ChModValue.createN(chModValue)
		chModValueI = None if chModValue is None else chModValue.toInt()
		assert isinstance(log, jk_logging.AbstractLogger)

		# ----

		with log.descend("Compressing " + repr(filePath) + " ...", logLevel=jk_logging.EnumLogLevel.NOTICE) as log2:
			filePath = os.path.abspath(filePath)
			assert os.path.isfile(filePath)

			compressionName, compressionFileExt, m = Packer._getCompressionParams(compression)

			log.notice("Packing with " + compressionName + " ...")

			orgFileSize = os.path.getsize(filePath)

			if toFilePath is None:
				toFilePath = filePath + compressionFileExt
			if toDirPath is not None:
				# override already existing directory
				_fileName = os.path.basename(toFilePath)
				toFilePath = os.path.join(toDirPath, _fileName)

			# TODO: check if target file already exists

			tStart = time.time()
			m(filePath, toFilePath, chModValueI, terminationFlag)
			tDuration = time.time() - tStart

			resultFileSize = os.path.getsize(toFilePath)

			if bDeleteOriginal:
				if os.path.isfile(filePath):
					os.unlink(filePath)
			else:
				if not os.path.isfile(filePath):
					raise Exception("Implementation error!")

			return SpoolInfo(filePath, toFilePath, compressionName, compressionFileExt, orgFileSize, resultFileSize, tDuration)
	#

#






















