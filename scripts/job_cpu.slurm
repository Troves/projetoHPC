
echo "  Job HPC Iniciado em: $(date)"
echo "  Job ID: $SLURM_JOB_ID"
echo "  Nó(s): $SLURM_JOB_NODELIST"
echo "  Número de Tarefas: $SLURM_NTASKS"

echo "Carregando módulos..."
module purge
module load python/3.10 openmpi/4.1.5 

VENV_PATH="/scratch/$USER/projeto-hpc/venv"
if [ -d "$VENV_PATH" ]; then
    source "$VENV_PATH/bin/activate"
else
    echo "Erro: Ambiente virtual não encontrado em $VENV_PATH"
    exit 1
fi
echo "Ambiente virtual ativado."

INPUT_DATA_DIR="/scratch/$USER/projeto-hpc/data_large/input"
OUTPUT_DIR="/scratch/$USER/projeto-hpc/results/run_${SLURM_JOB_ID}"

echo "Diretório de Entrada: $INPUT_DATA_DIR"
echo "Diretório de Saída: $OUTPUT_DIR"
mkdir -p $OUTPUT_DIR

echo "Iniciando a execução do srun..."

srun python src/main.py \
    --input-dir "$INPUT_DATA_DIR" \
    --output-dir "$OUTPUT_DIR" \
    --use-mpi

echo "  Job HPC Concluído em: $(date)"
