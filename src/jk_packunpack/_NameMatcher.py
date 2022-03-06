


import os
import typing
import re

import jk_typing
import jk_logging
import jk_json
import jk_prettyprintobj





class _NameMatcher(object):

	################################################################################################################################
	## Constructor
	################################################################################################################################

	#
	# Constructor method.
	#
	# @param		(str,Pattern)[] namePatterns			(optional) A list of names or name patterns
	# @param		bool bDefaultIfNone						(optional) What to return if no named pattern has been given: True or False
	#
	def __init__(self, namePatterns:typing.Iterable[typing.Union[str,re.Pattern]] = None, bDefaultIfNone:bool = True) -> None:
		if namePatterns is None:
			self.__bReturnImmediately = True
			self.__names = None
			self.__namePatterns = None

		else:
			self.__bReturnImmediately = False
			self.__names = []
			self.__namePatterns = []
			for x in namePatterns:
				if isinstance(x, str):
					self.__names.append(x)
				elif isinstance(x, re.Pattern):
					self.__namePatterns.append(x)
				else:
					raise TypeError(repr(type(x)))
			self.__names = set(self.__names)

		self.__bDefaultIfNone = bDefaultIfNone
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

	def match(self, name:str) -> bool:
		assert isinstance(name, str)

		if self.__bReturnImmediately:
			return self.__bDefaultIfNone

		if name in self.__names:
			return True

		for x in self.__namePatterns:
			assert isinstance(x, re.Pattern)
			m = x.match(name)
			if m:
				return True

		return False
	#

	@jk_typing.checkFunctionSignature()
	def matchDebug(self, name:str, posActivity:str, negActivity:str, log:jk_logging.AbstractLogger) -> bool:
		if self.__bReturnImmediately:
			log.debug("{}, always True -> {}".format(repr(name), posActivity if self.__bDefaultIfNone else negActivity))
			return self.__bDefaultIfNone

		if name in self.__names:
			log.debug("{}, in {} -> {}".format(repr(name), self.__names, posActivity))
			return True

		for x in self.__namePatterns:
			assert isinstance(x, re.Pattern)
			m = x.match(name)
			if m:
				log.debug("{}, matches pattern {} -> {}".format(repr(name), x, posActivity))
				return True

		log.debug("{}, does not match -> {}".format(repr(name), negActivity))
		return False
	#

#





