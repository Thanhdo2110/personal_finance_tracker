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
                echo "🚀 Đang đăng nhập và push image lên AWS ECR..."
                sh """
                    # 1. Cài đặt AWS CLI nếu chưa có
                    if [ ! -d "./aws-cli-bin" ]; then
                        echo "📦 Đang nạp bộ cài AWS CLI..."
                        curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" > /dev/null
                        unzip -q -o awscliv2.zip
                        ./aws/install -i ./aws-cli-bin -b ./aws-cli-bin --update
                    fi

                    # 2. KHAI BÁO KEY AWS ACADEMY CỦA BẠN TẠI ĐÂY
                    # Hãy mở tab "AWS CLI: Show" trên AWS Academy, copy và dán chính xác 3 chuỗi vào đây:
                    export AWS_ACCESS_KEY_ID="ĐIỀN_AWS_ACCESS_KEY_ID_VÀO_ĐÂY"
                    export AWS_SECRET_ACCESS_KEY="ĐIỀN_AWS_SECRET_ACCESS_KEY_VÀO_ĐÂY"
                    export AWS_SESSION_TOKEN="ĐIỀN_CHÂN_THỰC_CHUỖI_SESSION_TOKEN_SIÊU_DÀI_VÀO_ĐÂY"
                    export AWS_DEFAULT_REGION="${AWS_REGION}"

                    echo "🔐 Đang thực hiện login vào AWS ECR..."
                    # Gọi chính xác file binary gốc trong thư mục v2 để né lỗi 'not found'
                    ./aws-cli-bin/v2/current/bin/aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${AWS_REGISTRY}
                    
                    echo "📤 Đang push các bản Docker Images lên ECR..."
                    docker push ${AWS_REGISTRY}/${BACKEND_REPO}:${IMAGE_TAG}
                    docker push ${AWS_REGISTRY}/${FRONTEND_REPO}:${IMAGE_TAG}
                    docker push ${AWS_REGISTRY}/${BACKEND_REPO}:latest
                    docker push ${AWS_REGISTRY}/${FRONTEND_REPO}:latest
                """
            }
        }
        stage('Deploy to Dev (Docker Compose)') {
            steps {
                echo "🐳 Đang deploy cập nhật môi trường Dev qua Docker Compose..."
                sh """
                    export IMAGE_TAG=${IMAGE_TAG}
                    docker compose -f docker-compose.prod.yml up -d --force-recreate
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