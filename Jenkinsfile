pipeline {
    agent any
    
    environment {
        AWS_REGISTRY     = '552509717559.dkr.ecr.us-east-1.amazonaws.com'
        BACKEND_REPO     = 'personal-finance-tracker-backend'
        FRONTEND_REPO    = 'personal-finance-tracker-frontend'
        AWS_REGION       = 'us-east-1'
        IMAGE_TAG        = "${GIT_COMMIT[0..7]}" // Lấy 8 ký tự đầu của commit hash làm tag định danh độc nhất
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
                sh "docker build -t ${AWS_REGISTRY}/${BACKEND_REPO}:latest ./backend"
                sh "docker build -t ${AWS_REGISTRY}/${FRONTEND_REPO}:latest ./frontend"
            }
        }

        stage('Push to AWS ECR') {
            steps {
                echo "🚀 Đang đăng nhập và push image lên AWS ECR bằng Token bảo mật..."
                withCredentials([
                    string(credentialsId: 'aws-access-key-id', variable: 'AWS_ACCESS_KEY_ID'),
                    string(credentialsId: 'aws-secret-access-key', variable: 'AWS_SECRET_ACCESS_KEY'),
                    string(credentialsId: 'aws-session-token', variable: 'AWS_SESSION_TOKEN')
                ]) {
                    sh """
                        echo "🔑 Đang sinh Token đăng nhập thông qua Docker container phụ trợ..."
                        
                        AWS_TOKEN=\$(docker run --rm \
                            -e AWS_ACCESS_KEY_ID=\$AWS_ACCESS_KEY_ID \
                            -e AWS_SECRET_ACCESS_KEY=\$AWS_SECRET_ACCESS_KEY \
                            -e AWS_SESSION_TOKEN=\$AWS_SESSION_TOKEN \
                            amazon/aws-cli ecr get-login-password --region ${AWS_REGION})

                        echo "🔐 Tiến hành đăng nhập Docker vào ECR Registry..."
                        echo "\$AWS_TOKEN" | docker login --username AWS --password-stdin ${AWS_REGISTRY}

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
                echo "🐳 Đang deploy cập nhật môi trường Dev qua Docker Compose V2..."
                sh """
                    # Nạp biến IMAGE_TAG chạy trước và gọi trực tiếp docker compose phiên bản mới
                    IMAGE_TAG=${IMAGE_TAG} docker compose -f docker-compose.prod.yml up -d --force-recreate
                """
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