import sys 
import os 
import argparse
from glob import glob
from tqdm.contrib.concurrent import process_map 
import trimesh

SRC_FOLDER = os.path.join(os.path.dirname(__file__), '../..')
sys.path.append(SRC_FOLDER)
from util_file import load_yaml

data_cfg = load_yaml(os.path.join(SRC_FOLDER, 'config/data/objaverse.yaml'))
data_cfg['processed_folder'] = data_cfg['processed_folder'].replace("${data.root}", data_cfg['root'])
task_cfg = load_yaml(os.path.join(SRC_FOLDER, 'config/task/main.yaml'))

def glb2obj(glb_path, skip):
    obj_name = glb_path.split('/')[-1].replace('.glb', '')
    out_path = os.path.join(data_cfg['processed_folder'], obj_name, task_cfg['1-mesh_normalize']['input_path'])
    if os.path.exists(glb_path) and (not os.path.exists(out_path) or not skip):
        obj = trimesh.load(glb_path, force='mesh')
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        try:
            obj.export(out_path)
        except:
            print(f'Fail {glb_path}')
    return 

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-k', '--skip', action='store_false')
    args = parser.parse_args()
    
    raw_folder = os.path.join(data_cfg['root'], 'hf-objaverse-v1')
    glb_path_lst = glob(f'{raw_folder}/glbs/**/**.glb')
    skip_lst = [args.skip] * len(glb_path_lst)
    process_map(glb2obj, glb_path_lst, skip_lst, max_workers=8, chunksize=1)
    