import trimesh
import numpy as np
import json
import time
import argparse
import os

parser = argparse.ArgumentParser()
parser.add_argument("--total_split_num", type=int, required=True)
parser.add_argument("--split_id", type=int, required=True)
args = parser.parse_args()

def judge_one_model(model_id):
    physics_path = f'/mnt/afs/grasp-sim/data/objaverse-1400/assets/{model_id}/processed/simplified_500.obj'
    render_path = f'/mnt/afs/grasp-sim/data/objaverse-1400/assets/{model_id}/processed/normalized.obj'
    if os.path.exists(physics_path) and os.path.exists(render_path):
        physics_model = trimesh.load(physics_path, force='mesh')
        physics_model_vertices = physics_model.vertices
        render_model = trimesh.load(render_path, force='mesh')
        render_model_vertices = render_model.vertices

        max_bbox_error = np.max(physics_model_vertices, axis=0) - np.max(render_model_vertices, axis=0)
        min_bbox_error = np.min(physics_model_vertices, axis=0) - np.min(render_model_vertices, axis=0)
        
        bbox_error_1 = np.max(np.abs(max_bbox_error))
        bbox_error_2 = np.max(np.abs(min_bbox_error))
        if bbox_error_1 > 0.05 or bbox_error_2 > 0.05:
            with open('buggy.txt', 'a') as f:
                f.write(f'{model_id}\n')
            return [model_id]
    return []

model_ids = json.load(open('/mnt/afs/grasp-sim/yanmi/graspsim-new-pipeline/data/objaverse/annotation/objaverse-1400.json', 'r'))
model_ids = model_ids[args.split_id::args.total_split_num]

t0 = time.time()
buggy_ids = []
for i, model_id in enumerate(model_ids):
    buggy_ids += judge_one_model(model_id)
    t1 = time.time()
    left_time = (t1 - t0) / (i + 1) * (len(model_ids) - i - 1)
    print(f'{i}/{len(model_ids)}, left time: {left_time:.2f}s')

with open(f'outputs/buggy_ids_{args.split_id}.json', 'w') as f:
    json.dump(buggy_ids, f)