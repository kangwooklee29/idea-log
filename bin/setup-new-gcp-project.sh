#!/bin/bash

if ! command -v gcloud &>/dev/null; then
    echo "gcloud is not installed. Please install it and try again."
    exit 1
fi

gcloud auth login

SCRIPT_PATH="$(
    cd "$(dirname "$0")"
    pwd -P
)"
TIMESTAMP=$(date +%s)
PROJECT_ID="my-project-$TIMESTAMP"
PROJECT_NAME="MyProject$TIMESTAMP"
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format='value(projectNumber)')
echo "PROJECT_ID=\"$PROJECT_ID\"" >"$SCRIPT_PATH"/.env

echo "Creating new project: $PROJECT_ID"
gcloud projects create $PROJECT_ID --name="$PROJECT_NAME"

echo "Setting the project ID to $PROJECT_ID..."
gcloud config set project $PROJECT_ID

echo "Enabling necessary APIs..."
gcloud services enable cloudfunctions.googleapis.com
gcloud services enable cloudresourcemanager.googleapis.com

echo "Adding necessary roles to each service account..."
gcloud projects add-iam-policy-binding $PROJECT_ID --member=serviceAccount:$PROJECT_NUMBER@cloudbuild.gserviceaccount.com --role=roles/cloudfunctions.admin
gcloud iam service-accounts add-iam-policy-binding $PROJECT_ID@appspot.gserviceaccount.com --member=serviceAccount:$PROJECT_NUMBER@cloudbuild.gserviceaccount.com --role=roles/iam.serviceAccountUser

echo "APIs are successfully enabled and project is set."
