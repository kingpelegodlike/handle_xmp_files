Handle XMP Files
Create XmpView SlideShow file from images folder
The images selected for the SlideShow are found according to a contact list found in their XMP attribute

Installation:
Install exempi:
>sudo apt-get install libexempi-dev
>sudo apt-get install libexempi3
export environement variables
>export ARTIFACTORY_RO_TOKEN=*************************
>export ARTIFACTORY_RO_USER=xduval
>export PIP_EXTRA_INDEX_URL="https://{ARTIFACTORY_RO_USER}:{ARTIFACTORY_RO_TOKEN}@artifactory.global.ingenico.com/artifactory/api/pypi/core-pypi/simple"
>export PIP_TRUSTED_HOST=artifactory.global.ingenico.com
>export PIP_INDEX_URL="https://pypi.python.org/simple"
Installer l'environement virtuel avec pipenv:
>python3 -m pipenv install
>python3 -m pipenv shell
Installer l'environement virtuel python3.12 avec venv:
>python -m venv .venv312
>echo "*" > .venv312/.gitignore
>source .venv312/bin/activate
>python -m pip install --upgrade pip
>pip install -r requirements312.txt

Usage:
Lancer script:
>python handle_xmp_files.py -f /mnt/c/Perso/Images -o images
> python handle_xmp_files.py -f /mnt/c/Perso/Images -o duval -r "or" -c "Varunah DUVAL,Xavier DUVAL"
>python handle_xmp_files.py -f /mnt/c/Perso/Images -o duval -r or --contacts_file contact_list.json
Arrêter l'environement virtuel avec pipenv:
>exit
Arrêter l'environement virtuel venv:
>deactivate