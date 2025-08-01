from prompt_class import PromptTemplate


def generate_analysis_prompt(code: str, spec: str, pre_analysis_info: str):
    template = PromptTemplate()

    template.set_role_definition("You are an expert in analyzing timing safety issues in Verilog code. I will provide some relevant information below. Please combine this information and try to analyze the cause according to my requirements. The information provided in each section below is enclosed in '[]'.")

    buggy_code_content = '[\n'
    buggy_code_content += ''.join(code)
    buggy_code_content += '\n]'
    template.set_buggy_code(buggy_code_content)

    design_spec_content = '[\n'
    design_spec_content += ''.join(spec)
    design_spec_content += '\n]'
    template.set_design_spec(design_spec_content)

    pre_analysis_content = '[\n'
    pre_analysis_content += ''.join(pre_analysis_info)
    pre_analysis_content += '\n]'
    template.set_pre_analysis_info(pre_analysis_content)

    template.set_requirement("Please analyze the cause of the error code based on the information provided above. Provide detailed reasons for the error in a logical and progressive manner. No other explanation is required. Write the result in “{}”。")

    return template