#include <fstream>
#include <iostream>
#include <string>

static std::string compiler_id() {
#if defined(_MSC_VER)
    return "MSVC";
#elif defined(__clang__)
    return "Clang";
#elif defined(__GNUC__)
    return "GCC";
#else
    return "Unknown";
#endif
}

int main(int argc, char** argv) {
    if (argc != 2) {
        std::cerr << "usage: rcs026_toolchain_probe <output.json>\n";
        return 2;
    }
    long long compiler_version = 0;
#if defined(_MSC_VER)
    compiler_version = _MSC_VER;
#elif defined(__clang_major__)
    compiler_version = __clang_major__ * 10000LL + __clang_minor__ * 100LL + __clang_patchlevel__;
#elif defined(__GNUC__)
    compiler_version = __GNUC__ * 10000LL + __GNUC_MINOR__ * 100LL + __GNUC_PATCHLEVEL__;
#endif
    std::ofstream out(argv[1], std::ios::binary);
    if (!out) {
        std::cerr << "cannot open output\n";
        return 3;
    }
    out << "{\n"
        << "  \"schema\": \"rcs-026-toolchain-probe/1.0\",\n"
        << "  \"compiler_id\": \"" << compiler_id() << "\",\n"
        << "  \"compiler_version_numeric\": " << compiler_version << ",\n"
        << "  \"cplusplus\": " << static_cast<long long>(__cplusplus) << ",\n"
        << "  \"probe_value\": 26026\n"
        << "}\n";
    return 0;
}
