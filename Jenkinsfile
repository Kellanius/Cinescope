pipeline {
    agent any

    parameters {
        string(name: 'TEST_PLAN_ID', defaultValue: '', description: 'ID тест-плана из Test IT')
        string(name: 'TEST_RUN_ID', defaultValue: '', description: 'ID прогона из Test IT')
    }

    stages {
        stage('Checkout') {
            steps {
                echo 'Клонируем репозиторий...'
                git branch: 'main',
                    url: 'https://github.com/Kellanius/Cinescope.git',
                    credentialsId: 'github-token'
            }
        }

        stage('Setup Environment') {
            steps {
                echo 'Устанавливаем зависимости...'
                bat 'pip install -r requirements.txt'
            }
        }

        stage('Run Tests') {
            steps {
                echo 'Запускаем тесты с адаптером Test IT...'
                withCredentials([
                    string(credentialsId: 'testit-url', variable: 'TESTIT_URL'),
                    string(credentialsId: 'testit-token', variable: 'TESTIT_TOKEN'),
                    string(credentialsId: 'testit-project-id', variable: 'TESTIT_PROJECT_ID'),
                    string(credentialsId: 'testit-config-id', variable: 'TESTIT_CONFIG_ID')
                ]) {
                    bat """
                        pytest tests/ \\
                            --testit \\
                            --testit-url=${TESTIT_URL} \\
                            --testit-private-token=${TESTIT_TOKEN} \\
                            --testit-project-id=${TESTIT_PROJECT_ID} \\
                            --testit-configuration-id=${TESTIT_CONFIG_ID} \\
                            --testit-test-run-id=${params.TEST_RUN_ID} \\
                            --testit-test-plan-id=${params.TEST_PLAN_ID}
                    """
                }
            }
        }
    }

    post {
        always {
            echo 'Сборка завершена. Результаты отправлены в Test IT.'
        }
    }
}