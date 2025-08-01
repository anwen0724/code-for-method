

import os
import json
import time
from datetime import datetime
from pathlib import Path
import logging
import anthropic


class ClaudeBatchProcessor:
    def __init__(self, api_key=None):

        if api_key is None:
            api_key = "Your API key here"

        if not api_key:
            raise ValueError("请设置ANTHROPIC_API_KEY环境变量或传入api_key参数")


        self.client = anthropic.Anthropic(api_key=api_key)


        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('claude_batch.log', encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        self.logger.info("Claude Sonnet 4批处理器初始化完成")

    def call_api(self, prompt, model="claude-3-5-sonnet-20241022", max_tokens=8192,
                 temperature=0.7, system_prompt=None):

        try:

            messages = [
                {
                    "role": "user",
                    "content": prompt
                }
            ]


            request_params = {
                "model": model,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "messages": messages
            }


            if system_prompt:
                request_params["system"] = system_prompt

            response = self.client.messages.create(**request_params)


            response_dict = {
                "id": response.id,
                "type": response.type,
                "role": response.role,
                "model": response.model,
                "content": [
                    {
                        "type": content.type,
                        "text": content.text
                    }
                    for content in response.content
                ],
                "stop_reason": response.stop_reason,
                "stop_sequence": response.stop_sequence,
                "usage": {
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens
                }
            }

            return response_dict

        except Exception as e:
            self.logger.error(f"API调用失败: {e}")
            return None

    def read_prompt_files(self, prompt_folder):

        prompt_folder = Path(prompt_folder)
        if not prompt_folder.exists():
            self.logger.error(f"Prompt文件夹不存在: {prompt_folder}")
            return {}

        prompts = {}

        text_extensions = ['.txt', '.md', '.prompt']

        for ext in text_extensions:
            for file_path in prompt_folder.glob(f"*{ext}"):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read().strip()
                        if content:
                            prompts[file_path.stem] = content
                            self.logger.info(f"读取Prompt文件: {file_path.name}")
                        else:
                            self.logger.warning(f"文件为空: {file_path.name}")
                except Exception as e:
                    self.logger.error(f"读取文件失败 {file_path.name}: {e}")

        self.logger.info(f"总共读取到 {len(prompts)} 个有效的Prompt文件")
        return prompts

    def save_response(self, response_data, output_folder, prompt_name, iteration):

        output_folder = Path(output_folder)
        output_folder.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]


        json_filename = f"{prompt_name}_iter{iteration:02d}_{timestamp}.json"
        json_path = output_folder / json_filename

        try:
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(response_data, f, ensure_ascii=False, indent=2)

            self.logger.info(f"JSON响应已保存: {json_filename}")


            if response_data and 'content' in response_data and response_data['content']:
                content = response_data['content'][0]['text']
                txt_filename = f"{prompt_name}_iter{iteration:02d}_{timestamp}.txt"
                txt_path = output_folder / txt_filename

                with open(txt_path, 'w', encoding='utf-8') as f:
                    f.write(content)

                self.logger.info(f"文本内容已保存: {txt_filename}")


                if 'usage' in response_data:
                    return response_data['usage']

        except Exception as e:
            self.logger.error(f"保存文件失败: {e}")

        return None

    def calculate_cost(self, usage):


        input_price_per_1k = 0.003
        output_price_per_1k = 0.015

        input_cost = (usage.get('input_tokens', 0) / 1000) * input_price_per_1k
        output_cost = (usage.get('output_tokens', 0) / 1000) * output_price_per_1k

        return input_cost + output_cost

    def process_prompts(self, prompt_folder, output_folder, iterations=5, delay=2,
                        model="claude-3-5-sonnet-20241022", system_prompt=None):

        prompts = self.read_prompt_files(prompt_folder)

        if not prompts:
            self.logger.error("没有找到有效的Prompt文件")
            return

        total_prompts = len(prompts)
        total_calls = total_prompts * iterations

        self.logger.info(f"\n{'=' * 60}")
        self.logger.info(f"开始批量处理")
        self.logger.info(f"Prompt文件数量: {total_prompts}")
        self.logger.info(f"每个文件调用次数: {iterations}")
        self.logger.info(f"总计API调用: {total_calls}")
        self.logger.info(f"使用模型: {model}")
        self.logger.info(f"请求间隔: {delay}秒")
        if system_prompt:
            self.logger.info(f"系统提示词: {system_prompt[:100]}...")
        self.logger.info(f"{'=' * 60}\n")

        call_count = 0
        total_input_tokens = 0
        total_output_tokens = 0
        total_cost = 0.0
        successful_calls = 0
        failed_calls = 0

        start_time = time.time()

        for prompt_idx, (prompt_name, prompt_content) in enumerate(prompts.items(), 1):
            self.logger.info(f"\n处理Prompt [{prompt_idx}/{total_prompts}]: {prompt_name}")
            self.logger.info(f"Prompt长度: {len(prompt_content)} 字符")

            for i in range(1, iterations + 1):
                call_count += 1
                self.logger.info(f"  第 {i} 次调用 (总进度: {call_count}/{total_calls})")


                response = self.call_api(prompt_content, model=model, system_prompt=system_prompt)

                if response:

                    usage = self.save_response(response, output_folder, prompt_name, i)

                    if usage:
                        call_input_tokens = usage.get('input_tokens', 0)
                        call_output_tokens = usage.get('output_tokens', 0)
                        call_total_tokens = call_input_tokens + call_output_tokens
                        call_cost = self.calculate_cost(usage)

                        total_input_tokens += call_input_tokens
                        total_output_tokens += call_output_tokens
                        total_cost += call_cost

                        self.logger.info(f"    Token使用: 输入={call_input_tokens}, "
                                         f"输出={call_output_tokens}, "
                                         f"总计={call_total_tokens}")
                        self.logger.info(f"    本次成本: ${call_cost:.6f}")

                    successful_calls += 1
                else:
                    self.logger.error(f"    第 {i} 次调用失败")
                    failed_calls += 1


                if call_count < total_calls:
                    time.sleep(delay)

        end_time = time.time()
        total_time = end_time - start_time
        total_tokens = total_input_tokens + total_output_tokens


        self.logger.info(f"\n{'=' * 60}")
        self.logger.info(f"批量处理完成！")
        self.logger.info(f"处理时间: {total_time:.2f}秒 ({total_time / 60:.2f}分钟)")
        self.logger.info(f"Prompt文件: {total_prompts}个")
        self.logger.info(f"成功调用: {successful_calls}次")
        self.logger.info(f"失败调用: {failed_calls}次")
        self.logger.info(f"Token消耗:")
        self.logger.info(f"  输入Token: {total_input_tokens:,}")
        self.logger.info(f"  输出Token: {total_output_tokens:,}")
        self.logger.info(f"  总计Token: {total_tokens:,}")
        self.logger.info(f"总成本: ${total_cost:.4f}")
        if successful_calls > 0:
            avg_tokens = total_tokens / successful_calls
            avg_cost = total_cost / successful_calls
            self.logger.info(f"平均每次调用: {avg_tokens:.1f} tokens, ${avg_cost:.6f}")
        self.logger.info(f"输出文件夹: {output_folder}")
        self.logger.info(f"{'=' * 60}")


def main():


    CONFIG = {
        "prompt_folder": "./insufficient_pipi_stage_prompts",
        "output_folder": "./results/insufficient_pipi_stage_claude_outputs",
        "iterations": 5,
        "delay": 2.0,
        "model": "claude-3-5-sonnet-20241022",
        "system_prompt": None,

    }


    available_models = [
        "claude-3-5-sonnet-20241022",
        "claude-3-5-haiku-20241022",
        "claude-3-opus-20240229",
        "claude-3-sonnet-20240229",
        "claude-3-haiku-20240307",
    ]

    try:

        processor = ClaudeBatchProcessor()

        print(f"可用模型: {', '.join(available_models)}")
        print(f"当前使用模型: {CONFIG['model']}")


        prompt_folder = Path(CONFIG['prompt_folder'])
        if prompt_folder.exists():
            prompt_count = len(list(prompt_folder.glob('*.txt'))) + \
                           len(list(prompt_folder.glob('*.md'))) + \
                           len(list(prompt_folder.glob('*.prompt')))
            total_calls = prompt_count * CONFIG['iterations']
            estimated_cost = total_calls * 0.02

            print(f"发现Prompt文件: {prompt_count}个")
            print(f"预计总调用次数: {total_calls}")
            print(f"预计成本: ${estimated_cost:.2f} (粗略估算)")
        else:
            print(f"Prompt文件夹不存在: {CONFIG['prompt_folder']}")


        confirm = input("\n是否继续执行批量处理？(y/N): ").strip().lower()
        if confirm not in ['y', 'yes']:
            print("已取消执行")
            return


        processor.process_prompts(
            prompt_folder=CONFIG["prompt_folder"],
            output_folder=CONFIG["output_folder"],
            iterations=CONFIG["iterations"],
            delay=CONFIG["delay"],
            model=CONFIG["model"],
            system_prompt=CONFIG["system_prompt"]
        )

    except ValueError as e:
        print(f"配置错误: {e}")
        print("\n请按以下方式设置API密钥：")
        print("方法1: 设置环境变量")
        print("  Windows: set ANTHROPIC_API_KEY=your-api-key")
        print("  Linux/Mac: export ANTHROPIC_API_KEY=your-api-key")
        print("\n方法2: 在代码中直接传入")
        print("  processor = ClaudeBatchProcessor(api_key='your-api-key')")
        print("\n获取API密钥：")
        print("  访问 https://console.anthropic.com/")

    except Exception as e:
        print(f"运行错误: {e}")


if __name__ == "__main__":
    main()