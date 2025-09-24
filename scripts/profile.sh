
set -e

echo " Iniciando Scripts de Profiling  "

source venv/bin/activate

DATA_DIR="data_sample/input_small"
OUTPUT_DIR="results/profiling"
NUM_SAMPLES=50

rm -rf $DATA_DIR $OUTPUT_DIR
mkdir -p $OUTPUT_DIR
python data_sample/generator.py --count $NUM_SAMPLES --output-dir $DATA_DIR

echo -e "\n[PROFILE 1/2] Usando '/usr/bin/time -v' para análise de memória e I/O..."

/usr/bin/time -v python src/main.py \
    --input-dir $DATA_DIR \
    --output-dir "${OUTPUT_DIR}/time_serial" > "${OUTPUT_DIR}/time_output.log" 2>&1

echo "Análise de tempo concluída. Log completo em: ${OUTPUT_DIR}/time_output.log"
echo "Procure por 'Maximum resident set size' e 'User time'."

echo -e "\n[PROFILE 2/2] Usando 'cProfile' para encontrar funções lentas..."

PROFILE_FILE="${OUTPUT_DIR}/profile_stats.prof"
python -m cProfile -o $PROFILE_FILE src/main.py \
    --input-dir $DATA_DIR \
    --output-dir "${OUTPUT_DIR}/cprofile_serial"

echo "Perfilamento com cProfile concluído. Arquivo de estatísticas: $PROFILE_FILE"
echo "Para analisar os resultados, use o interpretador de stats do Python:"
echo "python -c \"import pstats; p = pstats.Stats('$PROFILE_FILE'); p.sort_stats('cumulative').print_stats(20)\""

echo "  Profiling Finalizado "