# 使用blender渲染MESH

## 所需环境

+ [blender 3.6.2](https://download.blender.org/release/Blender3.6/blender-3.6.2-windows-x64.msi)

## 安装python库

blender可以使用python脚本执行渲染，只需要将blender**内置的python**安装代码执行所需的python库即可。

### For Windows

```bash
cd /path/to/blender/version/python

.\bin\python.exe -m pip install natsort --target=.\lib\site-packages
.\bin\python.exe -m pip install numpy --target=.\lib\site-packages
.\bin\python.exe -m pip install matplotlib --target=.\lib\site-packages
.\bin\python.exe -m pip install hydra-core --upgrade --target=.\lib\site-packages
.\bin\python.exe -m pip install hydra_colorlog --upgrade --target=.\lib\site-packages
.\bin\python.exe -m pip install moviepy --target=.\lib\site-packages
.\bin\python.exe -m pip install shortuuid --target=.\lib\site-packages
```

## RUN

使用blender内置的python执行脚本，首先需要将blender的路径添加到环境变量，或者进入到blender的路径执行下述脚本

```bash
/path/to/blender/> blender --background --python /path/to/script/render.py -- #--args 其余参数
```

### 脚本参数

```python
"--input_mode", type=str, default="npy", choices=["npy", "dir"], help="文件类型"
"--npy_path", type=str, default="", help="npy文件地址" # 若输入模式为dir则不需要
"--dir", type=str, default="", help="输入文件地址" # 若输入模式为npy则不需要
"--res_dir", type=str, default="./", help="渲染结果保存地址"
"--data_dir", type=str, default="", help="需要渲染的文件地址"
"--mode", type=str, default="frame", choices=["frame", "video", "squence"], help="渲染模式"
"--exact_frame", type=int, default=None, help="渲染第几帧"
"--num", type=int, default=8, help="渲染几帧"
"--faces_path", type=str, default="./resource/smplh.faces", help="mesh面信息"
"--not_on_floor", action="store_false", help="是否保持mesh在地面之上"
"--resolution", type=str, choices=["ultra", "high", "med", "low"], default="med", help="渲染分辨率"
"--acclerator", type=str, default="gpu", help="使用gpu加速"
```

### 数据说明

需要预先准备以下两个文件：

+ npy文件中包含若干帧的顶点信息，`shape(frame, verts, 3)`

+ faces文件包含mesh的面信息，`shape(faces, 3)`



## 参考

[motion_latent_diffusion](https://github.com/ChenFengYe/motion-latent-diffusion)