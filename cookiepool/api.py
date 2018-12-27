# -*- coding: utf-8 -*-
from cookiepool.db import CookiesRedisClient
import json
def main():
    cookies = CookiesRedisClient(name="weibo").random()
    return json.loads(cookies)
if __name__ == '__main__':
    print(main())