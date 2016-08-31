This is simple ticket-system
============================

[![Build Status](https://travis-ci.org/b5y/ticket-system.svg?branch=master)]
(https://travis-ci.org/b5y/ticket-system)

Description:
-----------


##### This thicket system consists of:

 - tickets, which may contain comments
 - ticket can be created with state 'open', can change to 'answered' or 'closed' from 'waiting' or 'closed', 
 state 'closed' is final (can not be modified or add comments)

##### API:
 - create ticket
 - change state
 - add comment
 - get ticket
 
##### Using technologies:
 - Flask
 - psycopg2 (without ORM models)
 - uWSGI (emperor mode)
 - pylibmc (for memcache)