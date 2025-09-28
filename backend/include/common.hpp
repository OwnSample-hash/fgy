#pragma once

#include <boost/asio/ip/tcp.hpp>
#include <boost/beast/http.hpp>
#include <boost/mysql.hpp>
#include <boost/optional/optional_io.hpp>
#include <boost/program_options.hpp>
#include <boost/url/url.hpp>
#include <boost/url/url_view.hpp>
#include <nlohmann/json.hpp>

#define HTTP_DEFUALT_FIELDS(request)                                           \
  request.set(http::field::server, "Beast");                                   \
  request.set(http::field::content_type, "application/json");                  \
  request.keep_alive(request.keep_alive());

#define HTTP_ERROR_RESPONSE(status, evalue)                                    \
  res res{status, req.version()};                                              \
  HTTP_DEFUALT_FIELDS(res);                                                    \
  json j = {{"error", evalue}};                                                \
  res.body() = j.dump();                                                       \
  res.prepare_payload();                                                       \
  return res

namespace http = boost::beast::http;
namespace urls = boost::urls;
namespace mysql = boost::mysql;
namespace asio = boost::asio;
namespace po = boost::program_options;

using endpoint_type = boost::asio::ip::tcp::endpoint;
using req = http::request<http::string_body> const;
using res = http::response<http::string_body>;
using json = nlohmann::json;
