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

        // ✅ Вот он — правильный этап создания connection_config.ini
        stage('Create TestIT Config') {
            steps {
                withCredentials([
                    string(credentialsId: 'testit-url', variable: 'URL'),
                    string(credentialsId: 'testit-token', variable: 'TOKEN'),
                    string(credentialsId: 'testit-project-id', variable: 'PROJECT_ID'),
                    string(credentialsId: 'testit-config-id', variable: 'CONFIG_ID')
                ]) {
                    bat '''
                        echo [testit] > connection_config.ini
                        echo url = %URL% >> connection_config.ini
                        echo privateToken = %TOKEN% >> connection_config.ini
                        echo projectId = %PROJECT_ID% >> connection_config.ini
                        echo configurationId = %CONFIG_ID% >> connection_config.ini
                    '''
                    echo "✅ Файл connection_config.ini успешно создан"
                }
            }
        }

        stage('Run Tests') {
            steps {
                echo '🚀 Запускаем тесты...'
                bat """
                    "${env.PYTHON}" -m pytest tests/ --testit -v --tb=short
                """
            }
        }
    }

        stage('Debug testit module') {
        steps {
            bat '''
                "${env.PYTHON}" -c "import testit; print(dir(testit))"
            '''
        }
    }

    post {
        always {
            echo '🏁 Сборка завершена.'
        }
    }
}