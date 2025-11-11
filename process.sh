# conda activate /mnt/afs/grasp-sim/root/miniconda3/envs/meshproc
# python3 src/dataset/objaverse_v1/robust_download.py
# python3 src/dataset/objaverse_v1/organize.py
python3 src/script/process.py data=objaverse_v1 task=main +split_id=0 +total_split_num=1 +object_json=object.json