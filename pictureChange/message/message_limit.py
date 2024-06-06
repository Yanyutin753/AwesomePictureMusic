from plugins.pictureChange.message import message_reply as MessageReply


class MessageLimit(dict):

    def __init__(self):
        self.use_number = 0
        self.wait_number = 0

    def isLimit(self, max_number: int, e_context):
        if self.use_number >= max_number:
            self.wait_number += 1
            replyText = f"🧸当前排队人数为 {str(self.wait_number)}\n🚀 请耐心等待一至两分钟，再发送 '一张图片'，让我为您进行图片操作"
            MessageReply.reply_Text_Message(True, replyText, e_context)
            return True
        return False

    def success(self):
        if self.use_number > 0:
            self.use_number -= 1
            if self.max_number > self.use_number:
                self.wait_number = 0
        if self.wait_number > 0:
            self.wait_number -= 1

    def using(self):
        self.use_number += 1
