#!/usr/bin/env python
import smtplib
from datetime import timedelta

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

class Mailer(object):
    def __init__(self, mysql_values, mail_settings, time_now):
        self.mysql_values = mysql_values
        self.email_rcpts = mail_settings['email_rcpts']
        self.email_from = mail_settings['email_from']
        self.email_subject = mail_settings['email_subject']

        # time strings
        self.time_now_today = time_now.today()
        self.time_now_year = time_now.strftime("%Y")
        self.time_now_month = time_now.strftime("%m")
        self.time_now_day = time_now.strftime("%d")
        self.time_now_clock = time_now.strftime("%X")


    def _GenerateHTMLEmail(self):
        output = '<html>\n'
        output += '<head>\n'
        output += '<style>\n'
        output += ' table { border-collapse: collapse; }\n'
        output += ' th { background: #00cc00; color: #FFFFFF; text-align: left; }\n'
        output += ' table, th, td { border: 1px solid black; text-align: left; }\n'
        output += ' tr:nth-child(even){ background-color: #ccffcc; }\n'
        output += ' h2 { color: #000000; }\n'
        output += '</style>\n'
        output += '</head>\n'
        output += '<body>\n'
        output += '<h2> %s</h2>\n' % (self.email_subject)
        output += '<table>\n'
        output += '  <tr>\n'
        output += '    <th style="width: 70px;">Year</th>\n'
        output += '    <th style="width: 70px;">Month</th>\n'
        output += '    <th style="width: 70px;">VMs</th>\n'
        points = False
        for value in self.mysql_values:
            if value['points']:
                output += '    <th style="width: 70px;">Points</th>\n'
                points = True
                break
        output += '    <th style="width: 200px;">Type</th>\n'
        output += '  </tr>\n'
        for value in self.mysql_values:
            output += '  <tr>\n'
            output += '    <td>%s</td>\n' % (value['year'])
            output += '    <td>%s</td>\n' % (value['month'])
            output += '    <td>%s</td>\n' % (value['value'])
            if points:
                output += '    <td>%s</td>\n' % (value['points'])
            output += '    <td>%s</td>\n' % (value['license'])
            output += '  </tr>\n'

        output += '</table>\n'
        output += '<p>Message generated: %s-%s-%s %s</p>\n' % (self.time_now_year, self.time_now_month, self.time_now_day, self.time_now_clock)
        output += '</body>\n'
        output += '</html>'
        return output

    def _GenerateEmail(self):
        # create message
        message = MIMEMultipart()
        message['Subject'] = self.email_subject
        message['To'] = ", ".join(self.email_rcpts)
        message['From'] = self.email_from

        body = self._GenerateHTMLEmail()

        # Record the MIME type text/html.
        html_body = MIMEText(body, 'html')
        message.attach(html_body)

        # connect to smtp server
        server = smtplib.SMTP('localhost')

        # send message
        server.sendmail(self.email_from, self.email_rcpts, message.as_string())

        # disconnect from smtp server
        server.quit()

