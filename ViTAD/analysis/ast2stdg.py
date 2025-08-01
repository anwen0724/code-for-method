
from typing import Dict, List, Set, Optional, Tuple, Any
from dataclasses import dataclass
import pyverilog.vparser.ast as vast
from stdg_define import (
    CodeStructureGraph, CodeStructureNode, CodeStructureEdge,
    NodeType, EdgeType, ViolationInfo, ViolationType
)


@dataclass
class BuildContext:
    current_module: str = ""
    current_clock_domain: Optional[str] = None
    current_source_file: str = ""
    logic_block_counter: int = 0


class ASTToSTDGBuilder:

    def __init__(self):
        self.graph = CodeStructureGraph()
        self.context = BuildContext()

    def build_from_ast(self, ast_node: vast.Node, source_file: str = "") -> CodeStructureGraph:
        self.context.current_source_file = source_file
        self._visit_node(ast_node)
        return self.graph

    def _visit_node(self, node: vast.Node):
        if isinstance(node, vast.ModuleDef):
            self._handle_module_def(node)
        elif isinstance(node, vast.Decl):
            self._handle_declaration(node)
        elif isinstance(node, vast.Assign):
            self._handle_assign(node)
        elif isinstance(node, vast.Always):
            self._handle_always_block(node)
        elif isinstance(node, vast.InstanceList):
            self._handle_instance_list(node)


        if hasattr(node, 'children') and node.children:
            for child in node.children():
                if child:
                    self._visit_node(child)

    def _handle_module_def(self, node: vast.ModuleDef):
        self.context.current_module = node.name


        module_node = CodeStructureNode(
            node_id=f"module_{node.name}",
            node_type=NodeType.MODULE,
            name=node.name,
            module_name=node.name,
            source_location=f"{self.context.current_source_file}:{node.lineno}"
        )
        self.graph.add_node(module_node)


        if node.portlist:
            self._handle_port_list(node.portlist)

    def _handle_port_list(self, portlist: vast.Portlist):
        for port in portlist.ports:
            if isinstance(port, vast.Ioport):
                self._handle_io_port(port)

    def _handle_io_port(self, port: vast.Ioport):
        if isinstance(port.first, vast.Input):
            direction = "input"
            port_decl = port.first
        elif isinstance(port.first, vast.Output):
            direction = "output"
            port_decl = port.first
        elif isinstance(port.first, vast.Inout):
            direction = "inout"
            port_decl = port.first
        else:
            return


        width, width_range = self._extract_width_info(port_decl.width)


        port_node = CodeStructureNode(
            node_id=f"port_{port_decl.name}",
            node_type=NodeType.IO_PORT,
            name=port_decl.name,
            signal_name=port_decl.name,
            module_name=self.context.current_module,
            source_location=f"{self.context.current_source_file}:{port_decl.lineno}",
            signal_width=width,
            signal_range=width_range,
            properties={"direction": direction}
        )
        self.graph.add_node(port_node)

    def _handle_declaration(self, node: vast.Decl):
        for decl in node.list:
            if isinstance(decl, vast.Reg):
                self._create_register_node(decl)
            elif isinstance(decl, vast.Wire):
                self._create_signal_node(decl)

    def _create_register_node(self, reg_decl: vast.Reg):
        width, width_range = self._extract_width_info(reg_decl.width)

        reg_node = CodeStructureNode(
            node_id=f"reg_{reg_decl.name}",
            node_type=NodeType.REGISTER,
            name=reg_decl.name,
            signal_name=reg_decl.name,
            module_name=self.context.current_module,
            source_location=f"{self.context.current_source_file}:{reg_decl.lineno}",
            signal_width=width,
            signal_range=width_range,
            clock_domain=self.context.current_clock_domain
        )
        self.graph.add_node(reg_node)

    def _create_signal_node(self, wire_decl: vast.Wire):
        width, width_range = self._extract_width_info(wire_decl.width)

        signal_node = CodeStructureNode(
            node_id=f"signal_{wire_decl.name}",
            node_type=NodeType.SIGNAL,
            name=wire_decl.name,
            signal_name=wire_decl.name,
            module_name=self.context.current_module,
            source_location=f"{self.context.current_source_file}:{wire_decl.lineno}",
            signal_width=width,
            signal_range=width_range
        )
        self.graph.add_node(signal_node)

    def _handle_assign(self, node: vast.Assign):

        logic_id = f"assign_logic_{self.context.logic_block_counter}"
        self.context.logic_block_counter += 1

        assign_node = CodeStructureNode(
            node_id=logic_id,
            node_type=NodeType.LOGIC_BLOCK,
            name=f"assign_{self._extract_signal_name(node.left)}",
            module_name=self.context.current_module,
            source_location=f"{self.context.current_source_file}:{node.lineno}",
            properties={"assign_type": "continuous"}
        )
        self.graph.add_node(assign_node)


        right_signals = self._extract_signals_from_expression(node.right)
        left_signal = self._extract_signal_name(node.left)


        for signal in right_signals:
            source_id = self._get_node_id_by_signal(signal)
            if source_id:
                edge = CodeStructureEdge(
                    source=source_id,
                    target=logic_id,
                    edge_type=EdgeType.DATA_FLOW,
                    signal_name=signal,
                    source_location=f"{self.context.current_source_file}:{node.lineno}"
                )
                self.graph.add_edge(edge)


        target_id = self._get_node_id_by_signal(left_signal)
        if target_id:
            edge = CodeStructureEdge(
                source=logic_id,
                target=target_id,
                edge_type=EdgeType.DATA_FLOW,
                signal_name=left_signal,
                source_location=f"{self.context.current_source_file}:{node.lineno}"
            )
            self.graph.add_edge(edge)

    def _handle_always_block(self, node: vast.Always):

        clock_signal = self._extract_clock_from_sensitivity(node.sens_list)
        old_clock_domain = self.context.current_clock_domain
        self.context.current_clock_domain = clock_signal


        self._update_registers_clock_domain(clock_signal)


        if node.statement:
            self._handle_always_statement(node.statement, node.lineno)


        self.context.current_clock_domain = old_clock_domain

    def _handle_always_statement(self, stmt: vast.Node, base_lineno: int):
        if isinstance(stmt, vast.Block):

            for s in stmt.statements:
                self._handle_always_statement(s, base_lineno)

        elif isinstance(stmt, vast.IfStatement):
            self._handle_if_statement(stmt, base_lineno)

        elif isinstance(stmt, vast.NonblockingSubstitution):
            self._handle_nonblocking_assignment(stmt, base_lineno)

        elif isinstance(stmt, vast.BlockingSubstitution):
            self._handle_blocking_assignment(stmt, base_lineno)

    def _handle_if_statement(self, stmt: vast.IfStatement, base_lineno: int):

        logic_id = f"if_logic_{self.context.logic_block_counter}"
        self.context.logic_block_counter += 1

        condition_str = self._expression_to_string(stmt.cond)

        if_node = CodeStructureNode(
            node_id=logic_id,
            node_type=NodeType.LOGIC_BLOCK,
            name=f"if_condition_{condition_str}",
            module_name=self.context.current_module,
            source_location=f"{self.context.current_source_file}:{stmt.lineno}",
            clock_domain=self.context.current_clock_domain,
            properties={"logic_type": "conditional", "condition": condition_str}
        )
        self.graph.add_node(if_node)


        condition_signals = self._extract_signals_from_expression(stmt.cond)
        for signal in condition_signals:
            source_id = self._get_node_id_by_signal(signal)
            if source_id:
                edge = CodeStructureEdge(
                    source=source_id,
                    target=logic_id,
                    edge_type=EdgeType.CONTROL_FLOW,
                    signal_name=signal,
                    condition=condition_str,
                    source_location=f"{self.context.current_source_file}:{stmt.lineno}"
                )
                self.graph.add_edge(edge)


        if stmt.true_statement:
            self._handle_conditional_branch(stmt.true_statement, logic_id, condition_str, True)


        if stmt.false_statement:
            self._handle_conditional_branch(stmt.false_statement, logic_id, f"!({condition_str})", False)

    def _handle_conditional_branch(self, stmt: vast.Node, condition_logic_id: str, condition: str,
                                   is_true_branch: bool):
        if isinstance(stmt, vast.NonblockingSubstitution):
            self._handle_nonblocking_assignment(stmt, 0, condition_logic_id, condition)
        elif isinstance(stmt, vast.BlockingSubstitution):
            self._handle_blocking_assignment(stmt, 0, condition_logic_id, condition)
        elif isinstance(stmt, vast.Block):
            for s in stmt.statements:
                self._handle_conditional_branch(s, condition_logic_id, condition, is_true_branch)
        elif isinstance(stmt, vast.IfStatement):
            self._handle_if_statement(stmt, 0)

    def _handle_nonblocking_assignment(self, stmt: vast.NonblockingSubstitution, base_lineno: int,
                                       condition_logic_id: str = None, condition: str = None):

        logic_id = f"assign_logic_{self.context.logic_block_counter}"
        self.context.logic_block_counter += 1

        left_signal = self._extract_signal_name(stmt.left)

        assign_node = CodeStructureNode(
            node_id=logic_id,
            node_type=NodeType.LOGIC_BLOCK,
            name=f"assign_{left_signal}",
            module_name=self.context.current_module,
            source_location=f"{self.context.current_source_file}:{stmt.lineno}",
            clock_domain=self.context.current_clock_domain,
            properties={"assignment_type": "nonblocking"}
        )
        self.graph.add_node(assign_node)


        if condition_logic_id:
            control_edge = CodeStructureEdge(
                source=condition_logic_id,
                target=logic_id,
                edge_type=EdgeType.CONTROL_FLOW,
                condition=condition,
                source_location=f"{self.context.current_source_file}:{stmt.lineno}"
            )
            self.graph.add_edge(control_edge)


        right_signals = self._extract_signals_from_expression(stmt.right)
        for signal in right_signals:
            source_id = self._get_node_id_by_signal(signal)
            if source_id:
                edge = CodeStructureEdge(
                    source=source_id,
                    target=logic_id,
                    edge_type=EdgeType.DATA_FLOW,
                    signal_name=signal,
                    source_location=f"{self.context.current_source_file}:{stmt.lineno}"
                )
                self.graph.add_edge(edge)


        target_id = self._get_node_id_by_signal(left_signal)
        if target_id:
            edge = CodeStructureEdge(
                source=logic_id,
                target=target_id,
                edge_type=EdgeType.DATA_FLOW,
                signal_name=left_signal,
                source_location=f"{self.context.current_source_file}:{stmt.lineno}"
            )
            self.graph.add_edge(edge)
            print(f"DEBUG: 创建数据流边 {logic_id} -> {target_id} (信号: {left_signal})")
        else:
            print(f"DEBUG: 找不到左值信号的目标节点: {left_signal}")

            possible_ids = [f"reg_{left_signal}", f"port_{left_signal}", f"signal_{left_signal}"]
            existing_nodes = list(self.graph.nodes.keys())
            print(f"DEBUG: 可能的节点ID: {possible_ids}")
            print(f"DEBUG: 现有节点: {existing_nodes}")

    def _handle_blocking_assignment(self, stmt: vast.BlockingSubstitution, base_lineno: int,
                                    condition_logic_id: str = None, condition: str = None):

        logic_id = f"assign_logic_{self.context.logic_block_counter}"
        self.context.logic_block_counter += 1

        left_signal = self._extract_signal_name(stmt.left)

        assign_node = CodeStructureNode(
            node_id=logic_id,
            node_type=NodeType.LOGIC_BLOCK,
            name=f"assign_{left_signal}",
            module_name=self.context.current_module,
            source_location=f"{self.context.current_source_file}:{stmt.lineno}",
            clock_domain=self.context.current_clock_domain,
            properties={"assignment_type": "blocking"}
        )
        self.graph.add_node(assign_node)


        if condition_logic_id:
            control_edge = CodeStructureEdge(
                source=condition_logic_id,
                target=logic_id,
                edge_type=EdgeType.CONTROL_FLOW,
                condition=condition,
                source_location=f"{self.context.current_source_file}:{stmt.lineno}"
            )
            self.graph.add_edge(control_edge)

        right_signals = self._extract_signals_from_expression(stmt.right)
        for signal in right_signals:
            source_id = self._get_node_id_by_signal(signal)
            if source_id:
                edge = CodeStructureEdge(
                    source=source_id,
                    target=logic_id,
                    edge_type=EdgeType.DATA_FLOW,
                    signal_name=signal,
                    source_location=f"{self.context.current_source_file}:{stmt.lineno}"
                )
                self.graph.add_edge(edge)

        target_id = self._get_node_id_by_signal(left_signal)
        if target_id:
            edge = CodeStructureEdge(
                source=logic_id,
                target=target_id,
                edge_type=EdgeType.DATA_FLOW,
                signal_name=left_signal,
                source_location=f"{self.context.current_source_file}:{stmt.lineno}"
            )
            self.graph.add_edge(edge)

    def _handle_instance_list(self, node: vast.InstanceList):

        for instance in node.instances:
            if isinstance(instance, vast.Instance):
                instance_node = CodeStructureNode(
                    node_id=f"instance_{instance.name}",
                    node_type=NodeType.MODULE,
                    name=instance.name,
                    module_name=instance.module,
                    source_location=f"{self.context.current_source_file}:{instance.lineno}",
                    properties={"instance_type": instance.module}
                )
                self.graph.add_node(instance_node)


                if instance.portlist:
                    self._handle_instance_ports(instance)

    def _handle_instance_ports(self, instance: vast.Instance):


        pass


    def _extract_width_info(self, width_node) -> Tuple[int, Optional[str]]:
        if not width_node:
            return 1, None

        if isinstance(width_node, vast.Width):
            if len(width_node.children()) == 2:
                msb = width_node.children()[0]
                lsb = width_node.children()[1]
                if isinstance(msb, vast.IntConst) and isinstance(lsb, vast.IntConst):
                    width = int(msb.value) - int(lsb.value) + 1
                    range_str = f"[{msb.value}:{lsb.value}]"
                    return width, range_str

        return 1, None

    def _extract_clock_from_sensitivity(self, sens_list) -> Optional[str]:
        if not sens_list:
            return None

        for sens in sens_list.list:
            if isinstance(sens, vast.Sens):
                if sens.type == 'posedge' or sens.type == 'negedge':
                    if isinstance(sens.sig, vast.Identifier):
                        return sens.sig.name

        return None

    def _extract_signal_name(self, expr) -> str:
        if isinstance(expr, vast.Identifier):
            return expr.name
        elif isinstance(expr, vast.Lvalue):

            if hasattr(expr, 'var') and isinstance(expr.var, vast.Identifier):
                return expr.var.name
            elif hasattr(expr, 'children') and expr.children():
                child = expr.children()[0]
                if isinstance(child, vast.Identifier):
                    return child.name
        elif isinstance(expr, vast.Rvalue):

            if hasattr(expr, 'var') and isinstance(expr.var, vast.Identifier):
                return expr.var.name
            elif hasattr(expr, 'children') and expr.children():
                child = expr.children()[0]
                if isinstance(child, vast.Identifier):
                    return child.name
        elif isinstance(expr, vast.Partselect):
            if isinstance(expr.var, vast.Identifier):
                return expr.var.name
        elif isinstance(expr, vast.Pointer):
            if isinstance(expr.var, vast.Identifier):
                return expr.var.name
        elif hasattr(expr, 'name'):
            return expr.name


        print(f"DEBUG: 无法提取信号名，表达式类型: {type(expr)}")
        if hasattr(expr, '__dict__'):
            print(f"DEBUG: 表达式属性: {expr.__dict__}")

        return "unknown_signal"

    def _extract_signals_from_expression(self, expr) -> List[str]:
        signals = []

        if isinstance(expr, vast.Identifier):
            signals.append(expr.name)
        elif isinstance(expr, vast.Lvalue):

            if hasattr(expr, 'var') and isinstance(expr.var, vast.Identifier):
                signals.append(expr.var.name)
            elif hasattr(expr, 'children') and expr.children():
                for child in expr.children():
                    if child:
                        signals.extend(self._extract_signals_from_expression(child))
        elif isinstance(expr, vast.Rvalue):

            if hasattr(expr, 'var') and isinstance(expr.var, vast.Identifier):
                signals.append(expr.var.name)
            elif hasattr(expr, 'children') and expr.children():
                for child in expr.children():
                    if child:
                        signals.extend(self._extract_signals_from_expression(child))
        elif isinstance(expr, vast.Partselect):
            if isinstance(expr.var, vast.Identifier):
                signals.append(expr.var.name)
        elif isinstance(expr, vast.Pointer):
            if isinstance(expr.var, vast.Identifier):
                signals.append(expr.var.name)
        elif isinstance(expr, vast.IntConst):

            pass
        elif hasattr(expr, 'children') and expr.children:
            for child in expr.children():
                if child:
                    signals.extend(self._extract_signals_from_expression(child))
        elif hasattr(expr, 'name'):
            signals.append(expr.name)
        else:

            print(f"DEBUG: 未识别的表达式类型: {type(expr)}")

        return list(set(signals))

    def _expression_to_string(self, expr) -> str:
        if isinstance(expr, vast.Identifier):
            return expr.name
        elif isinstance(expr, vast.IntConst):
            return expr.value
        elif isinstance(expr, vast.Eq):
            left = self._expression_to_string(expr.left)
            right = self._expression_to_string(expr.right)
            return f"{left} == {right}"
        elif isinstance(expr, vast.Plus):
            left = self._expression_to_string(expr.left)
            right = self._expression_to_string(expr.right)
            return f"{left} + {right}"


        return "complex_expr"

    def _get_node_id_by_signal(self, signal_name: str) -> Optional[str]:

        possible_ids = [
            f"reg_{signal_name}",
            f"port_{signal_name}",
            f"signal_{signal_name}"
        ]

        for node_id in possible_ids:
            if node_id in self.graph.nodes:
                return node_id

        return None

    def _update_registers_clock_domain(self, clock_signal: str):
        if not clock_signal:
            return

        for node_id, node in self.graph.nodes.items():
            if (node.node_type == NodeType.REGISTER and
                    node.clock_domain is None):
                node.clock_domain = clock_signal