pipeline {
    agent any 

    stages {
        stage('Step 1: Code Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Step 2: Install Requirements') {
            steps {
                echo 'Installing Project Dependencies...'
                sh 'pip install -r requirements.txt --user || echo "Requirements already satisfied"'
            }
        }

        stage('Step 3: Build Docker Image') {
            steps {
                echo 'Creating Docker Image...'
                sh 'docker build -t student-app:latest .'
            }
        }

        stage('Step 4: Push to Docker Hub') {
            steps {
                echo 'Pushing Image to Cloud...'
                withCredentials([usernamePassword(credentialsId: 'docker-hub-creds', passwordVariable: 'DOCKER_PASS', usernameVariable: 'DOCKER_USER')]) {
                    sh "echo \$DOCKER_PASS | docker login -u \$DOCKER_USER --password-stdin"
                    sh "docker tag student-app:latest \$DOCKER_USER/student-app:latest"
                    sh "docker push \$DOCKER_USER/student-app:latest"
                }
            }
        }

        stage('Step 5: Deploy & Fix Permanent Port') {
            steps {
                echo 'Starting Automated K8s Deployment...'
                script {
                    // Minikube start check
                    sh "minikube status || minikube start"

                    // Apply K8s Manifests
                    sh "kubectl apply -f k8s/db-deployment.yaml --validate=false"
                    sh "kubectl apply -f k8s/app-deployment.yaml --validate=false"
                    
                    // --- STATIC PORT JUGAD (Tunnel in Background) ---
                    sh "nohup minikube tunnel > tunnel.log 2>&1 &"
                    
                    // Restart to pull latest image
                    sh "kubectl rollout restart deployment student-app"
                    sh "kubectl rollout status deployment student-app"

                    echo "--------------------------------------------------------"
                    echo "BHAI, AB MANUAAL KAAM KHATAM!"
                    echo "AAPKA APP HAMESHA YAHAN CHALEGA: http://localhost:30001"
                    echo "--------------------------------------------------------"
                }
            }
        }
    }
}