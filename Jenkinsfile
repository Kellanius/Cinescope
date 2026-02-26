pipeline {
    agent any
    stages {
        stage('Pull and check image') {
            steps {
                script {
                    docker.withRegistry('https://ghcr.io', 'github-token-for-docker') {
                        // Используем bat для команды на хосте Windows
                        bat "docker pull ghcr.io/kellanius/box-for-jenkins:latest"
                        // Внутри контейнера используем sh (он там есть)
                        docker.image('ghcr.io/kellanius/box-for-jenkins:latest').inside {
                            sh 'pip list | grep testit'
                        }
                    }
                }
            }
        }
    }
}