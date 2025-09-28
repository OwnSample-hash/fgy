#include "router.hpp"
#include <common.hpp>

bool match_prefix(urls::segments_view target, urls::segments_view prefix) {
  // Trivially reject target that cannot
  // contain the prefix
  if (target.size() < prefix.size())
    return false;

  // Match the prefix segments
  auto it0 = target.begin();
  auto end0 = target.end();
  auto it1 = prefix.begin();
  auto end1 = prefix.end();
  while (it0 != end0 && it1 != end1 && *it0 == *it1) {
    ++it0;
    ++it1;
  }
  return it1 == end1;
}

res Router::do_route(req req, const endpoint_type &rep) {
  if (middlewares_.size() > 0) {
    for (const auto middleware : middlewares_) {
      if (middleware->when() & BEFORE) {
        if (middleware->before(req, rep) == ABORT) {
          return res{http::status::bad_request, req.version()};
        }
      }
      if (middleware->when() & AFTER) {
        after_middlewares_.push_back(middleware);
      }
    }
  }
  for (const auto handler : handlers_) {
    if (match_prefix(urls::url_view(req.target()).segments(),
                     urls::url_view(handler->path).segments())) {
      switch (req.method()) {
#define X(verb_)                                                               \
  case http::verb::verb_: {                                                    \
    auto res_ = handler->verb_(req);                                           \
    if (after_middlewares_.size() > 0) {                                       \
      for (const auto middleware : after_middlewares_) {                       \
        if (middleware->after(res_, rep) == ABORT) {                           \
          return res{http::status::expectation_failed, req.version()};         \
        }                                                                      \
      }                                                                        \
      after_middlewares_.clear();                                              \
    }                                                                          \
    return res_;                                                               \
  }
        HTTP_VERBS
#undef X

      default:
        return res{http::status::not_implemented, req.version()};
      }
    }
  }
  return res{http::status::not_found, req.version()};
}

Router::~Router() {
  for (auto handler : handlers_) {
    delete handler;
  }
  for (auto middleware : middlewares_) {
    delete middleware;
  }
}
