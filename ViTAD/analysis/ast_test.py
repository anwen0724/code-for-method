def analyze_ast_structure(ast, case_name):

    print(f"\n--- {case_name} AST结构 ---")


    if hasattr(ast, 'children'):
        children = list(ast.children())
        print(f"顶层子节点数量: {len(children)}")
        for i, child in enumerate(children):
            print(f"  子节点 {i}: {type(child).__name__}")
            if hasattr(child, 'name'):
                print(f"    名称: {child.name}")


    module_node = find_module_definition(ast)
    if module_node:
        print(f"找到模块: {getattr(module_node, 'name', 'unnamed')}")
        return module_node
    else:
        print("未找到模块定义")
        return None


def detailed_analysis(ast):
    print(f"\n{'=' * 30}")
    print("详细AST分析")
    print(f"{'=' * 30}")


    module_node = find_module_definition(ast)
    if module_node:
        analyze_module_structure(module_node)


    print("\n=== 关键节点类型统计 ===")
    analyze_key_node_types(ast)




from pyverilog.vparser.parser import VerilogParser
from pyverilog.ast_code_generator.codegen import ASTCodeGenerator
import os
import tempfile











def analyze_pyverilog_ast():


    test_cases = [
        ("简单计数器", simple_verilog_code),
        ("流水线示例", medium_verilog_code),
        ("原始ALU代码", original_verilog_code)
    ]

    for case_name, verilog_code in test_cases:
        print(f"\n{'=' * 50}")
        print(f"测试用例: {case_name}")
        print(f"{'=' * 50}")


        with tempfile.NamedTemporaryFile(mode='w', suffix='.v', delete=False) as f:
            f.write(verilog_code)
            verilog_file = f.name

        try:

            print("正在解析Verilog文件...")
            parser = VerilogParser()
            ast, _ = parser.parse([verilog_file])

            print(f"✓ 解析成功！")
            print(f"AST类型: {type(ast)}")


            analyze_ast_structure(ast, case_name)


            if case_name == "简单计数器":
                detailed_analysis(ast)

        except Exception as e:
            print(f"✗ 解析失败: {e}")
            print(f"错误类型: {type(e).__name__}")


            if "Expected" in str(e):
                print("可能的问题：")
                print("- PyVerilog可能不支持某些Verilog语法")
                print("- 注释格式问题")
                print("- 复杂的表达式")
                print("- 三元操作符问题")

        finally:

            try:
                os.unlink(verilog_file)
            except:
                pass


def find_module_definition(ast):
    if hasattr(ast, 'children'):
        for child in ast.children():
            if 'ModuleDef' in type(child).__name__:
                return child

            result = find_module_definition(child)
            if result:
                return result
    return None


def analyze_module_structure(module_node):
    print(f"模块节点类型: {type(module_node).__name__}")
    print(f"模块名称: {getattr(module_node, 'name', 'N/A')}")

    if hasattr(module_node, 'children'):
        print(f"模块子节点数量: {len(list(module_node.children()))}")

        for i, child in enumerate(module_node.children()):
            node_type = type(child).__name__
            print(f"  子节点 {i}: {node_type}")


            if 'Portlist' in node_type or 'PortArg' in node_type:
                analyze_ports(child)


            elif 'Decl' in node_type:
                analyze_declarations(child)


            elif 'Always' in node_type:
                analyze_always_block(child)


            elif 'Assign' in node_type:
                analyze_assign_statement(child)


def analyze_ports(port_node):
    print(f"    端口节点: {type(port_node).__name__}")
    if hasattr(port_node, 'children'):
        for port in port_node.children():
            if hasattr(port, 'name'):
                direction = getattr(port, 'direction', 'unknown')
                print(f"      端口: {port.name} ({direction})")


def analyze_declarations(decl_node):
    print(f"    声明节点: {type(decl_node).__name__}")
    if hasattr(decl_node, 'children'):
        for decl in decl_node.children():
            if hasattr(decl, 'name'):
                decl_type = type(decl).__name__
                print(f"      声明: {decl.name} ({decl_type})")


def analyze_always_block(always_node):
    print(f"    Always块: {type(always_node).__name__}")


    if hasattr(always_node, 'sens_list'):
        print(f"      敏感信号列表: {type(always_node.sens_list).__name__}")
        analyze_sensitivity_list(always_node.sens_list)


    if hasattr(always_node, 'statement'):
        print(f"      语句块: {type(always_node.statement).__name__}")
        analyze_statement_block(always_node.statement, depth=3)


def analyze_sensitivity_list(sens_list):
    if hasattr(sens_list, 'children'):
        for sens in sens_list.children():
            sens_type = type(sens).__name__
            print(f"        敏感信号: {sens_type}")
            if hasattr(sens, 'sig'):
                print(f"          信号: {sens.sig}")
            if hasattr(sens, 'type'):
                print(f"          类型: {sens.type}")


def analyze_assign_statement(assign_node):
    print(f"    Assign语句: {type(assign_node).__name__}")
    if hasattr(assign_node, 'left'):
        print(f"      左值: {type(assign_node.left).__name__}")
    if hasattr(assign_node, 'right'):
        print(f"      右值: {type(assign_node.right).__name__}")


def analyze_statement_block(stmt_node, depth=0):
    indent = "  " * depth
    stmt_type = type(stmt_node).__name__
    print(f"{indent}语句: {stmt_type}")


    if 'If' in stmt_type:
        print(f"{indent}  条件: {type(getattr(stmt_node, 'cond', None)).__name__}")
        print(f"{indent}  then分支: {type(getattr(stmt_node, 'true_statement', None)).__name__}")
        if hasattr(stmt_node, 'false_statement') and stmt_node.false_statement:
            print(f"{indent}  else分支: {type(stmt_node.false_statement).__name__}")


    elif 'Assign' in stmt_type or 'NonblockingSubstitution' in stmt_type or 'BlockingSubstitution' in stmt_type:
        if hasattr(stmt_node, 'left'):
            print(f"{indent}  目标: {extract_signal_name(stmt_node.left)}")
        if hasattr(stmt_node, 'right'):
            print(f"{indent}  源: {extract_expression_signals(stmt_node.right)}")


    if hasattr(stmt_node, 'children') and depth < 5:
        for child in stmt_node.children():
            if child:
                analyze_statement_block(child, depth + 1)


def extract_signal_name(node):
    if hasattr(node, 'var'):
        if hasattr(node.var, 'name'):
            return node.var.name
    elif hasattr(node, 'name'):
        return node.name
    return f"<{type(node).__name__}>"


def extract_expression_signals(node):
    signals = []

    def traverse_expr(n):
        if hasattr(n, 'name'):
            signals.append(n.name)
        elif hasattr(n, 'var') and hasattr(n.var, 'name'):
            signals.append(n.var.name)
        elif hasattr(n, 'children'):
            for child in n.children():
                if child:
                    traverse_expr(child)

    traverse_expr(node)
    return signals if signals else [f"<{type(node).__name__}>"]


def analyze_key_node_types(ast):
    node_types = set()

    def collect_node_types(node):
        node_types.add(type(node).__name__)
        if hasattr(node, 'children'):
            for child in node.children():
                if child:
                    collect_node_types(child)

    collect_node_types(ast)

    print("发现的AST节点类型:")
    for node_type in sorted(node_types):
        print(f"  - {node_type}")


if __name__ == "__main__":
    print("开始分析PyVerilog AST结构...")
    try:
        analyze_pyverilog_ast()
        print("\nAST结构分析完成！")
    except ImportError:
        print("请先安装PyVerilog: pip install pyverilog")
    except Exception as e:
        print(f"分析过程中出现错误: {e}")
        import traceback

        traceback.print_exc()