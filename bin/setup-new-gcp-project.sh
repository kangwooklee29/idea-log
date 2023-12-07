#!/bin/bash

if ! command -v gcloud &>/dev/null; then
    echo "gcloud is not installed. Please install it and try again."
    exit 1
fi

if ! command -v jq &>/dev/null; then
    echo "jq is not installed. Please install it and try again."
    exit 1
fi

SCRIPT_PATH="$(
    cd "$(dirname "$0")"
    pwd -P
)"
CLIENT_SECRET_PATH="$SCRIPT_PATH/../client_secret.json"

if [ ! -f "$CLIENT_SECRET_PATH" ]; then
    echo "Error: $CLIENT_SECRET_PATH does not exist."
    exit 1
fi

gcloud auth login

FLASK_SECRET_KEY=$1

if [ -z "$FLASK_SECRET_KEY"]; then
    SCRIPT_NAME=$(basename "$0")
    echo "No FLASK_SECRET_KEY provided. Usage: ./$SCRIPT_NAME <FLASK_SECRET_KEY>"
    exit 1
fi

PROJECT_ID=$(jq -r '.web.project_id' "$CLIENT_SECRET_PATH")
sed -i "s/_PROJECT_ID: .*/_PROJECT_ID: '$PROJECT_ID'/" "$SCRIPT_PATH"/../cloudbuild-gcf.yaml

echo "Creating new project: $PROJECT_ID"
gcloud projects create $PROJECT_ID --name=Project-"$PROJECT_ID"

echo "Setting the project ID to $PROJECT_ID..."
gcloud config set project $PROJECT_ID

echo "Enabling necessary APIs..."
gcloud services enable cloudfunctions.googleapis.com
gcloud services enable cloudresourcemanager.googleapis.com
gcloud services enable apigateway.googleapis.com
gcloud services enable secretmanager.googleapis.com

echo "Adding necessary roles to each service account..."
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format='value(projectNumber)')
gcloud projects add-iam-policy-binding $PROJECT_ID --member=serviceAccount:$PROJECT_NUMBER@cloudbuild.gserviceaccount.com --role=roles/apigateway.admin
gcloud projects add-iam-policy-binding $PROJECT_ID --member=serviceAccount:$PROJECT_ID@appspot.gserviceaccount.com --role=roles/datastore.user
gcloud projects add-iam-policy-binding $PROJECT_ID --member=serviceAccount:$PROJECT_ID@appspot.gserviceaccount.com --role=roles/secretmanager.secretAccessor
gcloud projects add-iam-policy-binding $PROJECT_ID --member=serviceAccount:$PROJECT_NUMBER@cloudbuild.gserviceaccount.com --role=roles/editor
gcloud iam service-accounts add-iam-policy-binding $PROJECT_ID@appspot.gserviceaccount.com --member=serviceAccount:$PROJECT_NUMBER@cloudbuild.gserviceaccount.com --role=roles/iam.serviceAccountUser
echo "APIs are successfully enabled and project is set."

gcloud secrets create FLASK_SECRET_KEY --replication-policy=automatic
echo -n "$FLASK_SECRET_KEY" | gcloud secrets versions add FLASK_SECRET_KEY --data-file=-
echo "FLASK_SECRET_KEY is set successfully."
