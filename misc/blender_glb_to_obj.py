import os
import bpy
import json
import trimesh
import random
from tqdm import tqdm
import numpy as np
import json

def process_and_export(model_path, save_path, obj_id):
    # 清空当前场景中的物体
    bpy.ops.wm.read_factory_settings(use_empty=True)

    # 创建集合
    if "导入" not in bpy.data.collections:
        collection = bpy.data.collections.new("导入")
        bpy.context.scene.collection.children.link(collection)
    else:
        collection = bpy.data.collections["导入"]

    # 导入 .glb 文件
    bpy.ops.import_scene.gltf(filepath=model_path)

    # 将导入的物体放入集合
    for obj in bpy.context.selected_objects:
        bpy.data.collections["导入"].objects.link(obj)
        bpy.context.scene.collection.objects.unlink(obj)

    # 全选集合内的所有物体
    bpy.ops.object.select_all(action='DESELECT')
    for obj in collection.objects:
        obj.select_set(True)

    # 实现实例
    bpy.ops.object.make_single_user(object=True, obdata=True, material=False, animation=False)

    # 断开父子级并保持变换结果
    bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')

    # 删除所有空物体
    empty_objects = [obj for obj in bpy.data.objects if obj.type == 'EMPTY']
    for empty_obj in empty_objects:
        bpy.data.objects.remove(empty_obj, do_unlink=True)

    # 选择集合中的所有非网格物体并删除
    bpy.ops.object.select_all(action='DESELECT')
    for obj in collection.objects:
        if obj.type != 'MESH':
            obj.select_set(True)
    bpy.ops.object.delete(use_global=False)

    # 选择所有网格对象并合并
    bpy.ops.object.select_all(action='DESELECT')
    bpy.ops.object.select_by_type(type='MESH')
    selected_objects = bpy.context.selected_objects

    if len(selected_objects) > 1:
        bpy.context.view_layer.objects.active = selected_objects[0]
        bpy.ops.object.join()

    # 遍历场景中的所有网格物体
    merged_object = None
    for obj in bpy.context.scene.objects:
        if obj.type == 'MESH':
            merged_object = obj
            break

    # 如果合并后的物体不存在，则清空集合并跳过该文件
    if merged_object is None:
        bpy.ops.object.select_all(action='DESELECT')
        for obj in collection.objects:
            obj.select_set(True)
        bpy.ops.object.delete(use_global=False)
        bpy.ops.outliner.orphans_purge(do_local_ids=True, do_linked_ids=True, do_recursive=True)
        print(f"跳过文件 {model_path}: 合并后的物体不存在")
        return

    # 设置原点到几何中心
    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
    merged_object.location = (0, 0, 0)

    # 应用所有变换
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

    object_statistics = json.load(open(f'/mnt/afs/grasp-sim/data/objaverse/assets/{obj_id}/info/scale.json'))
    our_length = object_statistics['scale']
    
    # 计算最大尺寸并缩放到指定比例
    try:
        dimensions = merged_object.dimensions
        length = np.linalg.norm(np.array([dimensions.x, dimensions.y, dimensions.z]))
        if np.abs(length - our_length) > 0.01:
            with open('scele_error.txt', 'a') as f:
                f.write(f"{obj_id} {our_length} {length}\n")
            print(f"{merged_object.name} 尺寸错误: {e}")
            return
        
        scale_factor = 1.0 / length
        merged_object.scale = (scale_factor, scale_factor, scale_factor)

        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    except Exception as e:
        print(f"无法获取 {merged_object.name} 的尺寸: {e}")
        return

    # 导出为 .obj 文件
    output_path = os.path.join(save_path, f"{obj_id}.glb")
    bpy.ops.export_scene.gltf(filepath=output_path)
    mesh = trimesh.load(output_path, force='glb')
    mesh.export(os.path.join(save_path, f"{obj_id}.obj"))
    print(f"已成功处理并导出 {output_path}")

# model_ids = json.load(open('/mnt/afs/grasp-sim/yanmi/graspsim-new-pipeline/data/objaverse/annotation/valid_grasp.json', 'r'))
# random.shuffle(model_ids)

# has_visual_cnt = 0
# for model_id in tqdm(model_ids[:50]):
#     glb_path = f'/mnt/afs/grasp-sim/root/.objaverse/hf-objaverse-v1/organized_glbs/{model_id}.glb'

#     save_path = f'outputs/objs/{model_id}/'
#     os.makedirs(save_path, exist_ok=True)
#     process_and_export(glb_path, save_path, model_id)

#     file_list = os.listdir(save_path)
#     for file in file_list:
#         if file.endswith('.png'):
#             has_visual_cnt += 1
#             break

# print(has_visual_cnt)

glb_path = '/mnt/afs/grasp-sim/root/.objaverse/hf-objaverse-v1/organized_glbs/0166cd3012284d0cb89d0c6548f9680c.glb'

save_path = f'outputs/objs/0166cd3012284d0cb89d0c6548f9680c/'
os.makedirs(save_path, exist_ok=True)
process_and_export(glb_path, save_path, '0166cd3012284d0cb89d0c6548f9680c')