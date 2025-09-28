#include <handler.hpp>

class RootHandler : public IHandler {
public:
  RootHandler() { path = "/"; }
  ~RootHandler() override = default;
  res get(req req) override {
    res res{http::status::ok, req.version()};
    HTTP_DEFUALT_FIELDS(res);
    json j = {{"message", "Hello, World!"}};
    res.body() = j.dump();
    res.prepare_payload();
    return res;
  }
};