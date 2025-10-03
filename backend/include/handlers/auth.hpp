#pragma once

#include <boost/beast/http/status.hpp>
#include <handler.hpp>
#include <openssl/err.h>
#include <openssl/rand.h>

class Auth : public IHandler {
public:
  Auth() { path = "/auth"; };
  ~Auth() override = default;
  res post(req req) override;
};