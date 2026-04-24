pipeline {
    agent any 

    environment {
        DOCKER_HUB_USER = "techfaiyaz5" 
        APP_NAME = "student-app"
        FIXED_PORT = "30001"
        MY_HOME = "/var/lib/jenkins"
    }

    stages {

        stage('Step 1: Permission & System Fix') {
            steps {
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

        // ✅ FIX 1: minikube delete hataya — sirf check karo
        stage('Step 4: Infrastructure & HPA Setup') {
            steps {
                script {
                    echo 'Ensuring Minikube is Running...'
                    withEnv(["HOME=/var/lib/jenkins", "KUBECONFIG=/var/lib/jenkins/.kube/config", "PATH+EXTRA=/usr/local/bin:/usr/bin:/bin"]) {
                        
                        def status = sh(
                            script: "minikube status | grep -c 'Running' || echo '0'",
                            returnStdout: true
                        ).trim()

                        if (status == "0") {
                            echo "Minikube not running — Starting..."
                            sh "minikube start --driver=docker --force"
                        } else {
                            echo "Minikube already running — Skipping start"
                        }

                        sh "kubectl apply -f k8s/db-deployment.yaml --validate=false"
                        sh "kubectl apply -f k8s/app-deployment.yaml --validate=false"
                        sh "kubectl apply -f k8s/hpa.yaml"
                        sh "kubectl rollout restart deployment ${APP_NAME}"
                    }
                }
            }
        }

        // ✅ FIX 2: faiyyaz → ubuntu kar diya
        stage('Step 5: Scaling Metrics & Addons') {
            steps {
                script {
                    withEnv(["HOME=/var/lib/jenkins", "KUBECONFIG=/var/lib/jenkins/.kube/config", "PATH+EXTRA=/usr/local/bin"]) {
                        sh "minikube addons enable metrics-server"
                    }
                }
            }
        }

        // ✅ FIX 3: nohup hataya — systemd service se port-forward chalao
        stage('Step 6: Auto-Tunnel & Access') {
            steps {
                script {
                    withEnv(["HOME=/var/lib/jenkins", "KUBECONFIG=/var/lib/jenkins/.kube/config", "PATH+EXTRA=/usr/local/bin"]) {

                        sh "sudo pkill -f 'minikube tunnel' || true"
                        sh "sudo pkill -f 'kubectl port-forward' || true"
                        sh "sudo fuser -k ${FIXED_PORT}/tcp || true"

                        // Systemd service banao — Jenkins band hone ke baad bhi survive karega
                        sh """
                            sudo bash -c 'cat > /etc/systemd/system/kube-portforward.service << EOF
[Unit]
Description=Kubectl Port Forward for student-app
After=network.target

[Service]
User=ubuntu
Environment=KUBECONFIG=/var/lib/jenkins/.kube/config
ExecStart=/usr/local/bin/kubectl port-forward svc/student-app-service ${FIXED_PORT}:80 --address 0.0.0.0
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF'
                        """
                        sh "sudo systemctl daemon-reload"
                        sh "sudo systemctl restart kube-portforward"
                        sh "sudo systemctl enable kube-portforward"

                        echo "Waiting for port to be active..."
                        sh "sleep 5"

                        sh "kubectl rollout status deployment ${APP_NAME}"
                    }
                }
            }
        }

        stage('Step 7: Your App is Live') {
            steps {
                script {
                    def ip = sh(
                        script: "curl -s http://checkip.amazonaws.com || echo 'YOUR-EC2-IP'",
                        returnStdout: true
                    ).trim()
                    echo "=========================================="
                    echo "App Live at: http://${ip}:${FIXED_PORT}"
                    echo "=========================================="
                    echo "Load Test: while true; do wget -q -O- http://${ip}:${FIXED_PORT}; done"
                }
            }
        }
    }
}
