#!/usr/bin/python

import pwd
import os
from subprocess import call
from charmhelpers.core import host
from charmhelpers.core.hookenv import log, status_set, config
from charmhelpers.core.templating import render
from charms.reactive import when, when_not, set_flag, clear_flag, when_file_changed, endpoint_from_flag
from charms.reactive import Endpoint


@when('apache.available')
def finishing_up_setting_up_sites():
    host.service_reload('apache2')
    set_flag('apache.start')


@when('apache.start')
def apache_started():
    host.service_reload('apache2')
    status_set('maintenance', 'Apache started')


@when('endpoint.mysqlgdb.joined')
@when_not('endpoint.mysqlgdb.connected')
def connect_mysql_db():
    endpoint = endpoint_from_flag('endpoint.mysqlgdb.joined')
    endpoint.connect('gdb_mysql')
    status_set('maintenance', 'Connect mysql gdb')


##################################################
#                                                #
# Request successful, get data and render config # 
#                                                #
##################################################


@when('endpoint.mongodb.available')
def mysql_render_config():
    
    mongodb = endpoint_from_flag('endpoint.mongodb.available')

    render('mongo-config.j2', '/var/www/consumer-app-b/mongodb-config.html', {
        'gdb_host' : mongodb.hostname(),
        'gdb_port' : mongodb.port(),
        'gdb_dbname' : mongodb.databasename(),
        'gdb_user' : mongodb.user(),
        'gdb_password' : mongodb.password(),
        'connection_string' : mongodb.connection_string(),
    })
    status_set('maintenance', 'Rendering config file')
    set_flag('endpoint.mongodb.connected')
    set_flag('restart-app')

@when('restart-app')
def restart_app():
    host.service_reload('apache2')
    clear_flag('restart-app')
    status_set('active', 'Mongo-app ready')
