#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conans import ConanFile, CMake, tools
import os


class LibnameConan(ConanFile):
    name = "cassandra"
    version = "2.11.0"
    description = "Cassandra C++ Driver"
    url = "http://bitbucket-idb.nyoffice.tradeweb.com:7990/projects/TP/repos/conan-cassandra"
    homepage = "https://github.com/datastax/cpp-driver"

    # Indicates License type of the packaged library
    license = "Apache"

    # Remove following lines if the target lib does not use cmake.
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake"

    # Options may need to change depending on the packaged library.
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = "shared=False", "fPIC=True"

    # Custom attributes for Bincrafters recipe conventions
    source_subfolder = "source_subfolder"
    build_subfolder = "build_subfolder"

    requires = (
        "libuv/1.25.0@bincrafters/stable",
        "OpenSSL/1.0.2o@conan/stable",
    )

    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC

    def source(self):
        source_url = " https://codeload.github.com/datastax/cpp-driver"
        extracted_name = f"cpp-driver-{self.version}"
        tools.get("{0}/tar.gz/{1}".format(source_url, self.version), filename=f"{extracted_name}.tar.gz")
        os.rename(extracted_name, self.source_subfolder)

    def configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions['CASS_BUILD_STATIC'] = not self.options.shared
        cmake.definitions['CASS_BUILD_SHARED'] = self.options.shared
        cmake.definitions['LIBUV_ROOT_DIR'] = self.deps_cpp_info["libuv"].rootpath
        cmake.definitions['OPENSSL_ROOT_DIR'] = self.deps_cpp_info["OpenSSL"].rootpath
        if self.settings.os != 'Windows':
            cmake.definitions['CMAKE_POSITION_INDEPENDENT_CODE'] = self.options.fPIC
        cmake.configure()
        return cmake

    def build(self):
        tools.replace_in_file(os.path.join(self.source_subfolder, "CMakeLists.txt"),
                              "CMAKE_SOURCE_DIR", "CMAKE_CURRENT_SOURCE_DIR")
        cmake = self.configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE.txt", dst="license", src=self.source_subfolder)
        cmake = self.configure_cmake()
        cmake.install()
        # If the CMakeLists.txt has a proper install method, the steps below may be redundant
        # If so, you can just remove the lines below
        include_folder = os.path.join(self.source_subfolder, "include")
        self.copy(pattern="*", dst="include", src=include_folder)
        self.copy(pattern="*.dll", dst="bin", keep_path=False)
        self.copy(pattern="*.lib", dst="lib", keep_path=False)
        self.copy(pattern="*.a", dst="lib", keep_path=False)
        self.copy(pattern="*.so*", dst="lib", keep_path=False)
        self.copy(pattern="*.dylib", dst="lib", keep_path=False)

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.os == "Windows":
            self.cpp_info.libs.extend(["ws2_32", "psapi", "iphlpapi", "UserEnv"])
        else:
            self.cpp_info.libs.extend(["pthread", "rt"])
