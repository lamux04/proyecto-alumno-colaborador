from transformers import AutoConfig, AutoModel
from huggingface_hub import HfApi

# Nombre del modelo en Hugging Face
repo_id = "black-forest-labs/FLUX.1-dev"

# Inicializar la API de Hugging Face
api = HfApi()

# Listar todos los archivos en el repositorio
repo_files = api.list_repo_files(repo_id=repo_id)

# Filtrar solo los archivos de modelos usables
model_extensions = [".bin", ".safetensors", ".pt", ".ckpt", ".pth"]
model_files = [file for file in repo_files if any(file.lower().endswith(ext) for ext in model_extensions)]

# Si no hay archivos de modelos, salir
if not model_files:
    print("No se encontraron archivos de modelos usables.")
    exit()

# Tomar el primer archivo de modelo
first_model_file = model_files[0]
print(f"Procesando el primer archivo de modelo: {first_model_file}")

# Obtener información sobre el archivo
file_info = api.get_paths_info(repo_id=repo_id, paths=[first_model_file])[0]
file_size = file_info.size
print(f"Tamaño del archivo: {file_size / 1024 / 1024:.2f} MB")

# Obtener la configuración del modelo sin descargar los pesos
try:
    print("Cargando configuración del modelo...")
    config = AutoConfig.from_pretrained(repo_id)
    model = AutoModel.from_config(config)  # Crea el modelo sin cargar los pesos
    num_params = sum(p.numel() for p in model.parameters())  # Calcular el número de parámetros
    print(f"Número de parámetros: {num_params:,}")
except Exception as e:
    print(f"Error al cargar la configuración del modelo: {e}")