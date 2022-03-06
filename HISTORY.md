* 2021-01-11
	* Added `TerminationFlag`, so that processing can be interrupted
	* Added `spoolStream()`
	* Added `@deprecated` to currently obsolete `compressFile()` in `Packer`

* 2022-02-04
	* Refactoring
	* Updated `README.md`
	* Added documentation to various methods
	* Added `tarDirContents()`

* 2022-02-06
	* Improved chmod handling in `Packer`
	* Old `Packer` stored as `Packer1`
	* Old `Unpacker` stored as `Unpacker1`
	* Added more methods to `Packer`
	* Unit testing
	* Added `FileUncompressionGuess`
	* Improved documentation

* 2022-02-20
	* Reduced log level from INFO to NOTICE

* 2022-02-25
	* Fixed wrong function invoked in case of error
	* Moved to Python native tar support for compatibility to non-posix operating systems

* 2022-03-01
	* Improved inclusion/exclusion of files and directories for tar
	* Added duration time measurement

* 2022-03-06
	* Added support for packing/unpacking ZIP files


