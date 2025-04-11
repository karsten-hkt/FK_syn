import configparser
import subprocess

# 定义所有参数的默认值
DEFAULTS = {
    'model': 'default_model',
    'nt': 256,
    'dt': 1,
    'degrees': False,
    'f1': 0,
    'f2': 0,
    'smth': 1,
    'dk': 0.05,
    'taper': 0.3,
    'min_slowness': None,
    'max_slowness': None,
    'kmax': None,
    'receiver_depth': 0,
    'wave_direction': None,
    'debug_cmd': False,
    'mag': '4.5',  # 默认震级
    'strike': None,
    'dip': None,
    'rake': None,
    'azimuth': None,
    'duration': 0.5,  # 默认时长
    'rise_time': 0.5,  # 默认上升时间
    'filter': None,  # 默认不应用滤波器
    'displacement': False, # 计算位移，False为速度场
    'static_displacement': False,  # 默认不计算静态位移
    'source_time_fn': None,  # 默认不指定源时间函数
    'convolve_q': False,  # 默认不卷积 Futterman Q 操作符
}

def read_config(config_file):
    config = configparser.ConfigParser()
    config.read(config_file)
    return config

def get_param(config, section, param, default):
    value = config.get(section, param, fallback=None)
    return value if value not in [None, 'None'] else default

def command_fk_perl_program(config, depth, dist_list):
    # FK program name
    FK_program = get_param(config, 'programs_name', 'fk_program', 'fk.pl') 
    # 构造命令行
    command = [FK_program]

    # 获取每个参数的值，如果没有提供则使用默认值
    model = get_param(config, 'FK_setting', 'model', DEFAULTS['model'])
    nt = get_param(config, 'FK_setting', 'nt', DEFAULTS['nt'])
    dt = get_param(config, 'FK_setting', 'dt', DEFAULTS['dt'])
    degrees = config.getboolean('FK_setting', 'degrees', fallback=DEFAULTS['degrees'])
    f1 = get_param(config, 'FK_setting', 'f1', DEFAULTS['f1'])
    f2 = get_param(config, 'FK_setting', 'f2', DEFAULTS['f2'])
    smth = get_param(config, 'FK_setting', 'smth', DEFAULTS['smth'])
    dk = get_param(config, 'FK_setting', 'dk', DEFAULTS['dk'])
    taper = get_param(config, 'FK_setting', 'taper', DEFAULTS['taper'])
    min_slowness = get_param(config, 'FK_setting', 'min_slowness', DEFAULTS['min_slowness'])
    max_slowness = get_param(config, 'FK_setting', 'max_slowness', DEFAULTS['max_slowness'])
    kmax = get_param(config, 'FK_setting', 'kmax', DEFAULTS['kmax'])
    receiver_depth = get_param(config, 'FK_setting', 'receiver_depth', DEFAULTS['receiver_depth'])
    wave_direction = get_param(config, 'FK_setting', 'wave_direction', DEFAULTS['wave_direction'])
    debug_cmd = config.getboolean('FK_setting', 'debug_cmd', fallback=DEFAULTS['debug_cmd'])

    # -M 参数
    model_depth = f"{model}/{depth}"
    command.append(f'-M{model_depth}')

    # -D 参数: 如果 degrees 为 true，则添加 -D
    if degrees:
        command.append('-D')

    # -H 参数: 如果 f1 和 f2 都有值，则添加 -H
    if f1 and f2:
        command.append(f'-H{f1}/{f2}')

    # -N 参数: 添加 nt, dt, smth, dk, taper
    command.append(f'-N{nt}/{dt}/{smth}/{dk}/{taper}')

    # -P 参数: 如果 slowness 参数有值，则添加 -P
    if min_slowness is not None and max_slowness is not None and kmax is not None:
        command.append(f'-P{min_slowness}/{max_slowness}/{kmax}')

    # -R 参数: 如果 receiver_depth 有值，则添加 -R
    if receiver_depth is not None:
        command.append(f'-R{str(receiver_depth)}')

    # -U 参数: 如果 wave_direction 有值，则添加 -U
    if wave_direction is not None:
        command.append(f'-U{str(wave_direction)}')

    # -X 参数: 如果 debug_cmd 有值，则添加 -X
    if debug_cmd:
        command.append('-X')

    # 加入台站距离
    command_S0 = command.copy()
    command_S0.append('-S0')
    for dist in dist_list:
        # 将每个 dist 添加到命令中
        command_S0.append(f"{dist}")
    command_S2 = command.copy()
    command_S2.append('-S2')
    for dist in dist_list:
        # 将每个 dist 添加到命令中
        command_S2.append(f"{dist}")

    # 执行命令
    print(f"Running command for depth {depth}: {' '.join(command_S0)}")
    result = subprocess.run(command_S0, capture_output=True, text=True)
    print(f"Running command for depth {depth}: {' '.join(command_S2)}")
    result_S2 = subprocess.run(command_S2, capture_output=True, text=True)
    if result.returncode == 0:
        print(f"Perl program executed successfully for depth {depth}!")
        print(result.stdout)
    else:
        print(f"Perl program execution failed for depth {depth}!")
        print(result.stderr)

def command_syn_program(config,azimuth,st_name,dist,depth):
    # syn program name
    syn_program = get_param(config, 'programs_name', 'syn_program', 'syn')
    
    # 构造命令行
    command = [f'{syn_program}']

    # 必填参数
    mag = get_param(config, 'syn', 'mag', DEFAULTS['mag'])
    strike = get_param(config, 'syn', 'strike', DEFAULTS['strike'])
    dip = get_param(config, 'syn', 'dip', DEFAULTS['dip'])
    rake = get_param(config, 'syn', 'rake', DEFAULTS['rake'])
    displacement = config.getboolean('syn', 'displacement', fallback=DEFAULTS['displacement'])
    # 生成 -M 参数
    command.append(f"-M{mag}/{strike}/{dip}/{rake}")
    command.append(f"-A{azimuth}")

    if displacement:
        command.append("-I")

    # 可选参数处理
    duration = get_param(config, 'syn', 'duration', DEFAULTS['duration'])
    rise_time = get_param(config, 'syn', 'rise_time', DEFAULTS['rise_time'])
    if duration:
        command.append(f"-D{duration}/{rise_time}")
    
    # -F 参数
    filter_order = get_param(config, 'syn', 'filter_order', DEFAULTS['filter'])
    if filter_order:
        command.append(f"-F{filter_order}")
    
    # -G 参数
    model_name = get_param(config, 'FK_setting', 'model', DEFAULTS['model'])+'_'+str(int(depth))
    receiver_depth = get_param(config, 'FK_setting', 'receiver_depth', DEFAULTS['receiver_depth'])
    green_func = f"{model_name}/{dist}_{receiver_depth}.grn.0"
    if green_func:
        command.append(f"-G{green_func}")
    
    # -O 参数
    output_sac = f'{st_name}_{depth}_{dist}_{azimuth}'
    if output_sac:
        command.append(f"-O{output_sac}")
    
    # -P 参数
    static_displacement = config.getboolean('syn', 'static_displacement', fallback=DEFAULTS['static_displacement'])
    if static_displacement:
        command.append('-P')

    # -S 参数
    source_time_fn = get_param(config, 'syn', 'source_time_fn', DEFAULTS['source_time_fn'])
    if source_time_fn:
        command.append(f"-S{source_time_fn}")

    # -Q 参数
    convolve_q = config.getboolean('syn', 'convolve_q', fallback=DEFAULTS['convolve_q'])
    if convolve_q:
        command.append("-Q")

    # 打印最终的命令
    print(f"Running command: {' '.join(command)}")
    result = subprocess.run(command, capture_output=True, text=True)
    
    if result.returncode == 0:
        print("Syn program executed successfully!")
        print(result.stdout)
    else:
        print("Syn program execution failed!")
        print(result.stderr)
