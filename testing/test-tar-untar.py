#!/usr/bin/python3



import jk_logging
from jk_testing import Assert

from jk_packunpack import *




log = jk_logging.ConsoleLogger.create(logMsgFormatter=jk_logging.COLOR_LOG_MESSAGE_FORMATTER)



Packer.tarDir("testdata", "output/testdata.tar", log)

Unpacker.untarToDir("output/testdata.tar", "output2", log)

log.success("Success.")






