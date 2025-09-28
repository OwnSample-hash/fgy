#pragma once
#include <hiredis.h>

#define CMD(c, cmd, code)                                                      \
  redisReply *reply = reinterpret_cast<redisReply *>(redisCommand(c, cmd));    \
  code;                                                                        \
  freeReplyObject(reply)

#define l