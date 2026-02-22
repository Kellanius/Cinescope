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

        stage('Find Python') {
            steps {
                script {
                    // Поиск Python в PATH
                    def pythonPath = powershell(
                        returnStdout: true,
                        script: 'Get-Command python.exe -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Path'
                    ).trim()

                    if (pythonPath) {
                        env.PYTHON = pythonPath
                    } else {
                        // Стандартные пути установки
                        def possiblePaths = [
                            "C:\\Python39\\python.exe",
                            "C:\\Python310\\python.exe",
                            "C:\\Python311\\python.exe",
                            "C:\\Python38\\python.exe",
                            "C:\\Program Files\\Python39\\python.exe",
                            "C:\\Program Files\\Python310\\python.exe",
                            "C:\\Program Files\\Python311\\python.exe",
                            "C:\\Program Files (x86)\\Python39\\python.exe",
                            "C:\\Python314\\python.exe"
                        ]
                        pythonPath = null
                        for (path in possiblePaths) {
                            if (fileExists(path)) {
                                pythonPath = path
                                break
                            }
                        }
                        if (pythonPath) {
                            env.PYTHON = pythonPath
                        } else {
                            error('Python не найден. Установите Python в C:\\Python314 или добавьте в PATH.')
                        }
                    }
                    echo "✅ Используется Python: ${env.PYTHON}"
                }
            }
        }

        stage('Setup Environment') {
            steps {
                echo '📦 Устанавливаем зависимости...'
                bat """
                    "${env.PYTHON}" -m pip install --upgrade pip
                    "${env.PYTHON}" -m pip install --upgrade pytest
                    "${env.PYTHON}" -m pip install --upgrade testit-pytest
                    "${env.PYTHON}" -m pip install -r requirements.txt
                """
            }
        }

        stage('Verify TestIT plugin') {
            steps {
                echo '🔍 Проверяем, что testit-pytest установлен и виден:'
                bat """
                    "${env.PYTHON}" -m pip show testit-pytest || exit /b 1
                    "${env.PYTHON}" -m pytest --help | findstr testit || (echo "Плагин testit-pytest не загружен!" && exit /b 1)
                """
            }
        }

        stage('Check packages') {
            steps {
                echo '📋 Список установленных пакетов:'
                bat """
                    "${env.PYTHON}" -m pip list
                """
            }
        }

        stage('Run Tests') {
            steps {
                echo '🚀 Запускаем тесты с адаптером Test IT...'
                withCredentials([
                    string(credentialsId: 'testit-url', variable: 'TESTIT_URL'),
                    string(credentialsId: 'testit-token', variable: 'TESTIT_TOKEN'),
                    string(credentialsId: 'testit-project-id', variable: 'TESTIT_PROJECT_ID'),
                    string(credentialsId: 'testit-config-id', variable: 'TESTIT_CONFIG_ID')
                ]) {
                    bat """
                        "${env.PYTHON}" -m pytest tests/ ^
                        --testit ^
                        --testit-url=%TESTIT_URL% ^
                        --testit-private-token=%TESTIT_TOKEN% ^
                        --testit-project-id=%TESTIT_PROJECT_ID% ^
                        --testit-configuration-id=%TESTIT_CONFIG_ID% ^
                        --testit-test-run-id=${params.TEST_RUN_ID} ^
                        --testit-test-plan-id=${params.TEST_PLAN_ID}
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