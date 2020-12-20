#!/usr/bin/python3



import jk_logging
from jk_testing import Assert

from jk_packunpack import *




with jk_logging.wrapMain() as log:

	Packer.tarDir("testdata", "output/testdata.tar", log)

	Unpacker.untarToDir("output/testdata.tar", "output2", log)

	log.success("Success.")






