project(cmake_wrapper)

include(conanbuildinfo.cmake)
conan_basic_setup()

if (MINGW)
    add_compile_options(-Wno-unknown-pragmas -Wno-format -Wno-cpp)
endif()

add_subdirectory("source_subfolder")
