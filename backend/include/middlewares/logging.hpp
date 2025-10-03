#pragma once
#include <chrono>
#include <format>
#include <iostream>
#include <middleware.hpp>

using namespace std::literals;

class LoggingMiddleware : public IMiddleware {
  std::ostream &out = std::cout;
  std::string UserAgent = "";

public:
  LoggingMiddleware() = default;
  LoggingMiddleware(std::ostream &out) : out(out) {}
  ~LoggingMiddleware() override = default;
  MiddlewareResult before(const req &request, const endpoint_type &) override {
    UserAgent = request[http::field::user_agent];
    return CONTINUE;
  }
  MiddlewareResult after(const res &response,
                         const endpoint_type &rep) override {
    auto now = std::chrono::system_clock::now();
    out << rep.address().to_string() << " - ["
        << std::format("{:%d}/{:%b}/{:%Y}:{:%H}:{:%M}:{:%S0} {:%z}", now, now,
                       now, now, now, now, now)
        << "] \"" << response.result_int() << "\"" << response.payload_size()
        << " - \"" << UserAgent << "\"\n";
    return CONTINUE;
  }
  MiddlewareFire when() override { return BOTH; }
};