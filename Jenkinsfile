pipeline {
    agent any 

    environment {
        DOCKER_HUB_USER = "faiyyazkhan" 
        APP_NAME = "student-app"
    }

    stages {
        stage('Step 1: Code Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Step 2: Build & Cache Image') {
            steps {
                echo 'Building Image with Caching...'
                sh "docker build -t ${APP_NAME}:latest ."
            }
        }

        stage('Step 3: Push to Docker Hub') {
            steps {
                echo 'Pushing updated image to Cloud...'
                withCredentials([usernamePassword(credentialsId: 'docker-hub-creds', passwordVariable: 'DOCKER_PASS', usernameVariable: 'DOCKER_USER')]) {
                    sh "echo \$DOCKER_PASS | docker login -u \$DOCKER_USER --password-stdin"
                    sh "docker tag ${APP_NAME}:latest \$DOCKER_USER/${APP_NAME}:latest"
                    sh "docker push \$DOCKER_USER/${APP_NAME}:latest"
                }
            }
        }

        stage('Step 4: Infrastructure Setup') {
            steps {
                script {
                    echo 'Ensuring Minikube & Kubeconfig are ready...'
                    withEnv(["HOME=/home/faiyyaz", "PATH+EXTRA=/usr/local/bin"]) {
                        // Agar stop hai to start karega
                        sh "minikube status || minikube start --driver=docker"
                        
                        echo 'Applying K8s Configurations...'
                        sh "kubectl apply -f k8s/db-deployment.yaml --validate=false"
                        sh "kubectl apply -f k8s/app-deployment.yaml --validate=false"
                    }
                }
            }
        }

        stage('Step 5: Deployment & Auto-Tunnel') {
            steps {
                script {
                    echo 'Setting up tunnel and refreshing pods...'
                    withEnv(["HOME=/home/faiyyaz", "KUBECONFIG=/home/faiyyaz/.kube/config"]) {
                        
                        // Tunnel reset logic
                        sh "pkill -f 'minikube tunnel' || true"
                        sh "nohup minikube tunnel > tunnel.log 2>&1 &"
                        
                        // Force update with latest image from hub
                        sh "kubectl rollout restart deployment ${APP_NAME}"
                        sh "kubectl rollout status deployment ${APP_NAME}"

                        echo "--------------------------------------------------------"
                        echo "MUBARAK HO! SAB KUCH AUTO-SET HO GAYA HAI."
                        echo "APP LINK: http://localhost:30001"
                        echo "--------------------------------------------------------"
                    }
                }
            }
        }
    }
}