#include <common.hpp>
#include <iostream>
#include <orm/version.hpp>
#include <redis.hpp>
#include <tabulate.hpp>

#ifndef GIT_SHASH
#define GIT_SHASH "unknown"
#endif

#define STRINGIFY_(x) #x
#define STRINGIFY(x) STRINGIFY_(x)

#define NLOHMANN_JSON_VERSION_STRING                                           \
  STRINGIFY(NLOHMANN_JSON_VERSION_MAJOR)                                       \
  "." STRINGIFY(NLOHMANN_JSON_VERSION_MINOR) "." STRINGIFY(                    \
      NLOHMANN_JSON_VERSION_PATCH)

#define HIREDIS_VERSION_STRING                                                 \
  STRINGIFY(HIREDIS_MAJOR)                                                     \
  "." STRINGIFY(HIREDIS_MINOR) "." STRINGIFY(HIREDIS_PATCH)

using namespace tabulate;

void showVersions() {
  Table vtable;
  vtable.add_row({"Component", "Version"});
  vtable.add_row({"Application", GIT_SHASH});
  vtable.add_row({"Boost", BOOST_LIB_VERSION});
  vtable.add_row({"nlohmann JSON", NLOHMANN_JSON_VERSION_STRING});
  vtable.add_row({"hiredis", HIREDIS_VERSION_STRING});
  vtable.add_row({"OpenSSL", OPENSSL_VERSION_TEXT});
  vtable.add_row({"TinyORM", TINYORM_VERSION_STR});
  vtable.add_row({"tabulate", variant_lite_VERSION});
  std::cout << vtable << std::endl;
}