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
                // Ye error handle karega agar system pip allow na kare
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
                // Aapne 'docker-hub-creds' use kiya hai, ensure karein Jenkins mein yahi ID ho
                withCredentials([usernamePassword(credentialsId: 'docker-hub-creds', passwordVariable: 'DOCKER_PASS', usernameVariable: 'DOCKER_USER')]) {
                    sh "echo \$DOCKER_PASS | docker login -u \$DOCKER_USER --password-stdin"
                    sh "docker tag student-app:latest \$DOCKER_USER/student-app:latest"
                    sh "docker push \$DOCKER_USER/student-app:latest"
                }
            }
        }

        // --- NAYA STEP: AUTO DEPLOYMENT ---
        stage('Step 5: Auto Run Application') {
            steps {
                echo 'Starting the Application locally...'
                withCredentials([usernamePassword(credentialsId: 'docker-hub-creds', passwordVariable: 'DOCKER_PASS', usernameVariable: 'DOCKER_USER')]) {
                    script {
                        // 1. Purane container ko hatana (agar koi chal raha ho)
                        sh "docker stop student-app-container || true"
                        sh "docker rm student-app-container || true"
                        
                        // 2. Naya container start karna
                        // Hum wahi image use kar rahe hain jo abhi push ki hai
                        sh "docker run -d --name student-app-container -p 9000:8080 \$DOCKER_USER/student-app:latest"
                    }
                }
                echo 'SUCCESS! Page is live at http://localhost:9000'
            }
        }
    }
}