pipeline {
    agent any

    environment {
        KUBECONFIG = '/var/jenkins_home/.kube/config'
        IMAGE_NAME = 'sudarshan0907/notes-app-k8s'
        IMAGE_TAG = sh(script: 'git rev-parse --short HEAD', returnStdout: true).trim()
    }

    stages {
        stage("Clone Code") {
            steps {
                git url: "https://github.com/sudarshanvashisht/django-notes-app-k8s.git", branch: "main"
                echo "Deploying Build Tag: ${env.IMAGE_TAG}"
            }
        }

        stage("Build Docker Image") {
            steps {
                sh "docker build . -t ${env.IMAGE_NAME}:${env.IMAGE_TAG}"
            }
        }

        stage("Run Unit Tests") {
            steps {
                echo "Running Django REST API unit tests..."
                sh "docker run --rm ${env.IMAGE_NAME}:${env.IMAGE_TAG} python manage.py test"
            }
        }

        stage("Test & Run via Compose") {
            steps {
                sh "docker compose down || true"
                sh "cp .env.example .env || true"
                // Replace build block in compose to use our pre-built tagged image
                sh "sed -i 's|build: .|image: ${env.IMAGE_NAME}:${env.IMAGE_TAG}|g' docker-compose.yml"
                sh "docker compose up -d web mysql"
                sh "sleep 20"
                sh "docker compose ps"
                sh "docker compose logs web --tail 15"
                sh "docker compose logs mysql --tail 15"
            }
        }

        stage("Push to Docker Hub") {
            steps {
                script {
                    try {
                        withCredentials([usernamePassword(credentialsId: "dockerHub", passwordVariable: "dockerHubPass", usernameVariable: "dockerHubUser")]) {
                            sh "docker login -u ${env.dockerHubUser} -p ${env.dockerHubPass}"
                            sh "docker tag ${env.IMAGE_NAME}:${env.IMAGE_TAG} ${env.IMAGE_NAME}:latest"
                            sh "docker push ${env.IMAGE_NAME}:${env.IMAGE_TAG}"
                            sh "docker push ${env.IMAGE_NAME}:latest"
                        }
                    } catch (Exception e) {
                        echo "WARNING: Docker Hub credentials not configured. Skipping push stage: ${e.message}"
                    }
                }
            }
        }

        stage("Deploy to Kubernetes") {
            steps {
                // Load the locally built image into Kind cluster nodes
                sh "kind load docker-image ${env.IMAGE_NAME}:${env.IMAGE_TAG} --name tws-cluster"
                // Inject the dynamic tag into the deployment manifest and apply
                sh "sed -i 's/__IMAGE_TAG__/${env.IMAGE_TAG}/g' k8s/deployment.yml"
                // Apply all manifests including Ingress
                sh "kubectl apply -f k8s/"
                // Wait for the rollout to complete successfully
                sh "kubectl rollout status deployment notes-app-deployment -n notes-app --timeout=180s"
            }
        }
    }

    post {
        always {
            sh "docker compose down || true"
            sh "docker rmi ${env.IMAGE_NAME}:${env.IMAGE_TAG} || true"
            sh "docker image prune -f || true"
        }
        success {
            echo 'CI/CD Pipeline succeeded!'
        }
        failure {
            echo 'CI/CD Pipeline failed!'
        }
    }
}
