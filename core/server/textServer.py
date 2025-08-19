import requests
import json
import re
from typing import Optional, Tuple

class TextProcessor:
    
    def __init__(self, 
                 ollama_url: str = "http://localhost:11434",
                 preferred_model: str = "gemma3n:latest",
                 use_llm_first: bool = True,
                 enable_spell_checker: bool = True,
                 enable_translator: bool = True):
        """
        初始化文本处理器
        
        Args:
            ollama_url: Ollama 服务器 URL
            preferred_model: 首选的 Ollama 模型
            use_llm_first: 是否优先使用大模型（False 则优先使用传统方法）
            enable_spell_checker: 是否启用传统拼写检查器
            enable_translator: 是否启用传统翻译器
        """
        self.ollama_url = ollama_url
        self.preferred_model = preferred_model
        self.use_llm_first = use_llm_first
        self.enable_spell_checker = enable_spell_checker
        self.enable_translator = enable_translator

        # 将耗时的网络/第三方初始化移到后台线程，避免在 UI 线程阻塞
        self.available_models = []
        self.spell_checker = None
        self.translator = None

        # 异步初始化（非阻塞）
        try:
            import threading
            init_thread = threading.Thread(target=self._background_init, daemon=True)
            init_thread.start()
        except Exception:
            # 如果 threading 不可用，回退到同步初始化（保证兼容性）
            self.available_models = self._check_available_models()
            self.spell_checker = self._init_spell_checker() if enable_spell_checker else None
            self.translator = self._init_translator() if enable_translator else None

    def _background_init(self):
        """在后台线程中完成耗时初始化（检查可用模型、初始化拼写检查器和翻译器）"""
        try:
            self.available_models = self._check_available_models()
        except Exception as e:
            print(f"后台检查模型失败: {e}")

        try:
            if self.enable_spell_checker:
                self.spell_checker = self._init_spell_checker()
        except Exception as e:
            print(f"后台初始化拼写检查器失败: {e}")

        try:
            if self.enable_translator:
                self.translator = self._init_translator()
        except Exception as e:
            print(f"后台初始化翻译器失败: {e}")

    def warm_up_model(self):
        import threading
        import time

        def warm_up_task():
            start_time = time.time()
            print(f"正在预热模型: {self.preferred_model}")
            data = {
                "model": self.preferred_model,
                "prompt": " ",
                "stream": False
            }
            
            try:
                response = requests.post(
                    f"{self.ollama_url}/api/generate",
                    json=data,
                    timeout=30
                )
                end_time = time.time()
                elapsed_time = end_time - start_time
                print(f"预热完成: {response}，耗时: {elapsed_time:.2f} 秒")
            except Exception as e:
                print(f"预热失败: {e}")

        # 在后台线程中执行预热任务
        warm_up_thread = threading.Thread(target=warm_up_task, daemon=True)
        warm_up_thread.start()

    def set_ollama_url(self, url: str):
        """设置 Ollama 服务器 URL"""
        self.ollama_url = url
        self.available_models = self._check_available_models()
    
    def set_preferred_model(self, model: str):
        """设置首选模型"""
        self.preferred_model = model
    
    def set_use_llm_first(self, use_llm_first: bool):
        """设置是否优先使用大模型"""
        self.use_llm_first = use_llm_first
    
    def get_available_models(self) -> list:
        """获取可用模型列表"""
        return self.available_models.copy()
    
    def get_current_settings(self) -> dict:
        """获取当前设置"""
        return {
            "ollama_url": self.ollama_url,
            "preferred_model": self.preferred_model,
            "use_llm_first": self.use_llm_first,
            "enable_spell_checker": self.enable_spell_checker,
            "enable_translator": self.enable_translator,
            "available_models": self.available_models,
            "spell_checker_available": self.spell_checker is not None,
            "translator_available": self.translator is not None
        }

    def _init_spell_checker(self):
        """初始化拼写检查器"""
        try:
            from spellchecker import SpellChecker
            return SpellChecker()
        except ImportError as e:
            print(f"spellchecker 库未安装，使用基础规则检查: {e}")
            return None
        except Exception as e:
            print(f"spellchecker 初始化失败，使用基础规则检查: {e}")
            return None
    
    def _init_translator(self):
        """初始化翻译器"""
        try:
            from googletrans import Translator
            return Translator()
        except ImportError:
            print("googletrans 库未安装，翻译功能受限")
            return None
        
    def _check_available_models(self) -> list:
        """检查 ollama 中可用的模型"""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=3)
            if response.status_code == 200:
                models = response.json().get('models', [])
                return [model['name'] for model in models]
        except Exception as e:
            print(f"无法连接到 ollama: {e}")
        return []

    def _call_ollama(self, prompt: str, model: str = None) -> Optional[str]:
        """调用 ollama API"""
        if not self.available_models:
            return None
        
        # 选择模型：优先使用指定模型，否则使用首选模型，最后使用第一个可用模型
        if model and model in self.available_models:
            target_model = model
        elif self.preferred_model in self.available_models:
            target_model = self.preferred_model
        else:
            target_model = self.available_models[0]
            
        # print(f"使用模型: {target_model}")
        try:
            data = {
                "model": target_model,
                "prompt": prompt,
                "stream": False
            }
            
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                raw_response = result.get('response', '').strip()
                # 清理思考标签和其他不需要的内容
                cleaned_response = self._clean_llm_response(raw_response)
                return cleaned_response
        except Exception as e:
            print(f"ollama 调用失败: {e}")
        
        return None
    
    def _clean_llm_response(self, response: str) -> str:
        """
        清理大模型响应中的思考标签和其他不需要的内容
        
        Args:
            response: 原始的模型响应
            
        Returns:
            清理后的响应文本
        """
        if not response:
            return response
        
        # 移除 <think> 标签及其内容
        cleaned = re.sub(r'<think>.*?</think>', '', response, flags=re.DOTALL)
        
        # 移除其他可能的思考标签格式
        cleaned = re.sub(r'<thinking>.*?</thinking>', '', cleaned, flags=re.DOTALL)
        cleaned = re.sub(r'<reasoning>.*?</reasoning>', '', cleaned, flags=re.DOTALL)
        cleaned = re.sub(r'<analysis>.*?</analysis>', '', cleaned, flags=re.DOTALL)
        
        # 移除可能的思考过程标记
        cleaned = re.sub(r'思考过程[:：].*?(?=\n\n|\n[^思]|\Z)', '', cleaned, flags=re.DOTALL)
        cleaned = re.sub(r'分析[:：].*?(?=\n\n|\n[^分]|\Z)', '', cleaned, flags=re.DOTALL)
        
        # 清理多余的空行和空格
        cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)  # 多个换行符压缩为双换行
        cleaned = re.sub(r'^\s+|\s+$', '', cleaned)    # 移除首尾空白
        cleaned = re.sub(r'\n\s*\n', '\n', cleaned)    # 清理空行中的空格
        
        return cleaned.strip()
    
    def spell_check(self, text: str, force_method: str = None) -> Tuple[str, str]:
        """
        拼写检查功能
        
        Args:
            text: 要检查的文本
            force_method: 强制使用的方法 ('llm' 或 'traditional')，None 则根据设置自动选择
            
        返回: (corrected_text, method_used)
        """
        # 如果强制指定方法
        if force_method == 'llm':
            corrected_llm = self._spell_check_with_llm(text)
            if corrected_llm:
                return corrected_llm, "Ollama"
            else:
                return text, "Ollama (失败，返回原文)"
        elif force_method == 'traditional':
            corrected_traditional = self._spell_check_traditional(text)
            method_name = "pyspellchecker"
            return corrected_traditional, method_name
        # 根据设置自动选择
        if self.use_llm_first:
            # 优先尝试 ollama 大模型
            corrected_llm = self._spell_check_with_llm(text)
            if corrected_llm:
                return corrected_llm, "Ollama"
            
            # 降级到传统方法
            corrected_traditional = self._spell_check_traditional(text)
            method_name = "pyspellchecker"
            return corrected_traditional, method_name
        else:
            # 优先使用传统方法
            try:
                corrected_traditional = self._spell_check_traditional(text)
                method_name = "pyspellchecker"
                return corrected_traditional, method_name
            except RuntimeError:
                # 传统方法失败，尝试大模型
                corrected_llm = self._spell_check_with_llm(text)
                if corrected_llm:
                    return corrected_llm, "Ollama"
                else:
                    return text, "所有方法都失败，返回原文"

    def _spell_check_with_llm(self, text: str) -> Optional[str]:
        """使用大模型进行拼写检查"""
        if not self.available_models:
            return None
        
        prompt = f"""请检查并纠正以下文本中的拼写错误，只返回纠正后的文本，不要添加任何解释：

原文：{text}

纠正后的文本："""
        
        result = self._call_ollama(prompt)
        if result and result != text:
            return result
        return None
    
    def _spell_check_traditional(self, text: str) -> str:
        """传统拼写检查方法"""
        if self.spell_checker:
            # 使用 spellchecker 库
            return self._spell_check_with_library(text)
        else:
            raise RuntimeError("拼写检查器不可用")

    def _spell_check_with_library(self, text: str) -> str:
        """使用 spellchecker 库进行拼写检查"""
        words = text.split()
        corrected_words = []
        
        for word in words:
            # 提取纯字母部分
            clean_word = re.sub(r'[^\w]', '', word.lower())
            if clean_word and clean_word in self.spell_checker:
                corrected_words.append(word)
            elif clean_word:
                # 获取建议
                suggestions = self.spell_checker.candidates(clean_word)
                # 检查 suggestions 是否为 None
                if suggestions is not None:
                    suggestions_list = list(suggestions)
                    if suggestions_list:
                        # 使用第一个建议，保持原始大小写格式
                        corrected = suggestions_list[0]
                        if word[0].isupper():
                            corrected = corrected.capitalize()
                        # 保持标点符号
                        corrected_word = re.sub(r'\w+', corrected, word)
                        corrected_words.append(corrected_word)
                    else:
                        corrected_words.append(word)
                else:
                    # 如果 candidates 返回 None，保持原词
                    corrected_words.append(word)
            else:
                corrected_words.append(word)
        return ' '.join(corrected_words)

    def translate(self, text: str, target_lang: str = "中文", force_method: str = None) -> Tuple[str, str]:
        """
        翻译功能
        
        Args:
            text: 要翻译的文本
            target_lang: 目标语言
            force_method: 强制使用的方法 ('llm' 或 'traditional')，None 则根据设置自动选择
        """
        # 如果强制指定方法
        if force_method == 'llm':
            translated_llm = self._translate_with_llm(text, target_lang)
            if translated_llm:
                return translated_llm, "Ollama"
            else:
                return text, "Ollama (失败，返回原文)"
        elif force_method == 'traditional':
            return self._translate_traditional(text, target_lang)
        
        # 根据设置自动选择
        if self.use_llm_first:
            # 优先使用大模型
            translated_llm = self._translate_with_llm(text, target_lang)
            if translated_llm:
                return translated_llm, "Ollama"
            
            # 降级到传统翻译服务
            return self._translate_traditional(text, target_lang)
        else:
            # 优先使用传统方法
            translated_traditional, method = self._translate_traditional(text, target_lang)
            if "失败" not in method and "不可用" not in method:
                return translated_traditional, method
            
            # 传统方法失败，尝试大模型
            translated_llm = self._translate_with_llm(text, target_lang)
            if translated_llm:
                return translated_llm, "Ollama"
            else:
                return translated_traditional, method

    def _translate_with_llm(self, text: str, target_lang: str) -> Optional[str]:
        """使用大模型翻译"""
        if not self.available_models:
            return None
        
        prompt = f"""请将以下文本翻译成{target_lang}，只返回翻译结果，不要添加任何解释：

原文：{text}

译文："""
        
        return self._call_ollama(prompt)
    
    def _translate_traditional(self, text: str, target_lang: str) -> Tuple[str, str]:
        """传统翻译方法"""
        if self.translator:
            try:
                # 语言代码映射
                lang_map = {
                    "中文": "zh",
                    "英文": "en", 
                    "日文": "ja",
                    "韩文": "ko",
                    "法文": "fr",
                    "德文": "de",
                    "西班牙文": "es"
                }
                
                target_code = lang_map.get(target_lang, "zh")
                result = self.translator.translate(text, dest=target_code)
                
                # 处理可能的异步结果
                if hasattr(result, 'text'):
                    return result.text, "Google 翻译"
                elif hasattr(result, '__await__'):
                    # 如果是异步结果，我们需要同步等待它
                    import asyncio
                    try:
                        loop = asyncio.get_event_loop()
                        if loop.is_running():
                            # 在已运行的事件循环中，我们不能使用 run_until_complete
                            return f"[异步翻译暂不支持] {text}", "Google 翻译 (异步)"
                        else:
                            actual_result = loop.run_until_complete(result)
                            return actual_result.text, "Google 翻译"
                    except:
                        return f"[异步翻译失败] {text}", "Google 翻译 (异步)"
                else:
                    # 如果结果直接是字符串
                    return str(result), "Google 翻译"
                    
            except Exception as e:
                print(f"Google 翻译失败: {e}")
                return f"[翻译失败] {text}", "翻译服务不可用"
        
        return f"[需要翻译服务] {text}", "无可用服务"
    
    def polish(self, text: str, force_method: str = None) -> Tuple[str, str]:
        """
        文本润色
        
        Args:
            text: 要润色的文本
            force_method: 强制使用的方法 ('llm' 或 'traditional')，None 则根据设置自动选择
        """
        # 如果强制指定方法
        if force_method == 'llm':
            polished_llm = self._polish_with_llm(text)
            if polished_llm:
                return polished_llm, "Ollama"
            else:
                return text, "Ollama (失败，返回原文)"
        elif force_method == 'traditional':
            polished = self._polish_traditional(text)
            return polished, "Traditional Method"
        
        # 根据设置自动选择
        if self.use_llm_first:
            # 优先使用大模型
            polished_llm = self._polish_with_llm(text)
            if polished_llm:
                return polished_llm, "Ollama"
            
            # 传统润色（基础格式化）
            polished = self._polish_traditional(text)
            return polished, "Traditional Method"
        else:
            # 优先使用传统方法
            polished = self._polish_traditional(text)
            
            # 如果传统方法结果不理想，可以尝试大模型
            if len(polished.strip()) == 0:
                polished_llm = self._polish_with_llm(text)
                if polished_llm:
                    return polished_llm, "Ollama"
            
            return polished, "Traditional Method"

    def _polish_traditional(self, text: str) -> str:
        """传统润色方法"""
        # 基础文本格式化
        polished = text.strip()
        
        # 修正常见格式问题
        polished = re.sub(r'\s+', ' ', polished)  # 多余空格
        polished = re.sub(r'\s+([.!?])', r'\1', polished)  # 标点前空格
        polished = re.sub(r'([.!?])\s*([A-Z])', r'\1 \2', polished)  # 句子间空格
        
        return polished
    
    def _polish_with_llm(self, text: str) -> Optional[str]:
        """使用大模型润色"""
        if not self.available_models:
            return None
        
        prompt = f"""请润色以下文本，使其更加流畅和专业，只返回润色后的文本：

原文：{text}

润色后："""
        
        return self._call_ollama(prompt)
    
    def summarize(self, text: str, force_method: str = None) -> Tuple[str, str]:
        """
        文本总结
        
        Args:
            text: 要总结的文本
            force_method: 强制使用的方法 ('llm' 或 'traditional')，None 则根据设置自动选择
        """
        # 如果强制指定方法
        if force_method == 'llm':
            summary_llm = self._summarize_with_llm(text)
            if summary_llm:
                return summary_llm, "Ollama"
            else:
                return text, "Ollama (失败，返回原文)"
        elif force_method == 'traditional':
            summary = self._summarize_traditional(text)
            return summary, "Traditional Method"
        
        # 根据设置自动选择
        if self.use_llm_first:
            # 优先使用大模型
            summary_llm = self._summarize_with_llm(text)
            if summary_llm:
                return summary_llm, "Ollama"
            
            # 传统总结方法
            summary = self._summarize_traditional(text)
            return summary, "Traditional Method"
        else:
            # 优先使用传统方法
            summary = self._summarize_traditional(text)
            
            # 如果文本很长，传统方法可能效果不好，可以尝试大模型
            if len(text.split()) > 100:  # 超过100个词
                summary_llm = self._summarize_with_llm(text)
                if summary_llm and len(summary_llm) < len(summary):
                    return summary_llm, "Ollama"
            
            return summary, "Traditional Method"

    def _summarize_traditional(self, text: str) -> str:
        """传统总结方法"""
        sentences = re.split(r'[.!?]+', text.strip())
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if len(sentences) <= 2:
            return text
        elif len(sentences) <= 5:
            # 取前两句
            return '. '.join(sentences[:2]) + '.'
        else:
            # 取第一句和最后一句
            return f"{sentences[0]}. ...{sentences[-1]}."
        
    def _summarize_with_llm(self, text: str) -> Optional[str]:
        """使用大模型总结"""
        if not self.available_models:
            return None
        
        prompt = f"""请为以下文本生成简洁的摘要：

原文：{text}

摘要："""
        
        return self._call_ollama(prompt)
    
