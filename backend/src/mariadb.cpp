#include <boost/mysql/statement.hpp>
#include <mariadb.hpp>

void Mariadb::worker() {
  while (this->running) {
    std::unique_lock<std::mutex> lock(queue_mutex);
    not_empty.wait(lock, [this] { return !query_queue.empty(); });
    auto q = query_queue.front();
    query_queue.pop();
    lock.unlock();
    mysql::results results;
    if (q.params.size() > 0) {
      mysql::statement stmt = conn.prepare_statement(q.qurey);
      conn.execute(stmt.bind(q.params.begin(), q.params.end()), results);
    } else
      conn.execute(q.qurey, results);
    q.callback(results);
  }
}