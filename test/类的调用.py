class NotificationsDump(object):
    def __init__(self):
        self.event_type = '1'


    def on_message(self):
        message = {'event_type':'compute.instance.power_on.end'}
        self.event_type = message.get('event_type')
        #print(self.event_type)
        return self.event_type


        # self.event_type = message.get('event_type')
        # return  self.event_type

    def main(self):
        b = self.event_type
        return b


a = NotificationsDump()

print(a.on_message())
print(a.event_type)

#print(a.event_type)