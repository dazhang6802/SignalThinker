import copy

def timing_plan(configs, plansequence, phasevolume):
    saturation_gap = configs["SaturationGap"]
    phases = configs["phases"]
    phaseinstage = configs["phaseinstage"]
    phaseintergreen = configs["phaseintergreen"]
    stages = configs["stages"]
    # 构建类Ring结构
    rings = [[], []]
    lead_lag = []
    step = 0
    # count = 0
    for stage in plansequence:
        if type(stage) == int:
            lead_lag.append(0)
            rings[0].append(0)
            rings[1].append(0)
            ringno = 0
            # 阶段中的参与优化的关键相位填入环结构
            stagei = stage - 1
            for phasei in range(len(phaseinstage[stagei])):
                if phaseinstage[stagei][phasei] == 7:  # 只选择参与优化的关键相位
                    rings[ringno][step] = phasei + 1
                    ringno += 1
                    if ringno > 1:
                        break
            # 根据冲突关系调整环结构
            if step > 0:
                fromphase = rings[0][step - 1] - 1
                tophase = rings[0][step] - 1
                # 如果不冲突，则交换位置
                if phaseintergreen[fromphase][tophase] == 0:
                    i = rings[0][step]
                    rings[0][step] = rings[1][step]
                    rings[1][step] = i
            step = step + 1
        else:
            lead_lag[step - 1] = 1

    # 梳理环交通数据
    ring_volume = []
    for ring in range(len(rings)):
        ring_volume.append([])
        for phase in rings[ring]:
            if phase > 0:
                ring_volume[ring].append(phasevolume[phase - 1])
            else:
                ring_volume[ring].append(0)

    # 计算间隔间隔损失时间
    # ring0:1 2 3 4
    # ring1:5 6 7 8
    sum_interval = 0
    for step in range(len(rings[0])):
        P1 = rings[0][step] - 1
        P2 = rings[0][(step + 1) % len(rings[0])] - 1
        P5 = rings[1][step] - 1
        P6 = rings[1][(step + 1) % len(rings[0])] - 1
        sum_interval += max(
            phaseintergreen[P1][P2],
            phaseintergreen[P5][P6]
        )

    # 计算关键流量
    sum_volume = 0
    step = 0
    while step < len(lead_lag):
        # 无搭接，选本步最大流量
        if lead_lag[step] == 0:
            sum_volume += max(ring_volume[0][step], ring_volume[1][step])
            step = step + 1
        else:
            # 有搭接选搭接相位环的最大流量
            sum_volume += max(ring_volume[0][step] + ring_volume[0][step + 1],
                              ring_volume[1][step + 1] + ring_volume[1][step + 1])
            step = step + 2

    # 依据关键流量生成周期，最小60秒 最大180秒
    cycle = 60
    while cycle <= 180:
        capacity = int(3600.0 / cycle * (cycle - sum_interval) / saturation_gap)
        if capacity > sum_volume:
            break
        cycle = cycle + saturation_gap

    cycle = round(cycle)
    if cycle > 180:
        cycle = 180

    # 计算环相位绿信比
    ring_splits = []
    for ring in range(len(rings)):
        ring_splits.append([])
        for phasei in range(len(rings[ring])):
            if rings[ring][phasei] > 0:
                split = int(saturation_gap * ring_volume[ring][phasei] / (3600.0 / cycle))
                split = split + phases[rings[ring][phasei] - 1]["StartDelay"]
                if split < phases[rings[ring][phasei] - 1]["MinimumGreen"]:
                    split = phases[rings[ring][phasei] - 1]["MinimumGreen"]
                # 计算当前相位与下一个相位绿间隔
                interval = phaseintergreen[rings[ring][phasei] - 1][rings[ring][(phasei + 1) % len(rings[0])] - 1]
                split = split + interval
                ring_splits[ring].append(split)
            else:
                ring_splits[ring].append(0)

    ring_plan = {"cycle": cycle, "offset": 0, "split": ring_splits, "rings": rings}

    # 以下是phases in stage类方案
    plan_stages = []
    plan_splits = []
    step = 0
    sequencei = 0
    while step < len(lead_lag):
        if lead_lag[step] == 1:
            leadok = False
            # 有搭接，选择最合适搭接阶段
            # ring0:1 2 3 4
            # ring1:5 6 7 8
            # T1>T5 and T6>T2    or  T1<T5 and T6<T2
            # 同阶段时间差足够大
            T1 = ring_splits[0][step]
            T2 = ring_splits[0][step + 1]
            T5 = ring_splits[1][step]
            T6 = ring_splits[1][step + 1]
            P1 = rings[0][step]
            P2 = rings[0][step + 1]
            P5 = rings[1][step]
            P6 = rings[1][step + 1]
            # 同阶段间时间差足够大？
            if abs(T1 - T5) > saturation_gap and abs(T2 - T6) > saturation_gap:
                # 生成可能的相位组合
                phaselist = []
                if T1 > T5 and T6 > T2:
                    phaselist = [P1, P6]
                elif T1 < T5 and T6 < T2:
                    phaselist = [P2, P5]
                if len(phaselist) > 0:
                    # 备选阶段中是否存在对应的相位组合
                    for stage in plansequence[sequencei + 1]:
                        # 确认搭接相位与阶段关系
                        if phaseinstage[stage - 1][phaselist[0] - 1] > 0 \
                                and phaseinstage[stage - 1][phaselist[1] - 1] > 0:
                            # 差值最小的搭接值
                            lead_lag_time = min(abs(T1 - T5), abs(T2 - T6))
                            # 检查各个阶段最小时间限制
                            if lead_lag_time < stages[stage - 1]["Minimum"]:
                                # lead_lag阶段不满足lead-lag最小限制
                                break
                            # 前一个阶段
                            prestage = plansequence[sequencei]
                            prestagetime = max(ring_splits[0][step], ring_splits[1][step]) - lead_lag_time
                            if prestagetime < stages[prestage - 1]["Minimum"]:
                                # 阶段时间不满足前一个阶段最小限制
                                break
                            # 后一个阶段
                            nextstage = plansequence[sequencei + 2]
                            nextstagetime = max(ring_splits[0][step + 1], ring_splits[1][step + 1]) - lead_lag_time
                            if nextstagetime < stages[nextstage - 1]["Minimum"]:
                                # 阶段时间不满足前一个阶段最小限制
                                break
                            # 加前一个阶段
                            plan_stages.append(prestage)
                            plan_splits.append(prestagetime)
                            step += 1
                            sequencei += 2
                            # 加入搭接lead-lag阶段
                            plan_stages.append(stage)
                            plan_splits.append(lead_lag_time)
                            # 加入后一个阶段
                            plan_stages.append(nextstage)
                            plan_splits.append(nextstagetime)
                            step += 1
                            sequencei += 1
                            leadok = True
                            break
            if leadok:
                continue
        # 无搭接，选本步双环中最大时间
        stagetime = max(ring_splits[0][step], ring_splits[1][step])
        plan_stages.append(plansequence[sequencei])
        plan_splits.append(stagetime)
        if lead_lag[step] == 1:
            sequencei += 2
        else:
            sequencei += 1
        step += 1

    # 校验周期
    cycle = 0
    for split in plan_splits:
        cycle = cycle + split
    stage_plan = {"cycle": cycle, "offset": 0, "splits": plan_splits, "stages": plan_stages}
    return ring_plan, stage_plan



def stage_plan():
    global config
    if config["curplan"] is None:
        config["curplan"] = copy.deepcopy(config["stageplan"])
        config["step"] = 0
    if config["curplan"]["splits"][config["step"]] > 0:
        config["curplan"]["splits"][config["step"]] -= 1
        config["curstage"] = config["curplan"]["stages"][config["step"]]
        print(config["curstage"], config["curplan"]["splits"][config["step"]])
    else:
        config["step"] += 1
        if config["step"] == len(config["curplan"]["stages"]):
            config["curplan"] = None




if __name__ == "__main__":
    config = {}
    config["SaturationGap"] = 2.5
    # phases
    config["phases"] = [
        {"MinimumGreen": 5, "StartDelay": 3,"detectors":[],"s_gap":2.5},
        {"MinimumGreen": 5, "StartDelay": 3,"detectors":[],"s_gap":2.5},
        {"MinimumGreen": 5, "StartDelay": 3,"detectors":[],"s_gap":2.5},
        {"MinimumGreen": 5, "StartDelay": 3,"detectors":[],"s_gap":2.5},
        {"MinimumGreen": 5, "StartDelay": 3,"detectors":[],"s_gap":2.5},
        {"MinimumGreen": 5, "StartDelay": 3,"detectors":[],"s_gap":2.5},
        {"MinimumGreen": 5, "StartDelay": 3,"detectors":[],"s_gap":2.5},
        {"MinimumGreen": 5, "StartDelay": 3,"detectors":[],"s_gap":2.5}
    ]

    # Phase Inter_green,from phase #row ,col to Phase #col,0-nor conflict
    config["phaseintergreen"] = [
        [0, 5, 5, 5, 0, 0, 5, 5],
        [5, 0, 5, 5, 0, 0, 5, 5],
        [5, 5, 0, 5, 5, 5, 0, 0],
        [5, 5, 5, 0, 5, 5, 0, 0],
        [0, 0, 5, 5, 0, 5, 5, 5],
        [0, 0, 5, 5, 5, 0, 5, 5],
        [5, 5, 0, 0, 5, 5, 0, 5],
        [5, 5, 0, 0, 5, 5, 5, 0]
    ]

    # stages 阶段属性
    config["stages"] = [
        {"Minimum": 5},
        {"Minimum": 5},
        {"Minimum": 5},
        {"Minimum": 5},
        {"Minimum": 5},
        {"Minimum": 5},
        {"Minimum": 5},
        {"Minimum": 5}
    ]

    # bit0-存在(0不存在,1存在) bit1-固定(0按需,1固定) bit2-优化(0-不参与优化 1-参与优化)
    # 1 按需存在  3 固定存在 7 固定存在且优化
    # stage=#row  phase=#col
    config["phaseinstage"] = [
        [7, 0, 0, 0, 0, 0, 0, 0],
        [0, 7, 0, 0, 0, 7, 0, 0],
        [0, 0, 7, 0, 0, 0, 7, 0],
        [0, 0, 0, 7, 0, 0, 0, 7],
        [7, 0, 0, 0, 0, 7, 0, 0],
        [0, 7, 0, 0, 0, 0, 0, 0],
        [0, 0, 7, 0, 0, 0, 0, 7],
        [0, 0, 0, 7, 0, 0, 7, 0]
    ]

    config["detectors"]=[
        {
            "presence":0, #实时状态
            "lastchange":0,#最近一次状态变化时间
            "datetime":[],#最近一次统计数据时间
            "volume":[],#流量
            "occupancy":[],
            "headway":[],
            "begintime":0, #实时数据开始时刻
            "real_occ":0, #实时占有率
            "real_volume":0, #实时流量
            "real_headway":0 #实时车头时距
        }
    ]


    # int 表示固定存在，list为可选阶段，tuple为必选其一阶段
    plansequence = [1, [5, 6], 2, 3, [7, 8], 4]

    phasevolume = [270, 0, 80, 400,
                   0, 485, 120, 210]

    config["ringplan"], config["stageplan"] = timing_plan(config, plansequence, phasevolume)
    config["curplan"] = None
    config["step"] = 0
    config["curstage"] = 0


    print("starting")
