

import os
import typing
import tarfile

import jk_typing
import jk_utils
import jk_logging
import jk_json
import jk_prettyprintobj
import jk_simpleexec





class PosixExternalTar(object):

	_TAR_PATH = "/bin/tar"

	################################################################################################################################
	## Constructor
	################################################################################################################################

	#
	# Constructor method.
	#
	@jk_typing.checkFunctionSignature()
	def __init__(self):
		assert os.path.isfile(PosixExternalTar._TAR_PATH)
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
	# @param	str absDestTarFilePath			The (absolute) output file path
	# @param	str absSrcDirPath				The (absolute) source directory that contains all files and subdirectories to include
	# @param	str[] filesAndDirsToInclude		The files and directory names to include
	# @param	AbstractLogger log				The logger to use (if there is anything to log, e.g. error information)
	#
	@jk_typing.checkFunctionSignature()
	def tarDirContents(self,
			absDestTarFilePath:str,
			absSrcDirPath:str,
			filesAndDirsToInclude:typing.List[str],
			log:jk_logging.AbstractLogger,
		) -> None:

		log.notice("Invoking " + PosixExternalTar._TAR_PATH + " ...")
		cmdResult = jk_simpleexec.invokeCmd2(
			cmdPath = PosixExternalTar._TAR_PATH,
			cmdArgs = [
					"-cf",
					absDestTarFilePath
				] + filesAndDirsToInclude,
			workingDirectory = absSrcDirPath,
		)

		if cmdResult.returnCode != 0:
			cmdResult.dump(printFunc=log.error)
			raise Exception("Failed to run 'tar'!")
	#

	@jk_typing.checkFunctionSignature()
	def listTarContents(self,
			absTarFilePath:str,
			log:jk_logging.AbstractLogger,
		) -> typing.List[str]:

		log.notice("Invoking " + PosixExternalTar._TAR_PATH + " ...")
		cmdResult = jk_simpleexec.invokeCmd2(
			cmdPath = PosixExternalTar._TAR_PATH,
			cmdArgs = [
				"-tf",
				absTarFilePath
			],
		)

		if cmdResult.returnCode != 0:
			cmdResult.dump(printFunc=log.error)
			raise Exception("Failed to run 'tar'!")

		return cmdResult.stdOutLines
	#

	@jk_typing.checkFunctionSignature()
	def untarToDir(self,
			absTarFilePath:str,
			absDestDirPath:str,
			log:jk_logging.AbstractLogger,
		) -> None:

		if not os.path.isdir(absDestDirPath):
			os.makedirs(absDestDirPath)

		log.notice("Invoking " + PosixExternalTar._TAR_PATH + " ...")
		cmdResult = jk_simpleexec.invokeCmd2(
			cmdPath = PosixExternalTar._TAR_PATH,
			cmdArgs = [
					"-xf",
					absTarFilePath,
					"-C",
					absDestDirPath
				],
			workingDirectory = absDestDirPath,
		)

		if cmdResult.returnCode != 0:
			cmdResult.dump(printFunc=log.error)
			raise Exception("Failed to run 'tar'!")
	#

#






