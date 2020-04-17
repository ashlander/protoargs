from conans import ConanFile, CMake, tools
import os


class ProtoconfConan(ConanFile):
    name = "protoargs"
    version = "0.1.0"
    license = "BSD 2-Clause License"
    author = "Andrii Zhuk <andrewzhuk@gmail.com>"
    url = "<Package recipe repository url here, for issues about the package>"
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
    build_requires = "boost/1.69.0@conan/stable", "gtest/1.8.1@bincrafters/stable"
    requires = "protobuf/3.6.1@bincrafters/stable", "protoc_installer/3.6.1@bincrafters/stable"


    #def source(self): # TODO

    def build(self):
        cmake = CMake(self)

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

