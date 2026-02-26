pipeline {
    agent any
    stages {
        stage('Pull and check image') {
            steps {
                script {
                    docker.withRegistry('https://ghcr.io', 'github-token-for-docker') {
                        sh "docker pull ghcr.io/kellanius/box-for-jenkins:latest"
                        docker.image('ghcr.io/kellanius/box-for-jenkins:latest').inside {
                            sh 'pip list | grep testit'
                        }
                    }
                }
            }
        }
    }
}