import os
import sys

# 确保当前目录在导入路径中
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

class Srt2VoiceNode:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "srt_text": ("STRING", {"multiline": True, "default": "拷贝srt字幕文件内容到这里"}),
                "reference_audio": ("AUDIO", ),
                "speed": ("FLOAT", {"default": 1.0, "min": 0.5, "max": 2.0, "step": 0.1}),                
            }
        }

    RETURN_TYPES = ("AUDIO",)
    RETURN_NAMES = ("audio",)

    FUNCTION = "srt_to_voice"

    CATEGORY = "audio"

    def srt_to_voice(self, srt_text, reference_audio, speed):
        print('test1')
        print('test2')
        return (reference_audio,)


NODE_CLASS_MAPPINGS = {
    "Srt2VoiceNode": Srt2VoiceNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "Srt2VoiceNode": "Srt to Voice",
}