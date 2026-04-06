import os

AUX_BASE = "/mnt/raid0/ComfyUI/models"
TARGET_BASE = "/home/comfyui/ComfyUI/models"

categories = ["vae", "upscale_models", "diffusion_models", "checkpoints"]

def get_target(model):
    return os.path.join(TARGET_BASE, model)

def get_aux(model):
    return os.path.join(AUX_BASE, model)

def sync_aux_model(model):
    current_target = get_target(model)
    current_aux = get_aux(model)
    os.makedirs(current_target, exist_ok=True)
    aux_models = [
        os.path.join(current_aux, f) for f in os.listdir(current_aux)
        if os.path.isfile(os.path.join(current_aux, f))
    ]

    existing_symlinks = [
        os.path.join(current_target, f) for f in os.listdir(current_target)
        if os.path.islink(os.path.join(current_target, f))
    ]

    # Remove broken symlinks
    for link in existing_symlinks:
        if not os.path.exists(os.readlink(link)):
            print(f"Removing broken symlink: {link}")
            os.unlink(link)

    # Create correct symlinks
    for model in aux_models:
        target_link = os.path.join(current_target, os.path.basename(model))
        if not os.path.exists(target_link):
            os.symlink(model, target_link)
            print(f"Created symlink: {target_link} → {model}")


def sync_aux_models():
    [sync_aux_model(c) for c in categories]
