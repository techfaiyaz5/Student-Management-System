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
        stage('Step 5: Auto Run Application') {
            steps {
                echo 'Starting App and Database with Docker Compose...'
                script {
                    // 1. Purane saare containers aur networks ko clean karna
                    sh "docker-compose down || true"
                    
                    // 2. Sirf Docker Compose chalana (Ye DB aur App dono ko background mein start kar dega)
                    // Ye automatically 9000 port use karega jo aapki file mein hai
                    sh "docker-compose up -d"
                }
                echo 'SUCCESS! Your project is live at http://localhost:9000'
            }
        }
    }
}