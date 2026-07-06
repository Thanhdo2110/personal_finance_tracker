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
                withCredentials([usernamePassword(credentialsId: 'aws-credentials-id', 
                                                 usernameVariable: 'AWS_ACCESS_KEY_ID', 
                                                 passwordVariable: 'AWS_SECRET_ACCESS_KEY')]) {
                    sh """
                        # Tự động cài đặt AWS CLI dạng lightweight (nếu chưa có) hoặc dùng fallback login bằng Docker
                        # Giải pháp tối ưu hóa: Dùng API mã hóa để lấy Token đăng nhập thẳng vào Docker
                        
                        echo "Thực hiện đăng nhập ECR không cần công cụ AWS CLI..."
                        
                        # Sử dụng TOKEN thu được bằng cách giả lập auth thông qua biến môi trường bí mật
                        # Bằng cách ép Docker nhận diện Registry AWS qua config
                        
                        # Cách đơn giản nhất cho Jenkins Container: Chạy login bằng token được pass từ bên ngoài
                        # Nếu máy có curl, ta lấy token trực tiếp qua API AWS
                        
                        # Bản sửa lỗi không phụ thuộc vào lệnh 'aws':
                        # Chúng ta tạm thời bypass qua bước login kiểm tra bằng cách cài đặt nhanh aws-cli vào workspace hoặc dùng fallback:
                        
                        if ! command -v aws &> /dev/null
                        then
                            echo "⚠️ Không tìm thấy lệnh aws trong Jenkins container. Tiến hành cài đặt nhanh..."
                            curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" > /dev/null
                            unzip -q awscliv2.zip
                            ./aws/install -i ./aws-cli-bin -b ./aws-cli-bin
                            export PATH="\$PATH:\$(pwd)/aws-cli-bin"
                        fi

                        # Lúc này chắc chắn hệ thống đã có lệnh aws để chạy tiếp
                        aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${AWS_REGISTRY}
                        
                        # Đẩy cả bản tag commit và bản latest lên ECR
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