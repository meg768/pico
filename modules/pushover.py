


class Pushover:

    PRORITY_LOWEST     = -2
    PRORITY_LOW        = -1
    PRIORITY_NORMAL    = 0
    PRIORITY_HIGH      = 1
    PRIORITY_EMERGENCY = 2
    
    def __init__(self, user, token, debug = False):
        
        self.url   = 'https://api.pushover.net/1/messages.json'
        self.user  = user
        self.token = token
        self.debug = debug
        

    def print(self, *args):
        if self.debug:
            print(*args)
             
        
    def push(self, title = None, message = 'ABC', url = None, priority = PRIORITY_NORMAL):

        import request

        params = {
            'message' :  message,
            'priority':  priority,
            'token'   :  self.token,
            'user'    :  self.user
        }

        if title != None:
            params['title'] = title
            
        if url != None:
            params['url'] = title

        if priority != None:
            params['priority'] = priority

        reply = request.post(self.url, json = params).json()
        
        if (reply['status'] != 1):
            self.print(reply)
            raise Exception('Could not send message via Pushover.')

        return reply
        


        
if __name__ == '__main__':
    
    from config import PUSHOVER_USER, PUSHOVER_TOKEN
    
    pushover = Pushover(user = PUSHOVER_USER, token = PUSHOVER_TOKEN, debug = True)
    result = pushover.push(title = 'Title', message = 'What?', priority = pushover.PRIORITY_NORMAL)
    print('Finished', result)
    