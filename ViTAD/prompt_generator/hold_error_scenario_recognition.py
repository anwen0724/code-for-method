
import re
from typing import Dict, Tuple, Any




scenario_002_keywords = {
    "核心关键词": {
        "快速路径": [
            "快速路径", "fast path", "shortest path", "minimum delay",
            "最短路径", "最小延迟", "快速通道", "直通路径",
            "bypass path", "express path", "速度过快"
        ],
        "直连特征": [
            "直连", "直通", "bypass", "wire connection",
            "direct connection", "零延迟", "无逻辑", "直接连接",
            "wire through", "pass through", "透传"
        ],
        "保持违规": [
            "保持时间违规", "hold violation", "hold time violation",
            "保持时间不足", "hold slack negative", "hold margin",
            "保持余量", "hold time failure", "保持失败"
        ]
    },
    "支撑关键词": {
        "控制信号": [
            "控制信号", "control signal", "使能信号", "enable signal",
            "选择信号", "select signal", "控制位", "control bit",
            "标志位", "flag bit", "状态位", "status bit"
        ],
        "简单逻辑": [
            "反相器", "inverter", "缓冲器", "buffer", "非门", "not gate",
            "简单门", "simple gate", "单级逻辑", "single stage",
            "最少逻辑", "minimal logic", "基本门"
        ],
        "延迟描述": [
            "延迟极小", "minimal delay", "几乎无延迟", "near zero delay",
            "亚纳秒", "sub-nanosecond", "皮秒级", "picosecond",
            "超快", "ultra fast", "瞬时", "instantaneous"
        ]
    },
    "上下文关键词": {
        "路径特征": [
            "数据路径", "data path", "信号路径", "signal path",
            "传输路径", "transmission path", "连接路径", "connection path",
            "最小路径", "minimum path", "关键路径", "critical path"
        ],
        "时序问题": [
            "时序窗口", "timing window", "保持窗口", "hold window",
            "时序边界", "timing boundary", "时序约束", "timing constraint",
            "时序检查", "timing check", "时序分析", "timing analysis"
        ],
        "解决方案": [
            "插入延迟", "insert delay", "延迟单元", "delay cell",
            "缓冲延迟", "buffer delay", "增加延迟", "add delay",
            "延迟调整", "delay tuning", "延迟补偿", "delay compensation"
        ]
    }
}


scenario_003_keywords = {
    "核心关键词": {
        "异步信号": [
            "异步信号", "async signal", "asynchronous signal",
            "异步输入", "async input", "asynchronous input",
            "外部信号", "external signal", "异步数据", "async data",
            "非同步", "non-synchronous", "独立时钟", "independent clock"
        ],
        "同步缺失": [
            "未同步", "unsynchronized", "无同步器", "no synchronizer",
            "直接输入", "direct input", "绕过同步", "bypass sync",
            "同步器缺失", "missing synchronizer", "同步保护缺失", "no sync protection",
            "裸输入", "raw input"
        ],
        "亚稳态": [
            "亚稳态", "metastability", "亚稳定", "metastable",
            "不稳定状态", "unstable state", "中间状态", "intermediate state",
            "振荡", "oscillation", "不确定状态", "uncertain state"
        ]
    },
    "支撑关键词": {
        "信号类型": [
            "复位信号", "reset signal", "中断信号", "interrupt signal",
            "握手信号", "handshake signal", "请求信号", "request signal",
            "应答信号", "acknowledge signal", "外部时钟", "external clock",
            "输入引脚", "input pin", "IO信号", "IO signal"
        ],
        "时序风险": [
            "时序冲突", "timing conflict", "竞争冒险", "race condition",
            "时钟边沿", "clock edge", "建立保持", "setup hold",
            "时序窗口", "timing window", "危险窗口", "danger window",
            "时序违规", "timing violation"
        ],
        "接口特征": [
            "跨域", "cross domain", "域间", "inter-domain",
            "边界", "boundary", "接口", "interface",
            "外围", "peripheral", "端口", "port",
            "引脚", "pin", "外部连接", "external connection"
        ]
    },
    "上下文关键词": {
        "系统架构": [
            "多时钟域", "multi-clock domain", "时钟域交叉", "clock domain crossing",
            "异步系统", "asynchronous system", "混合时钟", "mixed clock",
            "系统接口", "system interface", "外部通信", "external communication"
        ],
        "设计问题": [
            "设计缺陷", "design flaw", "架构问题", "architecture issue",
            "接口设计", "interface design", "信号完整性", "signal integrity",
            "可靠性", "reliability", "稳定性", "stability"
        ],
        "解决方案": [
            "双触发器同步", "double flip-flop sync", "同步器链", "synchronizer chain",
            "握手协议", "handshake protocol", "异步FIFO", "async FIFO",
            "同步设计", "synchronous design", "时钟域隔离", "clock domain isolation"
        ]
    }
}




def extract_numerical_features(text: str) -> Dict[str, Any]:
    features = {}


    hold_patterns = [
        r'保持时间[：:\s]*(-?\d+\.?\d*)\s*(ps|ns|us)',
        r'hold\s+time[：:\s]*(-?\d+\.?\d*)\s*(ps|ns|us)',
        r'hold\s+slack[：:\s]*(-?\d+\.?\d*)\s*(ps|ns|us)',
        r'保持余量[：:\s]*(-?\d+\.?\d*)\s*(ps|ns|us)',
    ]

    for pattern in hold_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            try:
                value, unit = matches[0]
                value = float(value)

                if unit.lower() == 'ps':
                    value = value / 1000
                elif unit.lower() == 'us':
                    value = value * 1000
                features["hold_slack"] = value
                break
            except:
                continue


    delay_patterns = [
        r'延迟[：:\s]*(\d+\.?\d*)\s*(ps|ns|us)',
        r'delay[：:\s]*(\d+\.?\d*)\s*(ps|ns|us)',
        r'传播延迟[：:\s]*(\d+\.?\d*)\s*(ps|ns|us)',
        r'path\s+delay[：:\s]*(\d+\.?\d*)\s*(ps|ns|us)',
    ]

    for pattern in delay_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            try:
                value, unit = matches[0]
                value = float(value)

                if unit.lower() == 'ps':
                    value = value / 1000
                elif unit.lower() == 'us':
                    value = value * 1000
                features["delay_value"] = value
                break
            except:
                continue


    freq_patterns = [
        r'(\d+\.?\d*)\s*MHz',
        r'(\d+\.?\d*)\s*GHz',
        r'频率[：:\s]*(\d+\.?\d*)\s*(MHz|GHz)',
        r'frequency[：:\s]*(\d+\.?\d*)\s*(MHz|GHz)',
    ]

    for pattern in freq_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            try:
                if len(matches[0]) == 2:
                    value, unit = matches[0]
                else:
                    value, unit = matches[0], 'MHz'
                value = float(value)
                if unit.lower() == 'ghz':
                    value = value * 1000
                features["clock_freq"] = value
                break
            except:
                continue


    period_patterns = [
        r'周期[：:\s]*(\d+\.?\d*)\s*(ps|ns|us)',
        r'period[：:\s]*(\d+\.?\d*)\s*(ps|ns|us)',
        r'时钟周期[：:\s]*(\d+\.?\d*)\s*(ps|ns|us)',
    ]

    for pattern in period_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            try:
                value, unit = matches[0]
                value = float(value)

                if unit.lower() == 'ps':
                    value = value / 1000
                elif unit.lower() == 'us':
                    value = value * 1000
                features["clock_period"] = value
                break
            except:
                continue


    skew_patterns = [
        r'时钟偏斜[：:\s]*(\d+\.?\d*)\s*(ps|ns|us)',
        r'clock\s+skew[：:\s]*(\d+\.?\d*)\s*(ps|ns|us)',
        r'偏斜[：:\s]*(\d+\.?\d*)\s*(ps|ns|us)',
    ]

    for pattern in skew_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            try:
                value, unit = matches[0]
                value = float(value)

                if unit.lower() == 'ps':
                    value = value / 1000
                elif unit.lower() == 'us':
                    value = value * 1000
                features["clock_skew"] = value
                break
            except:
                continue

    return features




def keyword_matching(text: str) -> Dict[str, float]:
    scores = {
        "hold_002_fast_path": 0,
        "hold_003_async_input": 0
    }


    core_weight = 3.0
    support_weight = 2.0
    context_weight = 1.0




    for category in scenario_002_keywords["核心关键词"]:
        for keyword in scenario_002_keywords["核心关键词"][category]:
            if keyword.lower() in text.lower():
                scores["hold_002_fast_path"] += core_weight


    for category in scenario_002_keywords["支撑关键词"]:
        for keyword in scenario_002_keywords["支撑关键词"][category]:
            if keyword.lower() in text.lower():
                scores["hold_002_fast_path"] += support_weight


    for category in scenario_002_keywords["上下文关键词"]:
        for keyword in scenario_002_keywords["上下文关键词"][category]:
            if keyword.lower() in text.lower():
                scores["hold_002_fast_path"] += context_weight




    for category in scenario_003_keywords["核心关键词"]:
        for keyword in scenario_003_keywords["核心关键词"][category]:
            if keyword.lower() in text.lower():
                scores["hold_003_async_input"] += core_weight


    for category in scenario_003_keywords["支撑关键词"]:
        for keyword in scenario_003_keywords["支撑关键词"][category]:
            if keyword.lower() in text.lower():
                scores["hold_003_async_input"] += support_weight


    for category in scenario_003_keywords["上下文关键词"]:
        for keyword in scenario_003_keywords["上下文关键词"][category]:
            if keyword.lower() in text.lower():
                scores["hold_003_async_input"] += context_weight




    fast_path_patterns = [
        r'(\d+\.?\d*)\s*(ps|皮秒).*?(延迟|delay)',
        r'(零|zero|0)\s*(延迟|delay)',
        r'(直连|直通|bypass).*?(寄存器|register)',
        r'(wire|导线).*?(connection|连接)',
    ]

    for pattern in fast_path_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            scores["hold_002_fast_path"] += core_weight * len(matches)


    async_patterns = [
        r'(外部|external).*?(输入|input).*?(直接|direct)',
        r'(async|异步).*?(未|no|without).*?(sync|同步)',
        r'(metastable|亚稳态).*?(risk|风险|problem|问题)',
        r'(时钟域|clock\s+domain).*?(交叉|crossing)',
    ]

    for pattern in async_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            scores["hold_003_async_input"] += core_weight * len(matches)

    return scores


def numerical_validation(features: Dict[str, Any]) -> Dict[str, float]:
    scores = {
        "hold_002_fast_path": 0,
        "hold_003_async_input": 0
    }

    hold_slack = features.get("hold_slack")
    delay_value = features.get("delay_value")
    clock_freq = features.get("clock_freq")
    clock_skew = features.get("clock_skew")




    if hold_slack is not None:
        if hold_slack < -0.5:
            scores["hold_002_fast_path"] += 4
        elif hold_slack < -0.1:
            scores["hold_002_fast_path"] += 3
        elif hold_slack < 0:
            scores["hold_002_fast_path"] += 2


    if delay_value is not None:
        if delay_value <= 0.1:
            scores["hold_002_fast_path"] += 4
        elif delay_value <= 0.3:
            scores["hold_002_fast_path"] += 3
        elif delay_value <= 0.8:
            scores["hold_002_fast_path"] += 1


    if clock_freq is not None:
        if clock_freq >= 500:
            scores["hold_002_fast_path"] += 2
        elif clock_freq >= 200:
            scores["hold_002_fast_path"] += 1







    if clock_skew is not None:
        if clock_skew >= 1.0:
            scores["hold_003_async_input"] += 2
        elif clock_skew >= 0.5:
            scores["hold_003_async_input"] += 1


    if hold_slack is not None:
        if hold_slack < -2.0:
            scores["hold_003_async_input"] += 2


    if delay_value is not None and hold_slack is not None:
        if delay_value <= 0.2 and hold_slack < -0.2:

            scores["hold_002_fast_path"] += 2
            scores["hold_003_async_input"] -= 1

    return scores


def exclusion_check(text: str) -> Dict[str, float]:
    exclusion_scores = {
        "hold_002_fast_path": 0,
        "hold_003_async_input": 0
    }




    strong_exclusions_1 = [
        "异步信号", "async signal", "外部信号", "亚稳态",
        "时钟域交叉", "clock domain crossing", "同步器",
        "多时钟域", "multi-clock"
    ]

    for exclusion in strong_exclusions_1:
        if exclusion.lower() in text.lower():
            exclusion_scores["hold_002_fast_path"] -= 3


    weak_exclusions_1 = [
        "复杂逻辑", "complex logic", "多级延迟", "运算单元",
        "大延迟", "large delay"
    ]

    for exclusion in weak_exclusions_1:
        if exclusion.lower() in text.lower():
            exclusion_scores["hold_002_fast_path"] -= 1




    strong_exclusions_2 = [
        "直连", "direct connection", "bypass", "零延迟",
        "快速路径", "fast path", "最小延迟", "控制信号"
    ]

    for exclusion in strong_exclusions_2:
        if exclusion.lower() in text.lower():
            exclusion_scores["hold_003_async_input"] -= 3


    weak_exclusions_2 = [
        "同一时钟域", "same clock domain", "同步设计", "synchronous",
        "内部信号", "internal signal"
    ]

    for exclusion in weak_exclusions_2:
        if exclusion.lower() in text.lower():
            exclusion_scores["hold_003_async_input"] -= 1




    if any(word in text.lower() for word in ["快速路径", "fast path", "直连", "bypass"]):
        exclusion_scores["hold_003_async_input"] -= 1

    if any(word in text.lower() for word in ["异步", "async", "外部信号", "亚稳态"]):
        exclusion_scores["hold_002_fast_path"] -= 1

    return exclusion_scores


def context_analysis(text: str) -> Dict[str, float]:
    context_scores = {
        "hold_002_fast_path": 0,
        "hold_003_async_input": 0
    }




    fast_path_solutions = [
        "插入延迟", "insert delay", "延迟单元", "delay cell",
        "缓冲器", "buffer", "增加延迟", "add delay"
    ]

    if any(keyword in text.lower() for keyword in fast_path_solutions):
        context_scores["hold_002_fast_path"] += 2


    async_solutions = [
        "同步器", "synchronizer", "双触发器", "double flip-flop",
        "握手协议", "handshake", "异步FIFO", "async FIFO",
        "同步设计", "synchronous design"
    ]

    if any(keyword in text.lower() for keyword in async_solutions):
        context_scores["hold_003_async_input"] += 2




    control_keywords = [
        "控制逻辑", "control logic", "状态机", "state machine",
        "使能控制", "enable control", "选择器", "multiplexer"
    ]

    if any(keyword in text.lower() for keyword in control_keywords):
        context_scores["hold_002_fast_path"] += 1


    interface_keywords = [
        "系统接口", "system interface", "外部通信", "external comm",
        "IO接口", "IO interface", "外围设备", "peripheral"
    ]

    if any(keyword in text.lower() for keyword in interface_keywords):
        context_scores["hold_003_async_input"] += 1




    rtl_keywords = [
        "寄存器", "register", "组合逻辑", "combinational",
        "数据路径", "datapath", "信号连接", "signal connection"
    ]

    if any(keyword in text.lower() for keyword in rtl_keywords):
        context_scores["hold_002_fast_path"] += 0.5


    system_keywords = [
        "系统架构", "system architecture", "模块间", "inter-module",
        "跨域", "cross-domain", "顶层", "top-level"
    ]

    if any(keyword in text.lower() for keyword in system_keywords):
        context_scores["hold_003_async_input"] += 0.5

    return context_scores


def combine_scores(initial_scores: Dict[str, float],
                   numerical_scores: Dict[str, float],
                   exclusion_scores: Dict[str, float],
                   context_scores: Dict[str, float]) -> Dict[str, float]:
    final_scores = {}

    for scenario in initial_scores:
        final_scores[scenario] = (
                initial_scores[scenario] * 1.0 +
                numerical_scores[scenario] * 1.3 +
                exclusion_scores[scenario] * 1.0 +
                context_scores[scenario] * 0.7
        )

    return final_scores


def classify_hold_violation(text: str) -> Tuple[str, float]:


    initial_scores = keyword_matching(text)


    features = extract_numerical_features(text)
    numerical_scores = numerical_validation(features)


    exclusion_scores = exclusion_check(text)


    context_scores = context_analysis(text)


    final_scores = combine_scores(initial_scores, numerical_scores,
                                  exclusion_scores, context_scores)


    best_scenario = max(final_scores, key=final_scores.get)
    best_score = final_scores[best_scenario]


    total_positive_score = sum(max(0, score) for score in final_scores.values())
    confidence = best_score / total_positive_score if total_positive_score > 0 else 0


    min_score_threshold = 2.0
    min_confidence_threshold = 0.4

    if best_score < min_score_threshold or confidence < min_confidence_threshold:
        return "unknown", confidence

    return best_scenario, confidence




def test_hold_violation_classifier():

    test_cases = [
        {
            "text": "控制信号ctrl_en从寄存器reg_a直连到寄存器reg_b，组合逻辑延迟仅为50ps，保持时间违规-0.3ns",
            "expected": "hold_002_fast_path",
            "description": "快速路径-控制信号直连"
        },
        {
            "text": "外部异步输入信号ext_req未经同步器处理直接连接到同步电路，存在亚稳态风险和保持时间违规",
            "expected": "hold_003_async_input",
            "description": "异步信号-外部输入未同步"
        },
        {
            "text": "使能信号bypass路径延迟极小，fast path导致保持余量不足-0.15ns，需要插入延迟单元",
            "expected": "hold_002_fast_path",
            "description": "快速路径-使能信号bypass"
        },
        {
            "text": "时钟域交叉处异步信号直接输入，缺少同步器保护，引发metastability和hold violation",
            "expected": "hold_003_async_input",
            "description": "异步信号-时钟域交叉"
        }
    ]

    print("=== 保持时间违规分类器测试 ===\n")

    for i, test in enumerate(test_cases, 1):
        print(f"测试用例 {i}: {test['description']}")
        print(f"输入: {test['text']}")

        result, confidence = classify_hold_violation(test['text'])

        print(f"预期场景: {test['expected']}")
        print(f"分类结果: {result}")
        print(f"置信度: {confidence:.3f}")
        print(f"结果: {'✓ 正确' if test['expected'] in result else '✗ 错误'}")
        print("-" * 60)



if __name__ == "__main__":
    test_text1 = "错误产生原因：控制信号ctrl_enable从源寄存器src_ctrl_reg直连到目标寄存器dst_data_reg的使能端，路径中仅包含一个反相器门(INV1)，总组合逻辑延迟仅为45ps。在200MHz时钟频率下(5ns周期)，由于时钟树的轻微不平衡，目标寄存器dst_data_reg的时钟到达时间比源寄存器src_ctrl_reg提前120ps。当src_ctrl_reg在时钟上升沿输出ctrl_enable信号后，该信号经过极短的45ps传播延迟到达dst_data_reg，此时距离dst_data_reg的时钟沿仅有75ps时间窗口，远小于寄存器要求的150ps保持时间。关键路径{src_ctrl_reg->INV1->dst_data_reg}的保持时间余量为(-75ps)，导致dst_data_reg无法在时钟沿后维持稳定的使能状态，形成快速路径保持时间违规。"
    test_text2 = "错误产生原因：外部异步信号ext_interrupt_req从系统外部IO引脚直接连接到内部同步时钟域(clk_sys, 100MHz)的中断寄存器int_req_reg，未经过任何同步器保护电路。该异步信号的变化时刻完全独立于内部系统时钟clk_sys，当ext_interrupt_req信号恰好在clk_sys上升沿附近发生状态跳变时，由于信号传播延迟的随机性和外部环境噪声影响，可能在时钟沿后的保持时间窗口(200ps)内继续变化。关键路径{ext_interrupt_req->int_req_reg}缺乏时序保护，当异步信号在时钟沿后150ps时刻发生跳变，违反了寄存器的保持时间要求，保持余量为(-50ps)，导致int_req_reg进入亚稳态，输出在逻辑0和逻辑1之间振荡，形成异步输入引起的保持时间违规和亚稳态传播风险。"

    print(classify_hold_violation(test_text2))