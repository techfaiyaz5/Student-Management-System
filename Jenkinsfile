pipeline {
    agent any 

    environment {
        // Tumhare Docker Hub ka username yahan dalo
        DOCKER_HUB_USER = "techfaiyaz5" 
        APP_NAME = "student-app"
        // Universal Port jo humne fix kiya hai
        FIXED_PORT = "30001"
    }

    stages {
        stage('Step 1: Fresh Start (Cleanup)') {
            steps {
                echo 'Cleaning up old Docker artifacts for a Zero-State build...'
                // Purane containers aur dangling images saaf karega
                sh "docker system prune -f"
                // Purani image delete karega taaki cache ka chakkar na rahe
                sh "docker rmi ${DOCKER_HUB_USER}/${APP_NAME}:latest || true"
                checkout scm
            }
        }

        stage('Step 2: Fresh Build (No Cache)') {
            steps {
                echo 'Building Image from scratch...'
                // --no-cache se har baar fresh build hoga
                sh "docker build --no-cache -t ${APP_NAME}:latest ."
            }
        }

        stage('Step 3: Push to Docker Hub') {
            steps {
                echo 'Pushing fresh image to Cloud...'
                withCredentials([usernamePassword(credentialsId: 'docker-hub-creds', passwordVariable: 'DOCKER_PASS', usernameVariable: 'DOCKER_USER')]) {
                    sh "echo \$DOCKER_PASS | docker login -u \$DOCKER_USER --password-stdin"
                    sh "docker tag ${APP_NAME}:latest \$DOCKER_USER/${APP_NAME}:latest"
                    sh "docker push \$DOCKER_USER/${APP_NAME}:latest"
                }
            }
        }

        stage('Step 4: Smart Infrastructure Setup') {
            steps {
                script {
                    echo 'Ensuring Environment is ready...'
                    withEnv(["HOME=/home/faiyyaz", "PATH+EXTRA=/usr/local/bin"]) {
                        // Minikube check
                        sh "minikube status || minikube start --driver=docker"
                        
                        echo 'Applying K8s Configurations...'
                        sh "kubectl apply -f k8s/db-deployment.yaml --validate=false"
                        sh "kubectl apply -f k8s/app-deployment.yaml --validate=false"
                        
                        // Force update: Naye pods fresh image ke saath aayenge
                        sh "kubectl rollout restart deployment ${APP_NAME}"
                    }
                }
            }
        }

        stage('Step 5: Universal Port Access') {
            steps {
                script {
                    withEnv(["HOME=/home/faiyyaz", "KUBECONFIG=/home/faiyyaz/.kube/config"]) {
                        
                        // Check: Kya hum Local (Minikube) par hain?
                        def context = sh(script: "kubectl config current-context", returnStdout: true).trim()
                        
                        if (context.contains("minikube")) {
                            echo "Local Detected: Automating Port ${FIXED_PORT}..."
                            // Pehle se chal rahe port connection ko kill karo
                            sh "sudo fuser -k ${FIXED_PORT}/tcp || true"
                            // Background mein tunnel/port-forward setup
                            sh "nohup kubectl port-forward svc/student-app-service ${FIXED_PORT}:80 --address 0.0.0.0 > port-forward.log 2>&1 &"
                        } else {
                            echo "Cloud/AWS Detected: Skipping port-forward (AWS Security Groups handle this)."
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
            echo "MUBARAK HO! SAB KUCH FRESH AUR AUTO-SET HO GAYA HAI."
            echo "APP LINK: http://localhost:${FIXED_PORT}"
            echo "--------------------------------------------------------"
        }
    }
}