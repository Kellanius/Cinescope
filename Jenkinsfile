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
        // --- НОВОЕ: Переменные для Test IT (будут подставлены из credentials) ---
        TMS_URL = credentials('testit-url')
        TMS_PRIVATE_TOKEN = credentials('testit-token')
        TMS_PROJECT_ID = credentials('testit-project-id')
        TMS_CONFIGURATION_ID = credentials('testit-config-id')
        // Переменная для пути к фильтру
        FILTER_FILE = "%WORKSPACE%\\testit-filter.txt"
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

         // --- ЭТОТ ЭТАП БОЛЬШЕ НЕ НУЖЕН В ПРЕЖНЕМ ВИДЕ, НО МЫ ЕГО ПЕРЕДЕЛАЕМ ---
        stage('Create TestIT Config') {
            steps {
                withCredentials([
                    string(credentialsId: 'testit-url', variable: 'URL'),
                    string(credentialsId: 'testit-token', variable: 'TOKEN'),
                    string(credentialsId: 'testit-project-id', variable: 'PROJECT_ID'),
                    string(credentialsId: 'testit-config-id', variable: 'CONFIG_ID')
                ]) {
                    script {
                        // Теперь мы создаем конфиг для Playwright адаптера
                        bat """
                            echo { > tms.config.json
                            echo   "url": "${URL}", >> tms.config.json
                            echo   "privateToken": "${TOKEN}", >> tms.config.json
                            echo   "projectId": "${PROJECT_ID}", >> tms.config.json
                            echo   "configurationId": "${CONFIG_ID}", >> tms.config.json
                            echo   "adapterMode": 1 >> tms.config.json
                            echo } >> tms.config.json
                        """
                        echo "✅ Файл tms.config.json успешно создан"
                        bat "type tms.config.json"
                    }
                }
            }
        }

    stage('Setup VirtualEnv') {
        steps {
            echo '🔧 Создаём виртуальное окружение...'
            bat """
                echo "=== Текущий PATH ==="
                echo %PATH%
                echo "=== Проверка Node.js ==="
                where node

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

                echo "=== Установка testit-cli (если ещё нет) ==="
                pip install testit-cli || exit /b 1

                echo "=== Установка testit-adapter-playwright через npm ==="
                :: Проверяем наличие Node.js
                where node || (echo Node.js not found && exit /b 1)
                npm install -g testit-adapter-playwright

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
                pip show testit-api-client testit-python-commons testit-adapter-pytest testit-cli
            """
        }
    }

        stage('Clear pytest cache') {
            steps {
                bat 'if exist .pytest_cache rmdir /s /q .pytest_cache'
            }
        }

        // --- НОВЫЙ ЭТАП: Фильтрация тестов с помощью Test IT CLI ---
        stage('Filter tests by Test Run ID') {
            when {
                expression { params.TEST_RUN_ID != '' }
            }
            steps {
                bat """
                    call venv\\Scripts\\activate.bat
                    echo "=== Получение списка тестов для прогона ${params.TEST_RUN_ID} ==="
                    testit autotests_filter ^
                      --url %TMS_URL% ^
                      --token %TMS_PRIVATE_TOKEN% ^
                      --configuration-id %TMS_CONFIGURATION_ID% ^
                      --testrun-id ${params.TEST_RUN_ID} ^
                      --framework playwright ^
                      --debug ^
                      --output %FILTER_FILE%
                    echo "Команда завершилась с кодом %ERRORLEVEL%"
                    if exist %FILTER_FILE% (
                        echo "=== Содержимое фильтра ==="
                        type %FILTER_FILE%
                    ) else (
                        echo "Файл фильтра не создан"
                    )
                """
            }
        }

        stage('Run Tests') {
            steps {
                bat """
                    call venv\\Scripts\\activate.bat
                    set PYTHONPATH=%WORKSPACE%
                    set TMS_ADAPTER_MODE=1
                    set TMS_TEST_RUN_ID=${params.TEST_RUN_ID}

                    echo "=== Запуск тестов, соответствующих фильтру ==="
                    :: Преобразуем содержимое filter.txt в строку для ключа -k
                    :: Удаляем пустые строки и объединяем через or
                    set /p FILTER=<%FILTER_FILE%
                    set FILTER=%FILTER: =%
                    python -m pytest tests/ -k "%FILTER%" -v --tb=short --alluredir=allure-results
                """
            }
        }
    }

    post {
        always {
            echo '🏁 Сборка завершена.'
        }
    }
}