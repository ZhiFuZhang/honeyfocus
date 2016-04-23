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
from helper import web_log

define("debug", default=False, help="run in debug mode")
define("port", default=8888, help="run on the given port", type=int)

# bootstrap http://www.runoob.com/bootstrap/bootstrap-environment-setup.html


def main():
    options.parse_command_line()
    e = False
    #we only use 8888 when we coding the project
    if options.port == 8888:
        options.debug = True
        web_log.setLevel('DEBUG')
        globalsetting.gIfLocalJS = True
        #e = True
    d = options.debug
    db.init('sqlite:///' + os.path.join(os.path.dirname(__file__), "db/web.db"),
             e)
    
    master = service.Master()
    node = master.start()
    if node:
        print 'this is a master node'
    else:
        print 'this is a slave node'
        
    with session_scope() as session:
        um = oam.business.UserManage(session)
        um.init_admin()
    
    
        
    app = tornado.web.Application(
        [
            (r"/", oam.handler.LoginHandler),
            (r"/apiwechat[^/]*$", wechatgw.handler.WeChatHandler),
            (r'/oam/login$', oam.handler.LoginHandler),
            (r'/oam/manage$', oam.handler.ManageHandle),
            (r'/oam/wechat$', oam.handler.WeChatConfigHandle),
            (r'/oam/wechatpnp$', oam.handler.WeChatPnp),
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
    web_log.debug('start listening port:%d'%options.port)
    tornado.ioloop.IOLoop.current().start()
    master.release()
    
if __name__ == '__main__':
    main();