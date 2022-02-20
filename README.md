jk_packunpack
==========

Introduction
------------

Helper module to create or unpack tar archives, compress or uncompress files.

Information about this module can be found here:

* [github.org](https://github.com/jkpubsrc/python-module-jk-packunpack)
* [pypi.python.org](https://pypi.python.org/pypi/jk_packunpack)

Why this module?
----------------

For a wide variety of applications it would be very convenient to have a simple API for packing/unpacking tar files
and for compressing/uncompressing files with standard algorithms. This is the reason why this module has been
created: To simplify such tasks.

Important note
--------------------------

**ATTENTION:** The API of this module has been changed with the release `0.2022.2.6`.

The reasons for this quite uncommon modification:
* The author was able to improve the API and it does not make much sense to continue with an API of lower quality.
* To the knowledge of the author this module does not have many users anyway.
* An upgrade to the new API is simple.

Upgrading is very simple. For this you have two possibilities:
* If you want to continue using the old API please refer to classes `Packer1` and `Unpacker1` instead of  `Packer` and `Unpacker`.
* If you want to use the more advanced API modify your calls to methods in `Packer` and `Unpacker`. This is a simple step as the new implementations are very similar, you just need to invoke them with named arguments.

Limitations of this module
--------------------------

This module supports the following compression algorithms only:
* `gzip`
* `bzip2`
* `xz`
This compression/uncompression is performed using the standard implementations provided by Python.

Packing and unpacking of `tar` files is supported as well, but only on POSIX operating systems. The reason for this is that
internally the `tar` program is invoked directly, which is not available on non-POSIX operating systems.

How to use this module
----------------------

### Import this module

Please include this module into your application using the following code:

```python
import jk_packunpack
```

For logging import the `jk_logging` module:

```python
import jk_logging
```

### Compress a file

The following example demonstrates how to compress a file with `gzip`:

```python
inputFilePath = "myinputfile.txt"
compression = "gzip"
chmodValue = 0o700

with jk_logging.ConsoleLogger.create() as log:

	resultInfo = jk_packunpack.Packer.compressFile(
		filePath=inputFilePath,
		compression=compression,
		chModValue=chmodValue,
		log=log)

	print(resultInfo.toFilePath)
```

For `chmodValue` you can specify a string such as "`rw-rw----`" or an instance of `jk_utils.ChModValue` as well.

For compression you can specify any of these values: `gz`, `gzip`, `bz2`, `bzip2`, `xz`.

### Uncompress a file

The following example demonstrates how to uncompress a file:

```python
inputFilePath = "myinputfile.txt.gz"
chmodValue = 0o700

with jk_logging.ConsoleLogger.create() as log:

	resultFilePath = jk_packunpack.Unpacker.uncompressFile(
		filePath=inputFilePath,
		bDeleteOriginal=True,
		chModValue=chmodValue,
		log=log)

	print(resultFilePath)
```

For `chmodValue` you can specify a string such as "`rw-rw----`" or an instance of `jk_utils.ChModValue` as well.

Uncompressing will automatically detect the compression format used by inspecting the file extension.

### Pack a directory

The following example demonstrates how to pack the contents of a directory using `tar`:

```python
inputDirPath = "./my/example/dir"
outputTarFilePath = "./my/example-dir.tar"
chmodValue = 0o700

with jk_logging.ConsoleLogger.create() as log:

	jk_packunpack.Packer.tarDirContents(
		srcDirPath=inputDirPath,
		destTarFilePath=outputTarFilePath,
		chModValue=chmodValue,
		log=log)
```

For `chmodValue` you can specify a string such as "`rw-rw----`" or an instance of `jk_utils.ChModValue` as well.

### Unpack a directory

The following example demonstrates how to unpack a `tar` file to a directory:

```python
inputTarFilePath = "./my/example-dir.tar"
outputDirPath = "./my/new/dir"

with jk_logging.ConsoleLogger.create() as log:

	jk_packunpack.Unpacker.untarToDir(
		srcTarFilePath=inputTarFilePath,
		destDirPath=outputDirPath,
		log=log)
```

Contact Information
-------------------

This work is Open Source. This enables you to use this work for free.

Please have in mind this also enables you to contribute. We, the subspecies of software developers, can create great things. But the more collaborate, the more fantastic these things can become. Therefore Feel free to contact the author(s) listed below, either for giving feedback, providing comments, hints, indicate possible collaborations, ideas, improvements. Or maybe for "only" reporting some bugs:

* Jürgen Knauth: pubsrc@binary-overflow.de

License
-------

This software is provided under the following license:

* Apache Software License 2.0



