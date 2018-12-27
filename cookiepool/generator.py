# -*- coding: utf-8 -*-
import json,requests
from selenium import webdriver
from selenium.common.exceptions import WebDriverException, TimeoutException
# 判断代码位置是否加载所需加载项
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from cookiepool.db import *

class Genterator(object):
    def __init__(self,name='default'):
        # 设置为无头浏览，不显示浏览器
        options = webdriver.FirefoxOptions()
        options.add_argument('-headless')
        self.browser = webdriver.Firefox(options=options)
        self.name = name
        self.account_db = AccountRedisClient(name=self.name)
        self.cookies_db = CookiesRedisClient(name=self.name)

    def get_cookie(self,username,password):
        return NotImplementedError

    def set_cookies(self, account):
        results = self.get_cookie(account.get('username'), account.get('password'))
        if results:
            username, cookies = results
            print('Saving Cookies to Redis', username, cookies)
            self.cookies_db.set(username, cookies)

    def run(self):
        """
        运行, 得到所有账户, 然后顺次模拟登录
        :return:
        """
        accounts = self.account_db.all()
        cookies = self.cookies_db.all()
        accounts = list(accounts)
        valid_users = [cookie.get('username') for cookie in cookies]
        print('Getting', len(accounts), 'accounts from Redis')
        for account in accounts:
            if not account.get('username') in valid_users:
                print('Getting Cookies of ', self.name, account.get('username'), account.get('password'))
                self.set_cookies(account)
        print('Generator Run Finished')
    # 生成完成后关闭浏览器，删除浏览器对象
    def close(self):
        try:
            print('Closing Browser')
            self.browser.close()
            del self.browser
        except TypeError:
            print('Browser not opened')

class WeiBoGenterator(Genterator):
    def __init__(self,name="weibo"):
        Genterator.__init__(self,name)

    def _success_get_cookie(self):
        wait = WebDriverWait(self.browser, 5)
        success = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.nameBox')))
        if success:
            print("登录成功")
            self.browser.get("https://weibo.com/u/6564086940/home?wvr=5&uut=fin&from=reg")
            if "我的首页" in self.browser.title:
                print(self.browser.get_cookies())
                cookies = {}
                for cookie in self.browser.get_cookies():
                    cookies[cookie["name"]] = cookie["value"]
                print(cookies)
                print("成功获取到cookies")
                return json.dumps(cookies)

    def get_cookie(self,username,password):
        self.browser.delete_all_cookies()
        # 碰到的问题，模拟登陆首页https://weibo.com有问题，他会先在一个空白页停留一会，然后才进入主页，导致输入信息被刷新掉，而登录不进去
        self.browser.get("https://weibo.com/login.php")
        wait = WebDriverWait(self.browser, 20)
        try:
            loginname = wait.until(EC.presence_of_element_located((By.ID,'loginname')))
            loginname.send_keys(username)
            passwd = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,'div.info_list.password > div > input')))
            passwd.send_keys(password)
            submit = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,'div.info_list:nth-child(6) > a:nth-child(1)')))
            submit.click()
            try:
                result = self._success_get_cookie()
                if result:
                    return (username,result)
                self.browser.close()
            except TimeoutException:
                print("出现验证码,开始识别验证码")
                yzm = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR,'div.info_list.verify.clearfix a img')))
                yzm_url = yzm.get_attribute('src')
                # 手动输入，可以用云打码等平台自动打码
                with open("yzm.png","wb") as f:
                    f.write(requests.get(yzm_url).content)
                yzm_content = str(input("请输入验证码"))
                if not yzm_content:
                    print("验证码错误，请重新输入")
                    return
                yzm_input = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR,'div.input_wrap.W_fl input')))
                yzm_input.send_keys(yzm_content)
                submit.click()
                result = self._success_get_cookie()
                if result:
                    return (username,result)
        except WebDriverException as e:
            print(e.args)

if __name__ == "__main__":
    WeiBoGenterator().run()