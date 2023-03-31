import request


class Pushover:
    
    def __init__(self, user, token):
        
        self.url   = 'https://api.pushover.net/1/messages.json'
        self.user  = user
        self.token = token
        
    def push(self, message, title = None):

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
        
        
if __name__ == '__main__':
    print(1)