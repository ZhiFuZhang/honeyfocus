#-*- coding:utf-8 -*-

import tornado.ioloop
import tornado.web
from tornado.options import define, options
import os
#import wechatgw.base
import globalsetting
import db
import time
#import base
import oam.handler
from db import session_scope
define("debug", default=False, help="run in debug mode")
define("port", default=8888, help="run on the given port", type=int)

# bootstrap http://www.runoob.com/bootstrap/bootstrap-environment-setup.html


def main():
    options.parse_command_line()
    d = options.debug
    e = False
    #we only use 8888 when we coding the project
    if options.port == 8888:
        globalsetting.gIfLocalJS = True
        d = True
        e = True

    db.init('sqlite:///' + os.path.join(os.path.dirname(__file__), "db/web.db"),
             e)
    with session_scope() as session:
        um = oam.business.UserManage(session)
        um.init_admin()
        
    app = tornado.web.Application(
        [
            (r"/", oam.handler.LoginHandler),
            #(r"/([^/]+)/apiwechat[^/]*$", wechatgw.base.WeChatHandler),
            (r'/oam/login$', oam.handler.LoginHandler),
            (r'/oam/manage$', oam.handler.ManageHandle),
            #(r"/wechatToken$", wechatgw.base.WeChatTokenGet),
            #(r"/wechatToken/insert$", wechatgw.base.WeChatTokenInsert),
            #(r"/wechatToken/update$", wechatgw.base.WeChatTokenUpdate),
            #(r"/wechatToken/update$", wechatgw.base.WeChatTokenDelete),
            #(r"/a/message/updates", MessageUpdatesHandler),
            ],
        cookie_secret="aESvdUvjh@#Fd7894*&gj)#zjJ!)(+}/`jX",
        template_path=os.path.join(os.path.dirname(__file__), "template"),
        static_path=os.path.join(os.path.dirname(__file__), "static"),
        xsrf_cookies=True,
        xheaders = True,
        debug=d,
        )
    
    time.sleep(7)
    app.listen(options.port)
    tornado.ioloop.IOLoop.current().start()  
if __name__ == '__main__':
    main();