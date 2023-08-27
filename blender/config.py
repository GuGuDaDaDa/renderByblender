import importlib
from argparse import ArgumentParser
from omegaconf import OmegaConf
import os


def parse_args():
    parser = ArgumentParser()
    
    parser.add_argument("--input_mode", type=str, default="npy", choices=["npy", "dir"], help="文件类型")
    parser.add_argument("--npy_path", type=str, default="", help="npy文件地址") # 若输入模式为dir则不需要
    parser.add_argument("--dir", type=str, default="", help="输入文件地址") # 若输入模式为npy则不需要
    parser.add_argument("--res_dir", type=str, default="./", help="渲染结果保存地址")
    parser.add_argument("--data_dir", type=str, default="", help="需要渲染的文件地址")
    parser.add_argument("--mode", type=str, default="frame", choices=["frame", "video", "squence"], help="渲染模式")
    parser.add_argument("--exact_frame", type=int, default=None, help="渲染第几帧")
    parser.add_argument("--num", type=int, default=8, help="渲染几帧")
    parser.add_argument("--faces_path", type=str, default="./resource/smplh.faces", help="mesh面信息")
    parser.add_argument("--not_on_floor", action="store_false", help="是否保持mesh在地面之上")
    parser.add_argument("--resolution", type=str, choices=["ultra", "high", "med", "low"], default="med", help="渲染分辨率")
    parser.add_argument("--acclerator", type=str, default="gpu", help="使用gpu加速")
    
    # args, _ = parser.parse_known_args()
    args = parser.parse_args()
    
    return args