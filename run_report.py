#!/usr/bin/env python
# Created by robin.ostlund@cygate.se
import os
import datetime

from modules.mysql import MysqlConnector
from modules.config_reader import ConfigReader
from modules.mailer import Mailer

config_file_db = 'config/db.conf'
config_file_mail = 'config/mail.conf'

def main():
    time_now = datetime.datetime.now()

    # read config
    config_db = os.path.join(os.path.dirname(os.path.realpath(__file__)), config_file_db)
    config_mail = os.path.join(os.path.dirname(os.path.realpath(__file__)), config_file_mail)
    config_reader = ConfigReader(config_db = config_db, config_mail = config_mail)

    # connect to mysql
    mysql = MysqlConnector(config_reader.mysql_settings, time_now)

    reports = mysql._GetMonthlyReports()
    email = Mailer(reports, config_reader.mail_settings, time_now)
    email._GenerateEmail()

if __name__ == '__main__':
    main()

