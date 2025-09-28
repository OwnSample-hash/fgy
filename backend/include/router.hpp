#pragma once

#include "middleware.hpp"
#include <handler.hpp>
#include <vector>

class SubRouter {
  std::string base_path;
  std::vector<IHandler *> &handlers_;

public:
  SubRouter(std::string base_path, std::vector<IHandler *> &handlers_)
      : base_path(base_path), handlers_(handlers_) {}
  void registerHandler(IHandler *handler) {
    handler->path = base_path + handler->path;
    handlers_.push_back(handler);
  }
  void registerHandlers(std::vector<IHandler *> handlers) {
    for (auto handler : handlers) {
      handler->path = base_path + handler->path;
      handlers_.push_back(handler);
    }
  }
};

class Router {
  std::vector<IHandler *> handlers_;
  std::vector<IMiddleware *> middlewares_, after_middlewares_;

public:
  void Handler(IHandler *handler) { handlers_.push_back(handler); }
  SubRouter *registerSubRouter(std::string base_path) {
    return new SubRouter(base_path, handlers_);
  }
  void use(IMiddleware *middleware) { middlewares_.push_back(middleware); }
  res do_route(req req, const endpoint_type &rep);
  ~Router();
};