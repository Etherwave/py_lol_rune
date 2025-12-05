import psutil
import re
import base64
import requests
import json
import os

def get_lcu_pid():
    lcu_pid = -1
    for iter_proc in psutil.process_iter(['pid', 'name']):
        try:
            if iter_proc.info['name'] == "LeagueClientUx.exe":
                lcu_pid = iter_proc.info['pid']
                break
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    return lcu_pid

def get_url_headers():
    lcu_pid = get_lcu_pid()
    if lcu_pid == -1:
        return None, None
    proc = psutil.Process(lcu_pid)
    cmdline = " ".join(proc.cmdline())
    port_match = re.search(r'--app-port=(\d+)', cmdline)
    token_match = re.search(r'--remoting-auth-token=([\w-]+)', cmdline)
    if port_match and token_match:
        token = token_match.group(1)
        port = port_match.group(1)
        url = f"https://127.0.0.1:{port}"
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": "Basic " + base64.b64encode(("riot:" + token).encode("UTF-8")).decode("UTF-8")
        }
        return url, headers
    return None, None

def get_perks():
    perks_json_file_path = "./perks.json"
    if os.path.exists(perks_json_file_path):
        return json.load(open(perks_json_file_path, "r", encoding="utf-8"))
    url, headers = get_url_headers()
    if url is None or headers is None:
        return None
    response = requests.get(url + "/lol-perks/v1/perks", headers=headers, verify=False)
    # print(response.status_code)
    # print(response.json())
    json_data = response.json()
    if json_data is None:
        return None
    json.dump(json_data, open(perks_json_file_path, "w", encoding="utf-8"), ensure_ascii=False, indent=4)
    return json_data

def get_perks_name_id_map(perks_json_file_path):
    perks_name_id_map = {}
    if os.path.exists(perks_json_file_path):
        with open(perks_json_file_path, "r", encoding='utf-8') as f:
            perks_json = json.load(f)
    for item in perks_json:
        perks_name_id_map[item['name']] = item['id']
    return perks_name_id_map

def get_runes():
    runes = []
    url, headers = get_url_headers()
    if url is None or headers is None:
        return None
    response = requests.get(url + "/lol-perks/v1/pages", headers=headers, verify=False)
    if not response.ok:
        return []
    for item in json.loads(response.text):
        runes.append(item)
        name = item["name"]
        rune_file_path = f"./runes/{name}.rune"
        with open(rune_file_path, "w", encoding="utf-8") as f:
            json.dump(item, f, ensure_ascii=False, indent=4)
    return runes

def show_rune(rune_file_path):
    rune_json = None
    with open(rune_file_path, encoding='utf-8') as f:
        rune_json = json.loads(f.read())
    if rune_json is None:
        return
    primary_rune = rune_json["primaryStyleId"]
    secondary_rune = rune_json["subStyleId"]
    print("primary_rune: {} {}".format(primary_rune, rune_json["primaryStyleName"]))
    print("secondary_rune: {} {}".format(secondary_rune, rune_json["secondaryStyleName"]))
    selectedPerkIds = rune_json["selectedPerkIds"]
    print(selectedPerkIds)
    perks_name_id_map = get_perks_name_id_map("./perks.json")
    perks_id_name_map = {v: k for k, v in perks_name_id_map.items()}
    # print(perks_id_name_map)
    for perkId in selectedPerkIds:
        print(perkId, perks_id_name_map[perkId])

def get_perk_styles():
    perks_style_json_file_path = "./perk_styles.json"

    if os.path.exists(perks_style_json_file_path):
        return json.load(open(perks_style_json_file_path, "r", encoding="utf-8"))
    url, headers = get_url_headers()
    if url is None or headers is None:
        return None
    response = requests.get(url + "/lol-perks/v1/styles", headers=headers, verify=False)
    # print(response.status_code)
    # print(response.json())
    json_data = response.json()
    if json_data is None:
        return None
    json.dump(json_data, open(perks_style_json_file_path, "w", encoding="utf-8"), ensure_ascii=False, indent=4)
    return json_data


def set_rune(rune_file_path):
    rune_json = None
    with open(rune_file_path, encoding='utf-8') as f:
        rune_json = json.loads(f.read())
    if rune_json is None:
        return
    url, headers = get_url_headers()
    if url is None or headers is None:
        return None
    response = requests.post(url + "/lol-perks/v1/pages", headers=headers, verify=False, json=rune_json)
    if not response.ok:
        return None
    print(response.status_code)
    print(response.json())

def delete_rune():
    url, headers = get_url_headers()
    if url is None or headers is None:
        return None
    response = requests.delete(url + f"/lol-perks/v1/pages", headers=headers, verify=False)
    if not response.ok:
        return None
    print(response.status_code)
    # print(response.text)
    # print(response.json())


if __name__ == '__main__':
    # perks_json = get_perks()
    # for perk in perks_json:
    #     print(perk['id'], perk['name'])
    # perks_style_json = get_perk_styles()
    # for style in perks_style_json:
    #     print(style['id'], style['name'])
    get_runes()
    # show_rune("./runes/01.rune")
    # set_rune("./runes/01.rune")
    # delete_rune()
    # set_rune("./runes/1.rune")
