

import os
import typing
import tarfile

import jk_typing
import jk_utils
import jk_logging
import jk_json
import jk_prettyprintobj





class PythonNativeTar(object):

	################################################################################################################################
	## Constructor
	################################################################################################################################

	#
	# Constructor method.
	#
	@jk_typing.checkFunctionSignature()
	def __init__(self):
		pass
	#

	################################################################################################################################
	## Public Properties
	################################################################################################################################

	################################################################################################################################
	## Helper Methods
	################################################################################################################################

	################################################################################################################################
	## Public Methods
	################################################################################################################################

	#
	# Tar the contents of a directory.
	# An exception is raised on error.
	# Before an error is raised the logger may be used to provide a more detailed error message.
	#
	# @param	str absDestTarFilePath				The (absolute) output file path
	# @param	str absSrcDirPath					The (absolute) source directory that contains all files and subdirectories to include
	# @param	str[] filesAndDirsToInclude			The files and directory names to include
	# @param	AbstractLogger log					The logger to use (if there is anything to log, e.g. error information)
	# @param	Callable[TarInfo]:TarInfo filter	(optional) An optional filter function that is directly passed on to the
	#												python tarfile API. This filter function receives a TarInfo record of
	#												the current file to pack and can either return the same or a modified
	#												version of the TarInfo record or None to indicate that
	#												this entry should be excluded.
	#
	@jk_typing.checkFunctionSignature()
	def tarDirContents(
			self,
			absDestTarFilePath:str,
			absSrcDirPath:str,
			filesAndDirsToInclude:typing.List[str],
			log:jk_logging.AbstractLogger,
			*,
			filter:typing.Callable[[tarfile.TarInfo],typing.Union[tarfile.TarInfo,None]] = None,
		) -> None:

		with tarfile.open(absDestTarFilePath, "w") as tarOut:
			for fileName in filesAndDirsToInclude:
				srcFilePath = os.path.join(absSrcDirPath, fileName)
				tarOut.add(srcFilePath, fileName, recursive=True, filter=filter)
	#

	def listTarContents(
			self,
			absTarFilePath:str,
			log:jk_logging.AbstractLogger,
		) -> typing.List[str]:

		ret = []
		with tarfile.open(absTarFilePath, "r") as tarIn:
			for tarinfo in tarIn:
				ret.append(tarinfo.name)

		return ret
	#

	@jk_typing.checkFunctionSignature()
	def untarToDir(self,
			absTarFilePath:str,
			absDestDirPath:str,
			log:jk_logging.AbstractLogger,
		) -> None:

		if not os.path.isdir(absDestDirPath):
			os.makedirs(absDestDirPath)

		with tarfile.open(absTarFilePath, "r") as tarIn:
			tarIn.extractall(absDestDirPath)
	#

#






