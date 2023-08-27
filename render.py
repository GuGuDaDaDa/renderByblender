import os
import random
import shutil
import sys
from pathlib import Path

import natsort

try:
    import bpy

    sys.path.append(os.path.dirname(bpy.data.filepath))
except ImportError:
    raise ImportError(
        "Blender is not properly installed or not launch properly. See README.md to have instruction on how to install and use blender."
    )

import blender.launch.blender
import blender.launch.prepare  # noqa
import blender.config
from blender.config import parse_args
# from blender.utils.joints import smplh_to_mmm_scaling_factor


def extend_paths(path, keyids, *, onesample=True, number_of_samples=1):
    if not onesample:
        template_path = str(path / "KEYID_INDEX.npy")
        paths = [
            template_path.replace("INDEX", str(index)) for i in range(number_of_samples)
        ]
    else:
        paths = [str(path / "KEYID.npy")]

    all_paths = []
    for path in paths:
        all_paths.extend([path.replace("KEYID", keyid) for keyid in keyids])
    return all_paths


def render_cli() -> None:
    # parse options
    cfg = parse_args()  # parse config file
    print(cfg)
    
    # cfg.FOLDER = cfg.RENDER.FOLDER

    if cfg.input_mode.lower() == "npy":
        output_dir = Path(os.path.dirname(cfg.res_dir))
        paths = [cfg.npy_path]
    elif cfg.input_mode.lower() == "dir":
        output_dir = Path(cfg.res_dir)
        paths = []
        # 对文件排序
        file_list = natsort.natsorted(os.listdir(cfg.dir))
        
        # 随机开始位置
        # begin_id = random.randrange(0, len(file_list))
        # file_list = file_list[begin_id:]+file_list[:begin_id]

        # render mesh npy first
        for item in file_list:
            if item.endswith("_mesh.npy"):
                paths.append(os.path.join(cfg.dir, item))

        # then render other npy
        for item in file_list:
            if item.endswith(".npy") and not item.endswith("_mesh.npy"):
                paths.append(os.path.join(cfg.dir, item))
        
        # render obj file
        for item in file_list:
            if item.endswith(".obj"):
                paths.append(os.path.join(cfg.dir, item))
        
        # render ply file
        for item in file_list:
            if item.endswith(".ply"):
                paths.append(os.path.join(cfg.dir, item))

        print(f"begin to render for {paths[0]}")

    import numpy as np

    from blender.render.blender import render
    from blender.render.blender.tools import mesh_detect
    from blender.render.video import Video
    init = True
    for path in paths:
        # check existed mp4 or under rendering
        if cfg.mode == "video":
            if os.path.exists(path.replace(".npy", ".mp4")) or os.path.exists(path.replace(".npy", "_frames")):
                print(f"npy is rendered or under rendering {path}")
                continue
        else:
            # check existed png
            if os.path.exists(path.replace(".npy", ".png")):
                print(f"npy is rendered or under rendering {path}")
                continue
        
        # 输出路径
        if cfg.mode == "video":
            frames_folder = os.path.join(
                output_dir, path.replace(".npy", "_frames").split('/')[-1])
            os.makedirs(frames_folder, exist_ok=True)
        else:
            frames_folder = os.path.join(
                output_dir, path.replace(".npy", ".png").split('/')[-1])

        try:
            data = np.load(path)
            print(data.shape)
            # 渲染关节点
            # if cfg.RENDER.JOINT_TYPE.lower() == "humanml3d":
            #     is_mesh = mesh_detect(data)
            #     if not is_mesh:
            #         data = data * smplh_to_mmm_scaling_factor
        except FileNotFoundError:
            print(f"{path} not found")
            continue

        out = render(
            data,
            frames_folder,
            # canonicalize=cfg.RENDER.CANONICALIZE,
            exact_frame=cfg.exact_frame,
            num=cfg.num,
            mode=cfg.mode,
            faces_path=cfg.faces_path,
            # downsample=cfg.RENDER.DOWNSAMPLE,
            always_on_floor=cfg.not_on_floor,
            # oldrender=cfg.RENDER.OLDRENDER,
            # jointstype=cfg.RENDER.JOINT_TYPE.lower(),
            res=cfg.resolution,
            init=init,
            # gt=cfg.RENDER.GT,
            accelerator=cfg.acclerator,
            device=[0],
        )

        init = False

        if cfg.mode == "video":
            if cfg.RENDER.DOWNSAMPLE:
                video = Video(frames_folder, fps=cfg.RENDER.FPS)
            else:
                video = Video(frames_folder, fps=cfg.RENDER.FPS)

            vid_path = frames_folder.replace("_frames", ".mp4")
            video.save(out_path=vid_path)
            shutil.rmtree(frames_folder)
            print(f"remove tmp fig folder and save video in {vid_path}")

        else:
            print(f"Frame generated at: {out}")


if __name__ == "__main__":
    render_cli()
