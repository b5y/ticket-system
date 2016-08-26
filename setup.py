from setuptools import setup

setup(
    name='ticket-system',
    packages=['ticket-system'],
    include_package_data=True,
    install_requires=[
        'flask >= 0.11.1',
        'psycopg2 >= 2.6.2',
        'uwsgi >= 2.0.13.1',
        'pylibmc >= 1.5.1',
    ],
    setup_requires=[
        'pytest-runner',
    ],
    tests_require=[
        'pytest',
    ],
)
