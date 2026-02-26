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

        stage('Filter tests by Test Run ID') {
            when { expression { params.TEST_RUN_ID != '' } }
            steps {
                script {
                    bat """
                        docker run --rm ^
                          -v "${WORKSPACE}:/workspace" ^
                          -w /workspace ^
                          -e TMS_URL=%TMS_URL% ^
                          -e TMS_PRIVATE_TOKEN=%TMS_PRIVATE_TOKEN% ^
                          -e TMS_CONFIGURATION_ID=%TMS_CONFIGURATION_ID% ^
                          -e TEST_RUN_ID=${params.TEST_RUN_ID} ^
                          ghcr.io/kellanius/box-for-jenkins:latest ^
                          sh -c "testit autotests_filter --url \\$TMS_URL --token \\$TMS_PRIVATE_TOKEN --configuration-id \\$TMS_CONFIGURATION_ID --testrun-id \\$TEST_RUN_ID --framework playwright --debug --output filter.txt > filter_debug.log 2>&1; cat filter.txt; cat filter_debug.log"
                    """
                }
            }
        }

        stage('Run Tests') {
            steps {
                script {
                    bat """
                        docker run --rm ^
                          -v "${WORKSPACE}:/workspace" ^
                          -w /workspace ^
                          -e TMS_URL=%TMS_URL% ^
                          -e TMS_PRIVATE_TOKEN=%TMS_PRIVATE_TOKEN% ^
                          -e TMS_CONFIGURATION_ID=%TMS_CONFIGURATION_ID% ^
                          -e TMS_ADAPTER_MODE=1 ^
                          -e TMS_TEST_RUN_ID=${params.TEST_RUN_ID} ^
                          -e SUPER_ADMIN_USERNAME=%SUPER_ADMIN_USERNAME% ^
                          -e SUPER_ADMIN_PASSWORD=%SUPER_ADMIN_PASSWORD% ^
                          ghcr.io/kellanius/box-for-jenkins:latest ^
                          sh -c "if [ -f filter.txt ]; then pytest /workspace/tests -k \"\\\$(cat filter.txt | sed 's/\\\\\\\\ / /g; s/\\\\\\\\././g; s/|/ or /g' | sed 's/.*/(&)/')\" -v --tb=short --alluredir=/workspace/allure-results --testit; else pytest /workspace/tests -v --tb=short --alluredir=/workspace/allure-results --testit; fi"
                    """
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