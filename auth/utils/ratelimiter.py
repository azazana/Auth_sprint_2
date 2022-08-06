import json
import os
import time

from api import redis as redis_limit
from flask import request, abort
from redis import Redis


def get_identifier():
    return 'ip:' + request.remote_addr


def over_limit(
        conn: Redis,
        duration=int(os.getenv("RATE_LIMIT_DURATION", 60)),
        limit=int(os.getenv("RATE_LIMIT_LIMIT", 20))
):
    """Simple rate limit in 1 time duration"""
    bucket = ':%i:%i ' % (duration, time.time() // duration)
    identifier = get_identifier()
    key = identifier + bucket
    count = conn.incr(key)
    conn.expire(key, duration)
    if count > limit:
        return True
    return False


def rate_limit(limits):
    def rate_limit_func(func):
        def over_limit_multi_lua():
            """Rate limiting for 3 timespans and using 1 call to Redis with Lua script"""
            conn = redis_limit
            if not hasattr(conn, 'over_limit_multi_lua'):
                conn.over_limit_multi_lua = conn.register_script(over_limit_multi_lua_)

            if conn.over_limit_multi_lua(
                    keys=get_identifier(), args=[json.dumps(limits), time.time()]):
                abort(429, description="Too many requests")
            return func()

        over_limit_multi_lua.__name__ = func.__name__
        return over_limit_multi_lua

    return rate_limit_func


# def decorator_rate_limit(func):
#     def over_limit_multi_lua(redis, limits=[(1, 10), (60, 100), (3600, 250)]):
#         """Rate limiting for 3 timespans and using 1 call to Redis with Lua script"""
#         conn = redis
#         if not hasattr(conn, 'over_limit_multi_lua'):
#             conn.over_limit_multi_lua = conn.register_script(over_limit_multi_lua_)
#
#         if conn.over_limit_multi_lua(
#                 keys=get_identifier(), args=[json.dumps(limits), time.time()]):
#             abort(429, description="Too many requests")
#         func()
#
#     return over_limit_multi_lua


over_limit_multi_lua_ = '''
local limits = cjson.decode(ARGV[1])
local now = tonumber(ARGV[2])
for i, limit in ipairs(limits) do
    local duration = limit[1]
    local bucket = ':' .. duration .. ':' .. math.floor(now / duration)
    local key = KEYS[1] .. bucket
    local count = redis.call('INCR', key)
    redis.call('EXPIRE', key, duration)
    if tonumber(count) > limit[2] then
        return 1
    end
end
return 0
'''
