"""
Módulo de utilitários para operações de Entrada/Saída (I/O).

Contém funções para ler, escrever e listar arquivos DICOM.
Separar I/O da computação é uma boa prática em HPC. [cite: 67]
"""
import os
import pydicom
import json
from pydicom.dataset import Dataset

def find_dicom_files(input_dir: str) -> list[str]:
    """Encontra todos os arquivos .dcm em um diretório."""
    dicom_files = []
    for root, _, files in os.walk(input_dir):
        for file in files:
            if file.lower().endswith(".dcm"):
                dicom_files.append(os.path.join(root, file))
    return dicom_files

def read_dicom_file(file_path: str) -> Dataset | None:
    """Lê um arquivo DICOM e retorna um objeto Dataset."""
    try:
        return pydicom.dcmread(file_path)
    except Exception as e:
        print(f"Erro ao ler o arquivo {file_path}: {e}")
        return None

def write_dicom_file(output_path: str, ds: Dataset):
    """Escreve um objeto Dataset DICOM em um arquivo."""
    try:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        pydicom.dcmwrite(output_path, ds, write_like_original=False)
    except Exception as e:
        print(f"Erro ao escrever o arquivo {output_path}: {e}")

def write_statistics(output_path: str, stats: dict):
    """Escreve as estatísticas em um arquivo JSON."""
    try:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(stats, f, indent=4)
    except Exception as e:
        print(f"Erro ao escrever o arquivo de estatísticas {output_path}: {e}")