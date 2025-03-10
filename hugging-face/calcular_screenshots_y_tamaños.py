from huggingface_hub import HfApi

# Nombre del modelo en Hugging Face
repo_id = "Wan-AI/Wan2.1-T2V-14B"


# Inicializar la API de Hugging Face
api = HfApi()

# Listar todos los archivos en el repositorio
repo_files = api.list_repo_files(repo_id=repo_id)

# Filtrar solo los archivos de modelos usables
model_extensions = [".bin", ".safetensors", ".pt", ".ckpt", ".pth"]
model_files = [file for file in repo_files if any(file.lower().endswith(ext) for ext in model_extensions)]

# Obtener información sobre los archivos de modelos
paths_info = api.get_paths_info(repo_id=repo_id, paths=model_files)

# Calcular el tamaño total de los modelos
total_size = 0
for info in paths_info:
    total_size += info.size
    print(f"Archivo: {info.path}, Tamaño: {info.size / 1024 / 1024:.2f} MB")

# Mostrar el total
print(f"\nTotal de modelos usables: {len(model_files)}")
print(f"Tamaño total ocupado: {total_size / 1024 / 1024 / 1024:.2f} GB")