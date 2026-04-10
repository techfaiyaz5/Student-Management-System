pipeline {
    agent any

    environment {
        DOCKERHUB_USER = "faiyyazkhan"
        APP_NAME = "student-management-app"
        DOCKERHUB_CRED_ID = "docker-hub-creds"
    }

    stages {
        stage('Step 1: Checkout Code') {
            steps {
                checkout scm
            }
        }

        stage('Step 2: Syntax & Quality Check') {
            /* Hum yahan 'python' ka official docker image use kar rahe hain.
               Isse Jenkins host machine par Python ki zarurat nahi padegi.
            */
            agent {
                docker { 
                    image 'python:3.12-slim'
                    // 'reuseNode true' se checkout wala code isi container ko mil jayega
                    reuseNode true 
                }
            }
            steps {
                script {
                    echo "Environment ready! Installing Pyflakes inside temporary container..."
                    sh "pip install pyflakes"
                    echo "Checking Python syntax for errors..."
                    sh "python3 -m pyflakes . || (echo 'ERROR: Syntax Check Failed' && exit 1)"
                }
            }
        }

        stage('Step 3: Build Docker Image') {
            steps {
                script {
                    echo "Building Docker Image..."
                    sh "docker build -t ${DOCKERHUB_USER}/${APP_NAME}:${env.BUILD_NUMBER} ."
                    sh "docker tag ${DOCKERHUB_USER}/${APP_NAME}:${env.BUILD_NUMBER} ${DOCKERHUB_USER}/${APP_NAME}:latest"
                }
            }
        }

        stage('Step 4: Push to Docker Hub') {
            steps {
                withCredentials([usernamePassword(credentialsId: "${DOCKERHUB_CRED_ID}", passwordVariable: 'PASS', usernameVariable: 'USER')]) {
                    script {
                        sh "echo \$PASS | docker login -u \$USER --password-stdin"
                        sh "docker push ${DOCKERHUB_USER}/${APP_NAME}:${env.BUILD_NUMBER}"
                        sh "docker push ${DOCKERHUB_USER}/${APP_NAME}:latest"
                    }
                }
            }
        }
    }

    post {
        always {
            echo "Cleaning up local images..."
            // Taaki laptop ki disk full na ho jaye
            sh "docker rmi ${DOCKERHUB_USER}/${APP_NAME}:${env.BUILD_NUMBER} || true"
        }
        failure {
            echo "❌ BUILD FAILED: Check the logs above for errors."
        }
    }
}