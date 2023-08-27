import math
import os
import sys

import bpy
import numpy as np

from .camera import Camera
from .floor import get_trajectory, plot_floor, show_traj
from .sampler import get_frameidx
from .scene import setup_scene  # noqa
from .tools import delete_objs, load_numpy_vertices_into_blender, mesh_detect
from .vertices import prepare_vertices


def prune_begin_end(data, perc):
    to_remove = int(len(data)*perc)
    if to_remove == 0:
        return data
    return data[to_remove:-to_remove]


def render_current_frame(path):
    bpy.context.scene.render.filepath = path
    bpy.ops.render.render(use_viewport=True, write_still=True)



def render(npydata, frames_folder, *, mode, faces_path, gt=False,
           exact_frame=None, num=8, downsample=True,
           canonicalize=True, always_on_floor=False, denoising=True,
           oldrender=True,jointstype="mmm", res="high", init=True,
           accelerator='gpu',device=[0]):
    if init:
        # Setup the scene (lights / render engine / resolution etc)
        # 设置分辨率，光线，渲染引擎等
        setup_scene(res=res, denoising=denoising, oldrender=oldrender,accelerator=accelerator,device=device)

    # 只渲染mesh
    # is_mesh = mesh_detect(npydata)

    # Put everything in this folder
    # 设置输出文件夹
    if mode == "video":
        if always_on_floor:
            frames_folder += "_of"
        os.makedirs(frames_folder, exist_ok=True)

    elif mode == "sequence":
        img_name, ext = os.path.splitext(frames_folder)
        if always_on_floor:
            img_name += "_of"
        img_path = f"{img_name}{ext}"

    elif mode == "frame":
        img_name, ext = os.path.splitext(frames_folder)
        if always_on_floor:
            img_name += "_of"
        img_path = f"{img_name}_{exact_frame}{ext}"

    # remove X% of begining and end
    # as it is almost always static
    # in this part
    # 去除开头结尾
    if mode == "sequence":
        perc = 0.2 # 去除的比例
        npydata = prune_begin_end(npydata, perc)

    # if is_mesh:
    from .meshes import Meshes
    # 设置mesh数据（顶点，faces，颜色，材质等）
    data = Meshes(npydata, gt=gt, mode=mode,
                    faces_path=faces_path,
                    canonicalize=canonicalize,
                    always_on_floor=always_on_floor)
    # else:
    #     from .joints import Joints
    #     data = Joints(npydata, gt=gt, mode=mode,
    #                   canonicalize=canonicalize,
    #                   always_on_floor=always_on_floor,
    #                   jointstype=jointstype)

    # Number of frames possible to render
    nframes = len(data)

    # Create a floor
    # 画一个地板
    plot_floor(data.data, big_plane=False)

    # initialize the camera
    # 设置相机位置
    camera = Camera(first_root=data.get_root(0), mode=mode)

    # 获取需要渲染的索引
    frameidx = get_frameidx(mode=mode, nframes=nframes,
                            exact_frame=exact_frame,
                            frames_to_keep=num)

    nframes_to_render = len(frameidx)

    # center the camera to the middle
    if mode == "sequence":
        camera.update(data.get_mean_root())

    imported_obj_names = []
    for index, frameidx in enumerate(frameidx):
        if mode == "sequence":
            frac = index / (nframes_to_render-1)
            mat = data.get_sequence_mat(frac)
        else:
            mat = data.mat
            camera.update(data.get_root(frameidx))

        islast = index == (nframes_to_render-1)

        objname = data.load_in_blender(frameidx, mat)
        name = f"{str(index).zfill(4)}"

        if mode == "video":
            path = os.path.join(frames_folder, f"frame_{name}.png")
        else:
            path = img_path

        if mode == "sequence":
            imported_obj_names.extend(objname)
        elif mode == "frame":
            camera.update(data.get_root(frameidx))

        if mode != "sequence" or islast:
            render_current_frame(path)
            delete_objs(objname)

    # bpy.ops.wm.save_as_mainfile(filepath="/Users/mathis/TEMOS_github/male_line_test.blend")
    # exit()

    # remove every object created
    delete_objs(imported_obj_names)
    delete_objs(["Plane", "myCurve", "Cylinder"])

    if mode == "video":
        return frames_folder
    else:
        return img_path
