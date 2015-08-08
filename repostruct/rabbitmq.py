"""
RabbitMQ configuration (queues and topics).
"""
import pika

RESULTS_QUEUE = 'repos:results'
JOBS_QUEUE = 'repos:jobs'
FAILED_QUEUE = 'repos:failed'
GIT_ERROR_QUEUE = 'repos:git_error'
GIT_TIMEOUT_QUEUE = 'repos:timeout'


def configure_rabbitmq(channel):

    def queue_declare(queue):
        return channel.queue_declare(queue=queue, durable=True)

    queue_declare(JOBS_QUEUE)
    queue_declare(RESULTS_QUEUE)
    queue_declare(FAILED_QUEUE)
    queue_declare(GIT_TIMEOUT_QUEUE)
    queue_declare(GIT_ERROR_QUEUE)
