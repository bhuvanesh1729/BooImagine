#!/usr/bin/env python3
"""
BooImagine - Hugging Face Image Generation GUI Application

This application provides a user-friendly interface for browsing, selecting,
and utilizing Hugging Face models for image generation.
"""

import os
import sys
import json
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext, simpledialog
from PIL import Image, ImageTk
import requests
import io
import base64
from huggingface_hub import HfApi, ModelFilter
from transformers import pipeline
import torch
from datetime import datetime

class BooImagineApp:
    """Main application class for BooImagine."""
    
    def __init__(self, root):
        """Initialize the application."""
        self.root = root
        self.root.title("BooImagine - Hugging Face Image Generation")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 700)
        
        # Initialize variables
        self.current_model = None
        self.generated_image = None
        self.saved_prompts = self.load_saved_prompts()
        self.hf_api = HfApi()
        
        # Create the main UI
        self.create_ui()
        
        # Load models on startup in a separate thread
        threading.Thread(target=self.load_models, daemon=True).start()
    
    def create_ui(self):
        """Create the user interface."""
        # Main container
        self.main_container = ttk.Frame(self.root)
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create left and right panels
        self.left_panel = ttk.Frame(self.main_container)
        self.left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.right_panel = ttk.Frame(self.main_container)
        self.right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Set up panels
        self.setup_model_panel()
        self.setup_generation_panel()
    
    def setup_model_panel(self):
        """Set up the model selection panel."""
        # Model selection frame
        model_frame = ttk.LabelFrame(self.left_panel, text="Model Selection")
        model_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Search bar
        search_frame = ttk.Frame(model_frame)
        search_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        search_button = ttk.Button(search_frame, text="Search", command=self.search_models)
        search_button.pack(side=tk.RIGHT, padx=5)
        
        # Model listbox
        self.model_listbox = tk.Listbox(model_frame, height=10)
        self.model_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.model_listbox.bind('<<ListboxSelect>>', self.on_model_select)
        
        # Model info
        self.model_info = tk.Text(model_frame, height=5, wrap=tk.WORD)
        self.model_info.pack(fill=tk.X, padx=5, pady=5)
        
        # Load model button
        load_button = ttk.Button(model_frame, text="Load Selected Model", command=self.load_model)
        load_button.pack(fill=tk.X, padx=5, pady=5)
    
    def setup_generation_panel(self):
        """Set up the image generation panel."""
        # Generation frame
        gen_frame = ttk.LabelFrame(self.right_panel, text="Image Generation")
        gen_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Prompt frame
        prompt_frame = ttk.Frame(gen_frame)
        prompt_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(prompt_frame, text="Prompt:").pack(side=tk.LEFT)
        
        self.prompt_text = tk.Text(prompt_frame, height=3, wrap=tk.WORD)
        self.prompt_text.pack(fill=tk.X, expand=True, padx=5)
        
        # Buttons frame
        buttons_frame = ttk.Frame(gen_frame)
        buttons_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(buttons_frame, text="Generate", command=self.generate_image).pack(side=tk.LEFT, padx=2)
        ttk.Button(buttons_frame, text="Save Prompt", command=self.save_prompt).pack(side=tk.LEFT, padx=2)
        ttk.Button(buttons_frame, text="Load Prompt", command=self.load_prompt).pack(side=tk.LEFT, padx=2)
        
        # Style buttons
        styles_frame = ttk.LabelFrame(gen_frame, text="Styles")
        styles_frame.pack(fill=tk.X, padx=5, pady=5)
        
        styles = [
            ("Ghibli Style", "Convert to Studio Ghibli style"),
            ("Anime Style", "Convert to anime style"),
            ("Realistic", "Make more realistic"),
            ("Abstract", "Convert to abstract art"),
            ("Enhance", "Enhance image quality")
        ]
        
        for i, (text, prompt) in enumerate(styles):
            ttk.Button(
                styles_frame, 
                text=text, 
                command=lambda p=prompt: self.apply_style(p)
            ).pack(side=tk.LEFT, padx=2)
        
        # Image display
        self.image_label = ttk.Label(gen_frame)
        self.image_label.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def load_saved_prompts(self):
        """Load saved prompts from file."""
        try:
            with open('prompts.json', 'r') as f:
                return json.load(f)
        except:
            return {}
    
    def save_prompts_to_file(self):
        """Save prompts to file."""
        with open('prompts.json', 'w') as f:
            json.dump(self.saved_prompts, f)
    
    def load_models(self):
        """Load available models from Hugging Face."""
        try:
            models = self.hf_api.list_models(
                filter=ModelFilter(task="text-to-image")
            )
            
            self.model_listbox.delete(0, tk.END)
            for model in models:
                self.model_listbox.insert(tk.END, model.id)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load models: {str(e)}")
    
    def search_models(self):
        """Search for models based on input."""
        query = self.search_var.get()
        if not query:
            self.load_models()
            return
            
        try:
            models = self.hf_api.list_models(
                search=query,
                filter=ModelFilter(task="text-to-image")
            )
            
            self.model_listbox.delete(0, tk.END)
            for model in models:
                self.model_listbox.insert(tk.END, model.id)
        except Exception as e:
            messagebox.showerror("Error", f"Search failed: {str(e)}")
    
    def on_model_select(self, event):
        """Handle model selection."""
        selection = self.model_listbox.curselection()
        if not selection:
            return
            
        model_id = self.model_listbox.get(selection[0])
        try:
            info = self.hf_api.model_info(model_id)
            self.model_info.delete(1.0, tk.END)
            self.model_info.insert(tk.END, f"Model: {info.id}\nAuthor: {info.author}\n")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to get model info: {str(e)}")
    
    def load_model(self):
        """Load the selected model."""
        selection = self.model_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a model first")
            return
            
        model_id = self.model_listbox.get(selection[0])
        try:
            self.current_model = pipeline("text-to-image", model=model_id)
            messagebox.showinfo("Success", f"Model {model_id} loaded successfully")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load model: {str(e)}")
    
    def generate_image(self):
        """Generate image from prompt."""
        if not self.current_model:
            messagebox.showwarning("Warning", "Please load a model first")
            return
            
        prompt = self.prompt_text.get(1.0, tk.END).strip()
        if not prompt:
            messagebox.showwarning("Warning", "Please enter a prompt")
            return
            
        try:
            image = self.current_model(prompt)[0]
            self.display_image(image)
            self.generated_image = image
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate image: {str(e)}")
    
    def display_image(self, image):
        """Display the generated image."""
        # Convert PIL image to PhotoImage
        photo = ImageTk.PhotoImage(image)
        self.image_label.configure(image=photo)
        self.image_label.image = photo
    
    def save_prompt(self):
        """Save the current prompt."""
        prompt = self.prompt_text.get(1.0, tk.END).strip()
        if not prompt:
            messagebox.showwarning("Warning", "Please enter a prompt first")
            return
            
        name = simpledialog.askstring("Save Prompt", "Enter name for prompt:")
        if name:
            self.saved_prompts[name] = prompt
            self.save_prompts_to_file()
            messagebox.showinfo("Success", "Prompt saved successfully")
    
    def load_prompt(self):
        """Load a saved prompt."""
        if not self.saved_prompts:
            messagebox.showinfo("Info", "No saved prompts")
            return
            
        name = simpledialog.askstring("Load Prompt", "Enter prompt name:")
        if name in self.saved_prompts:
            self.prompt_text.delete(1.0, tk.END)
            self.prompt_text.insert(tk.END, self.saved_prompts[name])
        else:
            messagebox.showwarning("Warning", "Prompt not found")
    
    def apply_style(self, style_prompt):
        """Apply a style to the current prompt."""
        current = self.prompt_text.get(1.0, tk.END).strip()
        if current:
            self.prompt_text.insert(tk.END, f"\n{style_prompt}")
        else:
            self.prompt_text.insert(tk.END, style_prompt)

def main():
    """Main entry point."""
    root = tk.Tk()
    app = BooImagineApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
