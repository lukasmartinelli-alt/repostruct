"""
RabbitMQ configuration (queues and topics).
"""
import pika


METADATA_QUEUE = 'repos:metadata'
FILEPATHS_QUEUE = 'repos:filepaths'
REPOS_QUEUE = 'repos:repos'
FAILED_QUEUE = 'repos:failed'
GIT_TIMEOUT_QUEUE = 'repos:timeout'
GIT_ERROR_QUEUE = 'repos:git_error'


class PublishFailed(Exception)
    """RabbitMQ basic_publish fail"""
    pass


def configure_rabbitmq(channel):

    def queue_declare(queue):
        return channel.queue_declare(queue=queue, durable=True)

    queue_declare(REPOS_QUEUE)
    queue_declare(METADATA_QUEUE)
    queue_declare(FILEPATHS_QUEUE)
    queue_declare(FAILED_QUEUE)
    queue_declare(GIT_TIMEOUT_QUEUE)
    queue_declare(GIT_ERROR_QUEUE)


def durable_publish(queue, body):
        properties = properties=pika.BasicProperties(delivery_mode = 2)
        body = {
            "repo": repo_name
        }
        result = channel.basic_publish(exchange='', routing_key=queue,
                                       body=body, properties=properties)
        if not result:
            raise PublishFailed('Could not publish to {}'.format(queue))

        return result

