pipeline {
    agent any

    environment {
        AWS_REGISTRY     = '552509717559.dkr.ecr.us-east-1.amazonaws.com'
        BACKEND_REPO     = 'personal-finance-tracker-backend'
        FRONTEND_REPO    = 'personal-finance-tracker-frontend'
        AWS_REGION       = 'us-east-1'
        IMAGE_TAG        = "${GIT_COMMIT[0..7]}" // Lấy 8 ký tự đầu của commit hash làm tag định danh độc nhất
        DB_HOST          = 'db-finance-tracker.cwholn2fehh0.us-east-1.rds.amazonaws.com'
        DB_PORT          = '3306'
        DB_NAME          = 'finance_tracker'
    }

    stages {
        stage('Checkout Source') {
            steps {
                checkout scm
            }
        }

        stage('Build Docker Images') {
            steps {
                echo "🔨 Đang build Docker images với tag: ${IMAGE_TAG}..."
                sh "docker build -t ${AWS_REGISTRY}/${BACKEND_REPO}:${IMAGE_TAG} ./backend"
                sh "docker build -t ${AWS_REGISTRY}/${FRONTEND_REPO}:${IMAGE_TAG} ./frontend"

                // Đồng thời gán thêm tag latest để làm bản mặc định
                sh "docker tag ${AWS_REGISTRY}/${BACKEND_REPO}:${IMAGE_TAG} ${AWS_REGISTRY}/${BACKEND_REPO}:latest"
                sh "docker tag ${AWS_REGISTRY}/${FRONTEND_REPO}:${IMAGE_TAG} ${AWS_REGISTRY}/${FRONTEND_REPO}:latest"
            }
        }

        stage('Push to AWS ECR') {
             steps {
                 echo "🚀 Đang đăng nhập và push image lên AWS ECR..."
                  withCredentials([
               string(credentialsId: 'aws-access-key-id', variable: 'AWS_ACCESS_KEY_ID'),
              string(credentialsId: 'aws-secret-access-key', variable: 'AWS_SECRET_ACCESS_KEY'),
               string(credentialsId: 'aws-session-token', variable: 'AWS_SESSION_TOKEN')
        ]) {
            sh """
                echo "🔐 Đăng nhập Docker vào ECR Registry...."
                aws ecr get-login-password --region ${AWS_REGION} | \
                  docker login --username AWS --password-stdin ${AWS_REGISTRY}

                echo "📤 Đang đẩy các bản Docker Images lên AWS ECR..."
                docker push ${AWS_REGISTRY}/${BACKEND_REPO}:${IMAGE_TAG}
                docker push ${AWS_REGISTRY}/${FRONTEND_REPO}:${IMAGE_TAG}
                docker push ${AWS_REGISTRY}/${BACKEND_REPO}:latest
                docker push ${AWS_REGISTRY}/${FRONTEND_REPO}:latest
            """
        }
    }
}

        stage('Deploy to Dev (Docker Compose)') {
            steps {
                echo "🐳 Đang deploy cập nhật môi trường Dev bằng Docker thuần..."
                withCredentials([usernamePassword(credentialsId: 'mysql-db-creds', usernameVariable: 'DB_USER', passwordVariable: 'DB_PASSWORD')]) {
                    sh """
                        # 1. Dọn dẹp các container cũ nếu đang chạy để tránh trùng cổng (ports)
                        docker rm -f finance-tracker-frontend-dev || true
                        docker rm -f finance-tracker-backend-dev || true

                        # 2. Tạo một Docker Network chung để Frontend và Backend có thể nói chuyện với nhau
                        docker network create finance-tracker-network || true

                        echo "🚀 Khởi chạy Backend Container......."
                        docker run -d -t \\
                            --name finance-tracker-backend-dev \\
                            --network finance-tracker-network \\
                            -p 5001:5001 \\
                            -e DB_HOST=${DB_HOST} \\
                            -e DB_PORT=${DB_PORT} \\
                            -e DB_USER=\$DB_USER \\
                            -e DB_PASSWORD=\$DB_PASSWORD \\
                            -e DB_NAME=${DB_NAME} \\
                            ${AWS_REGISTRY}/${BACKEND_REPO}:${IMAGE_TAG}

                        echo "🚀 Khởi chạy Frontend Container..."
                        docker run -d -t \\
                            --name finance-tracker-frontend-dev \\
                            --network finance-tracker-network \\
                            -p 3001:3001 \\
                            ${AWS_REGISTRY}/${FRONTEND_REPO}:${IMAGE_TAG}

                        echo "✅ Môi trường Dev đã được cập nhật thành công!"
                    """
                }
            }
        }

        stage('Approval Gate') {
            steps {
                // Tạm dừng đường ống để bạn check môi trường Dev ổn định rồi mới bấm Duyệt lên Prod K8s
                input message: 'Bạn có duyệt triển khai ứng dụng lên cụm Production (Kubernetes Kind) không?', ok: 'Triển khai ngay!'
            }
        }

        stage('Deploy to Prod (Kubernetes Kind)') {
            steps {
                echo "☸️ Đang áp dụng cấu hình K8s Manifests lên cụm Kind thuộc namespace finance-apps..."
                sh """
                    kubectl apply -f k8s/namespace.yaml
                    kubectl apply -f k8s/secret.yaml
                    kubectl apply -f k8s/backend-deployment.yaml
                    kubectl apply -f k8s/frontend-deployment.yaml

                    # Ép các Deployment tái khởi động các Pod để cập nhật phiên bản mới ngay lập tức
                    kubectl rollout restart deployment/finance-backend -n finance-apps
                    kubectl rollout restart deployment/finance-frontend -n finance-apps
                """
            }
        }
    }

    post {
        success {
            echo '🎉 Pipeline hoàn thành xuất sắc! Toàn bộ hệ thống đã chạy phiên bản mới.'
        }
        failure {
            echo '❌ Pipeline gặp lỗi rồi! Bạn hãy kiểm tra lại Console Output để sửa nhé.'
        }
    }
}