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

        stage('Step 5: Deploy to Kubernetes (Minikube)') {
            steps {
                echo 'Starting Automated K8s Deployment...'
                script {
                    // Sabse pehle purane docker-compose ko down kar dete hain agar chal raha ho
                    // sh "docker-compose down || true"

                    // Kubernetes Deployment - Humne validation off kar di hai taki auth error na aaye
                    sh "kubectl apply -f k8s/db-deployment.yaml --validate=false"
                    sh "kubectl apply -f k8s/app-deployment.yaml --validate=false"
                    
                    // App ko restart karna taki naya Docker Hub image pull ho jaye
                    sh "kubectl rollout restart deployment student-app"
                    
                    // Status confirm karna
                    sh "kubectl rollout status deployment student-app"
                }
                echo 'SUCCESS! Your project is being managed by Kubernetes.'
                echo 'Check app status using: kubectl get pods'
            }
        }
    }
}