// Jenkins declarative pipeline — same gates as the GitHub Actions workflow.
// Runs unit tests, generates a suite, and enforces the coverage standard
// (generate/coverage --strict exit 2 below standard -> fails the build).
pipeline {
    agent any
    options { timestamps() }

    stages {
        stage('Setup') {
            steps {
                sh '''
                    python -m venv .venv
                    . .venv/bin/activate
                    pip install --upgrade pip
                    pip install -e ".[dev]"
                '''
            }
        }
        stage('Unit tests') {
            steps {
                sh '. .venv/bin/activate && pytest -q'
            }
        }
        stage('Coverage gate') {
            steps {
                sh '''
                    . .venv/bin/activate
                    python -m test_case_generator generate \
                        --feature "password reset email" --out-dir generated --strict
                    python -m test_case_generator coverage --prompts examples/generated --strict
                '''
            }
        }
    }

    post {
        always {
            archiveArtifacts artifacts: 'generated/*.yaml', allowEmptyArchive: true
        }
    }
}
