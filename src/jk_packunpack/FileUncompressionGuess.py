


import os
import typing
import collections





class FileUncompressionGuess(object):

	################################################################################################################################
	## Constructor
	################################################################################################################################

	#
	# Constructor method.
	#
	def __init__(self, compression:str, toFilePath:str):
		assert isinstance(compression, str)
		assert isinstance(toFilePath, str)

		self.__compression = compression
		self.__toFilePath = toFilePath
		self.__toFileName = os.path.basename(toFilePath)
	#

	################################################################################################################################
	## Public Properties
	################################################################################################################################

	@property
	def compression(self) -> str:
		return self.__compression
	#

	@property
	def toFilePath(self) -> str:
		return self.__toFilePath
	#

	@property
	def toFileName(self) -> str:
		return self.__toFileName
	#

	################################################################################################################################
	## Helper Methods
	################################################################################################################################

	################################################################################################################################
	## Public Methods
	################################################################################################################################

	def __len__(self):
		return 2
	#

	def __getitem__(self, ii):
		if ii == 0:
			return self.__compression
		elif ii == 1:
			return self.__toFilePath
		else:
			raise IndexError()
	#

	def toTuple2(self) -> tuple:
		return (self.__compression, self.__toFilePath)
	#

#






