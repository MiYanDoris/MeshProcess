import os 
import sys 
from copy import deepcopy
import logging 
import traceback
import multiprocessing
from tqdm import tqdm
import trimesh
import numpy as np
import lxml.etree as et

from concurrent.futures import ThreadPoolExecutor

def mesh_convex_decomp(config):
    input_path, output_path, quiet = config['input_path'], config['output_path'], config['quiet']
    command = f'third_party/CoACD/build/main -i {input_path} -o {output_path} -t 0.05'
    if quiet:
        command += ' > /dev/null 2>&1'
    os.system(command)
    return 

def mesh_remove_small_piece(config):
    input_path, output_path, min_volume = config["input_path"], config["output_path"], config['min_volume']
    parts = trimesh.load(input_path, force='mesh').split()
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


def export_urdf(config):
    input_path, export_mesh, output_path = config['input_path'], config['export_mesh'], config['output_path']
    
    parts = trimesh.load(input_path, force='mesh').split()
    root = et.Element('robot', name='root')
    
    prev_link_name = None
    for i, piece in enumerate(parts):
        piece_name = f'convex_piece_{i}'
        piece_filename = f'meshes/convex_piece_{i}.obj'
        piece_filepath = os.path.join(os.path.dirname(output_path), piece_filename)
        if export_mesh:
            os.makedirs(os.path.dirname(piece_filepath), exist_ok=True)
            piece.export(piece_filepath)

        link_name = 'link_{}'.format(piece_name)
        I = [['{:.2E}'.format(y) for y in x]  # NOQA
            for x in piece.moment_inertia]
        link = et.SubElement(root, 'link', name=link_name)
        inertial = et.SubElement(link, 'inertial')
        et.SubElement(inertial, 'origin', xyz="0 0 0", rpy="0 0 0")
        # et.SubElement(inertial, 'mass', value='{:.2E}'.format(piece.mass))
        et.SubElement(inertial, 'inertia', ixx=I[0][0], ixy=I[0][1], ixz=I[0][2],
            iyy=I[1][1], iyz=I[1][2], izz=I[2][2])
        
        # Visual Information
        visual = et.SubElement(link, 'visual')
        et.SubElement(visual, 'origin', xyz="0 0 0", rpy="0 0 0")
        geometry = et.SubElement(visual, 'geometry')
        et.SubElement(geometry, 'mesh', filename=piece_filename, scale="1.0 1.0 1.0")
        
        # Collision Information
        collision = et.SubElement(link, 'collision')
        et.SubElement(collision, 'origin', xyz="0 0 0", rpy="0 0 0")
        geometry = et.SubElement(collision, 'geometry')
        et.SubElement(geometry, 'mesh', filename=piece_filename, scale="1.0 1.0 1.0")

        # Create rigid joint to previous link
        if prev_link_name is not None:
            joint_name = '{}_joint'.format(link_name)
            joint = et.SubElement(root,
                                'joint',
                                name=joint_name,
                                type='fixed')
            et.SubElement(joint, 'origin', xyz="0 0 0", rpy="0 0 0")
            et.SubElement(joint, 'parent', link=prev_link_name)
            et.SubElement(joint, 'child', link=link_name)

        prev_link_name = link_name

    # Write URDF file
    tree = et.ElementTree(root)
    tree.write(output_path, pretty_print=True)
    
    return 

config = {
    'input_path': '/mnt/afs/yangtaoyu/LIBERO/data/debug/LIBERO_wooden_cabinet/wooden_cabinet.obj',
    'output_path': 'debug.obj',
    'quiet': False,
    'logger': False,
    'skip': False,
    'debug': False
}

mesh_convex_decomp(config)

config['input_path'] = 'debug.obj'
config['output_path'] = 'debug2.obj'
config['min_volume'] = 1e-4
mesh_remove_small_piece(config)

config['input_path'] = 'debug2.obj'
config['export_mesh'] = True
config['output_path'] = 'outputs/debug/debug.urdf'
export_urdf(config)