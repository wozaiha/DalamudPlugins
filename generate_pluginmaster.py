import json
import os
import codecs
from time import time
from sys import argv
from os.path import getmtime
from zipfile import ZipFile, ZIP_DEFLATED

DOWNLOAD_URL = 'https://raw.githubusercontent.com/wozaiha/DalamudPlugins/CustomRepo/plugins/{plugin_name}/{plugin_name}.zip'

DEFAULTS = {
    'IsHide': False,
    'IsTestingExclusive': False,
    'ApplicableVersion': 'any',
}

DUPLICATES = {
    'DownloadLinkInstall': ['DownloadLinkTesting', 'DownloadLinkUpdate'],
}

TRIMMED_KEYS = [
    'Author',
    'Name',
    'Description',
    'InternalName',
    'AssemblyVersion',
    'RepoUrl',
    'ApplicableVersion',
    'Tags',
    'DalamudApiLevel',
]

def main():
    # extract the manifests from inside the zip files
    master = extract_manifests()

    # trim the manifests
    master = [trim_manifest(manifest) for manifest in master]

    # convert the list of manifests into a master list
    add_extra_fields(master)

    # write the master
    write_master(master)

    # update the LastUpdated field in master
    last_updated()

    # update the Markdown
    #update_md(master)

def extract_manifests():
    manifests = []

    for dirpath, dirnames, filenames in os.walk('./plugins'):
        if len(filenames) == 0 or (dirpath.split('/')[-1].split('\\')[-1]+'.zip') not in filenames:
            continue
        plugin_name = dirpath.split('/')[-1].split('\\')[-1]
        latest_json = f'{dirpath}/{plugin_name}.json'
        with codecs.open(latest_json, "r", "utf-8") as f:
            content = f.read()
            if content.startswith(u'\ufeff'):
                content = content.encode('utf8')[3:].decode('utf8')
            manifests.append(json.loads(content))

    return manifests

def add_extra_fields(manifests):
    for manifest in manifests:
        # generate the download link from the internal assembly name
        manifest['DownloadLinkInstall'] = DOWNLOAD_URL.format(plugin_name=manifest["InternalName"])
        # add default values if missing
        for k, v in DEFAULTS.items():
            if k not in manifest:
                manifest[k] = v
        # duplicate keys as specified in DUPLICATES
        for source, keys in DUPLICATES.items():
            for k in keys:
                if k not in manifest:
                    manifest[k] = manifest[source]
        manifest['DownloadCount'] = 0

def write_master(master):
    # write as pretty json
    with open('pluginmaster.json', 'w') as f:
        json.dump(master, f, indent=4)

def trim_manifest(plugin):
    return {k: plugin[k] for k in TRIMMED_KEYS if k in plugin}

def last_updated():
    with open('pluginmaster.json') as f:
        master = json.load(f)

    for plugin in master:
        latest = f'plugins/{plugin["InternalName"]}/{plugin["InternalName"]}.zip'
        modified = int(getmtime(latest))

        if 'LastUpdated' not in plugin or modified != int(plugin['LastUpdated']):
            plugin['LastUpdated'] = str(modified)

    with open('pluginmaster.json', 'w') as f:
        json.dump(master, f, indent=4)

def update_md(master):
    with codecs.open('mdtemplate.txt', 'r', 'utf8') as mdt:
        md = mdt.read()
        for plugin in master:
            desc = plugin.get('Description', '')
            desc = desc.replace('\n', '<br>')
            md += f"\n| {plugin['Name']} | {plugin['Author']} | {desc} |"
        with codecs.open('plugins.md', 'w', 'utf8') as f:
            f.write(md)

if __name__ == '__main__':
    main()