# convert usd to obj and mesh decimation
import os
import bpy
from tqdm import tqdm

for i in range(16):
    usd_p = f'/mnt/afs/grasp-sim/data/objaverse-1400/blender_usd/transparent_bottle_{i}/model_obj.usd'
    folder = f'/mnt/afs/grasp-sim/data/objaverse-1400/assets/transparent_bottle_{i}/processed'
    os.makedirs(folder, exist_ok=True)
    obj_p = f'{folder}/normalized.obj'

    # Clears existing objects
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.wm.usd_import(filepath=usd_p)
    bpy.ops.wm.obj_export(filepath=obj_p)