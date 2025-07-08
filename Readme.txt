Install exempi:
>sudo apt-get install libexempi-dev
>sudo apt-get install libexempi3
export environement variables
>export ARTIFACTORY_RO_TOKEN=*************************
>export ARTIFACTORY_RO_USER=xduval
>export PIP_EXTRA_INDEX_URL="https://{ARTIFACTORY_RO_USER}:{ARTIFACTORY_RO_TOKEN}@artifactory.global.ingenico.com/artifactory/api/pypi/core-pypi/simple"
>export PIP_TRUSTED_HOST=artifactory.global.ingenico.com
>export PIP_INDEX_URL="https://pypi.python.org/simple"
Installer l'environement virtuel:
>python3 -m pipenv install
Lancer script:
>python3 -m pipenv run python handle_xmp_files.py -f /mnt/c/Perso/Images -o images
>python3 -m pipenv run python handle_xmp_files.py -f /mnt/c/Perso/Images -o duval -r "or" -c "Varunah DUVAL,Xavier DUVAL"