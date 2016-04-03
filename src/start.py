#-*- coding:utf-8 -*-
import tornado.ioloop
import tornado.web
from tornado.options import define, options
import os
import wechatgw
import globalsetting

define("debug", default=False, help="run in debug mode")
define("port", default=8888, help="run on the given port", type=int)

# bootstrap http://www.runoob.com/bootstrap/bootstrap-environment-setup.html

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        #self.write(vars(self.request.headers))
        self.render("adminbase.htm");
def main():
    options.parse_command_line()
    
    #we only use 8888 when we coding the project
    if options.port == 8888:
        globalsetting.gIfLocalJS = 1  
 
    app = tornado.web.Application(
        [
            (r"/", MainHandler),
            #(r"/([^/]+)/apiwechat[^/]*$", wechatgw.handler.WeChatHandler),
            #(r"/wechatToken$", wechatgw.handler.WeChatTokenGet),
            #(r"/wechatToken/insert$", wechatgw.handler.WeChatTokenInsert),
            #(r"/wechatToken/update$", wechatgw.handler.WeChatTokenUpdate),
            #(r"/wechatToken/update$", wechatgw.handler.WeChatTokenDelete),
            #(r"/a/message/updates", MessageUpdatesHandler),
            ],
        cookie_secret="aESvdUvjh@#Fd7894*&gj)#zjJ!)(+}/`jX",
        template_path=os.path.join(os.path.dirname(__file__), "template"),
        static_path=os.path.join(os.path.dirname(__file__), "static"),
        xsrf_cookies=True,
        xheaders = True,
        debug=options.debug,
        )
    app.listen(options.port)
    tornado.ioloop.IOLoop.current().start()  
if __name__ == '__main__':
    main();