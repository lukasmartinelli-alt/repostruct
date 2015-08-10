from setuptools import setup

requires = [
    'docopt==0.6.2',
    'requests==2.7.0',
    'python3-pika==0.9.14',
    'lxml==3.4.4',
    'cssselect==0.9.1',
    'fake-useragent==0.0.7',
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
               'repostruct/enqueue-repos-rabbitmq.py',
               'repostruct/clone-filepaths.py',
               'repostruct/extract-github-repos.py',
               'repostruct/fetch-latest-github-repos.py']
)
