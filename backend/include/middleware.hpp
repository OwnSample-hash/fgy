#pragma once
#include <handler.hpp>

enum MiddlewareResult { CONTINUE, ABORT };
enum MiddlewareFire { BEFORE = 1, AFTER, BOTH = BEFORE | AFTER };

class IMiddleware {
public:
  virtual ~IMiddleware() = default;
  virtual MiddlewareResult before(req &, const endpoint_type &) {
    return CONTINUE;
  }
  virtual MiddlewareResult after(res &, const endpoint_type &) {
    return CONTINUE;
  }
  virtual MiddlewareFire when() = 0;
};