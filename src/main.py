"""
Ponto de entrada principal para o pipeline de processamento DICOM.

Este script pode ser executado em modo serial ou em paralelo usando MPI.
Ele organiza a leitura, processamento e escrita dos dados.

Uso Serial:
  python src/main.py --input-dir data_sample/input --output-dir results/serial_output

Uso com MPI:
  mpirun -np 4 python src/main.py --input-dir data_sample/input --output-dir results/mpi_output --use-mpi
"""
import os
import time
import argparse
import json
from collections import defaultdict

from src.io_utils import find_dicom_files, read_dicom_file, write_dicom_file, write_statistics
from src.processing_utils import anonymize_dicom, compress_pixel_data, calculate_statistics

# Tenta importar mpi4py, mas não o torna uma dependência rígida para o modo serial
try:
    from mpi4py import MPI
except ImportError:
    MPI = None

def process_single_file(file_path: str, output_dir: str):
    """
    Executa o pipeline completo para um único arquivo DICOM.
    Retorna as estatísticas calculadas.
    """
    # 1. Leitura
    ds = read_dicom_file(file_path)
    if not ds:
        return None

    # 2. Processamento
    ds = anonymize_dicom(ds)
    ds = compress_pixel_data(ds)
    stats = calculate_statistics(ds)
    
    # 3. Escrita
    base_name = os.path.basename(file_path)
    output_dcm_path = os.path.join(output_dir, "dcm", base_name)
    output_stats_path = os.path.join(output_dir, "stats", base_name.replace(".dcm", ".json"))

    write_dicom_file(output_dcm_path, ds)
    write_statistics(output_stats_path, stats)
    
    return stats


def main():
    parser = argparse.ArgumentParser(description="Pipeline de Processamento DICOM HPC.")
    parser.add_argument("--input-dir", type=str, required=True, help="Diretório de entrada com arquivos DICOM.")
    parser.add_argument("--output-dir", type=str, required=True, help="Diretório de saída para resultados.")
    parser.add_argument("--use-mpi", action="store_true", help="Ativar modo de execução paralela com MPI.")
    args = parser.parse_args()

    # --- Inicialização MPI (se aplicável) ---
    comm = None
    rank = 0
    size = 1
    if args.use_mpi and MPI:
        comm = MPI.COMM_WORLD
        rank = comm.Get_rank()
        size = comm.Get_size()
    elif args.use_mpi and not MPI:
        raise ImportError("mpi4py não está instalado. Execute sem --use-mpi ou instale a dependência.")

    # --- Setup ---
    start_time = time.time()
    if rank == 0:
        print(f"Iniciando pipeline com {size} processo(s).")
        print(f"Diretório de entrada: {args.input_dir}")
        print(f"Diretório de saída: {args.output_dir}")
        os.makedirs(args.output_dir, exist_ok=True)

    # --- Distribuição de Tarefas (Rank 0) ---
    files_to_process = None
    if rank == 0:
        all_files = find_dicom_files(args.input_dir)
        if not all_files:
            print("Nenhum arquivo DICOM encontrado. Encerrando.")
            # Sinaliza para outros processos encerrarem
            if size > 1:
                for i in range(1, size):
                    comm.send([], dest=i, tag=11)
            return

        # Divide a lista de arquivos entre os processos
        files_to_process = [all_files[i::size] for i in range(size)]

    # --- Sincronização e Comunicação ---
    if size > 1:
        comm.Barrier()
        # Rank 0 envia as sub-listas, os outros recebem
        local_files = comm.scatter(files_to_process, root=0)
    else:
        local_files = files_to_process[0] if files_to_process else []

    # --- Processamento Local ---
    t_proc_start = time.time()
    local_stats_summary = defaultdict(float)
    files_processed_count = 0
    
    for file_path in local_files:
        stats = process_single_file(file_path, args.output_dir)
        if stats:
            local_stats_summary["total_mean_pixel"] += stats["mean_pixel"]
            files_processed_count += 1
    
    t_proc_end = time.time()
    
    # --- Agregação de Resultados (MPI) ---
    if size > 1:
        all_processed_counts = comm.gather(files_processed_count, root=0)
        all_mean_sums = comm.gather(local_stats_summary["total_mean_pixel"], root=0)
    else:
        all_processed_counts = [files_processed_count]
        all_mean_sums = [local_stats_summary["total_mean_pixel"]]


    # --- Relatório Final (Rank 0) ---
    if rank == 0:
        total_files_processed = sum(all_processed_counts)
        total_mean_pixel_sum = sum(all_mean_sums)
        
        overall_average_pixel = (total_mean_pixel_sum / total_files_processed) if total_files_processed > 0 else 0

        end_time = time.time()
        total_duration = end_time - start_time
        
        print("\n--- Relatório Final ---")
        print(f"Total de arquivos processados: {total_files_processed}")
        print(f"Tempo total de execução: {total_duration:.3f} segundos")
        if total_duration > 0:
            throughput = total_files_processed / total_duration
            print(f"Throughput: {throughput:.2f} arquivos/segundo")
        
        print(f"Média geral da intensidade de pixel: {overall_average_pixel:.2f}")
        
        # Salva um resumo
        summary = {
            "num_processes": size,
            "total_files_processed": total_files_processed,
            "total_duration_sec": total_duration,
            "throughput_files_per_sec": throughput if total_duration > 0 else 0,
            "overall_average_pixel": overall_average_pixel,
        }
        summary_path = os.path.join(args.output_dir, "summary.json")
        with open(summary_path, 'w') as f:
            json.dump(summary, f, indent=4)
        print(f"Resumo salvo em: {summary_path}")


if __name__ == "__main__":
    main()