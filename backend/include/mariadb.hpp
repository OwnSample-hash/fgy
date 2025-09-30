#pragma once

#include <boost/asio/ssl/context.hpp>
#include <boost/mysql/connection.hpp>
#include <boost/mysql/handshake_params.hpp>
#include <boost/mysql/tcp.hpp>
#include <common.hpp>
#include <condition_variable>
#include <config.hpp>
#include <functional>
#include <mutex>
#include <queue>
#include <string>
#include <thread>

struct query {
  std::string query;
  std::function<void(mysql::results &)> callback;
};

class Mariadb {
  asio::io_context ctx;
  asio::ssl::context ssl_ctx;
  mysql::tcp_ssl_connection conn;
  mysql::handshake_params params;

  void worker();
  std::queue<query> query_queue;
  std::thread worker_thread;
  std::mutex queue_mutex;
  std::condition_variable not_empty;
  bool running = true;

public:
  Mariadb()
      : ssl_ctx(asio::ssl::context::tls_client),
        conn(ctx.get_executor(), ssl_ctx),
        params(config.get("database")["user"],
               config.get("database")["password"],
               config.get("database")["name"]) {
    asio::ip::tcp::resolver resolver(ctx.get_executor());
    auto endpoints =
        resolver.resolve(std::string(config.get("database")["host"]),
                         std::string(config.get("database")["port"].dump()));
    conn.connect(*endpoints.begin(), params);
    worker_thread = std::thread(&Mariadb::worker, this);
  };
  ~Mariadb() {
    worker_thread.join();
    conn.close();
  }

  void enqueue(const std::string &query,
               const std::function<void(mysql::results &)> &callback) {
    std::lock_guard<std::mutex> lock(queue_mutex);
    query_queue.push({query, callback});
  }
};