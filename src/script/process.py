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

    # obj_lst = json.load(open('/mnt/afs/grasp-sim/yanmi/graspsim-new-pipeline/data/objaverse/annotation/objaverse-1400.json', 'r'))

    # obj_to_be_processed = []
    # print('Go through object lists...')
    # def judge_obj_to_be_processed(obj_id):
    #     if not os.path.exists(cfg['task']['1-get_basic_info']['output_path'].replace('${data.output_template}', cfg['data']['output_template']).replace('**', obj_id)):
    #         return [obj_id]
    #     return []
    
    # pool = ThreadPoolExecutor(max_workers=32)
    # result_iter = pool.map(judge_obj_to_be_processed, obj_lst)
    # for result in result_iter:
    #     obj_to_be_processed.extend(result)
    
    # with open('obj_to_be_processed.log', 'w') as f:
    #     f.write('\n'.join(obj_to_be_processed))
    # exit(0)

    obj_to_be_processed = open('obj_to_be_processed.log', 'r').read().split('\n')
    
    obj_lst = obj_to_be_processed[cfg['split_id']::cfg['total_split_num']]

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