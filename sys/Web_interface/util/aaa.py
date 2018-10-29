import redis

if __name__ == '__main__':
    pool = redis.ConnectionPool(host='localhost', port=6379, decode_responses=True)
    r = redis.Redis(connection_pool = pool)
    data = eval(r.get('data'))

    print type(data)
