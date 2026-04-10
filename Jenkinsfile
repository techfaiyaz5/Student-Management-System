pipeline {
    agent any

    environment {
        DOCKERHUB_USER = "faiyyazkhan" // Apna username badlein
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
            steps {
                script {
                    echo "Checking Python syntax for errors..."
                    // 'pyflakes' install hona chahiye: pip install pyflakes
                    // Agar syntax galat hai, toh ye pipeline yahi fail ho jayegi
                    sh "python3 -m pyflakes . || (echo 'ERROR: Syntax Check Failed' && exit 1)"
                }
            }
        }

        stage('Step 3: Build Docker Image') {
            // Ye tabhi chalega jab Step 2 pass hoga
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
                    sh "echo \$PASS | docker login -u \$USER --password-stdin"
                    sh "docker push ${DOCKERHUB_USER}/${APP_NAME}:${env.BUILD_NUMBER}"
                    sh "docker push ${DOCKERHUB_USER}/${APP_NAME}:latest"
                }
            }
        }
    }

    post {
        always {
            echo "Cleaning up local images..."
            sh "docker rmi ${DOCKERHUB_USER}/${APP_NAME}:${env.BUILD_NUMBER} || true"
        }
        failure {
            echo "❌ BUILD FAILED: Image was not pushed to Docker Hub due to code errors."
        }
    }
}