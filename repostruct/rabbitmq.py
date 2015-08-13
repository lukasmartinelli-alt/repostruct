"""
RabbitMQ configuration (queues and topics).
"""
import pika


METADATA_QUEUE = 'repos:metadata'
NO_METADATA_QUEUE = 'repos:no_metadata'
FILEPATHS_QUEUE = 'repos:filepaths'
FILEPATHS_ARCHIVE_QUEUE = 'repos:filepaths_archive'
REPOS_QUEUE = 'repos:repos'
FAILED_QUEUE = 'repos:failed'
GIT_TIMEOUT_QUEUE = 'repos:timeout'
GIT_ERROR_QUEUE = 'repos:git_error'
NOT_EXISTS_QUEUE = 'repos:not_exists'


def configure_rabbitmq(channel):
    """Setup all queues and topcis for RabbitMQ"""

    def queue_declare(queue):
        return channel.queue_declare(queue=queue, durable=True)

    queue_declare(REPOS_QUEUE)
    queue_declare(METADATA_QUEUE)
    queue_declare(FILEPATHS_QUEUE)
    queue_declare(FILEPATHS_ARCHIVE_QUEUE)
    queue_declare(FAILED_QUEUE)
    queue_declare(GIT_TIMEOUT_QUEUE)
    queue_declare(GIT_ERROR_QUEUE)
    queue_declare(NO_METADATA_QUEUE)
    queue_declare(NOT_EXISTS_QUEUE)


def durable_publish(channel, queue, body):
    properties = pika.BasicProperties(delivery_mode=2)
    channel.basic_publish(exchange='', routing_key=queue,
                          body=body, properties=properties)


def reject(channel, method):
    channel.basic_reject(delivery_tag=method.delivery_tag, requeue=False)
