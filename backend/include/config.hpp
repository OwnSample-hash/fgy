#pragma once

#include <common.hpp>

class FileNotFound : public std::runtime_error {
public:
  explicit FileNotFound(const std::string &msg) : std::runtime_error(msg) {}
};

class Config {
  json config;

public:
  Config() = default;
  ~Config() = default;

  void load(const std::string &path);
  void save(const std::string &path);
  json get();
  json get(const std::string &key);
  void set(const std::string &key, const json &value);
};

extern Config config;
