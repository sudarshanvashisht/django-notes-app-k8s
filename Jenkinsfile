pipeline {
    agent any

    options {
        timestamps()
        disableConcurrentBuilds()
    }

    environment {
        IMAGE_NAME = "sudarshan0907/notes-app-k8s"
        IMAGE_TAG = "${env.BUILD_NUMBER}"
    }

    stages {
        stage("Checkout") {
            steps {
                checkout scm
            }
        }

        stage("Backend checks") {
            steps {
                sh "python3 -m pip install --upgrade pip"
                sh "python3 -m pip install -r requirements.txt"
                sh "DJANGO_USE_SQLITE=true python3 manage.py check"
                sh "DJANGO_USE_SQLITE=true python3 manage.py test api"
            }
        }

        stage("Frontend checks") {
            steps {
                dir("mynotes") {
                    sh "npm ci"
                    sh "npm run test:ci"
                    sh "npm run build"
                }
            }
        }

        stage("Docker build") {
            steps {
                sh "docker build -t ${IMAGE_NAME}:${IMAGE_TAG} -t ${IMAGE_NAME}:latest ."
            }
        }

        stage("Push image") {
            when {
                branch "main"
            }
            steps {
                withCredentials([usernamePassword(credentialsId: "dockerHub", passwordVariable: "DOCKER_PASSWORD", usernameVariable: "DOCKER_USERNAME")]) {
                    sh "echo \"$DOCKER_PASSWORD\" | docker login -u \"$DOCKER_USERNAME\" --password-stdin"
                    sh "docker push ${IMAGE_NAME}:${IMAGE_TAG}"
                    sh "docker push ${IMAGE_NAME}:latest"
                }
            }
        }

        stage("Kubernetes render") {
            steps {
                sh "kubectl kustomize k8s > /dev/null"
            }
        }
    }
}
