#!/bin/bash
# Script pour importer le workflow n8n automatiquement

echo "Copie du fichier..."
docker cp n8n_workflow.json n8n:/tmp/workflow.json

echo "Import du workflow..."
docker exec -u node n8n n8n import:workflow --input=/tmp/workflow.json

echo "Terminé ! Veuillez REACTIVER le workflow dans l'interface n8n."
