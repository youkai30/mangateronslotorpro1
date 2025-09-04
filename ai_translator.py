# core/ai_translator.py
import os, torch, logging
from transformers import MarianMTModel, MarianTokenizer
from .cache_manager import ModelCacheManager
from .gpu_optimizer  import GPUOptimizer
from .model_compressor import ModelCompressor
from .config        import Config

class AITranslator:
    def __init__(self):
        Config.create_directories()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.cache   = ModelCacheManager(cache_dir=Config.CACHE_DIR,
                                         max_memory_models=Config.MAX_MEMORY_MODELS)
        self.gpu_opt = GPUOptimizer(memory_fraction=Config.GPU_MEMORY_FRACTION,
                                    mixed_precision=Config.ENABLE_MIXED_PRECISION)
        self.compr   = ModelCompressor()

        name = "Helsinki-NLP/opus-mt-en-ar"
        key  = self.cache.get_model_hash(name)

        self.logger.info("Loading tokenizer")
        self.tokenizer = self.cache.get_model(f"{key}_tok",
            lambda: MarianTokenizer.from_pretrained(name))
        self.logger.info("Loading model")
        self.model = self.cache.get_model(f"{key}_mdl",
            lambda: self._load_model(name))

    def _load_model(self, name):
        m = MarianMTModel.from_pretrained(name)
        if Config.COMPRESS_MODELS:
            m = self.compr.compress_model(m,
                  method=Config.COMPRESSION_METHOD,
                  compression_ratio=Config.COMPRESSION_RATIO)
        m = self.gpu_opt.optimize_model(m)
        return m

    def translate(self, texts, context=None):
        if isinstance(texts,str): texts=[texts]
        inst_map={"angry":".مع نبرة غضب.","happy":".بنبرة فرح.","neutral":""}
        inst = inst_map.get((context or {}).get("emotion","neutral"),"")
        inputs=[t+inst for t in texts]
        self.logger.debug(f"Translating texts: {inputs}")

        with self.gpu_opt.optimized_inference() as dev:
            tok = self.tokenizer(inputs,
                return_tensors="pt", padding=True, truncation=True,
                max_length=Config.MAX_SEQUENCE_LENGTH).to(dev)
            gen = self.model.generate(**tok,
                max_length=Config.MAX_SEQUENCE_LENGTH,
                num_beams=Config.TRANSLATION_BEAM_SIZE,
                length_penalty=Config.TRANSLATION_LENGTH_PENALTY,
                do_sample=True, top_p=0.9)
            res = [self.tokenizer.decode(g, skip_special_tokens=True) for g in gen]
            self.logger.debug(f"Translated to: {res}")
            return res

    def get_performance_stats(self):
        stats = self.gpu_opt.get_memory_info()
        self.logger.debug(f"Performance stats: {stats}")
        return stats