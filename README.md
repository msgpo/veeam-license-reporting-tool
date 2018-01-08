# Information
This is a tool for collecting license usage from Veeam Enterprise manager and stores that information to a database and then also can send these values in an email.


## Configuration example
config/collectors.conf

```sh
[my veeam enterprise hostname]
hostname = use your fqdn here to your veeam enterprise server
username = username to veeam enterprise manager
password = password to veeam enterprise manager
collector = veeam
point_value = how many points each vm costs (provided from your license provider)
license = veeam
```

config/db.conf
```sh
[default]
hostname = mysql server
database = mysql database
username = mysql username
password = mysql password
```

config/mail.conf
```sh
[default]
email_from = noreply@myserver.com
email_rcpts = myuser1@mydomain.com, myuser2@mydomain.com # use comma separation for multiple rcpts
email_subject = Veeam Usage Report
```

## Mysql database:
```sh
mysql> create database <mydatabase>;
mysql> grant all privileges on license_value_collector.* to '<myusername>'@'localhost' identified by '<mypassword>';

```

## Ansible playbook
```sh
---
    - hosts: myhost
    - tasks:
        - name: veeam-license-reporter - checkout git repos
            git:
                repo: "https://github.com/robinostlund/veeam-license-reporting-tool.git"
                dest: "/tmp/veeam-license-reporting-tool"
                version: "master"
                accept_hostkey: yes

        - name: veeam-license-reporter - configure veeam license collect crontab
            cron:
              name: "veeam license collector"
              job: "/tmp/veeam-license-reporting-tool/run_collector.py"
              minute: "10"
              hour: "12-20"
              user: "my user"

        - name: veeam-license-reporter - configure veeam license report crontab
            cron:
              name: "veeam license reporter"
              job: "/tmp/veeam-license-reporting-tool/run_report.py"
              minute: "1"
              hour: "9"
              day: "2"
              user: "my user"
```
