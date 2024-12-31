# projetFlask

## Installation

Pour installer le projet, suivez les étapes ci-dessous :

1. Clonez le dépôt :
  ```bash
  git clone
  https://github.com/WBoogey/projetFlask.git
  ```
2. Accédez au répertoire du projet :
  ```bash
  cd projetFlask
  ```
3. Installez les dépendances :
  ```bash
  pip install -r requirements.txt
  ```
4. Activez l'environement virtuel venv:
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```
5. lancez les test unitaire:
  ```bash
  export PYTHONPATH=$(pwd)
  pytest -v app/test/test_scrutin_model.py

  pytest -v app/test
  ```

## Structure du projet

- `templates` : Contient les fichiers HTML.
- `static` : Contient les fichiers JavaScript (js) et CSS.

## Lancement du projet

Pour lancer le projet, exécutez la commande suivante :
```bash
python -m main
```