import configparser
import os.path
import subprocess
from read_config import read_config, get_param, command_syn_program, command_fk_perl_program
import pandas as pd
import shutil
import glob

config_file = 'config.ini'  # 配置文件路径
config = read_config(config_file)

# 读取台站数据
station_file = str(get_param(config, 'input_output_setting', 'station_file', 'station'))
stations = pd.read_csv(station_file, sep=' ',header=None, names=['station_name', 'dist', 'az'])
print('------station-------')
print(stations)
# 打印模型数据
model_file = str(get_param(config, 'input_output_setting', 'model_file', 'model'))
model = pd.read_csv(model_file, sep=' ',header=None, names=['thickness', 'vs', 'vp', 'rho'])
print('------velocity model-------')
print(model)
# 获取 depth_min, depth_max, depth_step 并遍历深度
depth_min = int(get_param(config, 'FK_setting', 'depth_min', 10))
depth_max = int(get_param(config, 'FK_setting', 'depth_max', 15))
depth_step = int(get_param(config, 'FK_setting', 'depth_step', 1))

# 遍历深度并执行 FK.pl
for depth in range(depth_min, depth_max + 1, depth_step):
    dist_list = stations['dist'].tolist()  # 获取台站的距离信息并转化为列表
    command_fk_perl_program(config, depth, dist_list)
    # 遍历每个台站，执行相应操作
    for _, station in stations.iterrows():
        # 提取台站的信息：站点名称、距离、方位角
        station_name = station['station_name']
        dist = station['dist']
        azimuth = station['az']
        
        print(f"Processing station {station_name} at distance {dist} and azimuth {azimuth} for depth {depth}")
        
        # 调用 syn 程序处理台站
        command_syn_program(config, azimuth, station_name, dist, depth)

        if not os.path.exists(f'{station_name}'):
            os.mkdir(f'{station_name}')

        # 获取匹配的文件
        file_pattern = f"{station_name}_*"
        matching_files = glob.glob(file_pattern)

        if not matching_files:
            print(f"Warning: No files found matching pattern {file_pattern}")
            continue  # 跳过当前 station，避免 `shutil.move()` 抛出错误

        # 移动文件
        for file in matching_files:
            shutil.move(file, station_name)
