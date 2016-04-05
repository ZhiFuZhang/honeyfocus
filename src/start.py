#-*- coding:utf-8 -*-

import tornado.ioloop
import tornado.web
from tornado.options import define, options
import os
#import wechatgw.base
import globalsetting
import base
import oam.handler
define("debug", default=False, help="run in debug mode")
define("port", default=8888, help="run on the given port", type=int)

# bootstrap http://www.runoob.com/bootstrap/bootstrap-environment-setup.html


def main():
    options.parse_command_line()
    d = options.debug
    #we only use 8888 when we coding the project
    if options.port == 8888:
        globalsetting.gIfLocalJS = 1
        d = True
 
    app = tornado.web.Application(
        [
            (r"/", base.Mainhander),
            #(r"/([^/]+)/apiwechat[^/]*$", wechatgw.base.WeChatHandler),
            (r'/oam/login$', oam.handler.LoginHandler)
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
    app.listen(options.port)
    tornado.ioloop.IOLoop.current().start()  
if __name__ == '__main__':
    main();