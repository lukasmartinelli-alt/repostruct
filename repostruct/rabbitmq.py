"""
RabbitMQ configuration (queues and topics).
"""
METADATA_QUEUE = 'repos:metadata'
FILEPATHS_QUEUE = 'repos:filepaths'
REPOS_QUEUE = 'repos:repos'
FAILED_QUEUE = 'repos:failed'
GIT_TIMEOUT_QUEUE = 'repos:timeout'
GIT_ERROR_QUEUE = 'repos:git_error'


def configure_rabbitmq(channel):

    def queue_declare(queue):
        return channel.queue_declare(queue=queue, durable=True)

    queue_declare(REPOS_QUEUE)
    queue_declare(METADATA_QUEUE)
    queue_declare(FILEPATHS_QUEUE)
    queue_declare(FAILED_QUEUE)
    queue_declare(GIT_TIMEOUT_QUEUE)
    queue_declare(GIT_ERROR_QUEUE)
