import tornado.web
import globalsetting
class BaseHandler(tornado.web.RequestHandler):
    def initialize(self):
        self.title = u'无 标题'
    
    def render(self, template_name, **kwargs):
        k = dict(isLocalJS = globalsetting.gIfLocalJS)
        k.update(kwargs)
        tornado.web.RequestHandler.render(self, template_name, **k)