#!/usr/bin/python3


import os
import shutil

import jk_utils
import jk_logging
from jk_testing import Assert

import jk_packunpack




SOURCE_DIR_NAME = "testdata"
SOURCE_FILE_NAME = "myfile.txt"
SOURCE_FILE_NAME_2 = os.path.join("subdir", "myfile2.txt")
FILE_CHMOD = jk_utils.ChModValue("rw-------")
FILE_NAME_SET = set([
	SOURCE_FILE_NAME,
	SOURCE_FILE_NAME + ".gz",
	SOURCE_FILE_NAME + ".bz2",
	SOURCE_FILE_NAME + ".xz",
	SOURCE_FILE_NAME_2,
	"subdir",
])




def _recreateDir(dirPath:str):
	if os.path.isdir(dirPath):
		shutil.rmtree(dirPath, ignore_errors=False)
	os.mkdir(dirPath)
#

def _assertFilesAreEquals(filePathA:str, filePathB:str, log:jk_logging.AbstractLogger):
	with log.descend("Comparing: {} <-> {}".format(repr(filePathA), repr(filePathB)), logLevel=jk_logging.EnumLogLevel.NOTICE) as log2:
		if os.path.isdir(filePathA) and os.path.isdir(filePathB):
			return
		else:
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

	_assertFilesAreEquals(dirAFilePath, dirBFilePath, log)
#

def testPackingUnpacking(
		packing:str,
		inputDirPath:str,
		outputDirPath1:str,
		outputDirPath2:str,
		log:jk_logging.AbstractLogger,
	):

	tarFilePath = jk_packunpack.Packer.packDirContents(
		srcDirPath=inputDirPath,
		destTarFilePath=os.path.join(outputDirPath1, "dirA.tar"),
		packing=packing,
		chModValue=FILE_CHMOD,
		log=log,
	)
	Assert.isEqual(tarFilePath, os.path.join(outputDirPath1, "dirA.tar"))
	_stats = os.stat(tarFilePath, follow_symlinks=False)
	_mod = jk_utils.ChModValue(_stats.st_mode)
	Assert.isEqual(_mod, FILE_CHMOD)
	Assert.isEqual(set(jk_packunpack.Unpacker.listContents(
		filePath=tarFilePath,
		packing=packing,
		log=log,
	)), FILE_NAME_SET)

	ret = jk_packunpack.Unpacker.unpackToDir(
		srcFilePath=tarFilePath,
		destDirPath=outputDirPath2,
		packing=packing,
		log=log,
	)
	Assert.isNone(ret)

	for fileName in FILE_NAME_SET:
		_assertFilesAreEquals(os.path.join(inputDirPath, fileName), os.path.join(outputDirPath2, fileName), log)
#



with jk_logging.wrapMain() as log:

	baseDirPath = os.path.dirname(__file__)
	baseFileName, _ = os.path.splitext(os.path.basename(__file__))

	srcDirPath = os.path.join(baseDirPath, SOURCE_DIR_NAME)
	srcFilePath = os.path.join(srcDirPath, SOURCE_FILE_NAME)
	srcFilePath2 = os.path.join(srcDirPath, SOURCE_FILE_NAME_2)

	dirA = os.path.join(os.getcwd(), baseFileName + "-a")
	_recreateDir(dirA)
	dirB = os.path.join(os.getcwd(), baseFileName + "-b")
	_recreateDir(dirB)
	dirTar1 = os.path.join(os.getcwd(), baseFileName + "-tar1")
	_recreateDir(dirTar1)
	dirTar2 = os.path.join(os.getcwd(), baseFileName + "-tar2")
	_recreateDir(dirTar2)
	dirZip1 = os.path.join(os.getcwd(), baseFileName + "-zip1")
	_recreateDir(dirZip1)
	dirZip2 = os.path.join(os.getcwd(), baseFileName + "-zip2")
	_recreateDir(dirZip2)

	dirAFilePath = os.path.join(dirA, SOURCE_FILE_NAME)
	shutil.copyfile(srcFilePath, dirAFilePath)
	dirAFilePath2 = os.path.join(dirA, SOURCE_FILE_NAME_2)
	os.mkdir(os.path.dirname(dirAFilePath2))
	shutil.copyfile(srcFilePath2, dirAFilePath2)

	#----

	testCompressionUncompression("gz", dirA, dirB, log)

	testCompressionUncompression("bz2", dirA, dirB, log)

	testCompressionUncompression("xz", dirA, dirB, log)

	#----

	testPackingUnpacking("tar", dirA, dirTar1, dirTar2, log)

	testPackingUnpacking("zip", dirA, dirZip1, dirZip2, log)

	#----

	log.success("Success.")





