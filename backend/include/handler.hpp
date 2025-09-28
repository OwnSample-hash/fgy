#pragma once
#include <common.hpp>
#include <string>

#define HTTP_VERBS                                                             \
  X(delete_)                                                                   \
  X(get)                                                                       \
  X(head)                                                                      \
  X(post)                                                                      \
  X(put)                                                                       \
  X(options)                                                                   \
  X(patch)

class IHandler {
public:
  virtual ~IHandler() = default;
  std::string path;
#define X(verb)                                                                \
  virtual res verb(req req) {                                                  \
    return res{http::status::bad_request, req.version()};                      \
  };
  HTTP_VERBS
#undef X
};