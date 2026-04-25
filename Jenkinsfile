pipeline {
    agent any 

    environment {
        DOCKER_HUB_USER = "techfaiyaz5" 
        APP_NAME = "student-app"
        FIXED_PORT = "30001"
        // ✅ Global settings: Ab har stage ko pata hai config kahan hai
        KUBECONFIG = "/var/lib/jenkins/.kube/config"
        HOME = "/var/lib/jenkins"
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

        stage('Step 4: Infrastructure & Deployment') {
            steps {
                script {
                    echo 'Ensuring Minikube is Running...'
                    // Minikube status check
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

                    // Deployments apply karo
                    sh "kubectl apply -f k8s/db-deployment.yaml --validate=false"
                    sh "kubectl apply -f k8s/app-deployment.yaml --validate=false"
                    sh "kubectl apply -f k8s/hpa.yaml"
                    sh "kubectl rollout restart deployment ${APP_NAME}"
                }
            }
        }

        stage('Step 5: Scaling Metrics') {
            steps {
                sh 'sudo -u ubuntu minikube addons enable metrics-server'
            }
        }

        stage('Step 6: Port-Forward Service') {
            steps {
                script {
                    // Purane processes saaf karo
                    sh "sudo pkill -f 'minikube tunnel' || true"
                    sh "sudo pkill -f 'kubectl port-forward' || true"
                    sh "sudo fuser -k ${FIXED_PORT}/tcp || true"

                    // Service file update: Ab ye global KUBECONFIG use karega
                    sh """
                        sudo bash -c 'cat > /etc/systemd/system/kube-portforward.service << EOF
[Unit]
Description=Kubectl Port Forward for student-app
After=network.target

[Service]
User=ubuntu
Environment=KUBECONFIG=${KUBECONFIG}
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

                    echo "Waiting for rollout..."
                    sh "kubectl rollout status deployment ${APP_NAME}"
                }
            }
        }

        stage('Step 7: Success') {
            steps {
                script {
                    def ip = sh(
                        script: "curl -s http://checkip.amazonaws.com || echo 'YOUR-EC2-IP'",
                        returnStdout: true
                    ).trim()
                    
                    echo "App Live at: http://${ip}:${FIXED_PORT}"
                    
                    
                }
            }
        }
    }
}