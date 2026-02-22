pipeline {
    agent any

    parameters {
        string(name: 'TEST_PLAN_ID', defaultValue: '', description: 'ID тест-плана из Test IT')
        string(name: 'TEST_RUN_ID', defaultValue: '', description: 'ID прогона из Test IT')
    }

    environment {
        PROJECT_ROOT = "%WORKSPACE%"
        VENV = "%WORKSPACE%\\venv"
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
                    echo "✅ Файл connection_config.ini успешно создан"
                    bat "type connection_config.ini"
                }
            }
        }

        stage('Setup VirtualEnv') {
            steps {
                echo '🔧 Создаём виртуальное окружение...'
                bat """
                    "C:\\Python314\\python.exe" -m venv venv
                    call venv\\Scripts\\activate.bat
                    python -m pip install --upgrade pip
                    pip uninstall testit-adapter-pytest -y
                    pip install testit-adapter-pytest==3.12.1
                    pip install pytest allure-pytest playwright faker
                    pip install -r requirements.txt
                    playwright install
                    echo "=== Проверка: плагин testit-adapter-pytest установлен ==="
                    pip show testit-adapter-pytest
                    echo "=== Создаём заглушку testit.py ==="
                    echo "from testit_adapter_pytest import *" > testit.py
                """
            }
        }

        stage('Clear pytest cache') {
            steps {
                bat 'if exist .pytest_cache rmdir /s /q .pytest_cache'
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
                        call venv\\Scripts\\activate.bat
                        set PYTHONPATH=%WORKSPACE%
                        echo "=== Проверка: какой Python используется ==="
                        where python
                        echo "=== Проверка: плагин testit-adapter-pytest доступен ==="
                        venv\\Scripts\\python.exe -m pytest --collect-only --testit 2>&1 | findstr /C:"tmsTestPlanId" || echo "Плагин не найден!"
                        echo "=== Запуск тестов ==="
                        venv\\Scripts\\python.exe -m pytest tests ${args}
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