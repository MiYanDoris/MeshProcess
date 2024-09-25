import objaverse
import os 
import sys 
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
from src.util_file import OBJAVERSE_ROOT, load_json
import argparse
from glob import glob

def clean_tmp():
    fail_lst = glob(f'{OBJAVERSE_ROOT}/hf-objaverse-v1/glbs/**/**.tmp')
    if len(fail_lst) != 0:
        for fail_path in fail_lst:
            os.system(f'rm {fail_path}')
    return 

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--category', type=str, required=True,
        choices=['Human-Shape', 'Animals', 'Daily-Used', 'Furnitures',
                'Buildings&&Outdoor', 'Transportations', 'Plants', 
                'Food', 'Electronics', 'Poor-quality'])
    parser.add_argument('-n', '--n_process', type=int, default=10)
    args = parser.parse_args()

    # Load category annotation
    anno_path = os.path.join(OBJAVERSE_ROOT, 'category_annotation.json')
    if not os.path.exists(anno_path):
        os.system(f'wget -O {anno_path} https://virutalbuy-public.oss-cn-hangzhou.aliyuncs.com/share/aigc3d/category_annotation.json')
    anno = load_json(anno_path) 

    # Filter out specific category
    id_lst = [a['object_index'].split('.glb')[0] for a in anno if a['label'] == args.category]

    # Remove previous failed objects
    clean_tmp()
    
    # Download
    objects = objaverse.load_objects(
        uids=id_lst,
        download_processes=args.n_process
    )

