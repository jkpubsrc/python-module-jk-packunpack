#!/usr/bin/python3


import os

import jk_logging
from jk_testing import Assert

from jk_packunpack import *




with jk_logging.wrapMain() as log:

	resultFilePath = Packer.compressFile("testdata/myfile.txt", "bz2", False, None, log)
	Assert.isEqual(resultFilePath, os.path.abspath("testdata/myfile.txt.bz2"))

	resultFilePath2 = Unpacker.uncompressFile(resultFilePath, "output2/myfile.txt", False, None, log)
	Assert.isEqual(resultFilePath2, "output2/myfile.txt")

	log.success("Success.")





