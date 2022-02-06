#!/usr/bin/python3


import os
import shutil

import jk_utils
import jk_logging
from jk_testing import Assert

import jk_packunpack




SOURCE_DIR_NAME = "testdata"
SOURCE_FILE_NAME = "myfile.txt"
FILE_CHMOD = jk_utils.ChModValue("rw-------")




def _recreateDir(dirPath:str):
	if os.path.isdir(dirPath):
		shutil.rmtree(dirPath, ignore_errors=False)
	os.mkdir(dirPath)
#

def _assertFilesAreEquals(filePathA:str, filePathB:str):
	with open(filePathA, "rb") as fin:
		contentsA = fin.read()
	with open(filePathB, "rb") as fin:
		contentsB = fin.read()
	Assert.isEqual(contentsA, contentsB)
#

def testCompressionUncompression(
		compression:str,
		dirAPath:str,
		dirBPath:str,
		log:jk_logging.AbstractLogger,
	):

	dirAFilePath = os.path.join(dirAPath, SOURCE_FILE_NAME)

	result = jk_packunpack.Packer.compressFile(
		filePath=dirAFilePath,
		compression=compression,
		chModValue=FILE_CHMOD,
		log=log)
	Assert.isEqual(result.toFilePath, os.path.join(dirA, SOURCE_FILE_NAME + "." + compression))
	_stats = os.stat(result.toFilePath, follow_symlinks=False)
	_mod = jk_utils.ChModValue(_stats.st_mode)
	Assert.isEqual(_mod, FILE_CHMOD)
	dirAFilePathXZ = result.toFilePath

	dirBFilePath = os.path.join(dirBPath, SOURCE_FILE_NAME)

	dirBFilePath2 = jk_packunpack.Unpacker.uncompressFile(
		filePath=dirAFilePathXZ,
		toFilePath=dirBFilePath,
		chModValue=FILE_CHMOD,
		log=log)
	Assert.isEqual(dirBFilePath2, dirBFilePath)
	_stats = os.stat(dirBFilePath2, follow_symlinks=False)
	_mod = jk_utils.ChModValue(_stats.st_mode)
	Assert.isEqual(_mod, FILE_CHMOD)

	_assertFilesAreEquals(dirAFilePath, dirBFilePath)
#




with jk_logging.wrapMain() as log:

	baseDirPath = os.path.dirname(__file__)
	baseFileName, _ = os.path.splitext(os.path.basename(__file__))

	srcDirPath = os.path.join(baseDirPath, SOURCE_DIR_NAME)
	srcFilePath = os.path.join(srcDirPath, SOURCE_FILE_NAME)

	dirA = os.path.join(os.getcwd(), baseFileName + "-a")
	_recreateDir(dirA)
	dirB = os.path.join(os.getcwd(), baseFileName + "-b")
	_recreateDir(dirB)
	dirC = os.path.join(os.getcwd(), baseFileName + "-c")
	_recreateDir(dirC)

	dirAFilePath = os.path.join(dirA, SOURCE_FILE_NAME)
	shutil.copyfile(srcFilePath, dirAFilePath)

	#----

	testCompressionUncompression("gz", dirA, dirB, log)

	testCompressionUncompression("bz2", dirA, dirB, log)

	testCompressionUncompression("xz", dirA, dirB, log)

	#----

	dirBTarFilePath = jk_packunpack.Packer.tarDirContents(
		srcDirPath=dirA,
		destTarFilePath=os.path.join(dirB, "dirA.tar"),
		chModValue=FILE_CHMOD,
		log=log,
	)
	Assert.isEqual(dirBTarFilePath, os.path.join(dirB, "dirA.tar"))
	_stats = os.stat(dirBTarFilePath, follow_symlinks=False)
	_mod = jk_utils.ChModValue(_stats.st_mode)
	Assert.isEqual(_mod, FILE_CHMOD)

	ret = jk_packunpack.Unpacker.untarToDir(
		srcTarFilePath=dirBTarFilePath,
		destDirPath=dirC,
		log=log,
	)
	Assert.isNone(ret)

	_assertFilesAreEquals(os.path.join(dirA, SOURCE_FILE_NAME), os.path.join(dirC, SOURCE_FILE_NAME))
	_assertFilesAreEquals(os.path.join(dirA, SOURCE_FILE_NAME + ".gz"), os.path.join(dirC, SOURCE_FILE_NAME + ".gz"))
	_assertFilesAreEquals(os.path.join(dirA, SOURCE_FILE_NAME + ".bz2"), os.path.join(dirC, SOURCE_FILE_NAME + ".bz2"))
	_assertFilesAreEquals(os.path.join(dirA, SOURCE_FILE_NAME + ".xz"), os.path.join(dirC, SOURCE_FILE_NAME + ".xz"))

	#----

	log.success("Success.")





