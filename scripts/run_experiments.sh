
set -e

echo "  Iniciando Matriz de Experimentos "

source venv/bin/activate

PROCESS_COUNTS=(1 2 4 8 16)
DATASET_SIZES=("small" "medium")
declare -A SAMPLES_PER_SIZE=( ["small"]=100 ["medium"]=1000 )

RESULTS_CSV="results/metrics.csv"
BASE_DATA_DIR="data_sample"
BASE_OUTPUT_DIR="results/experiments"

echo "dataset_size,num_processes,total_time_sec,throughput_files_sec" > $RESULTS_CSV
rm -rf $BASE_OUTPUT_DIR
mkdir -p $BASE_OUTPUT_DIR

for size_name in "${DATASET_SIZES[@]}"; do
    num_samples=${SAMPLES_PER_SIZE[$size_name]}
    INPUT_DIR="${BASE_DATA_DIR}/input_${size_name}"
    
    echo -e "\n--- Preparando Dataset: ${size_name} (${num_samples} arquivos) ---"
    rm -rf $INPUT_DIR
    python data_sample/generator.py --count $num_samples --output-dir $INPUT_DIR
    
    for n_procs in "${PROCESS_COUNTS[@]}"; do
        echo "Executando com: Dataset=${size_name}, Processos=${n_procs}"
        
        OUTPUT_DIR="${BASE_OUTPUT_DIR}/${size_name}_np${n_procs}"
        mkdir -p $OUTPUT_DIR
        
        CMD="mpirun -np ${n_procs} python src/main.py \
                --input-dir ${INPUT_DIR} \
                --output-dir ${OUTPUT_DIR} \
                --use-mpi"
        
        exec_output=$(/usr/bin/time -f "%e" $CMD 2>&1)
        
        runtime=$(echo "$exec_output" | tail -n 1)
        
        summary_file="${OUTPUT_DIR}/summary.json"
        if [ -f "$summary_file" ]; then
            throughput=$(python -c "import json; f = open('$summary_file'); data = json.load(f); print(data.get('throughput_files_per_sec', 0))")
        else
            throughput="ERROR"
        fi

        echo "${size_name},${n_procs},${runtime},${throughput}" >> $RESULTS_CSV
        
        echo "Tempo: ${runtime}s, Throughput: ${throughput} files/s"
    done
done

echo "      Experimentos Concluídos!                   "
echo "Resultados salvos em: ${RESULTS_CSV}"