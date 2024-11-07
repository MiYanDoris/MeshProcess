# convert usd to obj and mesh decimation
import os
import bpy
from tqdm import tqdm

usd_p = '/mnt/afs/grasp-sim/data/objaverse/assets/f8a1e5cd151842a9b098692a4e4653b0/processed/nomalized.usd'
obj_p = 'test.obj'

# usd_p = '/mnt/afs/grasp-sim/data/objaverse/assets/0adcf1771a3c4b5c922c47dd09d149b0/processed/converted.usd'
# obj_p = 'old.obj'

# Clears existing objects
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.wm.usd_import(filepath=usd_p)
bpy.ops.wm.obj_export(filepath=obj_p)