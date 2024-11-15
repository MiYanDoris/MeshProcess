import os 
import sys 
from copy import deepcopy
import logging 
import traceback
import multiprocessing
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor

import hydra
from omegaconf import DictConfig

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from proc.mesh import *
from proc.basic import *

logger = logging.getLogger('Process')

def process_all(params):
    cfg, obj_id = params
    # read config
    new_task_cfg = deepcopy(cfg['task'])
    for task_name, task_cfg in new_task_cfg.items():
        func_name = task_name.split('-')[-1]
        for k, v in task_cfg.items():
            if k.endswith('_path'):
                task_cfg[k] = os.path.abspath(v.replace('**', obj_id))
        try:
            eval(func_name)(task_cfg, logger=logger, skip=cfg['skip'], debug=cfg['debug_id'] is not None)
        except Exception as e:
            error_traceback = traceback.format_exc()
            logger.info(f'Failure! Task: {task_name}, obj: {obj_id} \n {error_traceback}')
            return
    with open('done.log', 'a') as f:
        f.write(f'Success! obj: {obj_id}\n')
    return 

@hydra.main(config_path="../config", config_name="base", version_base=None)
def main(cfg: DictConfig) -> None:
    assert '**' in cfg['data']['input_template'] and len(cfg['data']['input_template'].split('**')) == 2

    obj_lst = json.load(open(cfg['object_json'], 'r'))

    obj_lst = obj_lst[cfg['split_id']::cfg['total_split_num']]

    logger.info("#"*30)
    logger.info(f"Input template: {cfg['data']['input_template']}")
    logger.info(f"Output template: {cfg['data']['output_template']}")
    logger.info(f"Object Number: {len(obj_lst)}")
    logger.info(f"Tasks: {list(cfg['task'].keys())}")
    logger.info("#"*30)
    
    if cfg['debug_id'] is not None:
        process_all((cfg, cfg['debug_id']))
    else:
        iterable_params = [(cfg, obj_id) for obj_id in obj_lst]
        with multiprocessing.Pool(processes=cfg['n_worker']) as pool:
            result_iter = pool.imap_unordered(process_all, iterable_params)
            results = list(result_iter)
    with open('done.log', 'a') as f:
        split_id = cfg['split_id']
        f.write(f'[INFO] process {split_id} done\n')
    return

if __name__ == '__main__':
   main()