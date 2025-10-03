#pragma once
#include <handler.hpp>
#include <string_view>

enum MiddlewareResult { CONTINUE, ABORT };
enum MiddlewareFire { BEFORE = 1, AFTER, BOTH = BEFORE | AFTER };

class IMiddleware {
public:
  virtual ~IMiddleware() = default;
  virtual MiddlewareResult before(const req &, const endpoint_type &) {
    return CONTINUE;
  }
  virtual MiddlewareResult after(const res &, const endpoint_type &) {
    return CONTINUE;
  }
  virtual MiddlewareFire when() = 0;
  virtual std::string_view path() { return "*"; }
};