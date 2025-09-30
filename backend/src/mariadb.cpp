#include <mariadb.hpp>

void Mariadb::worker() {
  while (this->running) {
    std::unique_lock<std::mutex> lock(queue_mutex);
    not_empty.wait(lock, [this] { return !query_queue.empty(); });
    auto q = query_queue.front();
    query_queue.pop();
    lock.unlock();

    mysql::results results;
    conn.execute(q.query, results);
    q.callback(results);
  }
}