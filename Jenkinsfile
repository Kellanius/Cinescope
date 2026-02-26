pipeline {
    agent any
    stages {
        stage('Pull and check image') {
            steps {
                script {
                    docker.withRegistry('https://ghcr.io', 'github-token-for-docker') {
                        bat "docker pull ghcr.io/kellanius/box-for-jenkins:latest"
                        // Явный запуск контейнера с переопределением рабочей директории
                        bat """
                            docker run --rm \\
                              -w /workspace \\
                              ghcr.io/kellanius/box-for-jenkins:latest \\
                              sh -c "pip list | grep testit || echo 'No testit packages found'"
                        """
                    }
                }
            }
        }
    }
}