#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conans import ConanFile, CMake, tools
import os


class CassandraConan(ConanFile):
    name = "cassandra"
    version = "2.11.0"
    description = "Cassandra C++ Driver"
    url = "http://bitbucket-idb.nyoffice.tradeweb.com:7990/projects/TP/repos/conan-cassandra"
    homepage = "https://github.com/datastax/cpp-driver"
    license = "Apache"

    exports = ["LICENSE.md"]
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake"

    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = "shared=False", "fPIC=True"

    source_subfolder = "source_subfolder"

    requires = (
        "libuv/1.27.0@bincrafters/stable",
        "OpenSSL/1.0.2o@conan/stable",
    )

    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC

    def configure(self):
        self.options["libuv"].shared = self.options.shared

    def source(self):
        source_url = " https://codeload.github.com/datastax/cpp-driver"
        extracted_name = 'cpp-driver-%s' % self.version
        tools.get("{0}/tar.gz/{1}".format(source_url, self.version), filename="%s.tar.gz" % extracted_name)
        os.rename(extracted_name, self.source_subfolder)

    def configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions['CASS_BUILD_STATIC'] = not self.options.shared
        cmake.definitions['CASS_BUILD_SHARED'] = self.options.shared
        cmake.definitions['LIBUV_ROOT_DIR'] = self.deps_cpp_info["libuv"].rootpath
        if self.settings.os == 'Windows' and self.options.shared:
            if self.settings.compiler == 'gcc':
                libuv_library = os.path.join(self.deps_cpp_info["libuv"].rootpath, "bin", "libuv.dll")
            else:
                libuv_library = os.path.join(self.deps_cpp_info["libuv"].rootpath, "lib", "libuv.dll.lib")
            cmake.definitions['LIBUV_LIBRARY'] = libuv_library
        cmake.definitions['OPENSSL_ROOT_DIR'] = self.deps_cpp_info["OpenSSL"].rootpath
        if self.settings.os != 'Windows':
            cmake.definitions['CMAKE_POSITION_INDEPENDENT_CODE'] = self.options.fPIC
        cmake.configure()
        return cmake

    def build(self):
        tools.replace_in_file(os.path.join(self.source_subfolder, "CMakeLists.txt"),
                              "CMAKE_SOURCE_DIR", "CMAKE_CURRENT_SOURCE_DIR")
        if self.settings.os == 'Windows' and self.settings.compiler == 'gcc' and self.options.shared:
            tools.replace_in_file(os.path.join(self.source_subfolder, "cmake", "modules", "CppDriver.cmake"),
                                  "if(WIN32)\n      install", "if(WIN32 AND NOT MINGW)\n      install")
            tools.replace_in_file(os.path.join(self.source_subfolder, "cmake", "modules", "CppDriver.cmake"),
                                  'elseif("${CMAKE_CXX_COMPILER_ID}" STREQUAL "GNU")',
                                  'elseif("${CMAKE_CXX_COMPILER_ID}" STREQUAL "GNU")\n' +
                                  'set(CASS_LIBS ${CASS_LIBS} iphlpapi psapi wsock32 crypt32 ws2_32 userenv)')
        cmake = self.configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE.txt", dst="license", src=self.source_subfolder)
        cmake = self.configure_cmake()
        cmake.install()

    def package_info(self):
        if self.options.shared:
            self.cpp_info.libs = ['cassandra']
        else:
            self.cpp_info.libs = ['cassandra_static']
        if self.settings.os == "Windows":
            self.cpp_info.libs.extend(["ws2_32", "psapi", "iphlpapi", "UserEnv"])
            if not self.options.shared:
                self.cpp_info.defines = ["CASS_STATIC"]
        elif self.settings.os == "Linux":
            self.cpp_info.libs.extend(["pthread", "rt"])
