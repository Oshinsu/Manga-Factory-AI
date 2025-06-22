"""Script d'entraînement LoRA pour personnages manga"""

import os
import json
import argparse
from pathlib import Path
import torch
from diffusers import StableDiffusionPipeline, AutoencoderKL
from diffusers.loaders import AttnProcsLayers
from diffusers.models.attention_processor import LoRAAttnProcessor
import numpy as np
from PIL import Image
from tqdm import tqdm

class CharacterLoRATrainer:
    def __init__(self, config):
        self.config = config
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        # Chargement du modèle de base
        self.pipeline = StableDiffusionPipeline.from_pretrained(
            config["base_model_path"],
            torch_dtype=torch.float16,
            safety_checker=None
        ).to(self.device)
        
        self.vae = self.pipeline.vae
        self.text_encoder = self.pipeline.text_encoder
        self.tokenizer = self.pipeline.tokenizer
        self.unet = self.pipeline.unet
        
    def prepare_dataset(self, dataset_path):
        """Prépare le dataset depuis les images de référence"""
        
        images = []
        captions = []
        
        dataset_dir = Path(dataset_path)
        
        # Chargement des images et captions
        for img_path in dataset_dir.glob("*.png"):
            caption_path = img_path.with_suffix(".txt")
            
            if caption_path.exists():
                img = Image.open(img_path).convert("RGB")
                img = img.resize((512, 512), Image.LANCZOS)
                images.append(img)
                
                with open(caption_path, "r") as f:
                    caption = f.read().strip()
                    # Ajout du trigger word
                    caption = f"{self.config['trigger_word']} {caption}"
                    captions.append(caption)
        
        return images, captions
    
    def initialize_lora(self):
        """Initialise les couches LoRA"""
        
        # Configuration LoRA
        lora_rank = self.config.get("rank", 32)
        lora_alpha = self.config.get("alpha", lora_rank)
        
        # Ajout des processeurs LoRA au UNet
        lora_attn_procs = {}
        for name in self.unet.attn_processors.keys():
            cross_attention_dim = None if name.endswith("attn1.processor") else self.unet.config.cross_attention_dim
            if name.startswith("mid_block"):
                hidden_size = self.unet.config.block_out_channels[-1]
            elif name.startswith("up_blocks"):
                block_id = int(name[len("up_blocks.")])
                hidden_size = list(reversed(self.unet.config.block_out_channels))[block_id]
            elif name.startswith("down_blocks"):
                block_id = int(name[len("down_blocks.")])
                hidden_size = self.unet.config.block_out_channels[block_id]
            
            lora_attn_procs[name] = LoRAAttnProcessor(
                hidden_size=hidden_size,
                cross_attention_dim=cross_attention_dim,
                rank=lora_rank,
                alpha=lora_alpha
            )
        
        self.unet.set_attn_processor(lora_attn_procs)
        
        # Paramètres à entraîner
        lora_layers = AttnProcsLayers(self.unet.attn_processors)
        return lora_layers
    
    def train(self, dataset_path, output_path):
        """Lance l'entraînement"""
        
        # Préparation du dataset
        images, captions = self.prepare_dataset(dataset_path)
        
        if not images:
            raise ValueError("Aucune image trouvée dans le dataset")
        
        # Initialisation LoRA
        lora_layers = self.initialize_lora()
        
        # Optimiseur
        optimizer = torch.optim.AdamW(
            lora_layers.parameters(),
            lr=self.config["learning_rate"],
            betas=(0.9, 0.999),
            weight_decay=0.01,
            eps=1e-08
        )
        
        # Training loop
        num_epochs = self.config["num_epochs"]
        batch_size = self.config["batch_size"]
        
        for epoch in range(num_epochs):
            epoch_loss = 0
            progress_bar = tqdm(range(0, len(images), batch_size), desc=f"Epoch {epoch+1}/{num_epochs}")
            
            for batch_start in progress_bar:
                batch_images = images[batch_start:batch_start + batch_size]
                batch_captions = captions[batch_start:batch_start + batch_size]
                
                # Encodage des images
                latents = []
                for img in batch_images:
                    img_tensor = torch.from_numpy(np.array(img)).float() / 127.5 - 1
                    img_tensor = img_tensor.permute(2, 0, 1).unsqueeze(0).to(self.device)
                    latent = self.vae.encode(img_tensor).latent_dist.sample() * 0.18215
                    latents.append(latent)
                
                latents = torch.cat(latents, dim=0)
                
                # Encodage du texte
                text_inputs = self.tokenizer(
                    batch_captions,
                    padding="max_length",
                    max_length=self.tokenizer.model_max_length,
                    truncation=True,
                    return_tensors="pt"
                )
                text_embeddings = self.text_encoder(text_inputs.input_ids.to(self.device))[0]
                
                # Ajout du bruit
                noise = torch.randn_like(latents)
                timesteps = torch.randint(0, 1000, (latents.shape[0],), device=self.device)
                noisy_latents = self.pipeline.scheduler.add_noise(latents, noise, timesteps)
                
                # Prédiction
                noise_pred = self.unet(noisy_latents, timesteps, text_embeddings).sample
                
                # Calcul de la loss
                loss = torch.nn.functional.mse_loss(noise_pred, noise, reduction="mean")
                
                # Backpropagation
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()
                
                epoch_loss += loss.item()
                progress_bar.set_postfix({"loss": loss.item()})
        
        # Sauvegarde du LoRA
        self.save_lora(output_path)
        
        return {
            "status": "completed",
            "final_loss": epoch_loss / len(images),
            "output_path": output_path
        }
    
    def save_lora(self, output_path):
        """Sauvegarde les poids LoRA"""
        
        # Extraction des poids LoRA
        unet_lora_layers = self.unet.state_dict()
        lora_state_dict = {k: v for k, v in unet_lora_layers.items() if "lora" in k}
        
        # Métadonnées
        metadata = {
            "trigger_word": self.config["trigger_word"],
            "base_model": self.config["base_model_path"],
            "rank": self.config.get("rank", 32),
            "alpha": self.config.get("alpha", 32),
            "training_steps": self.config["num_epochs"] * self.config.get("steps_per_epoch", 100)
        }
        
        # Sauvegarde
        torch.save({
            "state_dict": lora_state_dict,
            "metadata": metadata
        }, output_path)
        
        print(f"LoRA sauvegardé : {output_path}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, help="Chemin vers le fichier de configuration")
    parser.add_argument("--dataset", required=True, help="Chemin vers le dataset")
    parser.add_argument("--output", required=True, help="Chemin de sortie pour le LoRA")
    
    args = parser.parse_args()
    
    # Chargement de la configuration
    with open(args.config, "r") as f:
        config = json.load(f)
    
    # Entraînement
    trainer = CharacterLoRATrainer(config)
    result = trainer.train(args.dataset, args.output)
    
    print(f"Entraînement terminé : {result}")

if __name__ == "__main__":
    main()
