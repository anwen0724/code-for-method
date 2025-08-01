import re
import string


scenario_001_keywords = {
    "核心关键词": {
        "中文": ["逻辑层级", "组合逻辑", "逻辑链", "级联", "逻辑深度", "门级数"],
        "英文": ["logic levels", "combinational logic", "logic chain", "cascade",
                 "logic depth", "gate levels", "combinational delay"],
        "数值模式": [r"(\d+)级.*?逻辑", r"(\d+)\s*levels?\s*of\s*logic", r"logic.*?(\d+).*?levels?"]
    },

    "支撑关键词": {
        "逻辑门类型": ["AND门", "OR门", "XOR门", "NAND门", "NOR门", "非门", "与门", "或门",
                       "AND gate", "OR gate", "XOR gate", "NAND gate", "NOR gate", "inverter"],
        "选择器件": ["MUX", "DMUX", "decoder", "encoder", "多路选择器", "译码器", "编码器"],
        "问题描述": ["门延迟", "逻辑延迟", "组合延迟", "路径延迟", "gate delay",
                     "combinational path", "logic path"]
    },

    "上下文关键词": {
        "延迟累积": ["延迟累积", "叠加", "累加", "propagation", "累计延迟"],
        "优化建议": ["逻辑优化", "重构", "化简", "logic optimization", "restructure",
                     "reduce levels", "logic synthesis"]
    },

    "排除关键词": {
        "强排除": ["乘法器", "除法器", "DSP", "multiplier", "divider", "MAC",
                   "arithmetic unit", "运算单元", "算术单元"],
        "弱排除": ["流水线", "pipeline", "复杂运算", "floating point"]
    }
}

scenario_002_keywords = {
    "核心关键词": {
        "运算单元": ["乘法器", "除法器", "DSP", "MAC", "算术单元", "运算单元", "运算器",
                     "multiplier", "divider", "arithmetic unit", "DSP48", "DSP block"],
        "浮点运算": ["浮点", "floating point", "FPU", "浮点单元", "开方", "square root"],
        "复杂运算": ["乘累加", "multiply-accumulate", "卷积", "convolution", "滤波", "filter"]
    },

    "支撑关键词": {
        "位宽描述": [r"(\d+)位.*?(乘法器|加法器|运算)", r"(\d+)-?bit.*?(mult|add|arith)",
                     "32位", "64位", "16位", "32-bit", "64-bit", "16-bit"],
        "延迟特征": ["单元延迟", "运算延迟", "arithmetic delay", "multiplier delay",
                     "unit latency", "computational delay"],
        "性能指标": ["吞吐量", "throughput", "latency", "延迟", "timing critical"]
    },

    "上下文关键词": {
        "算法相关": ["DSP算法", "信号处理", "图像处理", "FIR", "IIR", "FFT", "数字滤波"],
        "优化建议": ["流水线", "pipeline", "并行", "parallel", "资源共享", "resource sharing",
                     "算法优化", "algorithm optimization"]
    },

    "排除关键词": {
        "强排除": ["基础逻辑门", "简单逻辑", "门电路", "basic gates", "simple logic"],
        "弱排除": ["多级逻辑", "逻辑链", "logic chain", "logic levels"]
    }
}

scenario_003_keywords = {
    "核心关键词": {
        "流水线": ["流水线", "pipeline", "流水", "分级处理", "多级处理", "stage"],
        "深度相关": ["深度不足", "级数不够", "stages insufficient", "depth insufficient",
                     "需要增加", "需要切分", "需要分割"],
        "单周期": ["单周期", "single cycle", "一个时钟", "单时钟", "one clock"]
    },

    "支撑关键词": {
        "瓶颈描述": ["瓶颈", "bottleneck", "关键级", "critical stage", "最慢级"],
        "处理模块": ["处理器", "processor", "数据通路", "datapath", "处理单元"],
        "算法模块": ["FIR滤波器", "FFT", "图像处理", "video processing", "DSP core"]
    },

    "上下文关键词": {
        "性能需求": ["高频", "高速", "real-time", "实时", "高性能", "high performance"],
        "延迟容忍": ["延迟可接受", "latency tolerant", "吞吐量优先", "throughput critical"],
        "架构调整": ["重新设计", "redesign", "架构优化", "architecture optimization"]
    },

    "排除关键词": {
        "强排除": ["简单逻辑", "基础门", "单个运算", "simple operation"],
        "弱排除": ["逻辑层级", "组合逻辑", "logic levels"]
    }
}

numerical_features = {
    "setup_001_combinational_chain": {
        "logic_levels": {
            "min": 6, "max": 20, "typical": 8,
            "strong_indicator": 10,
            "weak_threshold": 6
        },
        "delay_range": {
            "min": 2.0, "max": 8.0, "unit": "ns",
            "typical": 4.0
        },
        "gate_count": {
            "min": 10, "typical": 20
        }
    },

    "setup_002_arithmetic_unit": {
        "logic_levels": {
            "min": 3, "max": 8, "typical": 5
        },
        "delay_range": {
            "min": 3.0, "max": 15.0, "unit": "ns",
            "typical": 6.0
        },
        "bit_width": {
            "common": [16, 24, 32, 64],
            "strong_indicator": 32
        }
    },

    "setup_016_pipeline_insufficient": {
        "single_stage_delay": {
            "min": 8.0, "unit": "ns",
            "strong_indicator": 12.0
        },
        "target_frequency": {
            "min": 100, "unit": "MHz",
            "high_freq_threshold": 200
        },
        "algorithm_complexity": {
            "indicators": ["多步骤", "复杂算法", "迭代", "recursive"]
        }
    }
}


def classify_timing_scenario(text):


    processed_text = preprocess_text(text)


    features = extract_all_features(processed_text)


    initial_scores = keyword_matching(processed_text)


    numerical_scores = numerical_validation(features)


    exclusion_scores = exclusion_check(processed_text)


    context_scores = context_analysis(processed_text)


    final_scores = combine_scores(initial_scores, numerical_scores,
                                  exclusion_scores, context_scores)


    return final_decision(final_scores)


def preprocess_text(text):


    processed = text.strip()


    processed = re.sub(r'\s+', ' ', processed)
    processed = re.sub(r'\n+', ' ', processed)



    def lower_english_only(match):
        return match.group().lower()

    processed = re.sub(r'[a-zA-Z]+', lower_english_only, processed)



    processed = re.sub(r'(\d+\.?\d*)\s*(ns|ps|ms|MHz|GHz|级|位|bit)', r'\1\2', processed)


    replacements = {

        "逻辑级数": "逻辑层级",
        "门级数": "逻辑层级",
        "logic level": "logic levels",
        "combinational path": "combinational logic",
        "mult": "multiplier",
        "div": "divider",


        "，": ",",
        "。": ".",
        "：": ":",
        "；": ";",
    }

    for old, new in replacements.items():
        processed = processed.replace(old, new)


    processed = re.sub(r'[,，.。]{2,}', '.', processed)

    return processed


def extract_all_features(text):
    features = {}


    features["logic_levels"] = extract_logic_levels(text)


    features["delay_value"] = extract_delay_value(text)


    features["frequency"] = extract_frequency(text)


    features["bit_width"] = extract_bit_width(text)


    features["component_types"] = extract_component_types(text)


    features["algorithm_types"] = extract_algorithm_types(text)


    features["problem_types"] = extract_problem_types(text)


    features["text_stats"] = calculate_text_stats(text)

    return features


def extract_logic_levels(text):
    patterns = [
        r'(\d+)级.*?逻辑',
        r'(\d+)\s*levels?\s*of\s*logic',
        r'logic.*?(\d+).*?levels?',
        r'逻辑层级.*?(\d+)',
        r'逻辑深度.*?(\d+)',
        r'(\d+)级.*?门',
    ]

    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            try:
                level = int(matches[0])
                if 1 <= level <= 50:
                    return level
            except ValueError:
                continue

    return None


def extract_delay_value(text):
    patterns = [
        r'延迟.*?(\d+\.?\d*)\s*(ns|ps)',
        r'delay.*?(\d+\.?\d*)\s*(ns|ps)',
        r'(\d+\.?\d*)\s*(ns|ps).*?延迟',
        r'耗时.*?(\d+\.?\d*)\s*(ns|ps)',
        r'时序.*?(\d+\.?\d*)\s*(ns|ps)',
    ]

    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            try:
                value = float(matches[0][0])
                unit = matches[0][1].lower()


                if unit == 'ps':
                    value = value / 1000

                if 0.1 <= value <= 100:
                    return value
            except (ValueError, IndexError):
                continue

    return None


def extract_frequency(text):
    patterns = [
        r'频率.*?(\d+\.?\d*)\s*(MHz|GHz)',
        r'(\d+\.?\d*)\s*(MHz|GHz)',
        r'时钟.*?(\d+\.?\d*)\s*(MHz|GHz)',
        r'clock.*?(\d+\.?\d*)\s*(MHz|GHz)',
    ]

    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            try:
                value = float(matches[0][0])
                unit = matches[0][1].lower()


                if unit == 'ghz':
                    value = value * 1000

                if 1 <= value <= 10000:
                    return value
            except (ValueError, IndexError):
                continue

    return None


def extract_bit_width(text):
    patterns = [
        r'(\d+)位.*?(乘法器|加法器|运算器)',
        r'(\d+)-?bit.*?(mult|add|arith)',
        r'(\d+)位.*?数据',
        r'位宽.*?(\d+)',
        r'width.*?(\d+)',
    ]

    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            try:
                width = int(matches[0] if isinstance(matches[0], str) else matches[0][0])
                if 4 <= width <= 128:
                    return width
            except (ValueError, IndexError):
                continue

    return None


def extract_component_types(text):
    component_keywords = {
        "basic_gates": ["AND门", "OR门", "XOR门", "NAND门", "NOR门", "非门",
                        "and gate", "or gate", "xor gate", "nand gate", "nor gate", "inverter"],
        "arithmetic_units": ["乘法器", "除法器", "加法器", "减法器", "运算器",
                             "multiplier", "divider", "adder", "subtractor", "arithmetic"],
        "dsp_units": ["DSP", "MAC", "FIR", "IIR", "滤波器", "filter"],
        "selectors": ["MUX", "DMUX", "多路选择器", "译码器", "编码器",
                      "decoder", "encoder", "selector"],
        "memory": ["RAM", "ROM", "FIFO", "存储器", "memory", "buffer"]
    }

    found_components = []

    for category, keywords in component_keywords.items():
        for keyword in keywords:
            if keyword.lower() in text.lower():
                found_components.append(category)
                break

    return found_components


def extract_algorithm_types(text):
    algorithm_keywords = {
        "dsp_algorithms": ["FIR", "IIR", "FFT", "DFT", "卷积", "convolution", "滤波", "filter"],
        "image_processing": ["图像处理", "视频处理", "image processing", "video processing"],
        "communication": ["调制", "解调", "编码", "解码", "modulation", "demodulation"],
        "control": ["控制算法", "PID", "状态机", "control algorithm", "state machine"],
        "math": ["矩阵", "向量", "matrix", "vector", "linear algebra"]
    }

    found_algorithms = []

    for category, keywords in algorithm_keywords.items():
        for keyword in keywords:
            if keyword.lower() in text.lower():
                found_algorithms.append(category)
                break

    return found_algorithms


def extract_problem_types(text):
    problem_keywords = {
        "timing_violation": ["时序违规", "setup violation", "建立时间", "timing failure"],
        "delay_excessive": ["延迟过大", "延迟超标", "delay excessive", "timing critical"],
        "frequency_low": ["频率低", "速度慢", "performance low", "frequency insufficient"],
        "resource_shortage": ["资源不足", "resource insufficient", "utilization high"],
        "power_high": ["功耗高", "power consumption", "power high"]
    }

    found_problems = []

    for category, keywords in problem_keywords.items():
        for keyword in keywords:
            if keyword.lower() in text.lower():
                found_problems.append(category)
                break

    return found_problems


def calculate_text_stats(text):
    stats = {}


    stats["length"] = len(text)
    stats["word_count"] = len(text.split())
    stats["sentence_count"] = len(re.split(r'[.。!！?？]', text))


    chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
    english_chars = len(re.findall(r'[a-zA-Z]', text))
    total_chars = chinese_chars + english_chars

    if total_chars > 0:
        stats["chinese_ratio"] = chinese_chars / total_chars
        stats["english_ratio"] = english_chars / total_chars
    else:
        stats["chinese_ratio"] = 0
        stats["english_ratio"] = 0


    numbers = re.findall(r'\d+\.?\d*', text)
    stats["number_count"] = len(numbers)
    stats["number_density"] = len(numbers) / len(text.split()) if text.split() else 0


    technical_terms = ["逻辑", "延迟", "频率", "时钟", "流水线", "运算",
                       "logic", "delay", "frequency", "clock", "pipeline", "arithmetic"]
    term_count = sum(1 for term in technical_terms if term in text.lower())
    stats["technical_density"] = term_count / len(text.split()) if text.split() else 0

    return stats


def keyword_matching(text):
    scores = {
        "setup_001_combinational_chain": 0,
        "setup_002_arithmetic_unit": 0,
        "setup_003_pipeline_insufficient": 0
    }


    core_weight = 3.0
    support_weight = 2.0
    context_weight = 1.0




    for keyword in scenario_001_keywords["核心关键词"]["中文"]:
        if keyword in text:
            scores["setup_001_combinational_chain"] += core_weight


    for keyword in scenario_001_keywords["核心关键词"]["英文"]:
        if keyword.lower() in text.lower():
            scores["setup_001_combinational_chain"] += core_weight


    import re
    for pattern in scenario_001_keywords["核心关键词"]["数值模式"]:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            scores["setup_001_combinational_chain"] += core_weight * len(matches)


    for category in scenario_001_keywords["支撑关键词"]:
        for keyword in scenario_001_keywords["支撑关键词"][category]:
            if keyword.lower() in text.lower():
                scores["setup_001_combinational_chain"] += support_weight


    for category in scenario_001_keywords["上下文关键词"]:
        for keyword in scenario_001_keywords["上下文关键词"][category]:
            if keyword.lower() in text.lower():
                scores["setup_001_combinational_chain"] += context_weight




    for keyword in scenario_002_keywords["核心关键词"]["运算单元"]:
        if keyword.lower() in text.lower():
            scores["setup_002_arithmetic_unit"] += core_weight


    for keyword in scenario_002_keywords["核心关键词"]["浮点运算"]:
        if keyword.lower() in text.lower():
            scores["setup_002_arithmetic_unit"] += core_weight


    for keyword in scenario_002_keywords["核心关键词"]["复杂运算"]:
        if keyword.lower() in text.lower():
            scores["setup_002_arithmetic_unit"] += core_weight


    for pattern in scenario_002_keywords["支撑关键词"]["位宽描述"]:
        if isinstance(pattern, str):

            if pattern.lower() in text.lower():
                scores["setup_002_arithmetic_unit"] += support_weight
        else:

            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                scores["setup_002_arithmetic_unit"] += support_weight * len(matches)


    for keyword in scenario_002_keywords["支撑关键词"]["延迟特征"]:
        if keyword.lower() in text.lower():
            scores["setup_002_arithmetic_unit"] += support_weight


    for keyword in scenario_002_keywords["支撑关键词"]["性能指标"]:
        if keyword.lower() in text.lower():
            scores["setup_002_arithmetic_unit"] += support_weight


    for keyword in scenario_002_keywords["上下文关键词"]["算法相关"]:
        if keyword.lower() in text.lower():
            scores["setup_002_arithmetic_unit"] += context_weight


    for keyword in scenario_002_keywords["上下文关键词"]["优化建议"]:
        if keyword.lower() in text.lower():
            scores["setup_002_arithmetic_unit"] += context_weight




    for keyword in scenario_003_keywords["核心关键词"]["流水线"]:
        if keyword.lower() in text.lower():
            scores["setup_003_pipeline_insufficient"] += core_weight


    for keyword in scenario_003_keywords["核心关键词"]["深度相关"]:
        if keyword.lower() in text.lower():
            scores["setup_003_pipeline_insufficient"] += core_weight


    for keyword in scenario_003_keywords["核心关键词"]["单周期"]:
        if keyword.lower() in text.lower():
            scores["setup_003_pipeline_insufficient"] += core_weight


    for keyword in scenario_003_keywords["支撑关键词"]["瓶颈描述"]:
        if keyword.lower() in text.lower():
            scores["setup_003_pipeline_insufficient"] += support_weight


    for keyword in scenario_003_keywords["支撑关键词"]["处理模块"]:
        if keyword.lower() in text.lower():
            scores["setup_003_pipeline_insufficient"] += support_weight


    for keyword in scenario_003_keywords["支撑关键词"]["算法模块"]:
        if keyword.lower() in text.lower():
            scores["setup_003_pipeline_insufficient"] += support_weight


    for keyword in scenario_003_keywords["上下文关键词"]["性能需求"]:
        if keyword.lower() in text.lower():
            scores["setup_003_pipeline_insufficient"] += context_weight


    for keyword in scenario_003_keywords["上下文关键词"]["延迟容忍"]:
        if keyword.lower() in text.lower():
            scores["setup_003_pipeline_insufficient"] += context_weight


    for keyword in scenario_003_keywords["上下文关键词"]["架构调整"]:
        if keyword.lower() in text.lower():
            scores["setup_003_pipeline_insufficient"] += context_weight




    pipeline_patterns = [
        r'(\d+)级.*?流水线',
        r'(\d+)\s*stage.*?pipeline',
        r'pipeline.*?(\d+).*?stage',
        r'需要.*?(\d+)级',
        r'切分.*?(\d+)级',
        r'分.*?(\d+)级',
    ]

    for pattern in pipeline_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            scores["setup_003_pipeline_insufficient"] += core_weight * len(matches)


    arithmetic_patterns = [
        r'(\d+)位.*?(乘法器|加法器|运算器|multiplier|adder)',
        r'(DSP48|DSP\d+)',
        r'(MAC|multiply.*?accumulate)',
        r'(FPU|floating.*?point.*?unit)',
    ]

    for pattern in arithmetic_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            scores["setup_002_arithmetic_unit"] += core_weight * len(matches)

    return scores


def numerical_validation(features):
    scores = {
        "setup_001_combinational_chain": 0,
        "setup_002_arithmetic_unit": 0,
        "setup_003_pipeline_insufficient": 0
    }

    logic_levels = features.get("logic_levels")
    delay_value = features.get("delay_value")
    bit_width = features.get("bit_width")


    if logic_levels:
        if logic_levels >= 10:
            scores["setup_001_combinational_chain"] += 4
        elif logic_levels >= 6:
            scores["setup_001_combinational_chain"] += 2

    if delay_value:
        if 2.0 <= delay_value <= 8.0:
            scores["setup_001_combinational_chain"] += 2


    if delay_value and delay_value >= 3.0:
        if logic_levels and logic_levels <= 6:
            scores["setup_002_arithmetic_unit"] += 3

    if bit_width and bit_width >= 32:
        scores["setup_002_arithmetic_unit"] += 2


    if delay_value and delay_value >= 12.0:
        scores["setup_003_pipeline_insufficient"] += 4
    elif delay_value and delay_value >= 8.0:
        scores["setup_003_pipeline_insufficient"] += 2

    return scores


def exclusion_check(text):
    exclusion_scores = {
        "setup_001_combinational_chain": 0,
        "setup_002_arithmetic_unit": 0,
        "setup_003_pipeline_insufficient": 0
    }


    strong_exclusions_1 = ["乘法器", "除法器", "DSP", "multiplier", "arithmetic unit"]
    for exclusion in strong_exclusions_1:
        if exclusion in text.lower():
            exclusion_scores["setup_001_combinational_chain"] -= 3


    strong_exclusions_2 = ["基础逻辑门", "简单逻辑", "basic gates"]
    for exclusion in strong_exclusions_2:
        if exclusion in text.lower():
            exclusion_scores["setup_002_arithmetic_unit"] -= 3


    if any(word in text for word in ["多级逻辑", "逻辑链", "logic levels"]):
        exclusion_scores["setup_002_arithmetic_unit"] -= 1

    if any(word in text for word in ["乘法器", "运算单元", "multiplier"]):
        exclusion_scores["setup_001_combinational_chain"] -= 1

    return exclusion_scores


def context_analysis(text):
    context_scores = {
        "setup_001_combinational_chain": 0,
        "setup_002_arithmetic_unit": 0,
        "setup_003_pipeline_insufficient": 0
    }


    optimization_keywords = ["逻辑优化", "重构", "logic optimization"]
    if any(keyword in text for keyword in optimization_keywords):
        context_scores["setup_001_combinational_chain"] += 1

    pipeline_keywords = ["流水线", "pipeline", "分级", "stages"]
    if any(keyword in text for keyword in pipeline_keywords):
        context_scores["setup_003_pipeline_insufficient"] += 2

    algorithm_keywords = ["DSP算法", "FIR", "FFT", "滤波器", "图像处理"]
    if any(keyword in text for keyword in algorithm_keywords):
        context_scores["setup_002_arithmetic_unit"] += 1
        context_scores["setup_003_pipeline_insufficient"] += 1

    return context_scores


def combine_scores(initial_scores, numerical_scores, exclusion_scores, context_scores):
    final_scores = {}

    for scenario in initial_scores:
        final_scores[scenario] = (
                initial_scores[scenario] * 1.0 +
                numerical_scores[scenario] * 1.2 +
                exclusion_scores[scenario] * 1.0 +
                context_scores[scenario] * 0.8
        )

    return final_scores


def final_decision(scores):

    best_scenario = max(scores, key=scores.get)
    best_score = scores[best_scenario]


    total_positive_score = sum(max(0, score) for score in scores.values())
    confidence = best_score / total_positive_score if total_positive_score > 0 else 0


    min_score_threshold = 2.0
    min_confidence_threshold = 0.4

    if best_score < min_score_threshold or confidence < min_confidence_threshold:
        return "unknown", confidence

    return best_scenario, confidence

if __name__ == '__main__':
    test_text1 = "错误产生原因：关键路径src_reg->logic_chain[7:0]->dst_reg包含8级组合逻辑门链，主要由AND、OR、XOR门构成的复杂布尔运算。从src_reg寄存器输出的数据信号经过连续8级门延迟传播(每级约0.6ns)，总组合逻辑延迟达到4.8ns。由于目标时钟周期为5ns(200MHz)，减去寄存器建立时间(0.4ns)和时钟偏斜(0.2ns)后，可用组合逻辑时间窗口仅为4.4ns。当前路径的组合逻辑延迟(4.8ns)超出时间预算0.4ns，导致目标寄存器dst_reg在时钟上升沿到达时数据尚未稳定，建立时间余量不足(-0.4ns)，形成关键路径时序违规。"
    test_text2 = "错误产生原因：32位浮点乘法器(FPU_MULT)成为关键路径瓶颈，从输入寄存器mult_a_reg、mult_b_reg到输出寄存器result_reg的运算延迟达到7.2ns。该乘法器采用华莱士树结构进行部分积累加，包含符号处理、指数运算、尾数相乘和规格化等多个串行阶段，其中尾数乘法阶段的54位×54位乘法运算贡献了主要延迟(4.8ns)。在150MHz时钟频率下(6.67ns周期)，减去输入/输出寄存器的建立保持时间(0.8ns)和时钟偏斜(0.3ns)后，乘法器可用时间预算为5.57ns。当前运算单元延迟(7.2ns)严重超出预算1.63ns，导致result_reg无法在时钟沿建立稳定数据，建立时间余量为(-1.63ns)，形成运算路径时序违规。"
    test_text3 = "错误产生原因：16阶FIR数字滤波器采用单周期实现架构，所有乘加运算集中在一个时钟周期内完成。关键路径从输入数据寄存器data_in_reg经过16个系数乘法器(MULT0~MULT15)和15级加法器树(ADD_TREE[14:0])到输出寄存器filter_out_reg，总计算延迟达到13.5ns。其中乘法器阵列贡献6.8ns延迟，累加器树贡献6.7ns延迟。在100MHz目标频率下(10ns周期)，减去寄存器时序开销(1.2ns)和时钟网络延迟(0.4ns)后，可用计算时间窗口为8.4ns。当前单周期实现的计算延迟(13.5ns)远超时间预算5.1ns，导致输出寄存器filter_out_reg无法在时钟周期内获得稳定的滤波结果，建立时间余量严重不足(-5.1ns)，需要引入多级流水线架构将计算过程分解到3-4个时钟周期中以满足时序要求。"
























    print(classify_timing_scenario(test_text1))