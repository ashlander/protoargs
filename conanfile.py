from conans import ConanFile, CMake, tools
import os

class ProtoconfConan(ConanFile):
    name = "protoargs"
    version = "0.1.0"
    license = "BSD 2-Clause License"
    author = "Andrii Zhuk <andrewzhuk@gmail.com>"
    url = "https://github.com/ashlander/protoargs.git"
    description = "Code generated C++11 command line option parser, based on cxxopts and protobuf configuration"
    topics = ("bsw", "args")
    settings = "os", "compiler", "build_type", "arch"
    options = {"codecov": [True, False]
            , "clangcheck": [True, False]
            , "asancheck": [True, False]
            , "tsancheck": [True, False]
            , "usancheck": [True, False]
            , "tags": [True,False]}
    default_options = "codecov=False" , "clangcheck=False" , "asancheck=False" , "tsancheck=False" , "usancheck=False", "tags=False"
    generators = "cmake"
    build_requires = "boost/1.69.0", "gtest/[>=1.8.1]"
    requires = "protobuf/[>=3.6.1]"

    def isCI(self):
        try:
            ci = os.environ['CI_PIPELINE_ID']
        except Exception as e:
            ci = ""
        return ci != ""

    def source(self):
        # skip code download inside CI, just make a link
        if self.isCI(): 
            self.run("ln -s /builds/root/protoargs/src src")
        else:
            self.run("git clone https://github.com/ashlander/protoargs.git")
            self.run("ln -s protoargs/src src")


    def build(self):
        cmake = CMake(self)

        cmake.definitions["WITH_CONAN"] = "ON"

        if self.options.codecov == "True":
            cmake.definitions["WITH_CODECOV"] = "ON"

        if self.options.asancheck == "True":
            cmake.definitions["WITH_ASAN"] = "ON"

        if self.options.tsancheck == "True":
            cmake.definitions["WITH_TSAN"] = "ON"

        if self.options.usancheck == "True":
            cmake.definitions["WITH_USAN"] = "ON"

        if self.options.tags == "True":
            cmake.definitions["WITH_TAGS"] = "ON"

        cmake.configure(source_folder="src")

        cmake.build()

    def package(self):
        self.copy("*.py", dst="bin", keep_path=False)

    def package_info(self):
        self.cpp_info.libs = ["protoargs"]

