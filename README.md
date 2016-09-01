This is simple ticket-system
============================

[![Build Status](https://travis-ci.org/b5y/ticket-system.svg?branch=master)]
(https://travis-ci.org/b5y/ticket-system)

Description:
-----------


### This ticket system consists of:

 - tickets, which may contain comments
 - ticket can be created with state 'open', can change to 'answered' from 'waiting' or to 'closed' from 'closed', 
 state 'closed' is final (can not be modified or commented)

### API:
 - create ticket
 - change state
 - add comment
 - get ticket
 
### Using technologies:
 - Flask
 - psycopg2 (without ORM models)
 - uWSGI (emperor mode)
 - pylibmc (for memcache)