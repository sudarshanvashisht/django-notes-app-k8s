pipeline {
    agent any

    stages {
        stage("Clone Code") {
            steps {
                // Updated to your new GitHub repository
                git url: "https://github.com/sudarshanvashisht/django-notes-app-k8s.git", branch: "main"
            }
        }

        stage("Build Docker Image") {
            steps {
                sh "docker build . -t notes-app-k8s"
            }
        }

        stage("Test & Run via Docker") {
            steps {
                // Test locally with docker-compose before sending to Kubernetes
                sh "docker-compose down || true"
                sh "docker-compose up -d"
            }
        }

        stage("Push to Docker Hub") {
            steps {
                withCredentials([usernamePassword(credentialsId: "dockerHub", passwordVariable: "dockerHubPass", usernameVariable: "dockerHubUser")]) {
                    sh "docker tag notes-app-k8s ${env.dockerHubUser}/notes-app-k8s:latest"
                    sh "docker login -u ${env.dockerHubUser} -p ${env.dockerHubPass}"
                    sh "docker push ${env.dockerHubUser}/notes-app-k8s:latest"
                }
            }
        }

        stage("Deploy to Kubernetes") {
            steps {
                // Apply Kubernetes manifests and perform rollout update
                sh "kubectl apply -f k8s/"
                sh "kubectl rollout restart deployment notes-app-deployment -n notes-app"
            }
        }
    }
}
