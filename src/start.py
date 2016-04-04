#-*- coding:utf-8 -*-

import tornado.ioloop
import tornado.web
from tornado.options import define, options
import os
#import wechatgw.basehandler
import globalsetting
import basehandler
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
            (r"/", basehandler.Mainhander),
            #(r"/([^/]+)/apiwechat[^/]*$", wechatgw.basehandler.WeChatHandler),
            (r'/oam/login$', oam.handler.LoginHandler)
            #(r"/wechatToken$", wechatgw.basehandler.WeChatTokenGet),
            #(r"/wechatToken/insert$", wechatgw.basehandler.WeChatTokenInsert),
            #(r"/wechatToken/update$", wechatgw.basehandler.WeChatTokenUpdate),
            #(r"/wechatToken/update$", wechatgw.basehandler.WeChatTokenDelete),
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