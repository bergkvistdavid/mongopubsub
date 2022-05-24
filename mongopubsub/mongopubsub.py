from typing import Callable

from pymongo import MongoClient

from mongopubsub.message import Message


class MongoPubSub:
    def __init__(self, mongo_uri, database="mongopubsub", collection="topics"):
        self._db = MongoClient(mongo_uri)[database][collection]

    def subscribe(self, topic, callback: Callable[[Message], None]):
        """
        Subscribe to a topic.

        :param topic: The topic to subscribe to.
        :param callback: The callback to call when a message is received.
        """

        pipeline = [{
            "$match": {
                "operationType": {"$in": ["insert"]},
                "fullDocument.topic": topic
            },
        }]

        with self._db.watch(pipeline) as stream:
            for change in stream:
                message = Message.from_dict(change["fullDocument"])
                callback(message)

    def publish(self, message: Message):
        """
        Publish a message to a topic.

        :param message: The message to publish.
        """
        self._db.insert_one(message.to_dict())

    def publish_many(self, messages: list[Message]):
        """
        Publish a list of messages to a topic.

        :param messages: The list of messages to publish.
        """
        self._db.insert_many([message.to_dict() for message in messages])
