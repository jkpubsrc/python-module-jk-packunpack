



import jk_prettyprintobj





class SpoolInfo(jk_prettyprintobj.DumpMixin):

	################################################################################################################################
	## Constructor
	################################################################################################################################

	def __init__(self, fromFilePath:str, toFilePath:str, compressionName:str, compressionFileExt:str, fromFileSize:int, toFileSize:int):
		self.fromFilePath = fromFilePath
		self.toFilePath = toFilePath
		self.compressionName = compressionName
		self.compressionFileExt = compressionFileExt
		self.fromFileSize = fromFileSize
		self.toFileSize = toFileSize
	#

	################################################################################################################################
	## Public Properties
	################################################################################################################################

	@property
	def compressionRatio(self) -> float:
		if self.fromFileSize == 0:
			return 0
		else:
			return self.toFileSize / self.fromFileSize
	#

	@property
	def compressionRatioStr(self) -> str:
		if self.fromFileSize == 0:
			return "-"
		else:
			return str(round(100 * self.toFileSize / self.fromFileSize, 2)) + "%"
	#

	@property
	def decompressionRatio(self) -> float:
		if self.toFileSize == 0:
			return 0
		else:
			return self.fromFileSize / self.toFileSize
	#

	################################################################################################################################
	## Helper Methods
	################################################################################################################################

	def _dumpVarNames(self) -> list:
		return [
			"fromFilePath",
			"toFilePath",
			"compressionName",
			"compressionFileExt",
			"fromFileSize",
			"toFileSize",
			"compressionRatio",
			"decompressionRatio",
		]
	#

	################################################################################################################################
	## Public Methods
	################################################################################################################################

#



