pipeline {
    agent any

    parameters {
        string(name: 'TEST_PLAN_ID', defaultValue: '', description: 'ID тест-плана из Test IT (оставьте пустым для ручного запуска)')
        string(name: 'TEST_RUN_ID', defaultValue: '', description: 'ID прогона из Test IT (обычно пусто)')
        string(name: 'TEST_PATH', defaultValue: 'tests/', description: 'Путь к тестам (например, tests/ui/test_feedback_page.py или tests/ui/)')
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
                script {
                    // Базовые аргументы pytest
                    def args = "--testit -v --tb=short"

                    // Добавляем параметры Test IT, если они заданы
                    if (params.TEST_PLAN_ID) {
                        args += " --testit-test-plan-id=${params.TEST_PLAN_ID}"
                    }
                    if (params.TEST_RUN_ID) {
                        args += " --testit-test-run-id=${params.TEST_RUN_ID}"
                    }

                    // Запускаем тесты по указанному пути
                    bat """
                        "${env.PYTHON}" -m pytest ${params.TEST_PATH} ${args}
                    """
                }
            }
        }
    }

    post {
        always {
            echo '🏁 Сборка завершена.'
        }
    }
}