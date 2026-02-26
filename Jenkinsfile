pipeline {
    agent any

    parameters {
        string(name: 'TEST_PLAN_ID', defaultValue: '', description: 'ID тест-плана из Test IT')
        string(name: 'TEST_RUN_ID', defaultValue: '', description: 'ID прогона из Test IT')
    }

    environment {
        // Переменные для Test IT (подставляются из credentials)
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
                            echo { > tms.config.json
                            echo   "url": "${URL}", >> tms.config.json
                            echo   "privateToken": "${TOKEN}", >> tms.config.json
                            echo   "projectId": "${PROJECT_ID}", >> tms.config.json
                            echo   "configurationId": "${CONFIG_ID}", >> tms.config.json
                            echo   "adapterMode": 0 >> tms.config.json
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

        stage('Filter tests by Test Run ID') {
            when { expression { params.TEST_RUN_ID != '' } }
            steps {
                script {
                    docker.withRegistry('https://ghcr.io', 'github-token-for-docker') {
                        docker.image('ghcr.io/kellanius/box-for-jenkins:latest').inside("-v ${WORKSPACE}:/workspace -w /workspace") {
                            sh """
                                echo "=== Получение списка тестов для прогона ${params.TEST_RUN_ID} ==="
                                testit autotests_filter \\
                                  --url \$TMS_URL \\
                                  --token \$TMS_PRIVATE_TOKEN \\
                                  --configuration-id \$TMS_CONFIGURATION_ID \\
                                  --testrun-id ${params.TEST_RUN_ID} \\
                                  --framework playwright \\
                                  --debug \\
                                  --output filter.txt > filter_debug.log 2>&1
                                echo "Команда завершилась с кодом \$?"
                                echo "=== Содержимое filter.txt (фильтр для pytest) ==="
                                cat filter.txt
                                echo "=== Содержимое filter_debug.log (для отладки) ==="
                                cat filter_debug.log
                            """
                        }
                    }
                }
            }
        }

        stage('Run Tests') {
            steps {
                script {
                    docker.withRegistry('https://ghcr.io', 'github-token-for-docker') {
                        docker.image('ghcr.io/kellanius/box-for-jenkins:latest').inside("-v ${WORKSPACE}:/workspace -w /workspace") {
                            sh """
                                echo "=== Диагностика переменных Test IT ==="
                                echo "TMS_ADAPTER_MODE=1"
                                echo "TMS_TEST_RUN_ID=${params.TEST_RUN_ID}"
                                echo "TMS_URL=\$TMS_URL"

                                export PYTHONPATH=/workspace
                                export TMS_ADAPTER_MODE=1
                                export TMS_TEST_RUN_ID=${params.TEST_RUN_ID}

                                echo "=== Запуск тестов, соответствующих фильтру (adapterMode=1) ==="
                                if [ -f filter.txt ]; then
                                    FILTER=\$(cat filter.txt | sed 's/\\\\ / /g; s/\\\\././g; s/|/ or /g')
                                    FILTER="(\$FILTER)"
                                    echo "Фильтр для -k: \$FILTER"
                                    pytest /workspace/tests -k "\$FILTER" -v --tb=short --alluredir=/workspace/allure-results --testit
                                else
                                    echo "Файл filter.txt не найден. Запуск всех тестов."
                                    pytest /workspace/tests -v --tb=short --alluredir=/workspace/allure-results --testit
                                fi

                                echo "=== Завершено. Код возврата: \$? ==="
                            """
                        }
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
                            curl -X POST "${TMS_URL}/api/v2/testRuns/${params.TEST_RUN_ID}/complete" \
                              -H "Authorization: PrivateToken ${TOKEN}" \
                              -H "Content-Type: application/json" \
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
                            curl -X POST "${TMS_URL}/api/v2/testRuns/${params.TEST_RUN_ID}/complete" \
                              -H "Authorization: PrivateToken ${TOKEN}" \
                              -H "Content-Type: application/json" \
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