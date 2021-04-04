# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import requests as r
import time
import yaml
import datetime
import json
import os
from elasticsearch import Elasticsearch
from elasticsearch import ElasticsearchException

class WebSiteStatusResult:
    def __init__(self, status, request_time, reason):
        self.status = status
        self.request_time = request_time
        self.reason= reason

    def statusToString(self):
        if self.status:
            return 'up'
        else:
            return 'down'

    def toString(self):
            return f"'status': '{self.statusToString()}', 'request_time': {str(self.request_time)}, 'reason': {self.reason}"

class SiteMonitoringConfig:
    def __init__(self, url, timeout, id, description):
        self.url = url
        self.timeout = timeout
        self.id = id
        self.description = description
        self.alert = False
        self.alert_text = ''

    def setAlertForSite(self, alert, alert_text):
        self.alert = alert
        self.alert_text = alert_text

    def isValid(self):
        return self.url and self.id and self.timeout

    def toString(self):
        return f'Url : {self.url}, id : {self.id}, description: {self.description}, timeout: {self.timeout}'

class SiteMonitoringApp:
    def readConfigFile(self, file):
        with open(file, "r") as yamlfile:
            print("Reading config file ", file)
            conf_data = yaml.load(yamlfile, Loader=yaml.FullLoader)

            if (not 'conf' in conf_data): 
                raise Exception("Configuration file " + file + " syntaxe error. conf key is missing") 

            if (not 'sites' in conf_data): 
                raise Exception("Configuration file " + file + " syntaxe error. sites key is missing") 

            if type(conf_data['conf']) == type(None):
                raise Exception("Configuration file " + file + " syntaxe error. conf key has no value") 

            self.check_interval = conf_data['conf'].get('check_interval', 15)
            self.elasticsearch_host = conf_data['conf'].get('elasticsearch_host', 'localhost:9200')
            self.alert_webhook_url = conf_data['conf'].get('alert_webhook_url', '')

            print("Check interval : ", self.check_interval, 's')
            print("Elasticsearch host : ", self.elasticsearch_host)
            print("Alert WebHook url : ", self.alert_webhook_url)
                       
            if type(conf_data['sites']) == type(None):
                raise Exception("Configuration file " + file + " syntaxe error. sites key has no value") 

            self.sites = []
            for site in conf_data['sites']:
                site_id = list(site.keys())[0]
                site_config = site[site_id]
                site_monitoring_config = SiteMonitoringConfig(site_config.get('url', ''), site_config.get('timeout', ''), site_id, site_config.get('description', ''))
                if site_monitoring_config.isValid():
                    self.sites.append(site_monitoring_config)
                    print('Adding website', site_id, 'for monitoring with parameters', site_monitoring_config.toString())
                    if ('alert' in site_config) and (site_config['alert']['raise_alert'] == True):
                        site_monitoring_config.setAlertForSite(True, site_config['alert']['alert_text'])
                        print("Adding alert for", site_id)
                else:
                    print("Configuration invalide pour le site", site_id, ". Site ignoré.")

    def check_website_avalability(self, host, timeout):
        try:
            startTime = time.time()
            headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
            req = r.request('GET', host, headers=headers,timeout=timeout)
            endTime = time.time()
            request_time = round((endTime - startTime) * 1000)
            return WebSiteStatusResult(req.ok, request_time, req.status_code)
        except r.exceptions.RequestException as e:
            return WebSiteStatusResult(False, -1, str(e))

    def write_check_result_to_elastic(self, site, check_resut):
        doc = {
            '@timestamp': datetime.datetime.now(),
            'url': site.url,
            'id': site.id,
            'description': site.description,
            'status': check_resut.statusToString(),
            'request_time': check_resut.request_time
        }
        try:
            self.es.index(index='site_monitoring', body=doc)
        except ElasticsearchException as e:
            print("Error while writting in Elasticsearch : ", e)

    def check_and_send_alert(self, site, check_result):
        if site.alert and not check_result.status:
            payload = {
                'url':site.url,
                'description':site.description,
                'id': site.id,
                'text': site.alert_text,
                'reason': check_result.reason
            }
            try:
                print("Sending alert to", self.alert_webhook_url)
                r.post(self.alert_webhook_url, json=payload)
            except r.exceptions.RequestException as e:
                print("Error send alert to", self.alert_webhook_url, ":",e)


    def execute(self):
        while True:
            for site in self.sites:       
                print("Checking", site.url)
                check_result = self.check_website_avalability(site.url, site.timeout)

                print(check_result.toString())
                self.write_check_result_to_elastic(site, check_result)
                self.check_and_send_alert(site, check_result)

            time.sleep(self.check_interval)

    def __init__(self, conf_file):
        self.readConfigFile(conf_file)
        self.es = Elasticsearch(
            [self.elasticsearch_host]
        )
        
if __name__ == '__main__':
    conf_file = os.getenv('CONF_FILE', 'site_monitoring.yml')
    app = SiteMonitoringApp(conf_file)
    app.execute()

