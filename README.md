## Mysql database:
```sh
mysql> create database <mydatabase>;
mysql> grant all privileges on license_value_collector.* to '<myusername>'@'localhost' identified by '<mypassword>';

```

## Ansible playbook
```sh
---
    - hosts: <myhosts>
    - tasks:
        - name: checkout git repos
            git:
                repo: "https://github.com/robinostlund/veeam-license-reporting-tool.git"
                dest: "/tmp/veeam-license-reporting-tool"
                version: "master"
                accept_hostkey: yes

        - name: configure veeam license collect crontab
            cron:
              name: "veeam license collector"
              job: "/tmp/veeam-license-reporting-tool/run_collector.py"
              minute: "10"
              hour: "12-20"
              user: "my user"

        - name: configure veeam license report crontab
            cron:
              name: "veeam license reporter"
              job: "/tmp/veeam-license-reporting-tool/run_report.py"
              minute: "1"
              hour: "9"
              day: "2"
              user: "my user"
```
