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
                    def pythonPath = powershell(
                        returnStdout: true,
                        script: 'Get-Command python.exe -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Path'
                    ).trim()

                    if (pythonPath) {
                        env.PYTHON = pythonPath
                    } else {
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
                    "${env.PYTHON}" -m pip install pytest testit-pytest -r requirements.txt
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
                script {
                    // Формируем команду динамически
                    def testitArgs = "--testit"
                    if (params.TEST_RUN_ID) {
                        testitArgs += " --testit-test-run-id=${params.TEST_RUN_ID}"
                    }
                    if (params.TEST_PLAN_ID) {
                        testitArgs += " --testit-test-plan-id=${params.TEST_PLAN_ID}"
                    }

                    bat """
                        "${env.PYTHON}" -m pytest tests/ ${testitArgs}
                    """
                }
            }
        }

    post {
        always {
            echo '🏁 Сборка завершена. Результаты отправлены в Test IT.'
        }
    }
}