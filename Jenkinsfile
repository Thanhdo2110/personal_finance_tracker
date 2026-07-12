pipeline {

    agent any

    environment {
        AWS_REGION = 'us-east-1'
        AWS_REGISTRY = '552509717559.dkr.ecr.us-east-1.amazonaws.com'
        BACKEND_REPO = 'personal-finance-tracker-backend'
        FRONTEND_REPO = 'personal-finance-tracker-frontend'
    }

    stages {
        stage('Checkout Source') {
            steps {
                checkout scm
            }
        }

        stage('Prepare') {
            steps {
                script {
                    env.IMAGE_TAG = env.GIT_COMMIT.take(8)
                    echo "Using Image Tag: ${env.IMAGE_TAG}"
                }
            }
        }

        stage('Build Backend Image') {
            steps {
                sh """
                docker build \
                -t ${AWS_REGISTRY}/${BACKEND_REPO}:${IMAGE_TAG} \
                ./backend
                """
            }
        }

        stage('Build Frontend Image') {
            steps {
                sh """
                docker build \
                -t ${AWS_REGISTRY}/${FRONTEND_REPO}:${IMAGE_TAG} \
                ./frontend
                """
            }
        }

        stage('Login AWS ECR') {
            steps {
                withCredentials([
                    string(credentialsId: 'aws-access-key-id', variable: 'AWS_ACCESS_KEY_ID'),
                    string(credentialsId: 'aws-secret-access-key', variable: 'AWS_SECRET_ACCESS_KEY'),
                    string(credentialsId: 'aws-session-token', variable: 'AWS_SESSION_TOKEN')

                ]) {
                    sh """
                    aws ecr get-login-password --region ${AWS_REGION} |
                    docker login --username AWS --password-stdin ${AWS_REGISTRY}
                    """
                }
            }
        }

        stage('Push Docker Images') {
            steps {
                sh """
                docker push ${AWS_REGISTRY}/${BACKEND_REPO}:${IMAGE_TAG}
                docker push ${AWS_REGISTRY}/${FRONTEND_REPO}:${IMAGE_TAG}
                """
            }
        }

        stage('Deploy Development') {
            steps {
                sh """
                docker compose down || true
                docker compose up -d
                """
            }
        }

        stage('Verify Development') {
            steps {
                sh """
                docker ps
                """
            }
        }

        stage('Approval Gate') {
            steps {
                timeout(time: 10, unit: 'MINUTES') {
                    input(
                        message: 'Deploy to Production Kubernetes?',
                        ok: 'Deploy'
                    )
                }
            }
        }

        stage('Apply Kubernetes Manifests') {
            steps {
                sh """
                kubectl apply -f k8s/namespace.yaml

                kubectl apply -f k8s/secret.yaml

                kubectl apply -f k8s/configmap.yaml

                kubectl apply -f k8s/backend-deployment.yaml

                kubectl apply -f k8s/frontend-deployment.yaml
                """
            }
        }
        stage('Update Kubernetes Images') {
            steps {
                sh """
                kubectl set image deployment/finance-backend \
                backend=${AWS_REGISTRY}/${BACKEND_REPO}:${IMAGE_TAG} \
                -n finance-apps

                kubectl set image deployment/finance-frontend \
                frontend=${AWS_REGISTRY}/${FRONTEND_REPO}:${IMAGE_TAG} \
                -n finance-apps
                """
            }
        }

        stage('Verify Rollout') {
            steps {
                sh """
                kubectl rollout status deployment/finance-backend -n finance-apps
                kubectl rollout status deployment/finance-frontend -n finance-apps
                """
            }
        }

        stage('Verify Kubernetes') {
            steps {
                sh """
                kubectl get pods -n finance-apps
                kubectl get svc -n finance-apps
                """
            }
        }
    }

    post {
        success {
            echo 'Deployment completed successfully.'
        }

        failure {
            echo 'Deployment failed.'
            sh """
            kubectl rollout undo deployment/finance-backend -n finance-apps || true
            kubectl rollout undo deployment/finance-frontend -n finance-apps || true
            """
        }

        always {
            sh """
            docker image prune -af || true
            """
        }
    }
}