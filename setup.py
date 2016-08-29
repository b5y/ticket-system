from setuptools import setup, find_packages

setup(
    name='ticket-system',
    version='0.0.1',
    include_package_data=True,
    install_requires=[
        'flask >= 0.11.1',
        'psycopg2 >= 2.6.2',
        'uwsgi >= 2.0.13.1',
        'pylibmc >= 1.5.1',
    ],
    packages=find_packages(),
    setup_requires=[
        'pytest-runner',
    ],
    tests_require=[
        'pytest',
    ],
)
