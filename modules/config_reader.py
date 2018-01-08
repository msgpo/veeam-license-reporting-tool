#!/usr/bin/env python
import os
import ConfigParser

class ConfigReader(object):
    def __init__(self, config_db = False, config_collectors = False, config_mail = False):
        self.mysql_settings = {}
        self.collector_settings = []
        self.mail_settings = {}
        self.config_db = config_db
        self.config_collectors = config_collectors
        self.config_mail = config_mail
        self.config_parser_db = ConfigParser.ConfigParser()
        self.config_parser_collectors = ConfigParser.ConfigParser()
        self.config_parser_mail = ConfigParser.ConfigParser()

        # get config
        if self.config_db:
            self._ParseDbConfig()

        if self.config_collectors:
            self._ParseCollectorSettings()

        if self.config_mail:
            self._ParseMailConfig()

    def _ParseMailConfig(self):
        if os.path.isfile(self.config_mail):
            self.config_parser_mail.read(self.config_mail)
            if self.config_parser_mail.has_section('default'):
                if self.config_parser_mail.has_option('default', 'email_from') and self.config_parser_mail.has_option('default', 'email_rcpts'):
                    self.mail_settings['email_from'] = self.config_parser_mail.get('default', 'email_from')
                    self.mail_settings['email_rcpts'] = self.config_parser_mail.get('default', 'email_rcpts').split(',')
                    self.mail_settings['email_subject'] = self.config_parser_mail.get('default', 'email_subject')

                else:
                    raise BaseException('ERROR: missing options in default section (%s)' % (self.config_mail))
            else:
                raise BaseException('ERROR: missing default section in %s' % (self.config_mail))

        else:
            raise BaseException('ERROR: %s does not exist' % (self.config_mail))


    def _ParseDbConfig(self):
        if os.path.isfile(self.config_db):
            self.config_parser_db.read(self.config_db)
            if self.config_parser_db.has_section('default'):
                if self.config_parser_db.has_option('default', 'hostname') and self.config_parser_db.has_option('default', 'database') and self.config_parser_db.has_option('default', 'username') and self.config_parser_db.has_option('default', 'password'):
                    self.mysql_settings['hostname'] = self.config_parser_db.get('default', 'hostname')
                    self.mysql_settings['database'] = self.config_parser_db.get('default', 'database')
                    self.mysql_settings['username'] = self.config_parser_db.get('default', 'username')
                    self.mysql_settings['password'] = self.config_parser_db.get('default', 'password')
                else:
                    raise BaseException('ERROR: missing options in default section (%s)' %(self.config_db))
            else:
                raise BaseException('ERROR: missing default section in %s' % (self.config_db))

        else:
            raise BaseException('ERROR: %s does not exist' % (self.config_db))


    def _ParseCollectorSettings(self):
        if os.path.isfile(self.config_collectors):
            self.config_parser_collectors.read(self.config_collectors)
            conf_sections = self.config_parser_collectors.sections()
            for section in conf_sections:
                settings = {}
                if self.config_parser_collectors.has_option(section, 'hostname') and self.config_parser_collectors.has_option(section, 'username') and self.config_parser_collectors.has_option(section, 'password') and self.config_parser_collectors.has_option(section, 'collector') and self.config_parser_collectors.has_option(section, 'point_value') and self.config_parser_collectors.has_option(section, 'license'):
                    settings['section'] = section
                    settings['hostname'] = self.config_parser_collectors.get(section, 'hostname')
                    settings['username'] = self.config_parser_collectors.get(section, 'username')
                    settings['password'] = self.config_parser_collectors.get(section, 'password').replace('\\\\','\\')
                    settings['collector'] = self.config_parser_collectors.get(section, 'collector')
                    settings['point_value'] = self.config_parser_collectors.get(section, 'point_value')
                    settings['license'] = self.config_parser_collectors.get(section, 'license')

                    self.collector_settings.append(settings)
                else:
                    raise BaseException('ERROR: missing options in section: %s (%s)' % (section, self.config_collectors))
        else:
            raise BaseException('ERROR: %s does not exist' % (self.config_collectors))
