
set -e

echo "      Iniciando Teste de Execução Local          "

VENV_DIR="venv"
if [ -d "$VENV_DIR" ]; then
    echo "Ativando ambiente virtual..."
    source $VENV_DIR/bin/activate
else
    echo "Ambiente virtual não encontrado. Execute scripts/build.sh primeiro."
    exit 1
fi

DATA_DIR="data_sample/input"
OUTPUT_DIR="results/local_run"
NUM_SAMPLES=20 

rm -rf $DATA_DIR
rm -rf $OUTPUT_DIR
mkdir -p $OUTPUT_DIR

echo -e "\n[PASSO 1/3] Gerando ${NUM_SAMPLES} arquivos de dados de amostra em '${DATA_DIR}'..."
python data_sample/generator.py --count $NUM_SAMPLES --output-dir $DATA_DIR

echo -e "\n[PASSO 2/3] Executando o pipeline em modo SERIAL..."
SERIAL_OUTPUT_DIR="${OUTPUT_DIR}/serial"
mkdir -p $SERIAL_OUTPUT_DIR

time python src/main.py \
    --input-dir $DATA_DIR \
    --output-dir $SERIAL_OUTPUT_DIR

echo "Execução serial concluída. Resultados em: $SERIAL_OUTPUT_DIR"

N_PROCS=4 
echo -e "\n[PASSO 3/3] Executando o pipeline em modo PARALELO com ${N_PROCS} processos (MPI)..."
MPI_OUTPUT_DIR="${OUTPUT_DIR}/mpi_np${N_PROCS}"
mkdir -p $MPI_OUTPUT_DIR

time mpirun -np $N_PROCS python src/main.py \
    --input-dir $DATA_DIR \
    --output-dir $MPI_OUTPUT_DIR \
    --use-mpi

echo "Execução paralela concluída. Resultados em: $MPI_OUTPUT_DIR"

echo "      Teste de Execução Local Finalizado         "
