import sys 
import os 
from glob import glob
from tqdm.contrib.concurrent import process_map 

SRC_FOLDER = os.path.join(os.path.dirname(__file__), '../..')
sys.path.append(SRC_FOLDER)
from util_file import load_json

def create_softlink(input_path, output_path):
    if os.path.exists(input_path) and not os.path.exists(output_path):
        os.system(f'ln -s {input_path} {output_path}')
    return 

if __name__ == '__main__':
    raw_folder = os.path.join(os.path.expanduser('~'), '.objaverse/hf-objaverse-v1')
    output_folder = os.path.join(raw_folder, 'organized_glbs')
    os.makedirs(output_folder, exist_ok=True)
    
    input_path_lst = glob(f'{raw_folder}/glbs/**/**.glb')
    output_path_lst = [os.path.join(output_folder, input_path.split('/')[-1]) for input_path in input_path_lst]
    process_map(create_softlink, input_path_lst, output_path_lst, max_workers=32, chunksize=1)
    