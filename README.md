# covidash
A Dashboard for the coronavirus pandemic.

## Dependencies
The following are detailed instructions to setting up your python environment and running the code in this repo. We assume Python 3.7 is installed in a Ubuntu 18.04 system.

1. Install required system packages

    ```bash
    sudo apt-get install python3.7-dev
    sudo apt-get install libproj-dev proj-data proj-bin
    sudo apt-get install libgeos-dev
    ```

2. Clone the repository

    ```bash
    git clone https://github.com/NAMD/covidash.git path/to/clone/dir
    ```

3. Create and activate a new Python 3.7 environment

    ```bash
    python3.7 -m venv covidash-env
    source covidash-env/bin/activate
    ```

3. Install the requirements

    ```bash
    pip install -r requirements
    ```


## Rodando Streamlit no ambiente local

Endereço para documentação do [Streamlit](https://docs.streamlit.io/).

```bash
streamlit run dashboard/app.py
```


## Configuração Heroku

## Adiciona endereço do Heroku

```bash
git remote add heroku <heroku-remote>
```

### Adiciona buildpack APT no Heroku

https://elements.heroku.com/buildpacks/ivahero/heroku-buildpack-apt

```bash
heroku buildpacks:add --index 1 heroku-community/apt
```

## Deploy

```bash
git push heroku master
```
