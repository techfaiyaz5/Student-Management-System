pipeline {
    agent any 

    environment {
        DOCKER_HUB_USER = "techfaiyaz5" 
        APP_NAME = "student-app"
        FIXED_PORT = "30001"
    }

    stages {
        stage('Step 1: Permission & System Fix') {
            steps {
                echo 'Fixing Permissions to avoid "Permission Denied" errors...'
                // Ye line hamesha ke liye permission ka jhamela khatam kar degi
                sh "sudo chown -R jenkins:jenkins /home/faiyyaz/.minikube || true"
                sh "sudo chmod -R 777 /home/faiyyaz/.minikube || true"
                
                echo 'Cleaning up old Docker artifacts...'
                sh "docker system prune -f"
                sh "docker rmi ${DOCKER_HUB_USER}/${APP_NAME}:latest || true"
                checkout scm
            }
        }

        stage('Step 2: Fresh Build (No Cache)') {
            steps {
                echo 'Building Image from scratch...'
                sh "docker build --no-cache -t ${APP_NAME}:latest ."
            }
        }

        stage('Step 3: Push to Docker Hub') {
            steps {
                echo 'Pushing fresh image to Docker Hub...'
                withCredentials([usernamePassword(credentialsId: 'docker-hub-creds', passwordVariable: 'DOCKER_PASS', usernameVariable: 'DOCKER_USER')]) {
                    sh "echo \$DOCKER_PASS | docker login -u \$DOCKER_USER --password-stdin"
                    sh "docker tag ${APP_NAME}:latest \$DOCKER_USER/${APP_NAME}:latest"
                    sh "docker push \$DOCKER_USER/${APP_NAME}:latest"
                }
            }
        }

        stage('Step 4: Infrastructure & HPA Setup') {
            steps {
                script {
                    echo 'Ensuring Minikube is Running...'
                    withEnv(["HOME=/home/faiyyaz", "PATH+EXTRA=/usr/local/bin", "KUBECONFIG=/home/faiyyaz/.kube/config"]) {
                        // Sudo use kar rahe hain taaki host permission error na aaye
                        sh "sudo minikube start --driver=docker --force --user=jenkins"
                        
                        echo 'Applying K8s Configurations (DB, App, HPA)...'
                        sh "kubectl apply -f k8s/db-deployment.yaml --validate=false"
                        sh "kubectl apply -f k8s/app-deployment.yaml --validate=false"
                        sh "kubectl apply -f k8s/hpa.yaml"
                        
                        sh "kubectl rollout restart deployment ${APP_NAME}"
                    }
                }
            }
        }

        stage('Step 5: Scaling Metrics & Addons') {
            steps {
                script {
                    withEnv(["HOME=/home/faiyyaz", "PATH+EXTRA=/usr/local/bin"]) {
                        echo 'Enabling Metrics Server for Auto-Scaling...'
                        // Iske bina 0%/50% nahi dikhega
                        sh "minikube addons enable metrics-server"
                    }
                }
            }
        }

        stage('Step 6: Auto-Tunnel & Access') {
            steps {
                script {
                    withEnv(["HOME=/home/faiyyaz", "KUBECONFIG=/home/faiyyaz/.kube/config", "PATH+EXTRA=/usr/local/bin"]) {
                        
                        def context = sh(script: "kubectl config current-context", returnStdout: true).trim()
                        
                        if (context.contains("minikube")) {
                            echo "--- LOCAL DETECTED: Automating Tunnel & Port ${FIXED_PORT} ---"
                            
                            // Purane process saaf karo taaki port busy error na aaye
                            sh "sudo pkill -f 'minikube tunnel' || true"
                            sh "sudo fuser -k ${FIXED_PORT}/tcp || true"
                            
                            echo "Starting Tunnel & Port-Forward in Background..."
                            sh "nohup sudo minikube tunnel > tunnel.log 2>&1 &"
                            sh "nohup kubectl port-forward svc/student-app-service ${FIXED_PORT}:80 --address 0.0.0.0 > port-forward.log 2>&1 &"
                        }
                        
                        sh "kubectl rollout status deployment ${APP_NAME}"
                    }
                }
            }
        }
    }

    post {
        success {
            echo "--------------------------------------------------------"
            echo "MUBARAK HO! Faiyyaz bhai, sab kuch auto-set ho gaya hai."
            echo "APP LINK: http://localhost:${FIXED_PORT}"
            echo "CHECK SCALING: Run 'kubectl get hpa' in your terminal"
            echo "--------------------------------------------------------"
        }
    }
}