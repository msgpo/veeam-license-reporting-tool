#!/usr/bin/env python
# Created by robin.ostlund@cygate.se
import os
import sys
import datetime

from modules.baashunter import Baashunter
from modules.veeam import VeeamConnector
from modules.mysql import MysqlConnector
from modules.config_reader import ConfigReader

config_file_collectors = 'config/collectors.conf'
config_file_db = 'config/db.conf'

def main():
    sum_data = []
    time_now = datetime.datetime.now()

    # read config
    config_collectors = os.path.join(os.path.dirname(os.path.realpath(__file__)), config_file_collectors)
    config_db = os.path.join(os.path.dirname(os.path.realpath(__file__)), config_file_db)
    config_reader = ConfigReader(config_db = config_db, config_collectors = config_collectors)


    # collect data
    for server in config_reader.collector_settings:
        if server['collector'] == 'veeam' or server['collector'] == 'veeam cloud connect':
            collector = VeeamConnector(server)
            protected_vms = collector._CalculateProtectedVms()
            collector._RequestVeeamSessionDelete()

        elif server['collector'] == 'baashunter':
            collector = Baashunter(server)
            protected_vms = collector._RequestBaashunterVmstat()
            collector._RequestBaashunterSessionDelete()


        else:
            raise BaseException('ERROR: %s is not a valid collector' % (server['collector']))



        # add data to summary list
        sum_data.append({
            'hostname': server['hostname'],
            'protected_vms': protected_vms,
            'collector': server['collector'],
            'points': protected_vms * int(server['point_value']),
            'license': server['license']
        })

    if sum_data:
        # connect to mysql
        mysql = MysqlConnector(config_reader.mysql_settings, time_now)

        # create mysql table
        mysql._QueryCreateMysqlTable()

        # add summary data to mysql db
        mysql._QueryAddSumData(sum_data)

        # summary monthly data
        mysql._SummerizeMonthlyData()

        # remove old report values
        mysql._RemoveOldValuesFromReports()

        # close connection to mysql
        mysql._Close()

if __name__ == '__main__':
    main()
