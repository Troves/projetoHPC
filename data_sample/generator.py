import os
import argparse
import numpy as np
import pydicom
from pydicom.dataset import Dataset, FileMetaDataset
from pydicom.uid import ExplicitVRLittleEndian
from tqdm import tqdm

def generate_synthetic_dicom(file_path: str, patient_id: int, image_size: tuple = (512, 512)):
    file_meta = FileMetaDataset()
    file_meta.MediaStorageSOPClassUID = '1.2.840.10008.5.1.4.1.1.2'  
    file_meta.MediaStorageSOPInstanceUID = pydicom.uid.generate_uid()
    file_meta.TransferSyntaxUID = ExplicitVRLittleEndian
    file_meta.ImplementationClassUID = pydicom.uid.generate_uid()

    ds = Dataset()
    ds.file_meta = file_meta
    
    ds.PatientName = f"Paciente^Teste^{patient_id:04d}"
    ds.PatientID = f"PID{patient_id:04d}"
    ds.PatientBirthDate = "20000101"
    ds.StudyInstanceUID = pydicom.uid.generate_uid()
    ds.SeriesInstanceUID = pydicom.uid.generate_uid()
    ds.SOPInstanceUID = file_meta.MediaStorageSOPInstanceUID
    
    ds.Rows, ds.Columns = image_size
    ds.PixelSpacing = [1.0, 1.0]
    ds.SamplesPerPixel = 1
    ds.PhotometricInterpretation = "MONOCHROME2"
    ds.PixelRepresentation = 0
    ds.BitsAllocated = 16
    ds.BitsStored = 12
    ds.HighBit = 11
    
    x = np.arange(0, image_size[1], dtype=np.uint16)
    y = np.arange(0, image_size[0], dtype=np.uint16)
    xx, yy = np.meshgrid(x, y)
    pixel_data = (xx + yy).astype(np.uint16)
    noise = np.random.randint(0, 100, size=image_size, dtype=np.uint16)
    pixel_data += noise
    
    ds.PixelData = pixel_data.tobytes()

    ds.is_little_endian = True
    ds.is_implicit_VR = False

    pydicom.dcmwrite(file_path, ds, write_like_original=False)


def main():
    parser = argparse.ArgumentParser(description="Gerador de arquivos DICOM sintéticos.")
    parser.add_argument("--count", type=int, default=10, help="Número de arquivos a serem gerados.")
    parser.add_argument("--output-dir", type=str, required=True, help="Diretório de saída para os arquivos.")
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)

    print(f"Gerando {args.count} arquivos DICOM sintéticos em '{args.output_dir}'...")
    
    for i in tqdm(range(args.count), desc="Gerando Arquivos"):
        file_name = f"synthetic_image_{i:05d}.dcm"
        file_path = os.path.join(args.output_dir, file_name)
        generate_synthetic_dicom(file_path, patient_id=i + 1)
        
    print("Geração de dados concluída com sucesso.")


if __name__ == "__main__":
    main()