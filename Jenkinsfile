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

        // --- UPDATED STEP 5: PURE DOCKER COMPOSE ---
        stage('Step 5: Step 5: Deploy to Kubernetes') {
            steps {
                echo 'Deploying to Minikube Cluster...'
                script {
                   // 1. Pehle Database apply karein
                    sh "kubectl apply -f k8s/db-deployment.yaml"
                    
                    // 2. Phir App apply karein
                    sh "kubectl apply -f k8s/app-deployment.yaml"
                    
                    // 3. Rollout Restart (Nayi image force karne ke liye)
                    sh "kubectl rollout restart deployment student-app"
                    
                    // 4. Status Check
                    sh "kubectl rollout status deployment student-app"
                }
                echo 'SUCCESS! Your project is live at http://localhost:9000'
            }
        }
    }
}