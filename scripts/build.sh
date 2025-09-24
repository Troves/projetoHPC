set -e

echo " Construindo o ambiente do Projeto HPC "

if ! command -v python3 &> /dev/null
then
    echo "Erro: python3 não encontrado. Por favor, instale Python 3.10+."
    exit 1
fi

VENV_DIR="venv"

if [ -d "$VENV_DIR" ]; then
    echo "Ambiente virtual '$VENV_DIR' já existe. Pulando a criação."
else
    echo "Criando ambiente virtual em '$VENV_DIR'..."
    python3 -m venv $VENV_DIR
fi

echo "Ativando o ambiente virtual..."
source $VENV_DIR/bin/activate

echo "Instalando dependências de env/requirements.txt..."
pip install --upgrade pip
pip install -r env/requirements.txt

deactivate

echo ""
echo "Build concluído com sucesso!"
echo "Para ativar o ambiente, execute: source $VENV_DIR/bin/activate"
