#-*- coding:utf-8 -*-

import tornado.ioloop
import tornado.web
from tornado.options import define, options
import os
import wechatgw.handler
import globalsetting
import db
import time
#import base
import oam.handler
from db import session_scope
import service

define("debug", default=False, help="run in debug mode")
define("port", default=8888, help="run on the given port", type=int)

#master node means, it provides more functions, such as fetching access_token from wechat
define('master', default=False, help='run as masster node')
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
    
    lock = None
    if options.master:
        lock = service.Master()
        # fail to lock, means, the master node is started, set the master to false
        if not lock.lock():
            options.master = False
    
    
    with session_scope() as session:
        um = oam.business.UserManage(session)
        um.init_admin()
    
    
        
    app = tornado.web.Application(
        [
            (r"/", oam.handler.LoginHandler),
            (r"/apiwechat[^/]*$", wechatgw.handler.WeChatHandler),
            (r'/oam/login$', oam.handler.LoginHandler),
            (r'/oam/manage$', oam.handler.ManageHandle),
            (r'/oam/wechat$', oam.handler.WeChatConfigHandle)
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
    app.listen(options.port, '127.0.0.1')
    tornado.ioloop.IOLoop.current().start()
    if lock:
        lock.release()
if __name__ == '__main__':
    main();