#!/usr/bin/python3


import os

import jk_utils
import jk_logging
from jk_testing import Assert

from jk_packunpack import *




with jk_logging.wrapMain() as log:

	terminationFlag = jk_utils.TerminationFlag()

	result = Packer.compressFile2(
		filePath="testdata/myfile.txt",
		toFilePath=None,
		compression="gz",
		bDeleteOriginal=False,
		chModValue=jk_utils.ChModValue("rwx------"),
		terminationFlag=terminationFlag,
		log=log)
	Assert.isEqual(result.toFilePath, os.path.abspath("testdata/myfile.txt.gz"))

	resultFilePath2 = Unpacker.uncompressFile(
		filePath=result.toFilePath,
		toFilePath="output2/myfile.txt",
		bDeleteOriginal=False,
		terminationFlag=terminationFlag,
		log=log)
	Assert.isEqual(resultFilePath2, "output2/myfile.txt")

	log.success("Success.")





