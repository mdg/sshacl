# Shackles
A server-side script for restricting a remote users privileges on the system.

## Sample Library
 restart_apache:
     cmd: /etc/init.d/httpd
     arg: restart
     help: Restart the apache service
 backup_db:
     cmd: /opt/companyA/bin/backup.sh
     arg: %(period)s

## Sample Command
 exec: backup_db
 args:
     period: weekly

# Dependencies
 python >= 2.6
 pyyaml
 ssh
