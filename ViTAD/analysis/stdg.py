from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Set, Optional, Tuple, Any
import networkx as nx


class NodeType(Enum):
    REGISTER = "register"
    LOGIC_BLOCK = "logic_block"
    SIGNAL = "signal"
    MODULE = "module"
    IO_PORT = "io_port"

class EdgeType(Enum):
    DATA_FLOW = "data_flow"
    CONTROL_FLOW = "control_flow"
    CLOCK_EDGE = "clock_edge"
    MODULE_CONN = "module_conn"


class ViolationType(Enum):
    SETUP = "setup_violation"
    HOLD = "hold_violation"
    CDC = "cdc_violation"
    NONE = "no_violation"


class LogicType(Enum):
    ASSIGN_CONTINUOUS = "assign_continuous"
    ASSIGN_NONBLOCKING = "assign_nonblocking"
    ASSIGN_BLOCKING = "assign_blocking"
    CONDITIONAL = "conditional"
    CASE = "case"
    LOOP = "loop"
    RESET = "reset"
    UNKNOWN = "unknown"


@dataclass
class SourceCodeInfo:
    file_path: str = ""
    line_number: int = 0
    column_start: int = 0
    column_end: int = 0
    raw_statement: str = ""
    formatted_statement: str = ""
    statement_type: str = ""

    def get_location_string(self) -> str:
        return f"{self.file_path}:{self.line_number}"


@dataclass
class ViolationInfo:
    violation_type: ViolationType = ViolationType.NONE
    slack: Optional[float] = None
    startpoint: Optional[str] = None
    endpoint: Optional[str] = None
    path_group: Optional[str] = None
    required_time: Optional[float] = None
    arrival_time: Optional[float] = None
    source_clock_domain: Optional[str] = None
    target_clock_domain: Optional[str] = None
    is_cross_clock_domain: bool = False
    signal_width: Optional[int] = None
    cdc_risk_level: Optional[str] = None


@dataclass
class CodeStructureNode:
    node_id: str
    node_type: NodeType
    name: str


    source_info: SourceCodeInfo = None


    module_name: Optional[str] = None
    signal_name: Optional[str] = None
    signal_width: Optional[int] = None
    signal_range: Optional[str] = None
    is_multi_bit: bool = False


    clock_domain: Optional[str] = None
    clock_edge: Optional[str] = None
    reset_signal: Optional[str] = None
    reset_type: Optional[str] = None


    logic_type: LogicType = LogicType.UNKNOWN
    assignment_target: Optional[str] = None
    assignment_sources: List[str] = None
    condition_expression: Optional[str] = None


    violation_info: ViolationInfo = None


    properties: Dict = None

    def __post_init__(self):
        if self.violation_info is None:
            self.violation_info = ViolationInfo()
        if self.properties is None:
            self.properties = {}
        if self.assignment_sources is None:
            self.assignment_sources = []
        if self.source_info is None:
            self.source_info = SourceCodeInfo()


        if self.signal_width is not None and self.signal_width > 1:
            self.is_multi_bit = True

    def get_display_statement(self) -> str:
        if self.source_info.formatted_statement:
            return self.source_info.formatted_statement
        elif self.source_info.raw_statement:
            return self.source_info.raw_statement
        else:

            return self._generate_default_display()

    def _generate_default_display(self) -> str:
        if self.logic_type == LogicType.ASSIGN_CONTINUOUS:
            if self.assignment_target and self.assignment_sources:
                sources = " + ".join(self.assignment_sources)
                return f"assign {self.assignment_target} = {sources}"
        elif self.logic_type == LogicType.ASSIGN_NONBLOCKING:
            if self.assignment_target and self.assignment_sources:
                sources = " + ".join(self.assignment_sources)
                return f"{self.assignment_target} <= {sources}"
        elif self.logic_type == LogicType.CONDITIONAL:
            if self.condition_expression:
                return f"if ({self.condition_expression})"

        return self.name


@dataclass
class CodeStructureEdge:
    source: str
    target: str
    edge_type: EdgeType


    signal_name: Optional[str] = None
    condition: Optional[str] = None
    signal_width: Optional[int] = None


    source_info: SourceCodeInfo = None


    crosses_clock_domain: bool = False
    source_clock_domain: Optional[str] = None
    target_clock_domain: Optional[str] = None
    is_multi_bit_cdc: bool = False


    properties: Dict = None

    def __post_init__(self):
        if self.properties is None:
            self.properties = {}
        if self.source_info is None:
            self.source_info = SourceCodeInfo()


        if (self.crosses_clock_domain and
                self.signal_width is not None and
                self.signal_width > 1):
            self.is_multi_bit_cdc = True


class CodeStructureGraph:

    def __init__(self):
        self.graph = nx.DiGraph()
        self.nodes: Dict[str, CodeStructureNode] = {}
        self.edges: Dict[Tuple[str, str], CodeStructureEdge] = {}
        self.violation_registers: Set[str] = set()
        self.violation_paths: List[Dict] = []


        self.source_files: Dict[str, str] = {}
        self.line_to_statement: Dict[str, Dict[int, str]] = {}

    def add_source_file(self, file_path: str, content: str):
        self.source_files[file_path] = content


        lines = content.split('\n')
        self.line_to_statement[file_path] = {}
        for i, line in enumerate(lines, 1):
            self.line_to_statement[file_path][i] = line.strip()

    def add_node(self, node: CodeStructureNode):
        self.nodes[node.node_id] = node
        self.graph.add_node(node.node_id, **node.__dict__)


        if node.violation_info.violation_type != ViolationType.NONE:
            self.violation_registers.add(node.node_id)

    def add_edge(self, edge: CodeStructureEdge):
        edge_key = (edge.source, edge.target)


        if edge.source in self.nodes and edge.target in self.nodes:
            source_clock = self.nodes[edge.source].clock_domain
            target_clock = self.nodes[edge.target].clock_domain

            if source_clock and target_clock and source_clock != target_clock:
                edge.crosses_clock_domain = True
                edge.source_clock_domain = source_clock
                edge.target_clock_domain = target_clock


                if edge.signal_width is None:

                    source_node = self.nodes[edge.source]
                    if source_node.signal_width is not None:
                        edge.signal_width = source_node.signal_width

        self.edges[edge_key] = edge
        self.graph.add_edge(edge.source, edge.target, **edge.__dict__)

    def get_execution_trace_display(self, execution_path: List[str]) -> List[str]:
        display_path = []

        for node_id in execution_path:
            if node_id in self.nodes:
                node = self.nodes[node_id]

                if node.node_type == NodeType.LOGIC_BLOCK:

                    display_path.append(node.get_display_statement())
                else:

                    display_path.append(node.signal_name or node.name)
            else:
                display_path.append(node_id)

        return display_path

    def format_violation_trace_output(self, trace_id: int, path_info: Dict) -> str:
        output_lines = []


        output_lines.append(f"违规轨迹 {trace_id}:")


        entry_point = path_info['entry_point']
        if entry_point in self.nodes:
            entry_signal = self.nodes[entry_point].signal_name or self.nodes[entry_point].name
        else:
            entry_signal = entry_point
        output_lines.append(f"  入口点: {entry_signal}")


        violation_register = path_info['violation_register']
        if violation_register in self.nodes:
            viol_signal = self.nodes[violation_register].signal_name or self.nodes[violation_register].name
        else:
            viol_signal = violation_register
        output_lines.append(f"  违规寄存器: {viol_signal}")


        execution_path = path_info['execution_path']
        display_path = self.get_execution_trace_display(execution_path)
        output_lines.append(f"  执行路径: {' -> '.join(display_path)}")


        output_lines.append(f"  路径长度: {path_info['path_length']}")


        violations = path_info.get('violations', [])
        output_lines.append(f"  该路径上的违规信息 ({len(violations)}个):")

        for i, violation in enumerate(violations, 1):
            output_lines.append(f"    违规{i}:")
            output_lines.append(f"      违规类型: {violation['violation_type'].value}")
            output_lines.append(f"      时序裕量: {violation.get('timing_slack', 'N/A')}ns")
            output_lines.append(f"      起点->终点: {violation['startpoint']} -> {violation['endpoint']}")
            output_lines.append(f"      要求时间: {violation.get('required_time', 'N/A')}ns")
            output_lines.append(f"      到达时间: {violation.get('arrival_time', 'N/A')}ns")
            output_lines.append(f"      路径组: {violation.get('path_group', 'N/A')}")

        return '\n'.join(output_lines)


    def _evaluate_cdc_risk_level(self, signal_width: Optional[int]) -> str:
        if signal_width is None or signal_width == 1:
            return "low"
        elif signal_width <= 8:
            return "medium"
        else:
            return "high"

    def mark_violation_path(self, startpoint: str, endpoint: str, violation_info: ViolationInfo):

        if violation_info.violation_type == ViolationType.CDC:
            violation_info.cdc_risk_level = self._evaluate_cdc_risk_level(violation_info.signal_width)


        if startpoint in self.nodes:
            self.nodes[startpoint].violation_info = violation_info
            self.violation_registers.add(startpoint)

        if endpoint in self.nodes:
            self.nodes[endpoint].violation_info = violation_info
            self.violation_registers.add(endpoint)


        violation_path_dict = {
            'startpoint': startpoint,
            'endpoint': endpoint,
            'violation_info': violation_info
        }
        self.violation_paths.append(violation_path_dict)

    def find_entry_points(self, target_register: Optional[str] = None) -> List[str]:
        entry_points = []


        topological_entries = []
        for node_id in self.nodes:
            if len(list(self.graph.predecessors(node_id))) == 0:
                topological_entries.append(node_id)


        input_ports = []
        for node_id, node in self.nodes.items():
            if (node.node_type == NodeType.IO_PORT and
                    node.properties.get('direction') == 'input'):
                input_ports.append(node_id)


        reset_logic_entries = []
        for node_id, node in self.nodes.items():
            if (node.node_type == NodeType.LOGIC_BLOCK and
                    node.logic_type == LogicType.RESET):
                reset_logic_entries.append(node_id)


        if target_register and target_register in self.nodes:
            target_clock_domain = self.nodes[target_register].clock_domain


            domain_specific_entries = []


            for entry_id in reset_logic_entries:
                entry_node = self.nodes[entry_id]
                if entry_node.clock_domain == target_clock_domain:
                    domain_specific_entries.append(entry_id)


            for entry_id in input_ports:

                try:
                    if nx.has_path(self.graph, entry_id, target_register):
                        domain_specific_entries.append(entry_id)
                except nx.NetworkXError:
                    continue


            for entry_id in topological_entries:
                try:
                    if nx.has_path(self.graph, entry_id, target_register):
                        domain_specific_entries.append(entry_id)
                except nx.NetworkXError:
                    continue

            if domain_specific_entries:
                entry_points.extend(domain_specific_entries)
            else:

                entry_points.extend(reset_logic_entries)
                entry_points.extend(input_ports)
                entry_points.extend(topological_entries)
        else:

            entry_points.extend(reset_logic_entries)
            entry_points.extend(input_ports)


            if not entry_points:
                entry_points.extend(topological_entries)


        return list(set(entry_points))

    def find_execution_paths(self, start: str, end: str, max_paths: int = 10) -> List[List[str]]:
        try:

            paths = list(nx.all_simple_paths(self.graph, start, end))
            return paths[:max_paths]
        except nx.NetworkXNoPath:
            return []

    def find_full_execution_paths_to_violation(self, violation_register: str, max_paths: int = 10) -> List[Dict]:
        entry_points = self.find_entry_points(target_register=violation_register)
        full_execution_paths = []

        for entry_point in entry_points:
            try:

                paths = list(nx.all_simple_paths(self.graph, entry_point, violation_register))

                for path in paths[:max_paths]:
                    path_info = {
                        'entry_point': entry_point,
                        'violation_register': violation_register,
                        'execution_path': path,
                        'path_length': len(path)
                    }
                    full_execution_paths.append(path_info)

            except nx.NetworkXNoPath:
                continue

        return full_execution_paths

    def find_all_violation_execution_paths(self) -> List[Dict]:

        violation_registers = set()
        for violation_path in self.violation_paths:
            violation_registers.add(violation_path['endpoint'])


        unique_physical_paths = {}

        for violation_register in violation_registers:
            full_paths = self.find_full_execution_paths_to_violation(violation_register)

            for full_path in full_paths:

                path_key = (full_path['entry_point'], tuple(full_path['execution_path']))

                if path_key not in unique_physical_paths:
                    unique_physical_paths[path_key] = {
                        'entry_point': full_path['entry_point'],
                        'violation_register': violation_register,
                        'execution_path': full_path['execution_path'],
                        'path_length': full_path['path_length'],
                        'violations': []
                    }


        for violation_path in self.violation_paths:
            startpoint = violation_path['startpoint']
            endpoint = violation_path['endpoint']
            violation_info = violation_path['violation_info']


            for path_key, path_info in unique_physical_paths.items():
                execution_path = path_info['execution_path']


                if (startpoint in execution_path and
                        endpoint in execution_path and
                        execution_path.index(startpoint) < execution_path.index(endpoint)):
                    timing_info = {
                        'violation_type': violation_info.violation_type,
                        'timing_slack': violation_info.slack,
                        'required_time': violation_info.required_time,
                        'arrival_time': violation_info.arrival_time,
                        'path_group': violation_info.path_group,
                        'source_clock_domain': violation_info.source_clock_domain,
                        'target_clock_domain': violation_info.target_clock_domain,
                        'is_cross_clock_domain': violation_info.is_cross_clock_domain,
                        'startpoint': startpoint,
                        'endpoint': endpoint
                    }

                    path_info['violations'].append(timing_info)


        all_violation_paths = []
        for path_info in unique_physical_paths.values():
            if path_info['violations']:
                violation_execution_path = {
                    'entry_point': path_info['entry_point'],
                    'violation_register': path_info['violation_register'],
                    'execution_path': path_info['execution_path'],
                    'path_length': path_info['path_length'],
                    'violations': path_info['violations']
                }
                all_violation_paths.append(violation_execution_path)

        return all_violation_paths

    def get_clock_domains(self) -> Set[str]:
        domains = set()
        for node in self.nodes.values():
            if node.clock_domain:
                domains.add(node.clock_domain)
        return domains

    def get_register_nodes(self) -> List[str]:
        return [nid for nid, node in self.nodes.items()
                if node.node_type == NodeType.REGISTER]

    def analyze_multi_bit_cdc_risks(self) -> Dict:
        cdc_analysis = {
            'total_cdc_edges': 0,
            'single_bit_cdc': 0,
            'multi_bit_cdc': 0,
            'high_risk_cdc': [],
            'medium_risk_cdc': [],
            'low_risk_cdc': []
        }


        for edge_key, edge in self.edges.items():
            if edge.crosses_clock_domain:
                cdc_analysis['total_cdc_edges'] += 1

                width = edge.signal_width or 1
                risk_level = self._evaluate_cdc_risk_level(width)

                cdc_info = {
                    'edge': edge_key,
                    'signal_name': edge.signal_name,
                    'width': width,
                    'source_domain': edge.source_clock_domain,
                    'target_domain': edge.target_clock_domain,
                    'source_location': edge.source_info.get_location_string()
                }

                if risk_level == "high":
                    cdc_analysis['high_risk_cdc'].append(cdc_info)
                elif risk_level == "medium":
                    cdc_analysis['medium_risk_cdc'].append(cdc_info)
                else:
                    cdc_analysis['low_risk_cdc'].append(cdc_info)
                    cdc_analysis['single_bit_cdc'] += 1

                if width > 1:
                    cdc_analysis['multi_bit_cdc'] += 1

        return cdc_analysis