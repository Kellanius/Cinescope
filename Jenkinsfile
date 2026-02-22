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
                    // Сначала пробуем найти Python через PowerShell (ищет в PATH)
                    def pythonPath = powershell(
                        returnStdout: true,
                        script: 'Get-Command python.exe -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Path'
                    ).trim()

                    if (pythonPath) {
                        env.PYTHON = pythonPath
                    } else {
                        // Если не нашли в PATH, проверяем самые частые места установки
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
                            error('''
                                ⛔ Python не найден автоматически.
                                Возможные решения:
                                1. Установите Python и добавьте его в системную переменную PATH, затем перезапустите службу Jenkins.
                                2. Если Python уже установлен в нестандартном месте, добавьте его путь в список possiblePaths в этом Jenkinsfile.
                                3. Временно укажите полный путь к python.exe вручную (например, "C:\\путь\\к\\python.exe").
                            ''')
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
                    "${env.PYTHON}" -m pip install -r requirements.txt
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
                        --testit-url=${TESTIT_URL} ^
                        --testit-private-token=${TESTIT_TOKEN} ^
                        --testit-project-id=${TESTIT_PROJECT_ID} ^
                        --testit-configuration-id=${TESTIT_CONFIG_ID} ^
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