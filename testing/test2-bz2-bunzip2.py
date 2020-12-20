#!/usr/bin/python3


import os

import jk_utils
import jk_logging
from jk_testing import Assert

from jk_packunpack import *




with jk_logging.wrapMain() as log:

	result = Packer.compressFile2(
		filePath="testdata/myfile.txt",
		toFilePath=None,
		compression="bz2",
		bDeleteOriginal=False,
		chModValue=jk_utils.ChModValue("rwx------"),
		log=log)
	result.dump(printFunc=log.notice)
	Assert.isEqual(result.toFilePath, os.path.abspath("testdata/myfile.txt.bz2"))

	resultFilePath2 = Unpacker.uncompressFile(result.toFilePath, "output2/myfile.txt", False, log)
	Assert.isEqual(resultFilePath2, "output2/myfile.txt")

	log.success("Success.")





