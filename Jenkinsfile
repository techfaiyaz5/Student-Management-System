pipeline {
    agent any 

    environment {
        // Tumhara Docker Hub Username yahan set kar lo
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
                // Docker apne aap caching use karega agar layers change nahi hui hain
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
                   // Hum Jenkins ko 'faiyyaz' user ka environment de rahe hain
                   withEnv(["HOME=/home/faiyyaz", "PATH+EXTRA=/usr/local/bin"]) {
                        // Agar status fail hota hai toh fresh start karega
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
                    // 1. Pehle environment set karo (Taki permission error na aaye)
                    withEnv(["HOME=/home/faiyyaz", "KUBECONFIG=/home/faiyyaz/.kube/config"]) {
                        
                        echo 'Starting Tunnel in Background...'
                        sh "pkill -f 'minikube tunnel' || true"
                        sh "nohup minikube tunnel > tunnel.log 2>&1 &"
                        
                        echo 'Force Refreshing App...'
                        sh "kubectl rollout restart deployment student-app"
                        sh "kubectl rollout status deployment student-app"

                        // 2. Ye message script block ke ANDAR hona chahiye
                        echo "--------------------------------------------------------"
                        echo "BHAI, AB TO CHALNA HI PADEGA: http://localhost:30001"
                        echo "--------------------------------------------------------"
                    } // withEnv ka bracket band
                } // script ka bracket band
            } // steps ka bracket band
        } /