class Pushover:
    
    def __init__(self, user, token):
        
        self.url   = 'https://api.pushover.net/1/messages.json'
        self.user  = user
        self.token = token
        
    def send(self, message, title = None):
        import request

        params = {
            'message': message,
            'token':   self.token,
            'user':    self.user
        }

        if (title != None):
            params['title'] = title;

        reply = request.post(self.url, json = params).json()

        if (reply['status'] != 1):
            raise Exception('Could not send message')

        return reply
        