import json

model_ids = []
with open('done.log', 'r') as f:
    for line in f:
        model_ids.append(line.strip().split(' ')[-1])

json.dump(model_ids, open('/mnt/afs/grasp-sim/yanmi/graspsim-new-pipeline/data/objaverse/annotation/objaverse-1400-meshproc.json', 'w'), indent=2)