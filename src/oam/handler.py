
import handler
class OAMbase(handler.BaseHandler):
    pass  

#{% include *filename* %}
class LoginHandler(OAMbase):
    def get(self):
        self.title = u'登录 '
        self.render('')
    