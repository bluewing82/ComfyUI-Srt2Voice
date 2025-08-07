import os
import sys
import librosa
import torch
import torchaudio
import srt
import numpy as np
import tempfile
from tqdm import tqdm
from indextts.infer import IndexTTS
import logging

# 初始化日志
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] [%(levelname)s] %(message)s')

# 确保当前目录在导入路径中
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

class Srt2VoiceNode:
    def __init__(self):
        # 初始化TTS模型为None，延迟加载
        self.tts_model = None
        # 获取插件根目录（假设nodes.py在插件目录的某个子目录中）
        plugin_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        # 组合模型路径
        self.model_dir = os.path.join(plugin_root, "models", "IndexTTS-1.5")
        self.cfg_path = os.path.join(self.model_dir, "config.yaml")
        logger.info(f"[Srt2Voice] 模型目录: {self.model_dir}")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "srt_text": ("STRING", {"multiline": True, "default": "拷贝srt字幕文件内容到这里"}),
                "reference_audio": ("AUDIO", ),
            }
        }

    RETURN_TYPES = ("AUDIO",)
    RETURN_NAMES = ("audio",)

    FUNCTION = "srt_to_voice"

    CATEGORY = "audio"

    def _load_tts_model(self):
        """加载TTS模型"""
        if self.tts_model is not None:
            return
            
        logger.info(f"[Srt2Voice] 正在加载TTS模型...")
        try:
            # 检查设备
            device = "cuda" if torch.cuda.is_available() else "cpu"
            logger.info(f"[Srt2Voice] 使用设备: {device}")
            
            # 初始化IndexTTS模型
            self.tts_model = IndexTTS(
                cfg_path=self.cfg_path,
                model_dir=self.model_dir,
                is_fp16=(device == "cuda"),
                device=device
            )
            logger.info(f"[Srt2Voice] TTS模型加载成功")
        except Exception as e:
            logger.error(f"[Srt2Voice] 加载TTS模型失败: {e}")
            raise RuntimeError(f"无法加载TTS模型: {e}")

    def _parse_srt_text(self, srt_text):
        """解析SRT文本为字幕段列表"""
        subs = list(srt.parse(srt_text))
        return [{
            'start': sub.start.total_seconds(),
            'end': sub.end.total_seconds(),
            'text': sub.content.strip().replace('\n', ' ')
        } for sub in subs]

    def _save_temp_audio(self, audio_dict):
        """将ComfyUI音频格式保存为临时文件"""
        try:
            waveform = audio_dict["waveform"]
            sample_rate = audio_dict["sample_rate"]
            
            # 处理3D张量 [batch, channels, samples] -> [channels, samples]
            if waveform.dim() == 3:
                # 取第一个批次（通常只有一个）并去除批次维度
                waveform = waveform.squeeze(0)
                logger.info(f"[Srt2Voice] 3D张量转换为2D: {waveform.shape}")
            
            # 处理多声道音频 - 取平均值转为单声道
            if waveform.dim() == 2 and waveform.shape[0] > 1:
                waveform = torch.mean(waveform, dim=0, keepdim=True)
                logger.info(f"[Srt2Voice] 多声道转换为单声道: {waveform.shape}")
            
            # 确保最终是2D张量 [channels, samples]
            if waveform.dim() != 2:
                waveform = waveform.unsqueeze(0) if waveform.dim() == 1 else waveform
                logger.info(f"[Srt2Voice] 最终调整形状为: {waveform.shape}")
            
            # 创建临时文件
            temp_file = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
            temp_path = temp_file.name
            temp_file.close()
            
            # 保存音频
            torchaudio.save(temp_path, waveform, sample_rate)
            logger.info(f"[Srt2Voice] 参考音频已保存到临时文件: {temp_path}")
            return temp_path
        except Exception as e:
            logger.error(f"[Srt2Voice] 保存临时音频失败: {e}")
            raise

    def _adjust_audio_length(self, audio_path, target_duration, sr=24000):
        """调整音频长度以匹配目标时长"""
        try:
            # 加载音频
            y, orig_sr = librosa.load(audio_path, sr=sr)
            actual_duration = len(y) / sr
            
            # 需要加速
            if actual_duration > target_duration:
                speed_factor = actual_duration / target_duration
                y_adjusted = librosa.effects.time_stretch(y, rate=speed_factor)
                logger.info(f"[Srt2Voice] 音频加速: {speed_factor:.2f}x")
            
            # 需要补静音
            elif actual_duration < target_duration:
                silence_samples = int((target_duration - actual_duration) * sr)
                y_adjusted = np.concatenate([y, np.zeros(silence_samples)])
                logger.info(f"[Srt2Voice] 添加静音: {target_duration - actual_duration:.2f}s")
            
            # 长度刚好
            else:
                y_adjusted = y
            
            # 确保精确长度
            target_samples = int(target_duration * sr)
            if len(y_adjusted) > target_samples:
                y_adjusted = y_adjusted[:target_samples]
            elif len(y_adjusted) < target_samples:
                y_adjusted = np.pad(y_adjusted, (0, target_samples - len(y_adjusted)))
            
            return torch.from_numpy(y_adjusted).float().unsqueeze(0), sr
        except Exception as e:
            logger.error(f"[Srt2Voice] 调整音频长度失败: {e}")
            raise

    def srt_to_voice(self, srt_text, reference_audio):
        # 加载TTS模型
        self._load_tts_model()
        
        # 解析SRT文本
        srt_entries = self._parse_srt_text(srt_text)
        logger.info(f"[Srt2Voice] 解析到 {len(srt_entries)} 条字幕")
        
        # 保存参考音频为临时文件
        ref_audio_path = self._save_temp_audio(reference_audio)
        sr = 24000  # TTS模型输出采样率
        
        # 创建临时目录存储中间音频
        temp_dir = tempfile.mkdtemp()
        logger.info(f"[Srt2Voice] 临时目录创建于: {temp_dir}")
        
        final_audio = []  # 存储所有音频段
        current_time = 0.0  # 当前音频时间位置
        
        # 逐段合成语音
        for i, entry in enumerate(tqdm(srt_entries, desc="合成语音")):
            start = entry['start']
            end = entry['end']
            duration = end - start
            text = entry['text']
            
            # 添加静音段（如果需要）
            if start > current_time:
                silence_duration = start - current_time
                silence_samples = int(silence_duration * sr)
                silence_tensor = torch.zeros((1, silence_samples))
                final_audio.append(silence_tensor)
                current_time += silence_duration
                logger.info(f"[Srt2Voice] 添加静音: {silence_duration:.2f}s")
            
            # 合成语音
            temp_path = os.path.join(temp_dir, f"{i:04d}.wav")
            self.tts_model.infer(
                audio_prompt=ref_audio_path,
                text=text,
                output_path=temp_path,
                verbose=False
            )
            
            # 调整音频长度以匹配字幕时长
            audio_tensor, _ = self._adjust_audio_length(temp_path, duration, sr)
            final_audio.append(audio_tensor)
            current_time += duration
        
        # 拼接所有音频段
        logger.info(f"[Srt2Voice] 拼接音频段...")
        combined = torch.cat(final_audio, dim=1)
        
        # 转换为ComfyUI音频格式 [1, 1, samples]
        audio_output = {
            "waveform": combined.unsqueeze(0).unsqueeze(0),  # 添加批次和通道维度
            "sample_rate": sr
        }
        
        # 清理临时文件
        try:
            for file in os.listdir(temp_dir):
                os.remove(os.path.join(temp_dir, file))
            os.rmdir(temp_dir)
            os.unlink(ref_audio_path)
            logger.info(f"[Srt2Voice] 临时文件已清理")
        except Exception as e:
            logger.error(f"[Srt2Voice] 清理临时文件时出错: {e}")
        
        return (audio_output,)

NODE_CLASS_MAPPINGS = {
    "Srt2VoiceNode": Srt2VoiceNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "Srt2VoiceNode": "SRT to Voice",
}