pipeline {
    agent any

    parameters {
        string(name: 'TEST_PLAN_ID', defaultValue: '', description: 'ID тест-плана из Test IT')
        string(name: 'TEST_RUN_ID', defaultValue: '', description: 'ID прогона из Test IT')
    }

    environment {
        // Корень проекта — будет использоваться для PYTHONPATH
        PROJECT_ROOT = "%WORKSPACE%"
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

        stage('Create TestIT Config') {
            steps {
                withCredentials([
                    string(credentialsId: 'testit-url', variable: 'URL'),
                    string(credentialsId: 'testit-token', variable: 'TOKEN'),
                    string(credentialsId: 'testit-project-id', variable: 'PROJECT_ID'),
                    string(credentialsId: 'testit-config-id', variable: 'CONFIG_ID')
                ]) {
                    bat """
                        echo [testit] > connection_config.ini
                        echo url = %URL% >> connection_config.ini
                        echo privateToken = %TOKEN% >> connection_config.ini
                        echo projectId = %PROJECT_ID% >> connection_config.ini
                        echo configurationId = %CONFIG_ID% >> connection_config.ini
                        echo adapterMode = 0 >> connection_config.ini
                    """
                    echo "✅ Файл connection_config.ini успешно создан (режим 0)"
                }
            }
        }

        stage('Find Python') {
            steps {
                script {
                    def possiblePaths = [
                        "C:\\Python314\\python.exe",
                        "C:\\Users\\Kellanius\\PycharmProjects\\Cinescope\\.venv\\Scripts\\python.exe"
                    ]
                    def pythonPath = null
                    for (path in possiblePaths) {
                        if (fileExists(path)) {
                            pythonPath = path
                            break
                        }
                    }
                    if (!pythonPath) {
                        error("Python не найден. Пути: ${possiblePaths}")
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
                    "${env.PYTHON}" -m pip install pytest testit-adapter-pytest allure-pytest playwright faker
                    "${env.PYTHON}" -m pip install -r requirements.txt
                    "${env.PYTHON}" -m playwright install
                    echo "=== Проверка наличия модуля testit ==="
                    "${env.PYTHON}" -c "import testit; print('✅ Модуль testit доступен по пути:', testit.__file__)" || echo "❌ Модуль testit НЕ найден"
                    echo "=== Список установленных пакетов ==="
                    "${env.PYTHON}" -m pip list | findstr testit
                """
            }
        }

        stage('Clear pytest cache') {
            steps {
                bat """
                    "${env.PYTHON}" -m pytest --cache-clear
                """
            }
        }

        stage('Run Tests') {
            steps {
                script {
                    def args = "--testit -v --tb=short"

                    if (params.TEST_RUN_ID) {
                        args += " --tmsTestRunId=${params.TEST_RUN_ID}"
                    }
                    if (params.TEST_PLAN_ID) {
                        args += " --tmsTestPlanId=${params.TEST_PLAN_ID}"
                    }

                    bat """
                        set PYTHONPATH=%WORKSPACE%
                        "${env.PYTHON}" -m pytest ${params.TEST_PATH} ${args}
                    """
                }
            }
        }
    }

    post {
        always {
            echo '🏁 Сборка завершена. Результаты отправлены в Test IT.'
        }
    }
}