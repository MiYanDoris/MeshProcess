import os
import argparse

import numpy as np
import trimesh 
import coacd 
coacd.set_log_level("error")

from ..util_file import write_json, get_path_cfg

class MeshProcess:
    @classmethod
    def run(self, input_params):
        obj_folder, skip = input_params

        try:
            path_cfg = get_path_cfg('customized')
            path = {}
            for k, v in path_cfg.items():
                path[k] = os.path.join(obj_folder, v)

            # coacd 
            if not os.path.exists(path['urdf_coacd']) or not skip:
                tm_mesh = trimesh.load(path['mesh_raw'], force='mesh')
                tm_mesh = self._normalize(tm_mesh)
                coacd_parts = self._coacd(tm_mesh, path['mesh_coacd'])
                self._export_urdf(coacd_parts, path['urdf_coacd'])
            
            # manifold
            if not os.path.exists(path['mesh_manifold']) or not skip:
                self._manifold(path['mesh_coacd'], path['mesh_manifold'])
            
            # simplify
            if not os.path.exists(path['mesh_simplified']) or not skip:
                self._simplify(path['mesh_coacd'], path['mesh_simplified'])
                
            if not os.path.exists(path['info_simplified']) or not skip:
                os.makedirs(os.path.dirname(path['info_simplified']), exist_ok=True)
                self._get_obj_info(path['mesh_simplified'], path['info_simplified'])
        except:
            # print(f'Fail: {obj_folder}')
            return 
        return 
    
    @staticmethod
    def _manifold(input_path, output_path):
        os.system(f'third_party/ManifoldPlus/build/manifold --input {input_path} --output {output_path} > /dev/null 2>&1')
        return
    
    @staticmethod
    def _simplify(input_path, output_path, face_num=2000):
        os.system(f'third_party/Manifold/build/simplify -i {input_path} -o {output_path} -f {face_num} -m > /dev/null 2>&1')
        return
    
    @staticmethod
    def _normalize(tm_mesh):
        verts = np.array(tm_mesh.vertices)
        center = (np.max(verts, axis=0) + np.min(verts, axis=0)) / 2
        length = np.linalg.norm(np.max(verts, axis=0) - np.min(verts, axis=0)) / 2
        tm_mesh.vertices = (verts - center) / length
        return tm_mesh
    
    @staticmethod
    def _coacd(tm_mesh, output_path):
        mesh = coacd.Mesh(tm_mesh.vertices, tm_mesh.faces)
        parts = coacd.run_coacd(mesh) # a list of convex hulls.
        mesh_parts = []
        for p in parts:
            mesh_parts.append(trimesh.Trimesh(vertices=p[0], faces=p[1]))
        combined = trimesh.util.concatenate(mesh_parts)
        combined.export(output_path)
        return mesh_parts
    
    @staticmethod
    def _export_urdf(parts, urdf_path):
        # open an XML tree
        import lxml.etree as et
        root = et.Element('robot', name='root')
        
        # Loop through all pieces, adding each as a link
        prev_link_name = None
        for i, piece in enumerate(parts):
            # Save each nearly convex mesh out to a file
            piece_name = f'convex_piece_{i}'
            piece_filename = f'convex_piece_{i}.obj'
            piece_filepath = os.path.join(os.path.dirname(urdf_path), 'meshes', piece_filename)
            os.makedirs(os.path.dirname(piece_filepath), exist_ok=True)
            piece.export(piece_filepath)
            
            link_name = 'link_{}'.format(piece_name)
            I = [['{:.2E}'.format(y) for y in x]  # NOQA
                for x in piece.moment_inertia]

            # Write the link out to the XML Tree
            link = et.SubElement(root, 'link', name=link_name)

            # Inertial information
            inertial = et.SubElement(link, 'inertial')
            et.SubElement(inertial, 'origin', xyz="0 0 0", rpy="0 0 0")
            # et.SubElement(inertial, 'mass', value='{:.2E}'.format(piece.mass))
            et.SubElement(
                inertial,
                'inertia',
                ixx=I[0][0],
                ixy=I[0][1],
                ixz=I[0][2],
                iyy=I[1][1],
                iyz=I[1][2],
                izz=I[2][2])
            
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
        tree.write(urdf_path, pretty_print=True)
        return 
    
    @staticmethod
    def _export_xml():
        raise NotImplementedError
    
    @staticmethod
    def _get_obj_info(input_path, output_path):
        tm_mesh = trimesh.load(input_path, force='mesh')
        obb_length = tm_mesh.bounding_box_oriented.primitive.extents
        gravity_center = tm_mesh.center_mass
        write_json({'gravity_center': gravity_center.tolist(), 'obb': obb_length.tolist()}, output_path)
        return 

    

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-n', '--n_process', type=int, default=10)
    parser.add_argument('-k', '--skip', action='store_false')
    args = parser.parse_args()
    
    obj_lst = [os.path.join(args.folder, obj_code) for obj_code in os.listdir(args.folder)]
    skip_lst = [args.skip] * len(obj_lst)
    
    
    
    # if args.n_process == 1:
    #     for params in param_lst:
    #         MeshProcess.run(params)
    # else:  
    #     with multiprocessing.Pool(processes=args.n_process) as pool:
    #         it = track(
    #             pool.imap_unordered(MeshProcess.run, param_lst), 
    #             total=len(param_lst), 
    #             description='processing', 
    #         )
    #         list(it)