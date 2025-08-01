
import re
from typing import Dict, Tuple, Any, List




scenario_001_keywords = {
    "核心关键词": {
        "单bit特征": [
            "单bit", "single bit", "1bit", "一位", "单个位",
            "控制位", "control bit", "状态位", "status bit",
            "标志位", "flag bit", "使能位", "enable bit"
        ],
        "跨域传输": [
            "跨时钟域", "cross clock domain", "clock domain crossing", "CDC",
            "域间传输", "inter-domain", "跨域", "cross domain",
            "时钟域交叉", "clock crossing", "域交叉", "domain crossing"
        ],
        "同步缺失": [
            "未同步", "unsynchronized", "无同步器", "no synchronizer",
            "直接传输", "direct transfer", "同步器缺失", "missing synchronizer",
            "绕过同步", "bypass sync", "未保护", "unprotected"
        ]
    },
    "支撑关键词": {
        "信号类型": [
            "控制信号", "control signal", "使能信号", "enable signal",
            "复位信号", "reset signal", "中断信号", "interrupt signal",
            "握手信号", "handshake signal", "请求信号", "request signal",
            "应答信号", "acknowledge signal", "选择信号", "select signal",
            "时钟使能", "clock enable", "写使能", "write enable"
        ],
        "亚稳态风险": [
            "亚稳态", "metastability", "亚稳定", "metastable",
            "不稳定状态", "unstable state", "振荡", "oscillation",
            "不确定状态", "uncertain state", "中间状态", "intermediate state",
            "亚稳态传播", "metastable propagation"
        ],
        "CDC违规": [
            "CDC违规", "CDC violation", "跨域违规", "cross-domain violation",
            "时钟域违规", "clock domain violation", "CDC检查失败", "CDC check failure",
            "CDC约束", "CDC constraint", "CDC规则", "CDC rule"
        ]
    },
    "上下文关键词": {
        "问题表现": [
            "信号丢失", "signal loss", "误触发", "false trigger",
            "错误采样", "wrong sampling", "数据丢失", "data loss",
            "功能异常", "functional failure", "逻辑错误", "logic error",
            "间歇性问题", "intermittent issue"
        ],
        "解决方案": [
            "双触发器同步", "double flip-flop sync", "同步器链", "synchronizer chain",
            "二级同步", "two-stage sync", "同步器", "synchronizer",
            "边缘检测", "edge detection", "脉冲同步", "pulse sync",
            "握手协议", "handshake protocol"
        ],
        "设计层次": [
            "RTL设计", "RTL design", "寄存器级", "register level",
            "控制逻辑", "control logic", "状态机", "state machine",
            "接口设计", "interface design", "模块间通信", "inter-module comm"
        ]
    }
}


scenario_002_keywords = {
    "核心关键词": {
        "多bit特征": [
            "多bit", "multi-bit", "multi bit", "数据总线", "data bus",
            "并行数据", "parallel data", "总线宽度", "bus width",
            "数据位", "data bits", "位宽", "bit width", "总线位数", "bus bits"
        ],
        "数据一致性": [
            "数据不一致", "data inconsistency", "数据撕裂", "data tearing",
            "部分更新", "partial update", "数据破损", "data corruption",
            "不同步采样", "asynchronous sampling", "数据完整性", "data integrity",
            "一致性问题", "consistency problem"
        ],
        "格雷码相关": [
            "格雷码", "gray code", "grey code", "格雷码违规", "gray code violation",
            "格雷编码", "gray encoding", "二进制码", "binary code",
            "码制转换", "code conversion", "编码问题", "encoding issue"
        ]
    },
    "支撑关键词": {
        "数据类型": [
            "地址总线", "address bus", "数据总线", "data bus",
            "计数器", "counter", "指针", "pointer", "索引", "index",
            "配置数据", "configuration data", "状态数据", "status data",
            "参数数据", "parameter data", "寄存器组", "register bank"
        ],
        "位宽描述": [
            r'(\d+)\s*bit', r'(\d+)\s*位', r'(\d+)b\s*总线',
            "8位", "16位", "32位", "64位", "8bit", "16bit", "32bit", "64bit",
            "字节", "byte", "字", "word", "双字", "dword",
            "宽总线", "wide bus", "窄总线", "narrow bus"
        ],
        "传输问题": [
            "总线冲突", "bus conflict", "数据竞争", "data race",
            "采样错误", "sampling error", "时序冲突", "timing conflict",
            "传输错误", "transfer error", "数据错位", "data misalignment"
        ]
    },
    "上下文关键词": {
        "应用场景": [
            "FIFO接口", "FIFO interface", "存储器接口", "memory interface",
            "CPU接口", "CPU interface", "DMA传输", "DMA transfer",
            "外设接口", "peripheral interface", "通信接口", "communication interface",
            "数据通道", "data channel", "总线桥", "bus bridge"
        ],
        "解决方案": [
            "异步FIFO", "async FIFO", "异步队列", "async queue",
            "握手协议", "handshake protocol", "双端口RAM", "dual-port RAM",
            "缓冲区", "buffer", "同步FIFO", "sync FIFO",
            "请求应答", "request-acknowledge", "数据打拍", "data pipeline"
        ],
        "性能影响": [
            "吞吐量", "throughput", "带宽", "bandwidth", "延迟", "latency",
            "数据丢失", "data loss", "性能下降", "performance degradation",
            "传输效率", "transfer efficiency", "带宽利用率", "bandwidth utilization"
        ]
    }
}




def extract_numerical_features(text: str) -> Dict[str, Any]:
    features = {}


    bit_width_patterns = [
        r'(\d+)\s*bit(?:s)?',
        r'(\d+)\s*位',
        r'(\d+)b(?:\s|$)',
        r'位宽\s*[：:\s]*(\d+)',
        r'bus\s+width\s*[：:\s]*(\d+)',
        r'data\s+width\s*[：:\s]*(\d+)'
    ]

    for pattern in bit_width_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            try:
                width = int(matches[0])
                features["bit_width"] = width
                break
            except:
                continue


    freq_patterns = [
        r'(\d+\.?\d*)\s*MHz',
        r'(\d+\.?\d*)\s*GHz',
        r'频率\s*[：:\s]*(\d+\.?\d*)\s*(MHz|GHz)',
        r'frequency\s*[：:\s]*(\d+\.?\d*)\s*(MHz|GHz)'
    ]

    clock_frequencies = []
    for pattern in freq_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            try:
                if isinstance(match, tuple) and len(match) == 2:
                    value, unit = match
                    value = float(value)
                    if unit.lower() == 'ghz':
                        value = value * 1000
                else:
                    value = float(match)
                clock_frequencies.append(value)
            except:
                continue

    if clock_frequencies:
        features["clock_frequencies"] = clock_frequencies
        if len(clock_frequencies) >= 2:
            features["freq_ratio"] = max(clock_frequencies) / min(clock_frequencies)


    period_patterns = [
        r'周期\s*[：:\s]*(\d+\.?\d*)\s*(ps|ns|us)',
        r'period\s*[：:\s]*(\d+\.?\d*)\s*(ps|ns|us)',
        r'时钟周期\s*[：:\s]*(\d+\.?\d*)\s*(ps|ns|us)'
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


    fifo_patterns = [
        r'FIFO\s*深度\s*[：:\s]*(\d+)',
        r'FIFO\s*depth\s*[：:\s]*(\d+)',
        r'队列深度\s*[：:\s]*(\d+)',
        r'queue\s+depth\s*[：:\s]*(\d+)',
        r'(\d+)\s*深度.*FIFO',
        r'(\d+)\s*entry.*FIFO'
    ]

    for pattern in fifo_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            try:
                depth = int(matches[0])
                features["fifo_depth"] = depth
                break
            except:
                continue


    cdc_violation_patterns = [
        r'(\d+)\s*个?\s*CDC\s*违规',
        r'(\d+)\s*CDC\s*violation',
        r'CDC\s*违规\s*(\d+)',
        r'(\d+)\s*跨域违规'
    ]

    for pattern in cdc_violation_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            try:
                count = int(matches[0])
                features["cdc_violation_count"] = count
                break
            except:
                continue

    return features




def keyword_matching(text: str) -> Dict[str, float]:
    scores = {
        "cdc_001_single_bit": 0,
        "cdc_002_multi_bit_bus": 0
    }


    core_weight = 3.0
    support_weight = 2.0
    context_weight = 1.0




    for category in scenario_001_keywords["核心关键词"]:
        for keyword in scenario_001_keywords["核心关键词"][category]:
            if keyword.lower() in text.lower():
                scores["cdc_001_single_bit"] += core_weight


    for category in scenario_001_keywords["支撑关键词"]:
        for keyword in scenario_001_keywords["支撑关键词"][category]:
            if keyword.lower() in text.lower():
                scores["cdc_001_single_bit"] += support_weight


    for category in scenario_001_keywords["上下文关键词"]:
        for keyword in scenario_001_keywords["上下文关键词"][category]:
            if keyword.lower() in text.lower():
                scores["cdc_001_single_bit"] += context_weight




    for category in scenario_002_keywords["核心关键词"]:
        for keyword in scenario_002_keywords["核心关键词"][category]:
            if isinstance(keyword, str):
                if keyword.lower() in text.lower():
                    scores["cdc_002_multi_bit_bus"] += core_weight
            else:

                try:
                    matches = re.findall(keyword, text, re.IGNORECASE)
                    if matches:
                        scores["cdc_002_multi_bit_bus"] += core_weight * len(matches)
                except:
                    continue


    for category in scenario_002_keywords["支撑关键词"]:
        for keyword in scenario_002_keywords["支撑关键词"][category]:
            if isinstance(keyword, str):
                if keyword.lower() in text.lower():
                    scores["cdc_002_multi_bit_bus"] += support_weight
            else:

                try:
                    matches = re.findall(keyword, text, re.IGNORECASE)
                    if matches:
                        scores["cdc_002_multi_bit_bus"] += support_weight * len(matches)
                except:
                    continue


    for category in scenario_002_keywords["上下文关键词"]:
        for keyword in scenario_002_keywords["上下文关键词"][category]:
            if keyword.lower() in text.lower():
                scores["cdc_002_multi_bit_bus"] += context_weight




    single_bit_patterns = [
        r'(1|single|单个)\s*(bit|位).*?(跨|cross|CDC)',
        r'(控制|enable|reset|中断|interrupt).*?(信号|signal).*?(跨|cross)',
        r'(flag|标志|状态|status)\s*(bit|位).*?(域|domain)',
        r'(使能|enable)\s*(位|bit).*?(传输|transfer)'
    ]

    for pattern in single_bit_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            scores["cdc_001_single_bit"] += core_weight * len(matches)


    multi_bit_patterns = [
        r'(\d+)\s*(bit|位).*?(总线|bus).*?(跨|cross|CDC)',
        r'(数据|data)\s*(总线|bus).*?(跨域|cross.*domain)',
        r'(并行|parallel)\s*(数据|data).*?(传输|transfer).*?(CDC)',
        r'(多|multi).*?(bit|位).*?(不一致|inconsist|撕裂|tear)',
        r'(格雷码|gray\s*code).*?(违规|violation|问题|problem)'
    ]

    for pattern in multi_bit_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            scores["cdc_002_multi_bit_bus"] += core_weight * len(matches)

    return scores


def numerical_validation(features: Dict[str, Any]) -> Dict[str, float]:
    scores = {
        "cdc_001_single_bit": 0,
        "cdc_002_multi_bit_bus": 0
    }

    bit_width = features.get("bit_width")
    clock_frequencies = features.get("clock_frequencies", [])
    freq_ratio = features.get("freq_ratio")
    fifo_depth = features.get("fifo_depth")
    cdc_violation_count = features.get("cdc_violation_count")




    if bit_width is not None:
        if bit_width == 1:
            scores["cdc_001_single_bit"] += 4
        elif bit_width <= 4:
            scores["cdc_001_single_bit"] += 2
        elif bit_width >= 8:
            scores["cdc_001_single_bit"] -= 2


    if freq_ratio is not None:
        if freq_ratio >= 2.0:
            scores["cdc_001_single_bit"] += 2
        elif freq_ratio >= 1.5:
            scores["cdc_001_single_bit"] += 1


    if cdc_violation_count is not None:
        if cdc_violation_count <= 5:
            scores["cdc_001_single_bit"] += 2
        elif cdc_violation_count >= 10:
            scores["cdc_001_single_bit"] -= 1




    if bit_width is not None:
        if bit_width >= 32:
            scores["cdc_002_multi_bit_bus"] += 4
        elif bit_width >= 8:
            scores["cdc_002_multi_bit_bus"] += 3
        elif bit_width >= 2:
            scores["cdc_002_multi_bit_bus"] += 2
        elif bit_width == 1:
            scores["cdc_002_multi_bit_bus"] -= 3


    if fifo_depth is not None:
        if fifo_depth >= 16:
            scores["cdc_002_multi_bit_bus"] += 3
        elif fifo_depth >= 4:
            scores["cdc_002_multi_bit_bus"] += 2
        else:
            scores["cdc_002_multi_bit_bus"] += 1


    if freq_ratio is not None:
        if freq_ratio >= 4.0:
            scores["cdc_002_multi_bit_bus"] += 3
        elif freq_ratio >= 2.0:
            scores["cdc_002_multi_bit_bus"] += 2


    if cdc_violation_count is not None:
        if cdc_violation_count >= 10:
            scores["cdc_002_multi_bit_bus"] += 3
        elif cdc_violation_count >= 5:
            scores["cdc_002_multi_bit_bus"] += 2
        elif cdc_violation_count <= 2:
            scores["cdc_002_multi_bit_bus"] -= 1




    if bit_width is not None and cdc_violation_count is not None:
        if bit_width >= 8 and cdc_violation_count >= bit_width * 0.5:

            scores["cdc_002_multi_bit_bus"] += 2
        elif bit_width == 1 and cdc_violation_count <= 2:

            scores["cdc_001_single_bit"] += 2

    return scores


def exclusion_check(text: str) -> Dict[str, float]:
    exclusion_scores = {
        "cdc_001_single_bit": 0,
        "cdc_002_multi_bit_bus": 0
    }




    strong_exclusions_1 = [
        "数据总线", "data bus", "并行数据", "parallel data",
        "多bit", "multi-bit", "总线宽度", "bus width",
        "数据撕裂", "data tearing", "格雷码", "gray code"
    ]

    for exclusion in strong_exclusions_1:
        if exclusion.lower() in text.lower():
            exclusion_scores["cdc_001_single_bit"] -= 3


    weak_exclusions_1 = [
        "32位", "64位", "字节", "byte", "字", "word",
        "FIFO", "队列", "queue", "缓冲区", "buffer"
    ]

    for exclusion in weak_exclusions_1:
        if exclusion.lower() in text.lower():
            exclusion_scores["cdc_001_single_bit"] -= 1




    strong_exclusions_2 = [
        "单bit", "single bit", "1bit", "控制位", "control bit",
        "状态位", "status bit", "标志位", "flag bit",
        "使能位", "enable bit", "单个位", "一位"
    ]

    for exclusion in strong_exclusions_2:
        if exclusion.lower() in text.lower():
            exclusion_scores["cdc_002_multi_bit_bus"] -= 3


    weak_exclusions_2 = [
        "控制信号", "control signal", "使能信号", "enable signal",
        "中断", "interrupt", "复位", "reset", "握手", "handshake"
    ]

    for exclusion in weak_exclusions_2:
        if exclusion.lower() in text.lower():
            exclusion_scores["cdc_002_multi_bit_bus"] -= 1




    if any(word in text.lower() for word in ["单bit", "single bit", "1bit", "控制位"]):
        exclusion_scores["cdc_002_multi_bit_bus"] -= 2

    if any(word in text.lower() for word in ["多bit", "multi-bit", "数据总线", "data bus"]):
        exclusion_scores["cdc_001_single_bit"] -= 2

    return exclusion_scores


def context_analysis(text: str) -> Dict[str, float]:
    context_scores = {
        "cdc_001_single_bit": 0,
        "cdc_002_multi_bit_bus": 0
    }




    single_bit_solutions = [
        "双触发器同步", "double flip-flop sync", "二级同步", "two-stage sync",
        "同步器链", "synchronizer chain", "边缘检测", "edge detection",
        "脉冲同步", "pulse sync"
    ]

    if any(keyword in text.lower() for keyword in single_bit_solutions):
        context_scores["cdc_001_single_bit"] += 2


    multi_bit_solutions = [
        "异步FIFO", "async FIFO", "异步队列", "async queue",
        "双端口RAM", "dual-port RAM", "格雷码计数器", "gray code counter",
        "握手协议", "handshake protocol", "请求应答", "request-acknowledge"
    ]

    if any(keyword in text.lower() for keyword in multi_bit_solutions):
        context_scores["cdc_002_multi_bit_bus"] += 2




    single_bit_applications = [
        "控制逻辑", "control logic", "状态机", "state machine",
        "中断控制", "interrupt control", "使能控制", "enable control",
        "复位控制", "reset control", "时钟门控", "clock gating"
    ]

    if any(keyword in text.lower() for keyword in single_bit_applications):
        context_scores["cdc_001_single_bit"] += 1


    multi_bit_applications = [
        "数据传输", "data transfer", "存储器接口", "memory interface",
        "CPU接口", "CPU interface", "DMA传输", "DMA transfer",
        "外设接口", "peripheral interface", "通信协议", "communication protocol",
        "总线桥", "bus bridge", "数据通道", "data channel"
    ]

    if any(keyword in text.lower() for keyword in multi_bit_applications):
        context_scores["cdc_002_multi_bit_bus"] += 1




    single_bit_symptoms = [
        "信号丢失", "signal loss", "误触发", "false trigger",
        "间歇性问题", "intermittent issue", "功能异常", "functional failure",
        "逻辑错误", "logic error", "控制失效", "control failure"
    ]

    if any(keyword in text.lower() for keyword in single_bit_symptoms):
        context_scores["cdc_001_single_bit"] += 1


    multi_bit_symptoms = [
        "数据不一致", "data inconsistency", "数据撕裂", "data tearing",
        "数据破损", "data corruption", "部分更新", "partial update",
        "传输错误", "transfer error", "数据错位", "data misalignment",
        "吞吐量下降", "throughput degradation"
    ]

    if any(keyword in text.lower() for keyword in multi_bit_symptoms):
        context_scores["cdc_002_multi_bit_bus"] += 1




    rtl_single_keywords = [
        "寄存器控制", "register control", "信号连接", "signal connection",
        "位操作", "bit operation", "控制位设置", "control bit setting"
    ]

    if any(keyword in text.lower() for keyword in rtl_single_keywords):
        context_scores["cdc_001_single_bit"] += 0.5


    system_multi_keywords = [
        "数据流", "data flow", "系统架构", "system architecture",
        "模块通信", "module communication", "接口设计", "interface design",
        "总线架构", "bus architecture"
    ]

    if any(keyword in text.lower() for keyword in system_multi_keywords):
        context_scores["cdc_002_multi_bit_bus"] += 0.5

    return context_scores


def combine_scores(initial_scores: Dict[str, float],
                   numerical_scores: Dict[str, float],
                   exclusion_scores: Dict[str, float],
                   context_scores: Dict[str, float]) -> Dict[str, float]:
    final_scores = {}

    for scenario in initial_scores:
        final_scores[scenario] = (
                initial_scores[scenario] * 1.0 +
                numerical_scores[scenario] * 1.4 +
                exclusion_scores[scenario] * 1.1 +
                context_scores[scenario] * 0.8
        )

    return final_scores


def classify_cdc_violation(text: str) -> Tuple[str, float]:


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


    min_score_threshold = 2.5
    min_confidence_threshold = 0.45

    if best_score < min_score_threshold or confidence < min_confidence_threshold:
        return "unknown", confidence

    return best_scenario, confidence


def get_detailed_analysis(text: str) -> Dict[str, Any]:


    initial_scores = keyword_matching(text)
    features = extract_numerical_features(text)
    numerical_scores = numerical_validation(features)
    exclusion_scores = exclusion_check(text)
    context_scores = context_analysis(text)
    final_scores = combine_scores(initial_scores, numerical_scores,
                                  exclusion_scores, context_scores)


    best_scenario, confidence = classify_cdc_violation(text)


    analysis = {
        "classification": {
            "result": best_scenario,
            "confidence": confidence
        },
        "scores": {
            "keyword_matching": initial_scores,
            "numerical_validation": numerical_scores,
            "exclusion_check": exclusion_scores,
            "context_analysis": context_scores,
            "final_scores": final_scores
        },
        "features": features,
        "score_breakdown": {
            "cdc_001_single_bit": {
                "keyword": initial_scores["cdc_001_single_bit"],
                "numerical": numerical_scores["cdc_001_single_bit"],
                "exclusion": exclusion_scores["cdc_001_single_bit"],
                "context": context_scores["cdc_001_single_bit"],
                "final": final_scores["cdc_001_single_bit"]
            },
            "cdc_002_multi_bit_bus": {
                "keyword": initial_scores["cdc_002_multi_bit_bus"],
                "numerical": numerical_scores["cdc_002_multi_bit_bus"],
                "exclusion": exclusion_scores["cdc_002_multi_bit_bus"],
                "context": context_scores["cdc_002_multi_bit_bus"],
                "final": final_scores["cdc_002_multi_bit_bus"]
            }
        }
    }

    return analysis




def test_cdc_violation_classifier():

    test_cases = [
        {
            "text": "控制信号ctrl_valid从时钟域clk_a(100MHz)直接传输到时钟域clk_b(150MHz)，未使用同步器保护，出现CDC违规和亚稳态风险",
            "expected": "cdc_001_single_bit",
            "description": "单bit控制信号CDC问题"
        },
        {
            "text": "32位数据总线data_bus[31:0]跨越时钟域传输时出现数据撕裂，部分bit在不同时钟周期被采样，导致数据不一致，需要异步FIFO解决",
            "expected": "cdc_002_multi_bit_bus",
            "description": "32位数据总线CDC问题"
        },
        {
            "text": "使能信号enable从clk_domain1跨域到clk_domain2时丢失，single bit信号需要双触发器同步器链保护",
            "expected": "cdc_001_single_bit",
            "description": "单bit使能信号跨域问题"
        },
        {
            "text": "16bit地址总线addr_bus在跨时钟域传输过程中发生格雷码违规，并行数据完整性受损，吞吐量严重下降",
            "expected": "cdc_002_multi_bit_bus",
            "description": "16位地址总线格雷码问题"
        },
        {
            "text": "中断信号interrupt_req从外部异步域进入同步时钟域clk_sys，未经同步处理直接触发中断控制器，存在亚稳态传播风险",
            "expected": "cdc_001_single_bit",
            "description": "异步中断信号CDC问题"
        },
        {
            "text": "64位数据总线data_wide_bus跨越200MHz和50MHz时钟域时出现严重的数据不一致，需要深度为32的异步FIFO进行缓冲",
            "expected": "cdc_002_multi_bit_bus",
            "description": "64位宽总线FIFO需求"
        }
    ]

    print("=== CDC违规分类器测试 ===\n")

    correct_count = 0
    total_count = len(test_cases)

    for i, test in enumerate(test_cases, 1):
        print(f"测试用例 {i}: {test['description']}")
        print(f"输入: {test['text']}")

        result, confidence = classify_cdc_violation(test['text'])

        print(f"预期场景: {test['expected']}")
        print(f"分类结果: {result}")
        print(f"置信度: {confidence:.3f}")

        is_correct = test['expected'] in result
        if is_correct:
            correct_count += 1

        print(f"结果: {'✓ 正确' if is_correct else '✗ 错误'}")
        print("-" * 70)

    print(f"\n总体准确率: {correct_count}/{total_count} = {correct_count / total_count * 100:.1f}%")


def test_detailed_analysis():

    test_text = "32位数据总线data_bus[31:0]从100MHz时钟域传输到200MHz时钟域，出现数据撕裂和不一致问题，需要深度为16的异步FIFO解决"

    print("=== 详细分析测试 ===\n")
    print(f"输入文本: {test_text}\n")

    analysis = get_detailed_analysis(test_text)

    print("分类结果:")
    print(f"  场景: {analysis['classification']['result']}")
    print(f"  置信度: {analysis['classification']['confidence']:.3f}\n")

    print("数值特征:")
    for feature, value in analysis['features'].items():
        print(f"  {feature}: {value}")
    print()

    print("评分明细:")
    for scenario, breakdown in analysis['score_breakdown'].items():
        print(f"  {scenario}:")
        for stage, score in breakdown.items():
            print(f"    {stage}: {score:.2f}")
        print()




def batch_classify_cdc(texts: List[str]) -> List[Dict[str, Any]]:
    results = []

    for i, text in enumerate(texts):
        try:
            scenario, confidence = classify_cdc_violation(text)
            analysis = get_detailed_analysis(text)

            result = {
                "index": i,
                "text": text,
                "scenario": scenario,
                "confidence": confidence,
                "analysis": analysis
            }
            results.append(result)

        except Exception as e:
            result = {
                "index": i,
                "text": text,
                "scenario": "error",
                "confidence": 0.0,
                "error": str(e)
            }
            results.append(result)

    return results


def generate_cdc_report(texts: List[str]) -> str:
    results = batch_classify_cdc(texts)


    scenario_counts = {}
    total_confidence = 0
    valid_results = 0

    for result in results:
        scenario = result['scenario']
        if scenario != 'error' and scenario != 'unknown':
            scenario_counts[scenario] = scenario_counts.get(scenario, 0) + 1
            total_confidence += result['confidence']
            valid_results += 1


    report = "CDC问题分析报告\n"
    report += "=" * 50 + "\n\n"

    report += f"总计分析文本数量: {len(texts)}\n"
    report += f"成功分类数量: {valid_results}\n"
    report += f"平均置信度: {total_confidence / valid_results:.3f}\n\n" if valid_results > 0 else "平均置信度: N/A\n\n"

    report += "场景分布:\n"
    for scenario, count in scenario_counts.items():
        percentage = count / valid_results * 100 if valid_results > 0 else 0
        report += f"  {scenario}: {count} ({percentage:.1f}%)\n"

    report += "\n详细结果:\n"
    report += "-" * 50 + "\n"

    for result in results:
        report += f"文本 {result['index'] + 1}: {result['text'][:50]}...\n"
        report += f"  分类: {result['scenario']}\n"
        report += f"  置信度: {result['confidence']:.3f}\n\n"

    return report



if __name__ == "__main__":
    test_text1 = "错误产生原因：控制信号ctrl_enable从源时钟域clk_src(100MHz, 10ns周期)直接传输到目标时钟域clk_dst(150MHz, 6.67ns周期)，信号路径{ctrl_reg_src->ctrl_enable->ctrl_reg_dst}中未设置任何同步器保护电路。由于两个时钟域频率不同且相位关系不确定，当ctrl_enable信号在clk_src上升沿更新后，其状态变化时刻相对于clk_dst时钟沿是随机的。当信号跳变恰好发生在clk_dst时钟沿的建立/保持时间窗口内时，目标寄存器ctrl_reg_dst进入亚稳态，输出在逻辑0和逻辑1之间振荡约2-3个时钟周期。关键路径{ctrl_reg_src->ctrl_reg_dst}存在CDC违规，亚稳态信号传播到下游控制逻辑，导致系统功能间歇性异常，形成单bit信号跨时钟域传输违规。"
    test_text2 = "错误产生原因：32位数据总线data_bus[31:0]从源时钟域clk_fast(200MHz, 5ns周期)直接传输到目标时钟域clk_slow(50MHz, 20ns周期)，总线信号路径{src_data_reg[31:0]->data_bus[31:0]->dst_data_reg[31:0]}未经过任何跨域同步保护。由于32个数据位同时跨越时钟域边界，每个bit的传播延迟存在微小差异(±50ps)，加上两个时钟域的4:1频率比关系，当src_data_reg在clk_fast上升沿更新32位数据0x12345678时，这些bit到达dst_data_reg的时刻相对于clk_slow时钟沿是不确定的。部分bit(如[7:0])可能在clk_slow第N个周期被正确采样到0x78，而其他bit(如[31:24])由于传播延迟差异在第N+1个周期才被采样到0x12，导致目标寄存器在某个时钟周期读取到错误的混合数据0x12345600。关键路径{src_data_reg[31:0]->dst_data_reg[31:0]}存在严重的多bit CDC违规，数据撕裂和不一致问题导致系统数据完整性破坏，需要异步FIFO或握手协议确保数据总线的原子性传输。"

    print(classify_cdc_violation(test_text1))