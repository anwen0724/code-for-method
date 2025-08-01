from injector_base import VerilogInjector


class SetupViolationInjector(VerilogInjector):

    def inject_long_comb(self):
        lines = self.code.splitlines()
        injected = False
        new_lines = []

        for line in lines:
            new_lines.append(line)
            if not injected and "assign" in line and ";" in line:
                injected = True
                new_lines.append()