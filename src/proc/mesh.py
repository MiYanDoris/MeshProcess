import os
import sys
import numpy as np
import trimesh 
import json
import bpy


sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from util_file import task_wrapper


@task_wrapper
def mesh_normalize(config):
    input_path, output_path = config['input_path'], config['output_path']
    tm_mesh = trimesh.load(input_path, force='mesh')
    verts = np.array(tm_mesh.vertices)
    center = (np.max(verts, axis=0) + np.min(verts, axis=0)) / 2
    length = np.linalg.norm(np.max(verts, axis=0) - np.min(verts, axis=0)) / 2
    tm_mesh.vertices = (verts - center[None]) / length
    tm_mesh.export(output_path)
    return 


@task_wrapper
def mesh_convex_decomp(config):
    input_path, output_path, quiet = config['input_path'], config['output_path'], config['quiet']
    command = f'third_party/CoACD/build/main -i {input_path} -o {output_path} -t 0.05'
    if quiet:
        command += ' > /dev/null 2>&1'
    os.system(command)
    return 


@task_wrapper
def mesh_remove_small_piece(config):
    input_path, output_path, min_volume = config["input_path"], config["output_path"], config['min_volume']
    parts = trimesh.load(input_path, force='mesh').split()
    # print(len(parts))
    # for part in parts:
    #     if part.volume < min_volume:
    #         print('-' * 20)
    #         print(part)
    #         print(part.volume)
    #         parts.remove(part)
    new_mesh = trimesh.util.concatenate(parts)
    new_mesh_vertices = new_mesh.vertices

    # ensure mesh after filtering is the same as the original mesh
    old_mesh = trimesh.load(input_path, force='mesh')
    old_mesh_vertices = old_mesh.vertices

    max_bbox_error = np.max(new_mesh_vertices, axis=0) - np.max(old_mesh_vertices, axis=0)
    min_bbox_error = np.min(new_mesh_vertices, axis=0) - np.min(old_mesh_vertices, axis=0)
    
    bbox_error_1 = np.max(np.abs(max_bbox_error))
    bbox_error_2 = np.max(np.abs(min_bbox_error))
    if bbox_error_1 > 0.05 or bbox_error_2 > 0.05:
        raise Exception(f"filter small piece error: {bbox_error_1}, {bbox_error_2}")
    new_mesh.export(output_path)
    return

@task_wrapper
def mesh_manifold(config):
    input_path, output_path, quiet = config['input_path'], config['output_path'], config['quiet']
    command = f'third_party/CoACD/build/main -i {input_path} -ro {output_path} -pm on'
    if quiet:
        command += ' > /dev/null 2>&1'
    os.system(command)
    return 


@task_wrapper
def mesh_simplify(config):
    input_path, output_path, vert_num, gradation, quiet = config['input_path'], config['output_path'], config['vert_num'], config['gradation'], config['quiet']
    command = f'third_party/ACVD/bin/ACVD {input_path} {vert_num} {gradation} -o {os.path.dirname(output_path)+os.sep} -of {os.path.basename(output_path)} -m 1'
    if quiet:
        command += ' > /dev/null 2>&1'
    os.system(command)
    os.system(f"rm {os.path.join(os.path.dirname(output_path), 'smooth_'+os.path.basename(output_path))}")
    return
    

def judge_texture(dir_path):
    if os.path.exists(dir_path):
        file_list = os.listdir(dir_path)
        png_file_list = [f for f in file_list if f.endswith('.png')]
        if len(png_file_list) > 0:
            return True
        
        material_file = os.path.join(dir_path, 'material.mtl')
        if os.path.exists(material_file):
            meaningful_value = False
            with open(material_file, 'r') as f:
                for line in f:
                    if 'Kd' in line:
                        values = line.split(' ')
                        values = [float(v) for v in values[1:]]
                        meaningful_value = any([v != 0.0 and v != 0.4 and v != 1.0 for v in values])
                        if meaningful_value:
                            return True
    return False


@task_wrapper
def glb_to_mesh_and_normalize(config):
    input_path, save_path = config['input_path'], config['save_path']
    # 清空当前场景中的物体
    bpy.ops.wm.read_factory_settings(use_empty=True)

    # 创建集合
    if "导入" not in bpy.data.collections:
        collection = bpy.data.collections.new("导入")
        bpy.context.scene.collection.children.link(collection)
    else:
        collection = bpy.data.collections["导入"]

    # 导入 .glb 文件
    bpy.ops.import_scene.gltf(filepath=input_path)

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
        print(f"跳过文件 {input_path}: 合并后的物体不存在")
        raise Exception(f"跳过文件 {input_path}: 合并后的物体不存在")

    # 设置原点到几何中心
    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
    merged_object.location = (0, 0, 0)

    # 应用所有变换
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    
    # 计算最大尺寸并缩放到指定比例
    try:
        dimensions = merged_object.dimensions
        length = np.linalg.norm(np.array([dimensions.x, dimensions.y, dimensions.z]))
        scale_factor = 1.0 / length
        merged_object.scale = (scale_factor, scale_factor, scale_factor)

        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    except Exception as e:
        print(f"无法获取 {merged_object.name} 的尺寸: {e}")
        raise Exception(f"无法获取 {merged_object.name} 的尺寸: {e}")

    # 导出为 .obj 文件
    save_dir = os.path.dirname(save_path)
    os.makedirs(save_dir, exist_ok=True)
    glb_path = save_path.replace('.obj', '.glb')
    bpy.ops.export_scene.gltf(filepath=glb_path)
    mesh = trimesh.load(glb_path, force='glb')
    mesh.export(save_path)
    os.system(f"rm {glb_path}")
    if not judge_texture(save_dir):
        os.system(f"rm {save_dir}/*.obj")
        os.system(f"rm {save_dir}/*.mtl")
        os.system(f"rm {save_dir}/*.png")
        raise Exception(f"{save_path} has no texture")
    return


@task_wrapper
def mesh_change_format(config):
    input_path, output_path, keep_material = config['input_path'], config['output_path'], config['keep_material']
    tm_mesh = trimesh.load(input_path, force='mesh')
    if not keep_material:
        tm_mesh.visual = trimesh.visual.ColorVisuals()  
    tm_mesh.export(output_path)
    return 


@task_wrapper
def mesh_change_format_and_normalize(config):
    input_path, output_path, keep_material = config['input_path'], config['output_path'], config['keep_material']
    tm_mesh = trimesh.load(input_path, force='mesh')
    if not keep_material:
        tm_mesh.visual = trimesh.visual.ColorVisuals()  
    
    input_scale_path = config['input_scale_path']
    scale_info = json.load(open(input_scale_path, 'r'))
    verts = np.array(tm_mesh.vertices)
    tm_mesh.vertices = (verts - np.array(scale_info['center'])) / scale_info['scale']
    tm_mesh.export(output_path)
    return 
