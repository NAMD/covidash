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


## Running Streamlit in the development enviroment

Link to the [Streamlit](https://docs.streamlit.io/) Documentation.

```bash
streamlit run dashboard/app.py
```

## Heroku configuration

### Add Heroku git URL

```bash
git remote add heroku <heroku-remote>
```

### Add Heroku buildpack for APT

Buildpack [documentation](https://elements.heroku.com/buildpacks/ivahero/heroku-buildpack-apt).


To avoid the instalation of apt packages in every build:

```bash
heroku config:set APT_CACHING=yes
```

```bash
heroku buildpacks:add --index 1 heroku-community/apt
```

### Deploy

```bash
git push heroku master
```
