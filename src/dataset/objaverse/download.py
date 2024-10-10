import os 
import sys 
import argparse
from glob import glob

import objaverse
SRC_FOLDER = os.path.join(os.path.dirname(__file__), '../..')
sys.path.append(SRC_FOLDER)
from util_file import load_yaml, load_json


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--category', type=str, default='Food')
    parser.add_argument('-n', '--n_worker', type=int, default=10)
    args = parser.parse_args()

    meta_info = load_yaml(os.path.join(SRC_FOLDER, 'config/data/objaverse.yaml'))
    objaverse_root = meta_info['root']
    category_list = os.listdir(meta_info['category_root'])

    if args.category not in category_list:
        raise ValueError(f'Invalid category: {args.category}')

    # Remove previous failed objects
    fail_lst = glob(f'{objaverse_root}/hf-objaverse-v1/glbs/**/**.tmp')
    if len(fail_lst) != 0:
        for fail_path in fail_lst:
            os.system(f'rm {fail_path}')
    
    # Load object list
    id_lst = []
    subcategory_list = os.listdir(os.path.join(meta_info['category_root'], args.category, 'category_list'))
    for subcategory_file in subcategory_list:
        subcategory_path = os.path.join(meta_info['category_root'], args.category, 'category_list', subcategory_file)
        with open(subcategory_path, 'r') as f:
            id_lst.extend(f.read().splitlines())

    # Download
    objects = objaverse.load_objects(
        uids=id_lst,
        download_processes=args.n_worker
    )

