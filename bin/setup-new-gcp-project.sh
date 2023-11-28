#!/bin/bash

if ! command -v gcloud &>/dev/null; then
    echo "gcloud is not installed. Please install it and try again."
    exit 1
fi

gcloud auth login

PROJECT_ID=$1

SCRIPT_PATH="$(
    cd "$(dirname "$0")"
    pwd -P
)"

if [ -z "$PROJECT_ID" ]; then
    SCRIPT_NAME=$(basename "$0")
    echo "No PROJECT_ID provided. Usage: ./$SCRIPT_NAME <PROJECT_ID>"
    exit 1
fi

sed -i "s/_PROJECT_ID: .*/_PROJECT_ID: '$PROJECT_ID'/" "$SCRIPT_PATH"/../cloudbuild.yaml

echo "Creating new project: $PROJECT_ID"
gcloud projects create $PROJECT_ID --name=Project-"$PROJECT_ID"

echo "Setting the project ID to $PROJECT_ID..."
gcloud config set project $PROJECT_ID

echo "Enabling necessary APIs..."
gcloud services enable cloudfunctions.googleapis.com
gcloud services enable cloudresourcemanager.googleapis.com
gcloud services enable apigateway.googleapis.com

echo "Adding necessary roles to each service account..."
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format='value(projectNumber)')
gcloud projects add-iam-policy-binding $PROJECT_ID --member=serviceAccount:$PROJECT_NUMBER@cloudbuild.gserviceaccount.com --role=roles/apigateway.admin
gcloud projects add-iam-policy-binding $PROJECT_ID --member=serviceAccount:$PROJECT_ID@appspot.gserviceaccount.com --role=roles/datastore.user
gcloud iam service-accounts add-iam-policy-binding $PROJECT_ID@appspot.gserviceaccount.com --member=serviceAccount:$PROJECT_NUMBER@cloudbuild.gserviceaccount.com --role=roles/iam.serviceAccountUser
echo "APIs are successfully enabled and project is set."
