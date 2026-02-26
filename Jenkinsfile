pipeline {
    agent any

    parameters {
        string(name: 'TEST_PLAN_ID', defaultValue: '', description: 'ID тест-плана из Test IT')
        string(name: 'TEST_RUN_ID', defaultValue: '', description: 'ID прогона из Test IT')
    }

    environment {
        TMS_URL = credentials('testit-url')
        TMS_PRIVATE_TOKEN = credentials('testit-token')
        TMS_PROJECT_ID = credentials('testit-project-id')
        TMS_CONFIGURATION_ID = credentials('testit-config-id')
        SUPER_ADMIN_USERNAME = credentials('super-admin-email')
        SUPER_ADMIN_PASSWORD = credentials('super-admin-password')
    }

    stages {
        stage('Checkout') {
            steps {
                echo 'Клонируем репозиторий...'
                git branch: 'main',
                    url: 'https://github.com/kellanius/Cinescope.git',
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

        stage('Clear pytest cache') {
            steps {
                bat 'if exist .pytest_cache rmdir /s /q .pytest_cache'
            }
        }

        stage('Pull Docker image') {
            steps {
                script {
                    docker.withRegistry('https://ghcr.io', 'github-token-for-docker') {
                        bat "docker pull ghcr.io/kellanius/box-for-jenkins:latest"
                    }
                }
            }
        }

        // ЭТАП ПРОВЕРКИ ИМПОРТОВ (исправлен, без лишних steps)
        stage('Check imports') {
            steps {
                script {
                    docker.withRegistry('https://ghcr.io', 'github-token-for-docker') {
                        bat 'docker run --rm -w /workspace ghcr.io/kellanius/box-for-jenkins:latest sh -c "python -c \'import greenlet, pydantic_core, allure, playwright.sync_api; print(\\"greenlet:\\", greenlet.__version__); print(\\"pydantic_core:\\", pydantic_core.__version__); print(\\"allure imported successfully\\"); print(\\"playwright.sync_api imported successfully\\"); print(\\"All imports successful\\")\'"'
                    }
                }
            }
        }

        stage('Filter tests by Test Run ID') {
            when { expression { params.TEST_RUN_ID != '' } }
            steps {
                script {
                    docker.withRegistry('https://ghcr.io', 'github-token-for-docker') {
                        bat """
                            docker run --rm -v ${WORKSPACE}:/workspace -w /workspace ^
                              -e TMS_URL=%TMS_URL% ^
                              -e TMS_PRIVATE_TOKEN=%TMS_PRIVATE_TOKEN% ^
                              -e TMS_CONFIGURATION_ID=%TMS_CONFIGURATION_ID% ^
                              -e TEST_RUN_ID=${params.TEST_RUN_ID} ^
                              ghcr.io/kellanius/box-for-jenkins:latest ^
                              sh -c "testit autotests_filter --url \\\$TMS_URL --token \\\$TMS_PRIVATE_TOKEN --configuration-id \\\$TMS_CONFIGURATION_ID --testrun-id \\\$TEST_RUN_ID --framework playwright --debug --output filter.txt > filter_debug.log 2>&1; cat filter.txt; cat filter_debug.log"
                        """
                    }
                }
            }
        }

        stage('Run Tests') {
            steps {
                script {
                    docker.withRegistry('https://ghcr.io', 'github-token-for-docker') {
                        bat """
                            docker run --rm -v %WORKSPACE%:/workspace -w /workspace ^
                              -e TMS_URL=%TMS_URL% ^
                              -e TMS_PRIVATE_TOKEN=%TMS_PRIVATE_TOKEN% ^
                              -e TMS_CONFIGURATION_ID=%TMS_CONFIGURATION_ID% ^
                              -e TMS_ADAPTER_MODE=1 ^
                              -e TMS_TEST_RUN_ID=${params.TEST_RUN_ID} ^
                              -e SUPER_ADMIN_USERNAME=%SUPER_ADMIN_USERNAME% ^
                              -e SUPER_ADMIN_PASSWORD=%SUPER_ADMIN_PASSWORD% ^
                              ghcr.io/kellanius/box-for-jenkins:latest ^
                              python -c "import os, subprocess, sys; filter_file = '/workspace/filter.txt'; test_dir = '/workspace/tests'; allure_dir = '/workspace/allure-results'; cmd = [sys.executable, '-m', 'pytest', test_dir]; if os.path.exists(filter_file): with open(filter_file) as f: raw_filter = f.read().strip(); clean_filter = raw_filter.replace('\\\\\\\\ ', ' ').replace('\\\\\\\\.', '.').replace('|', ' or '); filter_expr = '(' + clean_filter + ')'; print('Filter for -k:', filter_expr); cmd.extend(['-k', filter_expr, '-v', '--tb=short', '--alluredir=' + allure_dir, '--testit']); else: print('filter.txt not found. Running all tests.'); cmd.extend(['-v', '--tb=short', '--alluredir=' + allure_dir, '--testit']); sys.exit(subprocess.run(cmd).returncode)"
                        """
                    }
                }
            }
        }
    } // stages

    post {
        success {
            script {
                if (params.TEST_RUN_ID) {
                    echo "Сборка успешна. Завершаем прогон ${params.TEST_RUN_ID} в Test IT как Completed."
                    withCredentials([string(credentialsId: 'testit-token', variable: 'TOKEN')]) {
                        bat """
                            curl -X POST "${TMS_URL}/api/v2/testRuns/${params.TEST_RUN_ID}/complete" ^
                              -H "Authorization: PrivateToken ${TOKEN}" ^
                              -H "Content-Type: application/json" ^
                              -d "{\\"status\\": \\"Completed\\", \\"message\\": \\"Pipeline succeeded.\\"}"
                        """
                    }
                }
            }
        }
        failure {
            script {
                if (params.TEST_RUN_ID) {
                    echo "Пайплайн упал. Завершаем прогон ${params.TEST_RUN_ID} в Test IT как Failed"
                    withCredentials([string(credentialsId: 'testit-token', variable: 'TOKEN')]) {
                        bat """
                            curl -X POST "${TMS_URL}/api/v2/testRuns/${params.TEST_RUN_ID}/complete" ^
                              -H "Authorization: PrivateToken ${TOKEN}" ^
                              -H "Content-Type: application/json" ^
                              -d "{\\"status\\": \\"Failed\\", \\"message\\": \\"Pipeline failed. Check Jenkins logs for details. Build: ${env.BUILD_URL}\\"}"
                        """
                    }
                }
            }
        }
        always {
            echo '🏁 Сборка завершена.'
        }
    }
}