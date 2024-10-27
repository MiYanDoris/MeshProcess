import os
import json

root_dir = '/mnt/afs/grasp-sim/root/.objaverse/hf-objaverse-v1/organized_glbs'
downloaded_glbs = os.listdir(root_dir)
downloaded_object_ids = [glbs.split('.')[0] for glbs in downloaded_glbs]
# json.dump(downloaded_object_ids, open('downloaded_object_ids-L40.json', 'w'), indent=2)
json.dump(downloaded_object_ids, open('downloaded_object_ids-4090.json', 'w'), indent=2)