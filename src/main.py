#!/usr/bin/env python3
"""
BooImagine - Hugging Face Image Generation GUI Application

This application provides a user-friendly interface for browsing, selecting,
and utilizing Hugging Face models for image generation.
"""

import os
import sys
import json
import logging
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import customtkinter as ctk
from PIL import Image, ImageTk
import requests
import io
import base64
from huggingface_hub import HfApi, hf_hub_download
from transformers import pipeline
import torch
from datetime import datetime
import humanize
import time
import traceback

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('booimagine.log')
    ]
)
logger = logging.getLogger(__name__)

# Set CustomTkinter appearance
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class ProgressFrame(ctk.CTkFrame):
    """A frame that shows progress with a progress bar and status text."""
    
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        self.grid_columnconfigure(0, weight=1)
        
        # Status label
        self.status_label = ctk.CTkLabel(self, text="Ready", font=("Helvetica", 12))
        self.status_label.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="w")
        
        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(self)
        self.progress_bar.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="ew")
        self.progress_bar.set(0)
        
        # Step label
        self.step_label = ctk.CTkLabel(self, text="", font=("Helvetica", 10))
        self.step_label.grid(row=2, column=0, padx=10, pady=(0, 10), sticky="w")
    
    def update_progress(self, progress, status=None, step=None):
        """Update the progress bar and status text."""
        self.progress_bar.set(progress)
        if status:
            self.status_label.configure(text=status)
        if step:
            self.step_label.configure(text=step)
        self.update()

class ModelInfoFrame(ctk.CTkFrame):
    """A frame that shows detailed information about a model."""
    
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        self.grid_columnconfigure(0, weight=1)
        
        # Model name and type
        self.name_label = ctk.CTkLabel(self, text="No model selected", font=("Helvetica", 14, "bold"))
        self.name_label.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="w")
        
        self.type_label = ctk.CTkLabel(self, text="", font=("Helvetica", 12))
        self.type_label.grid(row=1, column=0, padx=10, pady=(0, 5), sticky="w")
        
        # Model author and stats
        self.author_label = ctk.CTkLabel(self, text="", font=("Helvetica", 12))
        self.author_label.grid(row=2, column=0, padx=10, pady=(0, 5), sticky="w")
        
        self.stats_label = ctk.CTkLabel(self, text="", font=("Helvetica", 10))
        self.stats_label.grid(row=3, column=0, padx=10, pady=(0, 5), sticky="w")
        
        # Model description
        self.description_text = ctk.CTkTextbox(self, height=60)
        self.description_text.grid(row=4, column=0, padx=10, pady=(0, 5), sticky="ew")
        self.description_text.configure(state="disabled")
        
        # Model tags
        self.tags_label = ctk.CTkLabel(self, text="", font=("Helvetica", 10))
        self.tags_label.grid(row=5, column=0, padx=10, pady=(0, 5), sticky="w")
        
        # Model size and status
        self.size_label = ctk.CTkLabel(self, text="", font=("Helvetica", 10))
        self.size_label.grid(row=6, column=0, padx=10, pady=(0, 5), sticky="w")
        
        self.status_label = ctk.CTkLabel(self, text="", font=("Helvetica", 10))
        self.status_label.grid(row=7, column=0, padx=10, pady=(0, 5), sticky="w")
        
        # Read More button
        self.read_more_button = ctk.CTkButton(
            self, 
            text="Read More on Hugging Face",
            command=self.open_huggingface_page
        )
        self.read_more_button.grid(row=8, column=0, padx=10, pady=(0, 10), sticky="ew")
        self.read_more_button.configure(state="disabled")
        
        self.current_model_id = None
    
    def open_huggingface_page(self):
        """Open the model's Hugging Face page in the default browser."""
        if self.current_model_id:
            import webbrowser
            webbrowser.open(f"https://huggingface.co/{self.current_model_id}")
    
    def update_info(self, info=None, is_local=False, size=None):
        """Update the model information."""
        if info:
            self.current_model_id = info.id
            self.name_label.configure(text=info.id)
            
            # Determine model type from pipeline tag
            model_type = "Unknown"
            if hasattr(info, 'pipeline_tag'):
                model_type = info.pipeline_tag.replace('-', ' ').title()
            self.type_label.configure(text=f"Type: {model_type}")
            
            self.author_label.configure(text=f"Author: {info.author}")
            
            # Show stats (downloads, likes)
            stats = []
            if hasattr(info, 'downloads'):
                stats.append(f"{humanize.intword(info.downloads)} downloads")
            if hasattr(info, 'likes'):
                stats.append(f"{humanize.intword(info.likes)} likes")
            self.stats_label.configure(text=" • ".join(stats))
            
            # Show description
            self.description_text.configure(state="normal")
            self.description_text.delete("1.0", "end")
            if hasattr(info, 'description'):
                self.description_text.insert("1.0", info.description[:500] + "..." if len(info.description) > 500 else info.description)
            self.description_text.configure(state="disabled")
            
            if hasattr(info, 'tags') and info.tags:
                self.tags_label.configure(text=f"Tags: {', '.join(info.tags[:5])}")
            else:
                self.tags_label.configure(text="")
            
            if size:
                self.size_label.configure(text=f"Size: {humanize.naturalsize(size)}")
            else:
                self.size_label.configure(text="")
            
            if is_local:
                self.status_label.configure(text="Status: Downloaded locally")
            else:
                self.status_label.configure(text="Status: Available online")
            
            self.read_more_button.configure(state="normal")
            
        else:
            self.current_model_id = None
            self.name_label.configure(text="No model selected")
            self.type_label.configure(text="")
            self.author_label.configure(text="")
            self.stats_label.configure(text="")
            self.description_text.configure(state="normal")
            self.description_text.delete("1.0", "end")
            self.description_text.configure(state="disabled")
            self.tags_label.configure(text="")
            self.size_label.configure(text="")
            self.status_label.configure(text="")
            self.read_more_button.configure(state="disabled")

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
        self.local_models = []
        self.current_model_type = "text-to-image"  # Default model type
        self.input_image = None  # For image-to-image models
        
        # Create the main UI
        self.create_ui()
        
        # Load models on startup in a separate thread
        threading.Thread(target=self.load_models, daemon=True).start()
    
    def create_ui(self):
        """Create the user interface."""
        # Configure grid
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        
        # Create main frames
        self.left_panel = ctk.CTkFrame(self.root, corner_radius=10)
        self.left_panel.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        self.right_panel = ctk.CTkFrame(self.root, corner_radius=10)
        self.right_panel.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        
        # Configure grid for panels
        self.left_panel.grid_columnconfigure(0, weight=1)
        self.left_panel.grid_rowconfigure(0, weight=0)  # Search section
        self.left_panel.grid_rowconfigure(1, weight=1)  # Online models
        self.left_panel.grid_rowconfigure(2, weight=1)  # Local models
        self.left_panel.grid_rowconfigure(3, weight=0)  # Model info
        
        self.right_panel.grid_columnconfigure(0, weight=1)
        self.right_panel.grid_rowconfigure(0, weight=1)  # Image display
        self.right_panel.grid_rowconfigure(1, weight=0)  # Styles
        self.right_panel.grid_rowconfigure(2, weight=0)  # Progress
        self.right_panel.grid_rowconfigure(3, weight=0)  # Prompt section
        self.right_panel.grid_rowconfigure(4, weight=0)  # Buttons
        
        # Set up panels
        self.setup_model_panel()
        self.setup_generation_panel()
    
    def setup_model_panel(self):
        """Set up the model selection panel."""
        # Search section
        search_frame = ctk.CTkFrame(self.left_panel, corner_radius=10)
        search_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        search_frame.grid_columnconfigure(0, weight=1)
        
        search_label = ctk.CTkLabel(search_frame, text="Search Models", font=("Helvetica", 14, "bold"))
        search_label.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="w")
        
        search_entry = ctk.CTkEntry(search_frame, placeholder_text="Enter search terms...")
        search_entry.grid(row=1, column=0, padx=10, pady=(0, 5), sticky="ew")
        self.search_var = search_entry
        
        search_button = ctk.CTkButton(search_frame, text="Search", command=self.search_models)
        search_button.grid(row=2, column=0, padx=10, pady=(0, 10), sticky="ew")
        
        # Online models section
        online_frame = ctk.CTkFrame(self.left_panel, corner_radius=10)
        online_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        online_frame.grid_columnconfigure(0, weight=1)
        online_frame.grid_rowconfigure(1, weight=1)
        
        online_label = ctk.CTkLabel(online_frame, text="Online Models", font=("Helvetica", 14, "bold"))
        online_label.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="w")
        
        self.online_listbox = ctk.CTkScrollableFrame(online_frame)
        self.online_listbox.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew")
        self.online_models_list = []
        
        # Local models section
        local_frame = ctk.CTkFrame(self.left_panel, corner_radius=10)
        local_frame.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")
        local_frame.grid_columnconfigure(0, weight=1)
        local_frame.grid_rowconfigure(1, weight=1)
        
        local_label = ctk.CTkLabel(local_frame, text="Downloaded Models", font=("Helvetica", 14, "bold"))
        local_label.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="w")
        
        # Add dropdown for downloaded models
        self.local_model_var = ctk.StringVar(value="Select a downloaded model")
        self.local_model_dropdown = ctk.CTkOptionMenu(
            local_frame,
            variable=self.local_model_var,
            values=["No models found"],
            command=self.on_local_model_selected
        )
        self.local_model_dropdown.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="ew")
        
        # Scrollable frame for local models
        self.local_listbox = ctk.CTkScrollableFrame(local_frame)
        self.local_listbox.grid(row=2, column=0, padx=10, pady=(0, 10), sticky="nsew")
        self.local_models_list = []
        
        # Model info section
        info_frame = ctk.CTkFrame(self.left_panel, corner_radius=10)
        info_frame.grid(row=3, column=0, padx=10, pady=10, sticky="ew")
        info_frame.grid_columnconfigure(0, weight=1)
        
        self.model_info = ModelInfoFrame(info_frame)
        self.model_info.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        
        load_button = ctk.CTkButton(info_frame, text="Load Selected Model", command=self.load_model)
        load_button.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="ew")
    
    def setup_generation_panel(self):
        """Set up the image generation panel."""
        # Image display section
        image_frame = ctk.CTkFrame(self.right_panel, corner_radius=10)
        image_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        image_frame.grid_columnconfigure(0, weight=1)
        image_frame.grid_rowconfigure(0, weight=1)
        
        self.image_label = ctk.CTkLabel(image_frame, text="Generated image will appear here")
        self.image_label.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        # Styles section
        styles_frame = ctk.CTkFrame(self.right_panel, corner_radius=10)
        styles_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        
        styles_label = ctk.CTkLabel(styles_frame, text="Style Presets", font=("Helvetica", 14, "bold"))
        styles_label.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="w", columnspan=5)
        
        styles = [
            ("Ghibli Style", "Convert to Studio Ghibli style"),
            ("Anime Style", "Convert to anime style"),
            ("Realistic", "Make more realistic"),
            ("Abstract", "Convert to abstract art"),
            ("Enhance", "Enhance image quality")
        ]
        
        for i, (text, prompt) in enumerate(styles):
            style_button = ctk.CTkButton(
                styles_frame, 
                text=text, 
                command=lambda p=prompt: self.apply_style(p)
            )
            style_button.grid(row=1, column=i, padx=5, pady=(0, 10))
        
        # Progress and context section
        progress_context_frame = ctk.CTkFrame(self.right_panel, corner_radius=10)
        progress_context_frame.grid(row=2, column=0, padx=10, pady=10, sticky="ew")
        progress_context_frame.grid_columnconfigure(0, weight=1)
        progress_context_frame.grid_columnconfigure(1, weight=1)
        
        # Progress section
        self.progress_frame = ProgressFrame(progress_context_frame)
        self.progress_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        
        # Context tracking section
        context_frame = ctk.CTkFrame(progress_context_frame, corner_radius=10)
        context_frame.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        context_frame.grid_columnconfigure(0, weight=1)
        
        context_label = ctk.CTkLabel(context_frame, text="Context Window", font=("Helvetica", 12, "bold"))
        context_label.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="w")
        
        self.token_label = ctk.CTkLabel(context_frame, text="Tokens: 0/0")
        self.token_label.grid(row=1, column=0, padx=10, pady=(0, 5), sticky="w")
        
        self.memory_label = ctk.CTkLabel(context_frame, text="Memory: 0 MB")
        self.memory_label.grid(row=2, column=0, padx=10, pady=(0, 10), sticky="w")
        
        # Prompt section
        prompt_frame = ctk.CTkFrame(self.right_panel, corner_radius=10)
        prompt_frame.grid(row=3, column=0, padx=10, pady=10, sticky="ew")
        prompt_frame.grid_columnconfigure(0, weight=1)
        
        prompt_label = ctk.CTkLabel(prompt_frame, text="Prompt", font=("Helvetica", 14, "bold"))
        prompt_label.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="w")
        
        self.prompt_text = ctk.CTkTextbox(prompt_frame, height=100)
        self.prompt_text.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="ew")
        
        # Buttons section
        buttons_frame = ctk.CTkFrame(self.right_panel, corner_radius=10)
        buttons_frame.grid(row=4, column=0, padx=10, pady=10, sticky="ew")
        buttons_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
        
        generate_button = ctk.CTkButton(buttons_frame, text="Generate", command=self.generate_image)
        generate_button.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        
        save_prompt_button = ctk.CTkButton(buttons_frame, text="Save Prompt", command=self.save_prompt)
        save_prompt_button.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        
        load_prompt_button = ctk.CTkButton(buttons_frame, text="Load Prompt", command=self.load_prompt)
        load_prompt_button.grid(row=0, column=2, padx=10, pady=10, sticky="ew")
        
        save_image_button = ctk.CTkButton(buttons_frame, text="Save Image", command=self.save_image)
        save_image_button.grid(row=0, column=3, padx=10, pady=10, sticky="ew")
        
        # Store references to frames for later modification
        self.prompt_frame = prompt_frame
        self.buttons_frame = buttons_frame
        self.styles_frame = styles_frame
        self.image_frame = image_frame
    
    def setup_text_to_image_ui(self):
        """Configure UI for text-to-image models."""
        self.current_model_type = "text-to-image"
        
        # Update prompt label
        for widget in self.prompt_frame.winfo_children():
            if isinstance(widget, ctk.CTkLabel):
                widget.configure(text="Text Prompt")
        
        # Show styles frame
        self.styles_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        
        # Update generate button
        for widget in self.buttons_frame.winfo_children():
            if isinstance(widget, ctk.CTkButton) and widget.cget("text") == "Generate":
                widget.configure(text="Generate Image")
        
        # Clear any previous input image
        self.input_image = None
        
        # Update image label
        self.image_label.configure(text="Generated image will appear here")
    
    def setup_text_to_text_ui(self):
        """Configure UI for text-to-text models (chat-like interface)."""
        self.current_model_type = "text-to-text"
        
        # Update prompt label
        for widget in self.prompt_frame.winfo_children():
            if isinstance(widget, ctk.CTkLabel):
                widget.configure(text="Chat Input")
        
        # Hide styles frame
        self.styles_frame.grid_forget()
        
        # Update generate button
        for widget in self.buttons_frame.winfo_children():
            if isinstance(widget, ctk.CTkButton) and widget.cget("text") == "Generate" or widget.cget("text") == "Generate Image":
                widget.configure(text="Send Message")
        
        # Update image label to show chat history
        self.image_label.configure(text="Chat history will appear here")
        
        # Clear any previous input image
        self.input_image = None
    
    def setup_image_to_image_ui(self):
        """Configure UI for image-to-image models."""
        self.current_model_type = "image-to-image"
        
        # Update prompt label
        for widget in self.prompt_frame.winfo_children():
            if isinstance(widget, ctk.CTkLabel):
                widget.configure(text="Image Prompt")
        
        # Show styles frame
        self.styles_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        
        # Update generate button
        for widget in self.buttons_frame.winfo_children():
            if isinstance(widget, ctk.CTkButton) and widget.cget("text") == "Generate" or widget.cget("text") == "Generate Image":
                widget.configure(text="Transform Image")
        
        # Add upload image button if it doesn't exist
        upload_button_exists = False
        for widget in self.buttons_frame.winfo_children():
            if isinstance(widget, ctk.CTkButton) and widget.cget("text") == "Upload Image":
                upload_button_exists = True
                break
        
        if not upload_button_exists:
            # Reconfigure grid to add a new button
            self.buttons_frame.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)
            
            # Add upload button
            upload_button = ctk.CTkButton(
                self.buttons_frame,
                text="Upload Image",
                command=self.upload_image
            )
            upload_button.grid(row=0, column=4, padx=10, pady=10, sticky="ew")
        
        # Update image label
        self.image_label.configure(text="Upload an image to transform")
    
    def setup_text_to_video_ui(self):
        """Configure UI for text-to-video models."""
        self.current_model_type = "text-to-video"
        
        # Update prompt label
        for widget in self.prompt_frame.winfo_children():
            if isinstance(widget, ctk.CTkLabel):
                widget.configure(text="Video Prompt")
        
        # Show styles frame
        self.styles_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        
        # Update generate button
        for widget in self.buttons_frame.winfo_children():
            if isinstance(widget, ctk.CTkButton) and widget.cget("text") == "Generate" or widget.cget("text") == "Generate Image":
                widget.configure(text="Generate Video")
        
        # Update image label
        self.image_label.configure(text="Generated video will appear here")
        
        # Clear any previous input image
        self.input_image = None
    
    def upload_image(self):
        """Upload an image for image-to-image models."""
        try:
            file_path = filedialog.askopenfilename(
                title="Select Image",
                filetypes=[
                    ("Image files", "*.png *.jpg *.jpeg *.bmp *.gif"),
                    ("All files", "*.*")
                ]
            )
            
            if file_path:
                # Load the image
                image = Image.open(file_path)
                self.input_image = image
                
                # Display the image
                self.display_image(image)
                
                # Update status
                self.progress_frame.update_progress(1.0, "Ready", "Image uploaded successfully")
        except Exception as e:
            logger.error(f"Error uploading image: {str(e)}")
            logger.error(traceback.format_exc())
            self.progress_frame.update_progress(0, "Error", f"Failed to upload image: {str(e)}")
            messagebox.showerror("Error", f"Failed to upload image: {str(e)}")
    
    def load_saved_prompts(self):
        """Load saved prompts from file."""
        try:
            with open('prompts.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            # Create the file if it doesn't exist with an empty object
            empty_prompts = {"default": "A beautiful landscape"}
            with open('prompts.json', 'w') as f:
                json.dump(empty_prompts, f, indent=2)
            return empty_prompts
        except json.JSONDecodeError:
            # If the file exists but is invalid JSON, initialize it
            empty_prompts = {"default": "A beautiful landscape"}
            with open('prompts.json', 'w') as f:
                json.dump(empty_prompts, f, indent=2)
            return empty_prompts
        except Exception as e:
            logger.error(f"Error loading saved prompts: {str(e)}")
            return {"default": "A beautiful landscape"}
    
    def save_prompts_to_file(self):
        """Save prompts to file."""
        try:
            with open('prompts.json', 'w') as f:
                json.dump(self.saved_prompts, f)
        except Exception as e:
            logger.error(f"Error saving prompts: {str(e)}")
            messagebox.showerror("Error", f"Failed to save prompts: {str(e)}")
    
    def on_local_model_selected(self, model_id):
        """Handle selection from the local model dropdown."""
        if model_id != "No models found" and model_id != "Select a downloaded model":
            self.select_model(model_id, True)
    
    def load_models(self):
        """Load available models from Hugging Face and check for locally downloaded models."""
        try:
            self.progress_frame.update_progress(0.1, "Loading models...", "Checking for local models")
            
            # First check for locally downloaded models
            self.local_models = self.get_local_models()
            
            self.progress_frame.update_progress(0.3, "Loading models...", "Fetching models from Hugging Face Hub")
            
            # Then fetch models from Hugging Face Hub
            models = self.hf_api.list_models(
                task="text-to-image",
                limit=50  # Limit to 50 models for faster loading
            )
            
            self.progress_frame.update_progress(0.7, "Loading models...", "Populating model lists")
            
            # Clear existing model lists
            for widget in self.local_listbox.winfo_children():
                widget.destroy()
            
            for widget in self.online_listbox.winfo_children():
                widget.destroy()
            
            self.online_models_list = []
            self.local_models_list = []
            
            # Update dropdown for local models
            if self.local_models:
                self.local_model_dropdown.configure(values=self.local_models)
                self.local_model_var.set("Select a downloaded model")
                
                # Add local models to the list
                for i, model_id in enumerate(self.local_models):
                    model_button = ctk.CTkButton(
                        self.local_listbox,
                        text=model_id,
                        anchor="w",
                        command=lambda m=model_id: self.select_model(m, True)
                    )
                    model_button.grid(row=i, column=0, padx=5, pady=2, sticky="ew")
                    self.local_models_list.append(model_button)
            else:
                self.local_model_dropdown.configure(values=["No models found"])
                self.local_model_var.set("No models found")
                
                no_models_label = ctk.CTkLabel(self.local_listbox, text="No local models found")
                no_models_label.grid(row=0, column=0, padx=10, pady=10)
            
            # Add online models
            for i, model in enumerate(models):
                if model.id not in self.local_models:  # Avoid duplicates
                    model_button = ctk.CTkButton(
                        self.online_listbox,
                        text=model.id,
                        anchor="w",
                        command=lambda m=model.id: self.select_model(m, False)
                    )
                    model_button.grid(row=i, column=0, padx=5, pady=2, sticky="ew")
                    self.online_models_list.append(model_button)
            
            self.progress_frame.update_progress(1.0, "Ready", "Models loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load models: {str(e)}")
            logger.error(traceback.format_exc())
            self.progress_frame.update_progress(0, "Error", f"Failed to load models: {str(e)}")
            messagebox.showerror("Error", f"Failed to load models: {str(e)}")
    
    def get_local_models(self):
        """Get list of locally downloaded models."""
        local_models = []
        try:
            # Get the Hugging Face cache directory
            cache_dir = os.path.expanduser("~/.cache/huggingface/hub")
            if os.path.exists(cache_dir):
                logger.info(f"Checking cache directory: {cache_dir}")
                # Look for model directories
                for item in os.listdir(cache_dir):
                    model_dir = os.path.join(cache_dir, item, "models--")
                    if os.path.exists(model_dir):
                        logger.info(f"Found models directory: {model_dir}")
                        for model_folder in os.listdir(model_dir):
                            if model_folder.startswith("models--"):
                                # Convert folder name to model ID
                                parts = model_folder.split("--")[1:]
                                if len(parts) >= 2:
                                    model_id = "/".join(parts)
                                    logger.info(f"Found local model: {model_id}")
                                    local_models.append(model_id)
            
            # Also check for models in the diffusers cache
            diffusers_cache = os.path.expanduser("~/.cache/huggingface/diffusers")
            if os.path.exists(diffusers_cache):
                logger.info(f"Checking diffusers cache: {diffusers_cache}")
                for model_folder in os.listdir(diffusers_cache):
                    if os.path.isdir(os.path.join(diffusers_cache, model_folder)):
                        logger.info(f"Found local diffusers model: {model_folder}")
                        if model_folder not in local_models:
                            local_models.append(model_folder)
            
            logger.info(f"Total local models found: {len(local_models)}")
        except Exception as e:
            logger.error(f"Error getting local models: {str(e)}")
            logger.error(traceback.format_exc())
        return local_models
    
    def search_models(self):
        """Search for models based on input."""
        query = self.search_var.get()
        if not query:
            self.load_models()
            return
        
        self.progress_frame.update_progress(0.1, "Searching...", f"Searching for '{query}'")
        
        try:
            # Convert generator to list for length and iteration
            models = list(self.hf_api.list_models(
                search=query,
                task="text-to-image",
                limit=50
            ))
            
            self.progress_frame.update_progress(0.5, "Searching...", f"Found {len(models)} models")
            
            # Clear existing online model list
            for widget in self.online_listbox.winfo_children():
                widget.destroy()
            
            self.online_models_list = []
            
            # Add search results
            for i, model in enumerate(models):
                if model.id not in self.local_models:  # Avoid duplicates
                    model_button = ctk.CTkButton(
                        self.online_listbox,
                        text=model.id,
                        anchor="w",
                        command=lambda m=model.id: self.select_model(m, False)
                    )
                    model_button.grid(row=i, column=0, padx=5, pady=2, sticky="ew")
                    self.online_models_list.append(model_button)
            
            self.progress_frame.update_progress(1.0, "Ready", f"Found {len(models)} models matching '{query}'")
            
        except Exception as e:
            logger.error(f"Search failed: {str(e)}")
            logger.error(traceback.format_exc())
            self.progress_frame.update_progress(0, "Error", f"Search failed: {str(e)}")
            messagebox.showerror("Error", f"Search failed: {str(e)}")
    
    def select_model(self, model_id, is_local=False):
        """Handle model selection."""
        try:
            self.progress_frame.update_progress(0.2, "Loading model info...", f"Getting info for {model_id}")
            
            # Try to get more info from API
            try:
                info = self.hf_api.model_info(model_id)
                
                # Get model size if available
                size = None
                if hasattr(info, 'siblings'):
                    for sibling in info.siblings:
                        if hasattr(sibling, 'rfilename') and sibling.rfilename == 'model_index.json':
                            size = sibling.size
                            break
                
                self.model_info.update_info(info, is_local, size)
                
                # Adapt UI based on model type
                model_type = "text-to-image"  # Default type
                if hasattr(info, 'pipeline_tag'):
                    model_type = info.pipeline_tag
                
                # Configure UI based on model type
                if model_type == "text-to-text":
                    self.setup_text_to_text_ui()
                elif model_type == "image-to-image":
                    self.setup_image_to_image_ui()
                elif model_type == "text-to-video":
                    self.setup_text_to_video_ui()
                else:
                    self.setup_text_to_image_ui()  # Default UI
                
            except Exception as e:
                logger.error(f"Failed to get model info: {str(e)}")
                # If API call fails, just show the model ID
                self.model_info.update_info(None, is_local)
                self.model_info.name_label.configure(text=model_id)
                if is_local:
                    self.model_info.status_label.configure(text="Status: Downloaded locally")
                
                # Default to text-to-image UI
                self.setup_text_to_image_ui()
            
            self.progress_frame.update_progress(1.0, "Ready", "Model selected")
            
        except Exception as e:
            logger.error(f"Error in model selection: {str(e)}")
            logger.error(traceback.format_exc())
            self.progress_frame.update_progress(0, "Error", f"Error selecting model: {str(e)}")
    
    def load_model(self):
        """Load the selected model."""
        model_id = self.model_info.name_label.cget("text")
        if model_id == "No model selected":
            messagebox.showwarning("Warning", "Please select a model first")
            return
        
        try:
            # Create loading window with progress
            loading_window = ctk.CTkToplevel(self.root)
            loading_window.title("Loading Model")
            loading_window.geometry("400x200")
            loading_window.transient(self.root)
            loading_window.grab_set()
            
            # Configure grid
            loading_window.grid_columnconfigure(0, weight=1)
            
            # Add loading message
            loading_label = ctk.CTkLabel(
                loading_window, 
                text=f"Loading model: {model_id}\nThis may take a while...",
                font=("Helvetica", 14)
            )
            loading_label.grid(row=0, column=0, padx=20, pady=20)
            
            # Add progress bar
            progress_bar = ctk.CTkProgressBar(loading_window)
            progress_bar.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
            progress_bar.set(0)
            
            # Add status label
            status_label = ctk.CTkLabel(loading_window, text="Initializing...")
            status_label.grid(row=2, column=0, padx=20, pady=10)
            
            loading_window.update()
            
            def update_loading_progress(progress, status):
                progress_bar.set(progress)
                status_label.configure(text=status)
                loading_window.update()
            
            # Start loading in a separate thread
            def load_model_thread():
                try:
                    update_loading_progress(0.1, "Preparing to load model...")
                    
                    try:
                        # Try loading with StableDiffusionPipeline first
                        update_loading_progress(0.2, "Trying StableDiffusionPipeline...")
                        from diffusers import StableDiffusionPipeline
                        self.current_model = StableDiffusionPipeline.from_pretrained(model_id)
                    except Exception as e1:
                        logger.error(f"StableDiffusionPipeline failed: {str(e1)}")
                        try:
                            # If that fails, try the general pipeline
                            update_loading_progress(0.4, "Trying general pipeline...")
                            self.current_model = pipeline("text-to-image", model=model_id)
                        except Exception as e2:
                            logger.error(f"General pipeline failed: {str(e2)}")
                            # If both fail, try with AutoPipeline
                            update_loading_progress(0.6, "Trying AutoPipeline...")
                            from diffusers import AutoPipeline
                            self.current_model = AutoPipeline.from_pretrained(model_id)
                    
                    # Move to GPU if available
                    update_loading_progress(0.8, "Moving model to device...")
                    if torch.cuda.is_available():
                        self.current_model = self.current_model.to("cuda")
                    
                    update_loading_progress(1.0, "Model loaded successfully!")
                    
                    # Close loading window
                    self.root.after(1000, loading_window.destroy)
                    
                    # Update progress frame
                    self.progress_frame.update_progress(1.0, "Ready", f"Model {model_id} loaded successfully")
                    
                    # Show success message
                    messagebox.showinfo("Success", f"Model {model_id} loaded successfully")
                    
                except Exception as e:
                    logger.error(f"Failed to load model: {str(e)}")
                    logger.error(traceback.format_exc())
                    
                    # Close loading window
                    loading_window.destroy()
                    
                    # Update progress frame
                    self.progress_frame.update_progress(0, "Error", f"Failed to load model: {str(e)}")
                    
                    # Show error message
                    messagebox.showerror("Error", f"Failed to load model: {str(e)}\n\nPlease try a different model.")
            
            # Start the loading thread
            threading.Thread(target=load_model_thread, daemon=True).start()
            
        except Exception as e:
            logger.error(f"Error in load_model: {str(e)}")
            logger.error(traceback.format_exc())
            self.progress_frame.update_progress(0, "Error", f"Error loading model: {str(e)}")
            messagebox.showerror("Error", f"Error loading model: {str(e)}")
    
    def generate_image(self):
        """Generate image from prompt."""
        if not self.current_model:
            response = messagebox.askquestion("No Model Loaded", 
                                             "No model is currently loaded. Would you like to select and load a model now?")
            if response == 'yes':
                if not self.local_models_list and not self.online_models_list:
                    messagebox.showinfo("No Models", "No models found. Please search for a model first.")
                    return
                else:
                    # If we have local models, select the first one
                    if self.local_models_list:
                        self.select_model(self.local_models_list[0].cget("text"), True)
                    # Otherwise select the first online model
                    elif self.online_models_list:
                        self.select_model(self.online_models_list[0].cget("text"), False)
                    self.load_model()
            return
            
        prompt = self.prompt_text.get("1.0", "end-1c").strip()
        if not prompt:
            messagebox.showwarning("Warning", "Please enter a prompt")
            return
        
        # Update progress
        self.progress_frame.update_progress(0.1, "Generating image...", f"Processing prompt: {prompt[:30]}...")
        
        # Update token usage (approximate)
        self.update_token_usage(prompt)
        
        try:
            # Start generation in a separate thread
            def generate_thread():
                try:
                    # Generate the image
                    for i in range(1, 51):  # Simulate steps
                        self.progress_frame.update_progress(i/50, "Generating image...", f"Step {i}/50: Processing...")
                        time.sleep(0.05)  # Small delay to show progress
                    
                    # Generate the actual image
                    if self.current_model_type == "text-to-image":
                        result = self.current_model(prompt)
                        if isinstance(result, dict) and "images" in result:
                            image = result["images"][0]
                        else:
                            image = result[0]
                    elif self.current_model_type == "image-to-image" and self.input_image:
                        result = self.current_model(prompt, image=self.input_image)
                        if isinstance(result, dict) and "images" in result:
                            image = result["images"][0]
                        else:
                            image = result[0]
                    else:
                        # Default fallback
                        image = self.current_model(prompt)[0]
                    
                    # Display the image
                    self.display_image(image)
                    self.generated_image = image
                    
                    # Update progress
                    self.progress_frame.update_progress(1.0, "Ready", "Image generated successfully")
                    
                except Exception as e:
                    logger.error(f"Failed to generate image: {str(e)}")
                    logger.error(traceback.format_exc())
                    self.progress_frame.update_progress(0, "Error", f"Failed to generate image: {str(e)}")
                    messagebox.showerror("Error", f"Failed to generate image: {str(e)}")
            
            # Start the generation thread
            threading.Thread(target=generate_thread, daemon=True).start()
            
        except Exception as e:
            logger.error(f"Error in generate_image: {str(e)}")
            logger.error(traceback.format_exc())
            self.progress_frame.update_progress(0, "Error", f"Error generating image: {str(e)}")
            messagebox.showerror("Error", f"Error generating image: {str(e)}")
    
    def display_image(self, image_or_list):
        """Display the generated image."""
        try:
            # Handle both single images and lists of images
            if isinstance(image_or_list, list):
                image = image_or_list[0]  # Take the first image from the list
            else:
                image = image_or_list

            # Convert PIL image to CTkImage for better HighDPI support
            photo = ctk.CTkImage(light_image=image, dark_image=image, size=image.size)
            self.image_label.configure(image=photo, text="")
            self.image_label.image = photo  # Keep a reference!
        except Exception as e:
            logger.error(f"Error displaying image: {str(e)}")
            logger.error(traceback.format_exc())
            messagebox.showerror("Error", f"Failed to display image: {str(e)}")
    
    def save_image(self):
        """Save the generated image."""
        if not self.generated_image:
            messagebox.showwarning("Warning", "No image to save")
            return
        
        try:
            # Get save path from user
            file_path = filedialog.asksaveasfilename(
                defaultextension=".png",
                filetypes=[("PNG files", "*.png"), ("All files", "*.*")]
            )
            
            if file_path:
                self.generated_image.save(file_path)
                messagebox.showinfo("Success", "Image saved successfully")
        except Exception as e:
            logger.error(f"Error saving image: {str(e)}")
            logger.error(traceback.format_exc())
            messagebox.showerror("Error", f"Failed to save image: {str(e)}")
    
    def save_prompt(self):
        """Save the current prompt."""
        prompt = self.prompt_text.get("1.0", "end-1c").strip()
        if not prompt:
            messagebox.showwarning("Warning", "Please enter a prompt first")
            return
        
        try:
            name = simpledialog.askstring("Save Prompt", "Enter name for prompt:")
            if name:
                self.saved_prompts[name] = prompt
                self.save_prompts_to_file()
                messagebox.showinfo("Success", "Prompt saved successfully")
        except Exception as e:
            logger.error(f"Error saving prompt: {str(e)}")
            logger.error(traceback.format_exc())
            messagebox.showerror("Error", f"Failed to save prompt: {str(e)}")
    
    def load_prompt(self):
        """Load a saved prompt."""
        if not self.saved_prompts:
            messagebox.showinfo("Info", "No saved prompts")
            return
        
        try:
            # Create a dialog to select from saved prompts
            dialog = ctk.CTkToplevel(self.root)
            dialog.title("Load Prompt")
            dialog.geometry("300x400")
            dialog.transient(self.root)
            dialog.grab_set()
            
            # Configure grid
            dialog.grid_columnconfigure(0, weight=1)
            dialog.grid_rowconfigure(1, weight=1)
            
            # Add title
            title_label = ctk.CTkLabel(dialog, text="Select a Prompt", font=("Helvetica", 14, "bold"))
            title_label.grid(row=0, column=0, padx=10, pady=(10, 5))
            
            # Add scrollable frame for prompts
            prompt_frame = ctk.CTkScrollableFrame(dialog)
            prompt_frame.grid(row=1, column=0, padx=10, pady=(5, 10), sticky="nsew")
            
            def load_selected_prompt(prompt):
                self.prompt_text.delete("1.0", "end")
                self.prompt_text.insert("1.0", prompt)
                dialog.destroy()
            
            # Add buttons for each prompt
            for i, (name, prompt) in enumerate(self.saved_prompts.items()):
                prompt_button = ctk.CTkButton(
                    prompt_frame,
                    text=name,
                    command=lambda p=prompt: load_selected_prompt(p)
                )
                prompt_button.grid(row=i, column=0, padx=5, pady=2, sticky="ew")
            
        except Exception as e:
            logger.error(f"Error loading prompt: {str(e)}")
            logger.error(traceback.format_exc())
            messagebox.showerror("Error", f"Failed to load prompt: {str(e)}")
    
    def apply_style(self, style_prompt):
        """Apply a style to the current prompt."""
        try:
            current = self.prompt_text.get("1.0", "end-1c").strip()
            if current:
                self.prompt_text.insert("end", f"\n{style_prompt}")
            else:
                self.prompt_text.insert("1.0", style_prompt)
                
            # Update token usage after adding style
            self.update_token_usage(self.prompt_text.get("1.0", "end-1c"))
        except Exception as e:
            logger.error(f"Error applying style: {str(e)}")
            logger.error(traceback.format_exc())
            messagebox.showerror("Error", f"Failed to apply style: {str(e)}")
    
    def update_token_usage(self, text):
        """Update token usage display based on prompt text."""
        try:
            # Approximate token count (rough estimate: 4 chars = 1 token)
            token_count = len(text) // 4
            
            # Get model max tokens if available
            max_tokens = 77  # Default for SD models
            if hasattr(self.current_model, 'tokenizer') and hasattr(self.current_model.tokenizer, 'model_max_length'):
                max_tokens = self.current_model.tokenizer.model_max_length
            
            # Update token label
            self.token_label.configure(text=f"Tokens: {token_count}/{max_tokens}")
            
            # Estimate memory usage (very rough)
            if self.current_model:
                # Rough estimate of VRAM usage in MB
                memory_usage = 0
                if hasattr(torch.cuda, 'memory_allocated') and torch.cuda.is_available():
                    memory_usage = torch.cuda.memory_allocated() / (1024 * 1024)
                else:
                    # Rough estimate if we can't get actual memory usage
                    memory_usage = 2000  # Assume 2GB for a typical model
                
                self.memory_label.configure(text=f"Memory: {memory_usage:.1f} MB")
        except Exception as e:
            logger.error(f"Error updating token usage: {str(e)}")

def main():
    """Main entry point."""
    try:
        root = ctk.CTk()
        app = BooImagineApp(root)
        root.mainloop()
    except Exception as e:
        logger.error(f"Application error: {str(e)}")
        logger.error(traceback.format_exc())
        messagebox.showerror("Error", f"Application error: {str(e)}")

if __name__ == "__main__":
    main()
