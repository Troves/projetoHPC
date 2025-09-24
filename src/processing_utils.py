"""
Módulo de utilitários para processamento de imagens DICOM.

Contém as funções puras que realizam as operações no pipeline:
- Anonimização
- Compressão (simulada)
- Cálculo de estatísticas
"""
import numpy as np
from pydicom.dataset import Dataset

def anonymize_dicom(ds: Dataset) -> Dataset:
    """Remove informações de identificação pessoal do dataset DICOM."""
    # Tags a serem anonimizadas
    tags_to_anonymize = [
        "PatientName",
        "PatientID",
        "PatientBirthDate",
        "PatientAddress",
        # Adicione outras tags conforme necessário
    ]
    for tag in tags_to_anonymize:
        if tag in ds:
            ds[tag].value = "ANONYMIZED"
    
    # Também é uma boa prática remover curvas e overlays privados
    ds.remove_private_tags()
    
    return ds

def compress_pixel_data(ds: Dataset) -> Dataset:
    """
    Simula a compressão alterando o tipo de dados para um mais eficiente.
    
    Uma compressão real (ex: JPEG-LS) seria mais complexa. Para este projeto,
    vamos garantir que os dados de pixel usem o tipo de dados mais compacto
    possível, o que economiza espaço e pode acelerar o I/O.
    """
    if "PixelData" in ds:
        # Apenas um exemplo de otimização, não uma compressão real
        pixel_array = ds.pixel_array
        if pixel_array.dtype != np.uint16:
            ds.PixelData = pixel_array.astype(np.uint16).tobytes()
            ds.BitsStored = 16
            ds.HighBit = 15
    return ds


def calculate_statistics(ds: Dataset) -> dict:
    """Calcula estatísticas básicas da imagem DICOM."""
    stats = {
        "min_pixel": 0,
        "max_pixel": 0,
        "mean_pixel": 0.0,
        "std_dev_pixel": 0.0,
        "histogram": [],
    }
    
    if "PixelData" in ds:
        try:
            pixel_array = ds.pixel_array
            stats["min_pixel"] = int(pixel_array.min())
            stats["max_pixel"] = int(pixel_array.max())
            stats["mean_pixel"] = float(pixel_array.mean())
            stats["std_dev_pixel"] = float(pixel_array.std())
            
            # Histograma com 256 bins para visualização
            hist, _ = np.histogram(pixel_array.flatten(), bins=256, range=(0, 4096))
            stats["histogram"] = hist.tolist()
        except Exception as e:
            print(f"Erro ao calcular estatísticas: {e}")

    return stats