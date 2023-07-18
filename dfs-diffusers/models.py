import base64
import io
import os
from PIL import Image
import torch
from functools import partial
from fastapi import UploadFile

from diffusers import (
    StableDiffusionPipeline,
    StableDiffusionImg2ImgPipeline,
    StableDiffusionUpscalePipeline,
    StableDiffusionLatentUpscalePipeline,
    
    DDPMScheduler
)


class DiffuserBasedModel(object):
    text_img_model = None
    img_img_model = None
    upscaler_model = None

    @classmethod
    def generate(
        cls,
        prompt: str,
        n: int,
        size: str,
        response_format: str,
        image: UploadFile = None,
        step_count: int = 25,
        negative_prompt: str = None,
        seed: int = None,
        guidance_scale: float = 7.5,
    ):
        model_fn = cls.img_img_model if image else cls.text_img_model
        generator = torch.manual_seed(seed) if seed else None
        model_fn = partial(
            model_fn,
            prompt, generator=generator, num_inference_steps=step_count, negative_prompt=negative_prompt, num_images_per_prompt=n, guidance_scale=guidance_scale
        )
        if image:
            init_image = Image.open(io.BytesIO(image.file.read())).convert("RGB")
            init_image = init_image.resize(tuple(map(int, (size.split("x"))))) if size else init_image # breaks e.g 512x512 -> (512, 512)
            model_fn = partial(model_fn, image=init_image)
        images = model_fn().images
        data = []
        for img in images:
            buffered = io.BytesIO()
            img = img.resize(tuple(map(int, (size.split("x"))))) if size else img
            img.save(buffered, format="PNG")
            data.append({response_format: base64.b64encode(buffered.getvalue()).decode()})
        return data
    
    @classmethod
    def upscale(
        cls,
        prompt: str,
        n: int,
        size: str,
        response_format: str,
        image: UploadFile = None,
        step_count: int = 25,
        negative_prompt: str = None,
        seed: int = None,
        guidance_scale: float = 7.5,
    ):
        generator = torch.manual_seed(seed) if seed else None
        images = cls.upscaler_model(
            prompt=prompt,
            image=Image.open(io.BytesIO(image.file.read())).convert("RGB"),
            generator=generator,
            num_inference_steps=step_count,
            negative_prompt=negative_prompt,
            guidance_scale=guidance_scale,
        ).images

        data = []
        for img in images:
            buffered = io.BytesIO()
            img = img.resize(tuple(map(int, (size.split("x"))))) if size else img
            img.save(buffered, format="PNG")
            data.append({response_format: base64.b64encode(buffered.getvalue()).decode()})
        return data
    

    @classmethod
    def get_model(cls):
        if cls.text_img_model is None:
            model_id = os.getenv("MODEL_ID", "stabilityai/stable-diffusion-2-1")
            print("set text img model: ", model_id)
            if "latent" in model_id:
                cls.upscaler_model = StableDiffusionLatentUpscalePipeline.from_pretrained(model_id, torch_dtype=torch.float16)\
                                            .to(os.getenv("DEVICE", "cpu"))
                cls.upscaler_model.enable_attention_slicing()
                return cls.upscaler_model
            
            cls.text_img_model = StableDiffusionPipeline.from_pretrained(
                os.getenv("MODEL_ID", "stabilityai/stable-diffusion-2-1"), torch_dtype=torch.float16
            )
            cls.text_img_model = cls.text_img_model.to(os.getenv("DEVICE", "cpu"))
            cls.text_img_model.enable_attention_slicing()
            
            cls.img_img_model = StableDiffusionImg2ImgPipeline(**cls.text_img_model.components)
            cls.upscaler_model = StableDiffusionUpscalePipeline(
                **cls.text_img_model.components,
                low_res_scheduler=DDPMScheduler.from_config(cls.text_img_model.scheduler.config)
            )
            
        return cls.text_img_model

