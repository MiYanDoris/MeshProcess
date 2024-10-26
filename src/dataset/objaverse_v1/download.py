import os 
import sys 
import argparse
from glob import glob
import json

import objaverse
SRC_FOLDER = os.path.join(os.path.dirname(__file__), '../..')
sys.path.append(SRC_FOLDER)
from util_file import load_yaml


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-n', '--n_worker', type=int, default=10)
    args = parser.parse_args()

    meta_info = load_yaml(os.path.join(SRC_FOLDER, 'config/data/objaverse_v1.yaml'))
    objaverse_root = meta_info['root']

    # Remove previous failed objects
    fail_lst = glob(f'{objaverse_root}/hf-objaverse-v1/glbs/**/**.tmp')
    if len(fail_lst) != 0:
        for fail_path in fail_lst:
            os.system(f'rm {fail_path}')
    
    # Load object list
    # id_lst = []
    # category_list = os.listdir(meta_info['category_root'])
    # for category in category_list:
    #     category_file = os.path.join(meta_info['category_root'], category)
    #     with open(category_file, 'r') as f:
    #         id_lst.extend(f.read().splitlines())

    root_dir = '/mnt/afs/grasp-sim/data/objaverse'
    valid_id_file = f'{root_dir}/strict_filter.json'
    id_lst = json.load(open(valid_id_file, 'r'))

    print("There are", len(id_lst), "objects in all")
    # Download
    objects = objaverse.load_objects(
        uids=id_lst,
        download_processes=args.n_worker
    )
    print('[INFO] Finished downloading!!!!')