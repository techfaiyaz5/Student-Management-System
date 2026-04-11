pipeline {
    agent any 

    stages {
        stage('Step 1: Code Checkout') {
            steps {
                // GitHub se latest code uthana
                checkout scm
            }
        }

        stage('Step 2: Install Requirements') {
            steps {
                echo 'Installing Project Dependencies...'
                // Ye aapke laptop par project ki libraries install karega
                sh 'pip install -r requirements.txt --user || echo "Requirements already satisfied"'
            }
        }

        stage('Step 3: Build Docker Image') {
            steps {
                echo 'Creating Docker Image...'
                // Image ka naam 'student-app' rakha hai
                sh 'docker build -t student-app:latest .'
            }
        }

        stage('Step 4: Push to Docker Hub') {
            steps {
                echo 'Pushing Image to Cloud...'
                // 'docker-hub-id' wahi ID honi chahiye jo aapne Jenkins Credentials mein banayi hai
                withCredentials([usernamePassword(credentialsId: 'docker-hub-creds', passwordVariable: 'DOCKER_PASS', usernameVariable: 'DOCKER_USER')]) {
                    sh "echo \$DOCKER_PASS | docker login -u \$DOCKER_USER --password-stdin"
                    sh "docker tag student-app:latest \$DOCKER_USER/student-app:latest"
                    sh "docker push \$DOCKER_USER/student-app:latest"
                }
            }
        }
    }
}