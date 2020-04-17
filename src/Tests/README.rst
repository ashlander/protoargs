Building Tests with Conan (Recomended)
======================================

Build dependencies:

* conan
* ctags (optional)

.. code:: bash

     mkdir debug
     cd debug && conan install -s build_type=Debug ../.
     conan build ../.

..

Building Tests extras
=====================

**-o tags=True**        Tags file generation on

**-o codecov=True**     Enable code coverage

**-o clangcheck=True**  Enable clang static analyzer build

**-o asancheck=True**   Enable build with Address Sanitizer

**-o tsancheck=True**   Enable build with Thread Sanitizer

**-o usancheck=True**   Enable build with Undefined Sanitizer

Building Tests without Conan
============================

Install dependencies:

* protobuf with protoc
* gtest
* ctags (optional)

See conanfile.py for more information on versions

Building Tests Debug
====================

Go inside **src** directory.

.. code:: bash

    cmake -DWITH_CONAN=OFF -DCMAKE_BUILD_TYPE=Debug CMakeLists.txt

    make
..

Building Tests Release
======================

Go inside **src** directory.

.. code:: bash

    cmake -DWITH_CONAN=OFF -DCMAKE_BUILD_TYPE=Release CMakeLists.txt

    make

..

Building extras
===============

**-DWITH_CONAN=ON**     [default = **ON**]     if need build and package with conan

**-DWITH_TAGS=ON**      [default = **OFF**]    if need tags file generation

**-DWITH_CODECOV=ON**   [default = **OFF**]    Enable code coverage

**-DWITH_ASAN=ON**      [default = **OFF**]    Enable build with Address Sanitizer

**-DWITH_TSAN=ON**      [default = **OFF**]    Enable build with Thread Sanitizer

**-DWITH_USAN=ON**      [default = **OFF**]    Enable build with Undefined Sanitizer

