import os
import json
import time
from datetime import datetime
from pathlib import Path
import logging
from openai import OpenAI


class GPT4BatchProcessor:
    def __init__(self, api_key=None):


        if api_key is None:
            api_key = api_key = "Your API key here"

        if not api_key:
            raise ValueError("请设置OPENAI_API_KEY环境变量或传入api_key参数")


        self.client = OpenAI(api_key=api_key)


        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('gpt4_batch.log', encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        self.logger.info("GPT-4批处理器初始化完成")

    def call_api(self, prompt, model="gpt-4o", max_tokens=16384, temperature=0.7, system_prompt=None):
        try:

            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                stream=False
            )

            response_dict = {
                "id": response.id,
                "object": response.object,
                "created": response.created,
                "model": response.model,
                "choices": [
                    {
                        "index": choice.index,
                        "message": {
                            "role": choice.message.role,
                            "content": choice.message.content
                        },
                        "finish_reason": choice.finish_reason
                    }
                    for choice in response.choices
                ],
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
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


            if response_data and 'choices' in response_data and response_data['choices']:
                content = response_data['choices'][0]['message']['content']
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

    def calculate_cost(self, usage, model):
        pricing = {
            "gpt-4o": {"input": 0.0025, "output": 0.01},
            "gpt-4o-mini": {"input": 0.00015, "output": 0.0006},
            "gpt-4-turbo": {"input": 0.01, "output": 0.03},
            "gpt-4": {"input": 0.03, "output": 0.06},
            "gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015},
        }

        if model not in pricing:
            return 0.0

        input_cost = (usage.get('prompt_tokens', 0) / 1000) * pricing[model]['input']
        output_cost = (usage.get('completion_tokens', 0) / 1000) * pricing[model]['output']

        return input_cost + output_cost

    def process_prompts(self, prompt_folder, output_folder, iterations=5, delay=1,
                        model="gpt-4o", system_prompt=None):

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
        total_tokens = 0
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
                        call_tokens = usage.get('total_tokens', 0)
                        call_cost = self.calculate_cost(usage, model)
                        total_tokens += call_tokens
                        total_cost += call_cost

                        self.logger.info(f"    Token使用: 输入={usage.get('prompt_tokens', 0)}, "
                                         f"输出={usage.get('completion_tokens', 0)}, "
                                         f"总计={call_tokens}")
                        self.logger.info(f"    本次成本: ${call_cost:.6f}")

                    successful_calls += 1
                else:
                    self.logger.error(f"    第 {i} 次调用失败")
                    failed_calls += 1


                if call_count < total_calls:
                    time.sleep(delay)

        end_time = time.time()
        total_time = end_time - start_time

        self.logger.info(f"\n{'=' * 60}")
        self.logger.info(f"批量处理完成！")
        self.logger.info(f"处理时间: {total_time:.2f}秒 ({total_time / 60:.2f}分钟)")
        self.logger.info(f"Prompt文件: {total_prompts}个")
        self.logger.info(f"成功调用: {successful_calls}次")
        self.logger.info(f"失败调用: {failed_calls}次")
        self.logger.info(f"总Token消耗: {total_tokens:,}")
        self.logger.info(f"总成本: ${total_cost:.4f}")
        if successful_calls > 0:
            self.logger.info(
                f"平均每次调用: {total_tokens / successful_calls:.1f} tokens, ${total_cost / successful_calls:.6f}")
        self.logger.info(f"输出文件夹: {output_folder}")
        self.logger.info(f"{'=' * 60}")


def main():

    CONFIG = {
        "prompt_folder": "./insufficient_pipi_stage_prompts",
        "output_folder": "./results/insufficient_pipi_stage_gpt_outputs",
        "iterations": 5,
        "delay": 1.0,
        "model": "gpt-4o",
        "system_prompt": None
    }

    available_models = [
        "gpt-4o",
        "gpt-4o-mini",
        "gpt-4-turbo",
        "gpt-4",
        "gpt-3.5-turbo",
    ]

    try:
        processor = GPT4BatchProcessor()

        print(f"可用模型: {', '.join(available_models)}")
        print(f"当前使用模型: {CONFIG['model']}")
        print(f"预计总调用次数: {len(list(Path(CONFIG['prompt_folder']).glob('*.txt')))} × {CONFIG['iterations']} = ?")

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
        print("  Windows: set OPENAI_API_KEY=your-api-key")
        print("  Linux/Mac: export OPENAI_API_KEY=your-api-key")
        print("\n方法2: 在代码中直接传入")
        print("  processor = GPT4BatchProcessor(api_key='your-api-key')")
        print("\n获取API密钥：")
        print("  访问 https://platform.openai.com/api-keys")

    except Exception as e:
        print(f"运行错误: {e}")


if __name__ == "__main__":
    main()