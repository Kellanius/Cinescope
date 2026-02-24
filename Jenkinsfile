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
        }

        stage('Setup VirtualEnv') {
            steps {
                echo '🔧 Создаём виртуальное окружение...'
                bat """
                    "%PYTHON%" -m venv venv
                    call venv\\Scripts\\activate.bat
                    python -m pip install --upgrade pip

                    :: Удаляем старую заглушку testit.py, если она есть
                    if exist testit.py del testit.py

                    echo "=== Удаление старых версий testit-пакетов ==="
                    pip uninstall testit-adapter-pytest testit-python-commons testit-api-client -y

                    echo "=== Установка совместимых версий для Test IT 5.6 ==="
                    pip install testit-api-client || exit /b 1
                    pip install testit-python-commons || exit /b 1
                    pip install testit-adapter-pytest || exit /b 1

                    echo "=== Установка остальных зависимостей ==="
                    pip install -r requirements.txt
                    pip install allure-pytest playwright faker
                    playwright install

                    echo "=== Переустановка greenlet для устранения проблем с импортом ==="
                    pip uninstall greenlet -y
                    pip install greenlet==3.3.2 --force-reinstall --no-cache-dir
                    python -c "import greenlet; print('✅ greenlet imported successfully')" || (echo "❌ Ошибка импорта greenlet" && exit 1)

                    echo "=== Переустановка pydantic и pydantic-core ==="
                    pip uninstall pydantic pydantic-core -y
                    pip install pydantic==2.12.5 --force-reinstall --no-cache-dir
                    pip install pydantic-core==2.41.5 --force-reinstall --no-cache-dir
                    python -c "from pydantic_core import __version__; print('✅ pydantic-core imported successfully')" || (echo "❌ Ошибка импорта pydantic-core" && exit 1)

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

                    // --- ЭТО КЛЮЧЕВОЙ МОМЕНТ ---
                    // Мы передаем testRunId из параметра сборки.
                    // Именно это значение Test IT присылает при запуске из UI.
                    if (params.TEST_RUN_ID) {
                        args += " --tmsTestRunId=${params.TEST_RUN_ID}"
                        echo "Будет использован testRunId: ${params.TEST_RUN_ID}"
                    } else {
                        // Если TEST_RUN_ID не передан (например, ручной запуск), то работать не будет.
                        // Можно либо упасть с ошибкой, либо переключиться на режим 2.
                        // Но для UI он обязан быть.
                        error "Параметр TEST_RUN_ID не задан. Для запуска из UI он обязателен."
                    }
                    
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
                        echo "=== Проверка: модуль testit доступен ==="
                        python -c "import testit; print('✅ testit module loaded, attributes:', dir(testit))" || (echo "❌ Модуль testit не найден!" && exit 1)
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