pipeline {
    agent any
    stages {
        stage('Check versions') {
            steps {
                script {
                    docker.withRegistry('https://ghcr.io', 'github-token-for-docker') {
                        bat "docker run --rm -w /workspace ghcr.io/kellanius/box-for-jenkins:latest sh -c \"pip list | grep testit || echo 'No testit packages found'\""
                    }
                }
            }
        }
    }
}