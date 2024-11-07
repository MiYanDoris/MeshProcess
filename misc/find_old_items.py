import os

root_dir = '/mnt/afs/grasp-sim/data/objaverse/assets'
object_id_lst = os.listdir(root_dir)

for object_id in object_id_lst:
    object_urdf_path = os.path.join(root_dir, object_id, 'urdf/meshes')
    if os.path.exists(object_urdf_path):
        # find old items on the directory
        items = os.listdir(object_urdf_path)
        create_time_lst = [os.path.getctime(os.path.join(object_urdf_path, item)) for item in items]
        duration = max(create_time_lst) - min(create_time_lst)
        if duration > 100:
            print('delete', object_id)
            os.system(f'rm -r {object_urdf_path}')