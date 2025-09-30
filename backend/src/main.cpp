#include "config.hpp"
#include "mariadb.hpp"
#include "middlewares/logging.hpp"
#include "router.hpp"
#include <boost/asio/ip/tcp.hpp>
#include <boost/asio/strand.hpp>
#include <boost/beast/core.hpp>
#include <boost/beast/http.hpp>
#include <boost/beast/version.hpp>
#include <boost/config.hpp>
#include <boost/program_options/options_description.hpp>
#include <cassert>
#include <handlers/root.hpp>
#include <iostream>
#include <memory>
#include <redis.hpp>
#include <signal.h>

// This class handles an HTTP server connection.
class Session : public std::enable_shared_from_this<Session> {
  tcp::socket socket_;
  beast::flat_buffer buffer_;
  http::request<http::string_body> req_;
  Router &r;

public:
  explicit Session(tcp::socket socket, Router &r)
      : socket_(std::move(socket)), r(r) {}

  void run() { do_read(); }

private:
  void do_read() {
    auto self(shared_from_this());
    http::async_read(socket_, buffer_, req_,
                     [this, self](beast::error_code ec, std::size_t) {
                       if (!ec) {
                         do_write(r.do_route(req_, socket_.remote_endpoint()));
                       }
                     });
  }

  void do_write(http::response<http::string_body> res) {
    auto self(shared_from_this());
    auto sp =
        std::make_shared<http::response<http::string_body>>(std::move(res));
    http::async_write(socket_, *sp,
                      [this, self, sp](beast::error_code ec, std::size_t) {
                        ec = socket_.shutdown(tcp::socket::shutdown_send, ec);
                      });
  }
};

// This class accepts incoming connections and launches the sessions.
class Listener : public std::enable_shared_from_this<Listener> {
  net::io_context &ioc_;
  tcp::acceptor acceptor_;
  Router &r;

public:
  Listener(net::io_context &ioc, tcp::endpoint endpoint, Router &r)
      : ioc_(ioc), acceptor_(net::make_strand(ioc)), r(r) {
    beast::error_code ec;

    // Open the acceptor
    ec = acceptor_.open(endpoint.protocol(), ec);
    if (ec) {
      std::cerr << "Open error: " << ec.message() << std::endl;
      return;
    }

    // Allow address reuse
    ec = acceptor_.set_option(net::socket_base::reuse_address(true), ec);
    if (ec) {
      std::cerr << "Set option error: " << ec.message() << std::endl;
      return;
    }

    // Bind to the server address
    ec = acceptor_.bind(endpoint, ec);
    if (ec) {
      std::cerr << "Bind error: " << ec.message() << std::endl;
      return;
    }

    // Start listening for connections
    ec = acceptor_.listen(net::socket_base::max_listen_connections, ec);
    if (ec) {
      std::cerr << "Listen error: " << ec.message() << std::endl;
      return;
    }

    do_accept();
  }

private:
  void do_accept() {
    acceptor_.async_accept(net::make_strand(ioc_), [this](beast::error_code ec,
                                                          tcp::socket socket) {
      if (!ec) {
        std::make_shared<Session>(std::move(socket), r)->run();
      }
      do_accept();
    });
  }
};

redisContext *c;

void handle_stop(int) {
  // Add any cleanup code here if necessary
  std::cout << "Server is shutting down..." << std::endl;
  redisFree(c);
  exit(0);
}

int main(int argc, const char **argv) {
  po::options_description desc;
  desc.add_options()("help,h", "Show help message")(
      "config,c", po::value<std::string>(), "Path to config file");
  po::variables_map vm;
  try {
    po::store(po::parse_command_line(argc, argv, desc), vm);
    po::notify(vm);
  } catch (const std::exception &e) {
    std::cerr << "Error parsing command line: " << e.what() << std::endl;
    return 1;
  }
  if (vm.count("help")) {
    std::cout << desc << std::endl;
    return 0;
  }
  try {
    if (vm.count("config")) {
      config.load(vm["config"].as<std::string>());
    } else {
      config.load("config.json");
    }
  } catch (const FileNotFound &e) {
    std::cerr << e.what() << ", creating default config" << std::endl;
    config.set("argon2", {
                             {"t_cost", 1},
                             {"m_cost", 65536},
                             {"parallelism", 1},
                         });
    config.set("database", {
                               {"name", "mydb"},
                               {"user", "admin"},
                               {"password", "admin"},
                               {"host", "127.0.0.1"},
                               {"port", 3306},
                           });
    config.set("http", {
                           {"bind", "0.0.0.0"},
                           {"port", 8080},
                       });
    config.set("redis", {
                            {"host", "127.0.0.1"},
                            {"port", 6379},
                            {"password", ""},
                        });
    if (vm.count("config")) {
      config.save(vm["config"].as<std::string>());
    } else {
      config.save("config.json");
    }
  } catch (const std::exception &e) {
    std::cerr << "Error loading config: " << e.what() << std::endl;
    return 1;
  }
  signal(SIGINT, handle_stop);
  signal(SIGTERM, handle_stop);
  Mariadb db;
  c = redisConnect("127.0.0.1", 6379);
  if (c == NULL || c->err) {
    if (c != NULL) {
      printf("Error: %s\n", c->errstr);
      // handle error
    } else {
      printf("Can't allocate redis context\n");
    }

    exit(1);
  }

  CMD(c, "SET foo bar", { std::cout << "SET: " << reply->str << std::endl; });

  Router r;
  r.use(new LoggingMiddleware());

  auto api = r.registerSubRouter("/api");
  api->registerHandlers({new RootHandler()});

  auto const address = net::ip::make_address("0.0.0.0");
  unsigned short port = 8080;

  net::io_context ioc{1};

  std::make_shared<Listener>(ioc, tcp::endpoint{address, port}, r);
  std::cout << "Up and listening on port " << port << std::endl;

  ioc.run();
  //} catch (const std::exception &e) {
  //  std::cerr << "Error: " << e.what() << std::endl;
  //}
}