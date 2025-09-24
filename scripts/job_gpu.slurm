
echo "================================================="
echo "  Job de GPU Iniciado em: $(date)"
echo "  Job ID: $SLURM_JOB_ID"
echo "  GPU(s) alocada(s): $CUDA_VISIBLE_DEVICES"
echo "================================================="

echo "Carregando módulos de GPU..."
module purge
module load python/3.10 cuda/11.8

VENV_PATH="/scratch/$USER/projeto-hpc/venv"
if [ -d "$VENV_PATH" ]; then
    source "$VENV_PATH/bin/activate"
else
    echo "Erro: Ambiente virtual não encontrado."
    exit 1
fi

INPUT_DATA_DIR="/scratch/$USER/projeto-hpc/data_large/input"
OUTPUT_DIR="/scratch/$USER/projeto-hpc/results/run_${SLURM_JOB_ID}_gpu"
mkdir -p $OUTPUT_DIR

echo "Iniciando script com suporte a GPU..."

echo "Este é um script de exemplo. A lógica de GPU precisa ser implementada."

echo "================================================="
echo "  Job de GPU Concluído em: $(date)"
echo "================================================="