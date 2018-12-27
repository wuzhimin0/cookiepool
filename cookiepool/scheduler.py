# -*- coding: utf-8 -*-
import time
from cookiepool.generator import *
from cookiepool.tester import *
from multiprocessing import Process
from cookiepool.settings import *

class Scheduler(object):
    def valid_cookie(self,cycle=CYCLE):
        while True:
            print('Checking Cookies')
            try:
                    WeiBoTester().run()
                    print('Tester Finished')
                    time.sleep(cycle)
            except Exception as e:
                print(e.args)

    def generate_cookie(self,cycle=CYCLE):
        while True:
            print('Generating Cookies')
            try:
                    WeiBoGenterator().run()
                    print('Generator Finished')
                    WeiBoGenterator().close()
                    print('Deleted Generator')
                    time.sleep(cycle)
            except Exception as e:
                print(e.args)

    def run(self):
        if GENERATOR_PROCESS:
            generate_process = Process(target=self.generate_cookie)
            generate_process.start()

        if VALID_PROCESS:
            valid_process = Process(target=self.valid_cookie)
            valid_process.start()