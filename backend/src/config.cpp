#include <config.hpp>
#include <fstream>
#include <stdexcept>

void Config::load(const std::string &path) {
  std::ifstream file(path);
  if (!file.is_open()) {
    throw FileNotFound("Failed to open config file: " + path);
  }
  try {
    file >> config;
  } catch (const json::parse_error &e) {
    throw std::runtime_error("Failed to parse config file: " +
                             std::string(e.what()));
  }
  file.close();
}

void Config::save(const std::string &path) {
  std::ofstream file(path);
  if (!file.is_open()) {
    throw std::runtime_error("Failed to open config file for writing: " + path);
  }
  file << config.dump(4);
  file.close();
}

json Config::get() { return config; }

json Config::get(const std::string &key) {
  if (config.contains(key)) {
    return config[key];
  }
  throw std::runtime_error("Config key not found: " + key);
}

void Config::set(const std::string &key, const json &value) {
  config[key] = value;
}

Config config;