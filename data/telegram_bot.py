import telegram


class TelegramBot:
    """
    Template for telegram bot object using telegram bot API.
    Args:
        token (str): Bot's unique identification token.
        chat_id (str): Receiver's chat id.
    """


    def __init__(self, token: str, chat_id: str):
        self.token = token
        self.chat_id = chat_id
        self.bot = telegram.Bot(token)


    async def send_message(self, message: str) -> None:
        """
        Use this method to send text messages.
        Args:
            message (str): Text message.
        """

        async with self.bot:
            await self.bot.send_message(
                text=message,
                chat_id=self.chat_id
            )


    async def send_document(self, document_path: str) -> None:
        """
        Use this method to send documents.
        Args:
            document_path (str):  Location of the document in the file system.
        """

        async with self.bot:
            await self.bot.send_document(
                chat_id=self.chat_id,
                document=document_path
            )