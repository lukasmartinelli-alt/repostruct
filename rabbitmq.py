import pika

JOBS_QUEUE = 'repos:jobs'
FAILED_QUEUE = 'repos:failed'
DELETED_QUEUE = 'repos:deleted'
TOO_BIG_QUEUE = 'repos:toobig'

def configure_rabbitmq(channel):

    def queue_declare(queue)
        return channel.queue_declare(queue=queue, durable=True)

    queue_declare(JOBS_QUEUE)
    queue_declare(FAILED_QUEUE)
    queue_declare(DELETED_QUEUE)
    queue_declare(TOO_BIG_QUEUE)
