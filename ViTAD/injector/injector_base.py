from pyverilog.vparser.parser import parse


class VerilogInjector:
    def __init__(self, source_code: str):
        self.code = source_code
        self.ast = self._parse_to_ast()

    def _parse_to_ast(self):
        ast, _ = parse([self.code])
        return ast

    def find_injection_points(self):
        raise NotImplementedError

    def inject(self):
        raise NotImplementedError
