import time
import os
from flask import request
from redis import Redis
import json


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


def over_limit_multi_lua(conn, limits=[(1, 10), (60, 10), (3600, 250)]):
    """Rate limiting for 3 timespans and using 1 call to Redis with Lua script"""
    if not hasattr(conn, 'over_limit_multi_lua'):
        conn.over_limit_multi_lua = conn.register_script(over_limit_multi_lua_)

    return conn.over_limit_multi_lua(
        keys=get_identifier(), args=[json.dumps(limits), time.time()])


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
