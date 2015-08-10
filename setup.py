from setuptools import setup

requires = [
    'docopt==0.6.2',
    'requests==2.6.0',
    'python3-pika==0.9.14',
]

setup(
    name='repostruct',
    version='0.1',
    url='http://github.com/lukasmartinelli/repostruct/',
    author="Lukas Martinelli",
    author_email="me@lukasmartinelli.ch",
    packages=['repostruct'],
    include_package_data=True,
    install_requires=requires,
    zip_safe=False,
    scripts = ['repostruct/fetch-metadata.py',
               'repostruct/rabbitmq-enqueue.py',
               'repostruct/last-github-repos.py']
)
