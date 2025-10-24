pipeline {
    agent any

    environment {
        REGISTRY = "docker.io"
        IMAGE_NAME = "nachiyar/myapp"
        TAG = "v${BUILD_NUMBER}"
        KUBECONFIG = "/root/.kube/config"
    }

    stages {
        stage('Clean Workspace') {
            steps {
               deleteDir() // Deletes all files in the workspace
            }
        }


        stage('Checkout') {
            steps {
                git branch: 'main', url: 'https://github.com/Nachiyar2702/webapp.git'
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    sh "docker build -t ${IMAGE_NAME}:${TAG} ."
                }
            }
        }

        stage('Vulnerability Scan') {
            steps {
                script {
                    // Using Trivy (simple and widely accepted tool)
                    sh "trivy image --exit-code 1 --severity HIGH,CRITICAL ${IMAGE_NAME}:${TAG} || true"
                }
            }
        }

        stage('Push to DockerHub') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'dockerhub-creds', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
                    sh """
                        echo $DOCKER_PASS | docker login -u $DOCKER_USER --password-stdin
                        docker push ${IMAGE_NAME}:${TAG}
                    """
                }
            }
        }

        stage('Deploy to Minikube') {
            steps {
                script {
                    sh """
                        kubectl set image deployment/myapp myapp=${IMAGE_NAME}:${TAG} --record || \
                        kubectl apply -f deployment.yaml
                    """
                }
            }
        }
    }

    post {
        always {
            echo "Pipeline completed — cleaning up local images"
            sh "docker rmi ${IMAGE_NAME}:${TAG} || true"
        }
    }
}
