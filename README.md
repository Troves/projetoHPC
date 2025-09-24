# Projeto HPC - Pipeline Paralelo para Processamento de Imagens DICOM

## Visão Geral

Este projeto implementa um pipeline de processamento de imagens médicas no formato DICOM, otimizado para execução em ambientes de computação de alto desempenho (HPC). [cite_start]O objetivo é processar um volume massivo de exames de forma eficiente, aplicando anonimização, compressão e extração de estatísticas em paralelo. [cite: 14]

[cite_start]O problema abordado é de grande relevância para a área da saúde, onde hospitais e centros de pesquisa precisam gerenciar e analisar terabytes de dados de imagem, garantindo a privacidade do paciente e a eficiência do armazenamento. [cite: 4] Este pipeline foi projetado para ser escalável, rodando desde um notebook de desenvolvimento até um supercomputador como o Santos Dumont.

## Requisitos

* Python 3.10+
* Ambiente virtual (`venv` ou `conda`)
* MPI (como OpenMPI ou MPICH) e `mpi4py`
* [cite_start]SLURM para submissão de jobs no cluster [cite: 9, 192]
* Bibliotecas listadas em `env/requirements.txt`

## Como Rodar (Localmente)

Siga estes passos para configurar e executar o projeto em sua máquina local.

1.  **Construir o ambiente:**
    * Este script criará um ambiente virtual Python e instalará as dependências.

    ```bash
    bash scripts/build.sh
    ```

2.  **Ativar o ambiente virtual:**

    ```bash
    source venv/bin/activate
    ```

3.  **Gerar dados de amostra:**
    * Cria 100 arquivos DICOM sintéticos em `data_sample/input/`.

    ```bash
    python data_sample/generator.py --count 100 --output-dir data_sample/input
    ```

4.  **Executar o teste local:**
    * Este script executa a versão serial e a versão paralela (com 4 processos) nos dados de amostra. Os resultados são salvos em `results/`.

    ```bash
    bash scripts/run_local.sh
    ```

## Como Rodar (Santos Dumont)

Para executar no supercomputador Santos Dumont, siga estas instruções:

1.  **Login e Transferência:**
    * Faça login no nó de acesso do SD.
    * Transfira a pasta `projeto-hpc` para o seu `/home`.

2.  **Use o sistema de arquivos `/scratch`:**
    * **NUNCA** rode jobs que geram muitos dados no `/home`. Use o `/scratch`.
    * Copie o projeto para o seu diretório scratch.

    ```bash
    # No nó de login do SD
    cp -r ~/projeto-hpc /scratch/$USER/
    cd /scratch/$USER/projeto-hpc
    ```

3.  **Carregar Módulos e Construir Ambiente:**
    * O Santos Dumont usa um sistema de módulos. Carregue os módulos necessários antes de construir.

    ```bash
    # Exemplo de módulos (ajuste conforme o ambiente do SD)
    module load python/3.10
    module load openmpi/4.1.5
    
    # Construa o ambiente (irá criar um venv localmente no /scratch)
    bash scripts/build.sh
    ```

4.  **Gerar Dados em Larga Escala:**
    * Ative o ambiente e gere um conjunto de dados maior.

    ```bash
    source venv/bin/activate
    python data_sample/generator.py --count 10000 --output-dir /scratch/$USER/projeto-hpc/data_large/input
    ```

5.  **Submeter o Job:**
    * Use o `sbatch` para submeter o script SLURM. Ajuste os parâmetros (`--ntasks`, `--time`) no arquivo `.slurm` conforme necessário.

    ```bash
    # Submeter o job para a fila de CPUs
    sbatch scripts/job_cpu.slurm
    ```

6.  **Acompanhar o Job:**
    * Use os seguintes comandos para monitorar a execução:

    ```bash
    squeue -u $USER                 # Ver a fila de jobs
    sacct -j <JOB_ID>               # Ver detalhes de um job concluído
    tail -f results/proj_cpu_*.out  # Ver a saída em tempo real
    ```

## Estrutura do Repositório

[cite_start]A estrutura de pastas e arquivos está detalhada na árvore no início deste documento, seguindo as boas práticas para projetos HPC reprodutíveis. [cite: 34]

## Resultados

Os resultados dos experimentos, incluindo logs, métricas de performance e gráficos, são salvos no diretório `results/`. O script `scripts/run_experiments.sh` pode ser usado para automatizar a coleta de dados de escalabilidade, que são salvos em `results/metrics.csv`. A análise completa está no `report/RELATORIO.txt`.
