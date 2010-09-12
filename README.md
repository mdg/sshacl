# sshacl
A server-side script for restricting a remote users privileges on the system.

## Sample Library
 restart_apache:
     cmd: /etc/init.d/httpd restart
     help: Restart the apache service
 backup_db:
     cmd: /opt/companyA/bin/backup.sh %(period)s
     help: Backup the database for the given period
 process_logs:
     cmd: process_logs %(log_type)s %(application)s
     help: Process a given type of log for the given application

## Sample Call
 exec: backup_db
 args:
     period: weekly


# Glossary
## Action
An available action that is executable by a remote client
## ActionLibrary
The suite of available actions that are available to be executed
## Call
A request by a remote client to actually execute an action


# Dependencies
 python >= 2.6
 pyyaml
 ssh
