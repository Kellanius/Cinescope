pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                echo 'Клонируем репозиторий...'
                git branch: 'main',
                    url: 'https://github.com/Kellanius/Cinescope.git',
                    credentialsId: 'github-token'
            }
        }

        stage('Find Python') {
            steps {
                script {
                    def possiblePaths = [
                        "C:\\Python314\\python.exe",
                        "C:\\Users\\Kellanius\\PycharmProjects\\Cinescope\\.venv\\Scripts\\python.exe",
                        "C:\\Users\\Kellanius\\AppData\\Local\\Programs\\Python\\Python311\\python.exe"
                    ]
                    def pythonPath = null
                    for (path in possiblePaths) {
                        if (fileExists(path)) {
                            pythonPath = path
                            break
                        }
                    }
                    if (!pythonPath) {
                        error("Python не найден. Проверь пути: ${possiblePaths}")
                    }
                    env.PYTHON = pythonPath
                    echo "✅ Используется Python: ${env.PYTHON}"
                }
            }
        }

        stage('Setup Environment') {
            steps {
                echo '📦 Устанавливаем зависимости...'
                bat """
                    "${env.PYTHON}" -m pip install --upgrade pip
                    "${env.PYTHON}" -m pip install pytest testit-pytest allure-pytest playwright faker
                    "${env.PYTHON}" -m pip install -r requirements.txt
                    "${env.PYTHON}" -m playwright install
                """
            }
        }

        stage('Create testit.ini') {
            steps {
                withCredentials([
                    string(credentialsId: 'testit-url', variable: 'URL'),
                    string(credentialsId: 'testit-token', variable: 'TOKEN'),
                    string(credentialsId: 'testit-project-id', variable: 'PROJECT_ID'),
                    string(credentialsId: 'testit-config-id', variable: 'CONFIG_ID')
                ]) {
                    bat """
                        echo [testit] > testit.ini
                        echo url = %URL% >> testit.ini
                        echo privateToken = %TOKEN% >> testit.ini
                        echo projectId = %PROJECT_ID% >> testit.ini
                        echo configurationId = %CONFIG_ID% >> testit.ini
                        echo testRunName = Autotest Run from Jenkins >> testit.ini
                    """
                }
            }
        }

        stage('Run Tests') {
            steps {
                echo '🚀 Запускаем тесты с подробным выводом...'
                bat """
                    "${env.PYTHON}" -m pytest tests/ --testit -v --tb=short
                """
            }
        }
    }

    post {
        always {
            echo '🏁 Сборка завершена. Проверь логи выше.'
        }
    }
}