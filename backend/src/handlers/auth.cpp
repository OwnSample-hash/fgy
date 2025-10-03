#include <handlers/auth.hpp>

#include "argon2.h"
#include <vector>

res Auth::post(req req) {
  if (req.body().empty()) {
    HTTP_ERROR_RESPONSE(http::status::bad_request, "Missing body");
  }
  auto j = json::parse(req.body(), nullptr, false);
  std::string username, password;
  if (j.contains("username") && j["username"].is_string()) {
    username = j["username"];
  } else {
    HTTP_ERROR_RESPONSE(http::status::bad_request,
                        "Missing or invalid credentials");
  }
  if (j.contains("password") && j["password"].is_string()) {
    password = j["password"];
  } else {
    HTTP_ERROR_RESPONSE(http::status::bad_request,
                        "Missing or invalid credentials");
  }
  std::vector<unsigned char> salt(16);
  int ret = RAND_bytes(salt.data(), salt.size());
  if (ret != 1) {
    ERR_print_errors_fp(stderr);
    HTTP_ERROR_RESPONSE(http::status::internal_server_error,
                        "Failed to process request");
  }
  char hash[128];
  argon2id_hash_encoded(1, 47104, 1, password.c_str(), password.size(),
                        salt.data(), salt.size(), 32, hash, sizeof(hash));
}