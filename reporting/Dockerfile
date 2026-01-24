FROM python:3.10-slim

WORKDIR /app

# On installe les outils de compilation de base
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc python3-dev && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# On force la mise à jour de pip et l'installation
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# ETAPE DE TEST : Si cette ligne échoue au build, on saura pourquoi
RUN python -c "import evidently; print('Installation OK')"

COPY project.py .

# Utilisation du point-virgule pour ne pas crash si le script échoue
CMD python project.py ; evidently ui --host 0.0.0.0 --port 8000 --workspace workspace   