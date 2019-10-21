Logger Source
=============

Is taken from **CppMT** project https://github.com/gnebehay/CppMT

It was modified to output more information, like thread id, path and line number in code.

Other modification - if LOG() entry is not used now (event with DEBUG4 level), but may be used later, and you do not want to comment out it (some people as myself like to remove it as garbage), use logIGNORE log level instead.
