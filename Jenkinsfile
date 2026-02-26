stage('Check imports') {
    steps {
        script {
            docker.withRegistry('https://ghcr.io', 'github-token-for-docker') {
                bat """
                    docker run --rm -w /workspace ghcr.io/kellanius/box-for-jenkins:latest sh -c "
                        python -c 'import greenlet; print(greenlet.__version__)' &&
                        python -c 'from pydantic_core import __version__; print(__version__)' &&
                        python -c 'import allure; print(allure.__version__)' &&
                        python -c 'import playwright.sync_api; print(\"Playwright OK\")' ||
                        echo 'Some import failed'
                    "
                """
            }
        }
    }
}