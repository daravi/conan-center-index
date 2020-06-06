from conans import ConanFile, CMake, tools
import os


class PugiXmlConan(ConanFile):
    name = "pugixml"
    version = "1.10"
    description = "Light-weight, simple and fast XML parser for C++ with XPath support"
    topics = ("xml-parser", "xpath", "xml", "dom")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://pugixml.org/"
    license = "MIT"
    generators = "cmake"
    settings = ("os", "arch", "compiler", "build_type")
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "header_only": [True, False],
        "wchar_mode": [True, False],
        "no_exceptions": [True, False]
    }
    default_options = {
        'shared': False,
        'fPIC': True,
        'header_only': False,
        'wchar_mode': False,
        'no_exceptions': False
    }

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC

    def configure(self):
        if self.options.header_only:
            if self.settings.os != 'Windows':
                del self.options.fPIC
            del self.options.shared
            self.settings.clear()

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename(self.name + "-" + self.version, self._source_subfolder)

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["BUILD_TESTS"] = False
        if self.settings.os == 'Windows' and self.settings.compiler == 'Visual Studio':
            cmake.definitions['CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS'] = self.options.shared
        cmake.configure(
            source_folder=self._source_subfolder,
            build_folder=self._build_subfolder
        )
        return cmake

    def build(self):
        header_file = os.path.join(self._source_subfolder, "src", "pugiconfig.hpp")
        if self.options.wchar_mode:
            tools.replace_in_file(header_file, "// #define PUGIXML_WCHAR_MODE", '''#define PUGIXML_WCHAR_MODE''')
        if self.options.no_exceptions:
            tools.replace_in_file(header_file, "// #define PUGIXML_NO_EXCEPTIONS", '''#define PUGIXML_NO_EXCEPTIONS''')

        if self.options.header_only:
            tools.replace_in_file(header_file, "// #define PUGIXML_HEADER_ONLY", '''#define PUGIXML_HEADER_ONLY''')
        else:
            cmake = self._configure_cmake()
            cmake.build()

    def package(self):
        readme_contents = tools.load(os.path.join(self._source_subfolder, "readme.txt"))
        license_contents = readme_contents[readme_contents.find("This library is"):]
        tools.save(os.path.join(self.package_folder, "licenses", "LICENSE"), license_contents)
        if self.options.header_only:
            source_dir = os.path.join(self._source_subfolder, "src")
            self.copy(pattern="*", dst="include", src=source_dir)
        else:
            cmake = self._configure_cmake()
            cmake.install()
            tools.rmdir(os.path.join(self.package_folder, 'lib', 'cmake'))
            tools.rmdir(os.path.join(self.package_folder, 'lib', 'pkgconfig'))

    def package_info(self):
        self.output.info(os.path.join(self.package_folder, "lib", "cmake", self.name))
        if self.options.header_only:
            self.info.header_only()
        else:
            self.cpp_info.libs = tools.collect_libs(self)
