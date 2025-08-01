from prompt_class import PromptTemplate


def generate_setupORholdup_repair_prompt(code: str, spec: str, base_info: str, analysis_info: str, error_cause: str, repair_suggestion: str):
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

    basic_info_content = '[\n'
    basic_info_content += ''.join(base_info)
    basic_info_content += '\n]'
    template.set_basic_info(basic_info_content)

    pre_analysis_info_content = '[\n'
    pre_analysis_info_content += ''.join(analysis_info)
    pre_analysis_info_content += ']'
    template.set_pre_analysis_info(pre_analysis_info_content)

    error_cause_description_content = '[\n'
    error_cause_description_content += ''.join(error_cause)
    error_cause_description_content += '\n]'
    template.set_error_cause_description(error_cause_description_content)

    repair_suggestion_content = '[\n'
    repair_suggestion_content += ''.join(repair_suggestion)
    repair_suggestion_content += '\n]'
    template.set_repair_suggestion(repair_suggestion_content)

    template.set_requirement("Please analyze the cause of the error code based on the information provided above. Provide detailed reasons for the error in a logical and progressive manner. No other explanation is required. Write the result in “{}”。")

    return template


def generate_cdc_repair_prompt(code: str, spec: str, base_info: str, analysis_info: str, error_cause: str, repair_suggestion: str):
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


    basic_info_content = '[\n'
    basic_info_content += ''.join(base_info)
    basic_info_content += '\n]'
    template.set_basic_info(basic_info_content)

    pre_analysis_info_content = '[\n'
    pre_analysis_info_content += ''.join(analysis_info)
    pre_analysis_info_content += ']'
    template.set_pre_analysis_info(pre_analysis_info_content)

    error_cause_description_content = '[\n'
    error_cause_description_content += ''.join(error_cause)
    error_cause_description_content += '\n]'
    template.set_error_cause_description(error_cause_description_content)

    repair_suggestion_content = '[\n'
    repair_suggestion_content += ''.join(repair_suggestion)
    repair_suggestion_content += '\n]'
    template.set_repair_suggestion(repair_suggestion_content)


    template.set_requirement("Please analyze the cause of the error code based on the information provided above. Provide detailed reasons for the error in a logical and progressive manner. No other explanation is required. Write the result in “{}”。")

    return template