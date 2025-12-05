import base64
import json
import os
import requests
import psutil
import re

class LCU:

    def __init__(self):
        self.lcu_exe_name = 'LeagueClientUx.exe'
        self.lcu_pid = -1
        self.token = None
        self.port = None
        self.url = f"https://127.0.0.1:{self.port}"
        self.headers = None

    def get_lcu_auth(self):
        self.token = None
        self.port = None
        proc = None
        if self.lcu_pid != -1:
            try:
                proc = psutil.Process(self.lcu_pid)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                proc = None
                self.lcu_pid = -1
        if not proc:
            for iter_proc in psutil.process_iter(['pid', 'name']):
                try:
                    if iter_proc.info['name'] == "LeagueClientUx.exe":
                        self.lcu_pid = iter_proc.info['pid']
                        proc = psutil.Process(self.lcu_pid)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    proc = None

        if proc is None:
            return False

        cmdline = " ".join(proc.cmdline())
        self.lcu_pid = proc.pid
        port_match = re.search(r'--app-port=(\d+)', cmdline)
        token_match = re.search(r'--remoting-auth-token=([\w-]+)', cmdline)
        if port_match and token_match:
            self.token = token_match.group(1)
            self.port = port_match.group(1)
            self.url = f"https://127.0.0.1:{self.port}"
            self.headers = {
                "Accept": "application/json",
                "Content-Type": "application/json",
                "Authorization": "Basic " + base64.b64encode(("riot:" + self.token).encode("UTF-8")).decode("UTF-8")
            }
        if self.lcu_pid == -1:
            return False
        return True

    def get_runes(self):
        if not self.get_lcu_auth():
            return []
        url = self.url + "/lol-perks/v1/pages"
        response = requests.get(url, headers=self.headers, verify=False)
        if not response.ok:
            return []
        runes = []
        for item in json.loads(response.text):
            if item['isDeletable']:
                runes.append(item)
        return runes

    def delete_all_runes(self):
        if not self.get_lcu_auth():
            return False
        url = self.url + "/lol-perks/v1/pages"
        response = requests.delete(url, headers=self.headers, verify=False)
        if not response.ok:
            return False
        return True

    def apply_rune(self, rune_filepath):
        if not self.delete_all_runes():
            return False
        if not self.get_lcu_auth():
            return False
        with open(rune_filepath, encoding='utf-8') as f:
            rune = f.read()

        url = self.url + "/lol-perks/v1/pages"
        rune_json = json.loads(rune)
        rune_json['name'] = os.path.basename(rune_filepath)[:-5]
        response = requests.post(url, json=rune_json, headers=self.headers, verify=False)
        if not response.ok:
            return False
        return True

    def get_perks(self):
        if not self.get_lcu_auth():
            return None
        url = self.url + "/lol-perks/v1/perks"
        response = requests.get(url, headers=self.headers, verify=False)
        json_data = response.json()
        if json_data is None:
            return None
        return json_data

    def get_perk_styles(self):
        if not self.get_lcu_auth():
            return None
        url = self.url + "/lol-perks/v1/styles"
        response = requests.get(url, headers=self.headers, verify=False)
        json_data = response.json()
        if json_data is None:
            return None
        return json_data
