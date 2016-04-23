#-*- coding:utf-8 -*-

import unittest
from tornado.options import define, options
from helper import web_log
import db
import start

class BaseTestCase(unittest.TestCase):
    def beforeSetup(self):
        pass
    
    def afterSetup(self):
        pass
    def setUp(self):
        self.beforeSetup()
        options.parse_command_line()
        web_log.setLevel('DEBUG')
        if hasattr(self, 'dbecho'):
            db.init('sqlite:///:memory:', self.dbecho)
        else:
            db.init('sqlite:///:memory:', False)
        self.afterSetup()
    
    def tearDown(self):
        unittest.TestCase.tearDown(self)
    

class BaseTestCaseInit(BaseTestCase):
    def beforeSetup(self):
        self.dbecho = True
    def test1(self):
        pass
    
suite = unittest.TestLoader().loadTestsFromTestCase(BaseTestCaseInit)
if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite)