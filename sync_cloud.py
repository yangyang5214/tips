# -*- coding: utf-8 -*-
import sys
import json
import os
import hashlib
import logging
import datetime

logging.basicConfig(level=logging.INFO)


def main():
    # some check
    if not os.path.exists(local_path):
        return
    if not os.listdir(local_path):
        return

    # backup
    backup_file = os.path.join(local_path, '.backup.json')
    local_checksum_file = os.path.join(local_path, local_checksum)
    os.system('cp {} {}'.format(local_checksum_file, backup_file))

    # 生成本地快照
    hash_map = {}
    generate_hash(local_path, hash_map)
    save_json_to_file(hash_map, local_checksum_file)

    # 删除远程文件（如果文件删掉的话）
    now = read_json_file(local_checksum_file)
    backup = read_json_file(backup_file)
    rm_files = set(backup.keys()) - set(now.keys())
    if rm_files:
        cmd = ' && '.join(build_rm_file(rm_files))
        logging.info("cmd: {}".format(cmd))
        os.system('ssh {} \"{}\"'.format(remote_host, cmd))

    # 覆盖更新的文件
    changed = []
    for key in now:
        if backup.get(key):
            if backup.get(key) != now.get(key):
                changed.append(key)
        else:
            changed.append(key)

    if changed:
        for c in changed:
            cmd = 'scp {} {}:{}'.format(c, remote_host, os.path.join(remote_path, c.replace(local_path, '')))
            create_dir(path=c, is_remote=True)
            logging.info('cmd: {}'.format(cmd))
            os.system(cmd)


def build_rm_file(files):
    result = []
    for item in files:
        final_path = item.replace(local_path, remote_path)
        arr = final_path.rsplit('/', 1)
        arr[1] = '.' + arr[1] + str(datetime.datetime.now().strftime('%Y.%m.%d'))
        result.append('mv {} {}'.format(final_path, '/'.join(arr)))
    return result


def create_dir(path, is_remote=False):
    if is_remote:
        path = path.replace(local_path, remote_path)
        dir_path = os.path.dirname(path)
        cmd = 'ssh {} \"{}\"'.format(remote_host, "mkdir -p {}".format(dir_path))
        logging.info('cmd: {}'.format(cmd))
        os.system(cmd)
    else:
        path = path.replace(remote_path, local_path)
        dir_path = os.path.dirname(path)
        if not os.path.exists(dir_path):
            os.system('mkdir {}'.format(dir_path))


def read_json_file(path):
    logging.info("path: {}".format(path))
    with open(path) as f:
        return json.load(f)


def get_missing_and_change(map1, map2):
    result = []
    for key in map1:
        if key in map2:
            if map2.get(key) != map1.get(key):
                result.append(key)
        else:
            result.append(key)
    return result


def save_json_to_file(json_data, path):
    with open(path, 'w+') as f:
        json.dump(json_data, f)


def generate_hash(path, hash_map):
    for file_name in os.listdir(path):
        if file_name.startswith('.'):
            continue
        full_path = os.path.join(path, file_name)
        if os.path.isdir(full_path):
            generate_hash(full_path, hash_map)
        else:
            hash_map[full_path] = hashlib.md5(open(full_path, 'rb').read()).hexdigest()
    return hash_map


local_path = '/opt/cloud/'
remote_path = '/opt/cloud/note/'

local_checksum = '.checksum.json'

remote_host = 'beer'

if __name__ == '__main__':
    main()
