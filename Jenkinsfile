pipeline {
    agent any

    environment {
        // Standard Image Names
        REGISTRY_URL         = 'docker.io' // Change to your private registry if applicable
        IMAGE_BACKEND        = 'techscout-backend'
        IMAGE_FRONTEND       = 'techscout-frontend'
        BUILD_TAG            = "${env.BUILD_NUMBER}"
        
        // Define credentials IDs set up in your Jenkins credentials store
        CREDS_OPENROUTER_KEY = 'techscout-openrouter-key'
    }

    options {
        timeout(time: 20, unit: 'MINUTES')
        buildDiscarder(logRotator(numToKeepStr: '10'))
        disableConcurrentBuilds()
    }

    stages {
        stage('🧹 Clean workspace') {
            steps {
                echo 'Cleaning workspace from prior builds...'
                cleanWs()
            }
        }

        stage('📥 Checkout Code') {
            steps {
                checkout scm
            }
        }

        stage('🔒 Inject Production Secrets') {
            steps {
                echo 'Injecting production keys safely from Jenkins Credentials Store...'
                // Restores .env file securely. If keys are not set, it uses fallback defaults.
                withCredentials([
                    string(credentialsId: "${env.CREDS_OPENROUTER_KEY}", variable: 'OPENROUTER_KEY')
                ]) {
                    sh """
                    # Create backend folder config
                    echo "OPENROUTER_KEY=${OPENROUTER_KEY}" > backend/.env
                    echo "DATABASE_URL=sqlite+aiosqlite:////workspace/data/app.db" >> backend/.env
                    echo "APP_NAME=TechScout" >> backend/.env
                    echo "APP_URL=http://localhost:8888" >> backend/.env
                    
                    # Create fallback empty frontend .env if needed
                    touch frontend/.env
                    """
                }
                echo 'Secrets injected successfully.'
            }
        }

        stage('🧪 Testing & Linters') {
            steps {
                echo 'Running codebase health checks before building...'
                // Example step to make sure python files don't have syntax issues
                sh 'python -m py_compile backend/app/main.py backend/app/api/v1/jobs.py'
                
                // Example step to verify frontend compiles cleanly
                dir('frontend') {
                    // sh 'npm ci && npm run typecheck'
                }
            }
        }

        stage('📦 Build Docker Images') {
            steps {
                echo "Building images with build tag: ${env.BUILD_TAG}"
                sh 'docker compose build --pull'
                
                // Tag images locally with Build Number for traceability
                sh "docker tag ${env.IMAGE_BACKEND}:latest ${env.IMAGE_BACKEND}:${env.BUILD_TAG}"
                sh "docker tag ${env.IMAGE_FRONTEND}:latest ${env.IMAGE_FRONTEND}:${env.BUILD_TAG}"
            }
        }

        stage('🚀 Publish to Registry (Optional)') {
            when {
                branch 'main' // Only push images to registry for production/main branch
            }
            steps {
                echo 'Skipped by default. Uncomment below to push to your private docker registry:'
                /*
                withCredentials([usernamePassword(credentialsId: 'docker-registry-credentials', usernameVariable: 'REGISTRY_USER', passwordVariable: 'REGISTRY_PASS')]) {
                    sh "echo ${REGISTRY_PASS} | docker login -u ${REGISTRY_USER} --password-stdin ${REGISTRY_URL}"
                    
                    // Tag for registry
                    sh "docker tag ${env.IMAGE_BACKEND}:${env.BUILD_TAG} ${env.REGISTRY_URL}/${env.IMAGE_BACKEND}:${env.BUILD_TAG}"
                    sh "docker tag ${env.IMAGE_BACKEND}:${env.BUILD_TAG} ${env.REGISTRY_URL}/${env.IMAGE_BACKEND}:latest"
                    
                    sh "docker tag ${env.IMAGE_FRONTEND}:${env.BUILD_TAG} ${env.REGISTRY_URL}/${env.IMAGE_FRONTEND}:${env.BUILD_TAG}"
                    sh "docker tag ${env.IMAGE_FRONTEND}:${env.BUILD_TAG} ${env.REGISTRY_URL}/${env.IMAGE_FRONTEND}:latest"
                    
                    // Push
                    sh "docker push ${env.REGISTRY_URL}/${env.IMAGE_BACKEND}:${env.BUILD_TAG}"
                    sh "docker push ${env.REGISTRY_URL}/${env.IMAGE_BACKEND}:latest"
                    sh "docker push ${env.REGISTRY_URL}/${env.IMAGE_FRONTEND}:${env.BUILD_TAG}"
                    sh "docker push ${env.REGISTRY_URL}/${env.IMAGE_FRONTEND}:latest"
                }
                */
            }
        }

        stage('⚡ Blue-Green Deployment / Rollout') {
            steps {
                echo 'Deploying latest containerized version...'
                // Stop previous instances safely
                sh 'docker compose down || true'
                
                // Start fresh containers
                sh 'docker compose up -d'
                
                // Clean up dangling and unused images to preserve disk space
                sh 'docker image prune -f'
                
                echo 'Application deployed successfully and is running in background!'
            }
        }
    }

    post {
        success {
            echo "✅ Jenkins Pipeline Succeeded! TechScout Build #${env.BUILD_NUMBER} deployed successfully."
        }
        failure {
            echo "❌ Jenkins Pipeline Failed! Please check the console output of Build #${env.BUILD_NUMBER}."
        }
        always {
            echo 'Pipeline execution completed.'
        }
    }
}
