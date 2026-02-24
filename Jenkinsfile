pipeline {
    agent any

    parameters {
        string(name: 'TEST_PLAN_ID', defaultValue: '', description: 'ID тест-плана из Test IT')
        string(name: 'TEST_RUN_ID', defaultValue: '', description: 'ID прогона из Test IT')
    }

    environment {
        PYTHON = "C:\\python312\\python.exe"
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
                    script {
                        def testPlanId = params.TEST_PLAN_ID ?: ''
                        bat """
                            echo [testit] > connection_config.ini
                            echo url = %URL% >> connection_config.ini
                            echo privateToken = %TOKEN% >> connection_config.ini
                            echo projectId = %PROJECT_ID% >> connection_config.ini
                            echo configurationId = %CONFIG_ID% >> connection_config.ini
                            echo adapterMode = 0 >> connection_config.ini
                        """
                        if (testPlanId) {
                            bat """
                                echo testPlanId = ${testPlanId} >> connection_config.ini
                            """
                        }
                        echo "✅ Файл connection_config.ini успешно создан"
                        bat "type connection_config.ini"
                    }
                }
            }
        }

        stage('Setup VirtualEnv') {
            steps {
                echo '🔧 Создаём виртуальное окружение...'
                bat """
                    "%PYTHON%" -m venv venv
                    call venv\\Scripts\\activate.bat
                    python -m pip install --upgrade pip

                    echo "=== Удаление старых версий testit-пакетов ==="
                    pip uninstall testit-adapter-pytest testit-python-commons testit-api-client -y

                    echo "=== Установка совместимых версий для Test IT 5.6 ==="
                    pip install testit-api-client==7.0.0 || exit /b 1
                    pip install testit-python-commons==3.11.2 || exit /b 1
                    pip install testit-adapter-pytest==3.11.2 || exit /b 1

                    echo "=== Установка остальных зависимостей ==="
                    pip install -r requirements.txt
                    pip install allure-pytest playwright faker
                    playwright install

                    echo "=== Проверка установленных версий ==="
                    pip show testit-api-client testit-python-commons testit-adapter-pytest
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

                    // tmsTestRunId поддерживается как аргумент командной строки
                    if (params.TEST_RUN_ID) {
                        args += " --tmsTestRunId=${params.TEST_RUN_ID}"
                    }
                    // tmsTestPlanId НЕ поддерживается как аргумент командной строки в версии 3.12.1
                    // Передается через connection_config.ini в stage 'Create TestIT Config'

                    def testRunId = params.TEST_RUN_ID ?: ''
                    def testPlanId = params.TEST_PLAN_ID ?: ''
                    
                    bat """
                        call venv\\Scripts\\activate.bat
                        set PYTHONPATH=%WORKSPACE%
                        echo "=== Проверка: какой Python используется ==="
                        where python
                        echo "=== Проверка: плагин testit-adapter-pytest установлен ==="
                        venv\\Scripts\\pip.exe show testit-adapter-pytest
                        echo "=== Проверка: доступность плагина через импорт ==="
                        venv\\Scripts\\python.exe -c "import testit_adapter_pytest; print('Plugin imported OK')" || echo "Plugin import failed!"
                        echo "=== Проверка: pytest видит опции плагина ==="
                        venv\\Scripts\\python.exe -m pytest --help 2>&1 | findstr /C:"tms" || echo "Плагин testit не найден в списке опций pytest!"
                        echo "=== Важно: tmsTestPlanId передается через connection_config.ini, а не через CLI аргумент ==="
                        echo "=== Проверка: файл connection_config.ini существует ==="
                        if exist connection_config.ini (
                            type connection_config.ini
                        ) else (
                            echo ОШИБКА: файл connection_config.ini не найден!
                        )
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