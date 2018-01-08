#!/usr/bin/env python
import MySQLdb
from datetime import timedelta
from warnings import filterwarnings

class MysqlConnector(object):
    def __init__(self, mysql_settings, time_now):
        self.mysql_host = mysql_settings['hostname']
        self.mysql_port = 3306
        self.mysql_user = mysql_settings['username']
        self.mysql_pass = mysql_settings['password']
        self.mysql_db = mysql_settings['database']
        self.mysql_charset = 'utf8'
        self.response = None

        # create db connection
        self.conn = MySQLdb.connect(host = self.mysql_host, user = self.mysql_user, passwd = self.mysql_pass, db = self.mysql_db)

        # create cursor
        self.cursor = self.conn.cursor(MySQLdb.cursors.DictCursor)

        # time strings
        self.time_now_today = time_now.today()
        self.time_now_year = time_now.strftime("%Y")
        self.time_now_month = time_now.strftime("%m")
        self.time_now_day = time_now.strftime("%d")
        self.time_last_year = ((self.time_now_today).replace(day=1) - timedelta(days=1)).strftime("%Y")
        self.time_last_month = ((self.time_now_today).replace(day=1) - timedelta(days=1)).strftime("%m")

    def _GetRows(self, query):
        self.cursor.execute(query)
        self.response = self.cursor.fetchall()

    def _GetRow(self, query):
        self.cursor.execute(query)
        self.response = self.cursor.fetchone()

    def _Query(self, query):
        self.cursor.execute(query)
        self.conn.commit()

    def _Close(self):
        self.cursor.close()
        self.conn.close()

    def _QueryCreateMysqlTable(self):
        filterwarnings('ignore', category = MySQLdb.Warning)
        # create table if not exists
        self._Query('CREATE TABLE IF NOT EXISTS reports (id INT NOT NULL AUTO_INCREMENT, hostname VARCHAR(100) NOT NULL, collector VARCHAR(100) NOT NULL, license VARCHAR(100) NOT NULL, year VARCHAR(10) NOT NULL, month VARCHAR(10) NOT NULL, day VARCHAR(10) NOT NULL, value INT NOT NULL, points INT NOT NULL, added TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, PRIMARY KEY(id))')
        self._Query('CREATE TABLE IF NOT EXISTS reports_monthly_summary (id INT NOT NULL AUTO_INCREMENT, license VARCHAR(100) NOT NULL, year VARCHAR(10) NOT NULL, month VARCHAR(10) NOT NULL, value INT NOT NULL, points INT NOT NULL, added TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, PRIMARY KEY(id))')

    def _QueryAddSumData(self, sum_data):
        for data in sum_data:
            # check so we don't already have saved data for this month
            self._GetRow('SELECT id FROM reports WHERE hostname = "%s" AND collector = "%s" AND year = "%s" AND month = "%s" AND day = "%s"' % (data['hostname'], data['collector'], self.time_now_year, self.time_now_month, self.time_now_day))
            if not self.response:
                # save data to db
                self._Query('INSERT INTO reports (hostname, collector, license, year, month, day, value, points) VALUES ("%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s")' % (data['hostname'], data['collector'], data['license'], self.time_now_year, self.time_now_month, self.time_now_day, data['protected_vms'], data['points']))

    def _SummerizeMonthlyData(self):
        self._GetRows('SELECT license FROM reports GROUP BY license')
        if not self.response:
            return

        for value in self.response:
            license_type = value['license']
            # check so we don't already have saved data for this month
            self._GetRow('SELECT id FROM reports_monthly_summary WHERE license = "%s" AND year = "%s" AND month = "%s"' % (license_type, self.time_last_year, self.time_last_month))
            if not self.response:
                total_value = 0
                total_points = 0
                # get all hosts
                self._GetRows('SELECT hostname FROM reports GROUP BY hostname')
                if self.response:
                    for hostname in self.response:
                        # get average data on each server
                        self._GetRow('SELECT ROUND(AVG(value),0) AS average_value, ROUND(AVG(points),0) AS average_points FROM reports WHERE license = "%s" AND year = "%s" AND month = "%s" AND hostname = "%s"' % (license_type, self.time_last_year, self.time_last_month, hostname['hostname']))
                        if self.response:
                            average_value = self.response['average_value']
                            average_points = self.response['average_points']
                            # if we don't have any previous data ignore it
                            if not average_value or not average_points:
                                continue

                            total_value += average_value
                            total_points += average_points

                # save data to db
                self._Query('INSERT INTO reports_monthly_summary (license, year, month, value, points) VALUES ("%s", "%s", "%s", "%s", "%s")' % (license_type, self.time_last_year, self.time_last_month, total_value, total_points))

    def _RemoveOldValuesFromReports(self):
        older_than_x_days = ((self.time_now_today).replace(day=1) - timedelta(days=730)).strftime("%Y")
        self._Query('DELETE FROM reports WHERE year < %s' % (older_than_x_days))

    def _GetMonthlyReports(self):
        self._GetRows('SELECT * FROM reports_monthly_summary ORDER BY id DESC')
        if not self.response:
            return

        return self.response

