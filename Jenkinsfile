pipeline {
    agent any
    
    parameters {
        string(name: 'STUDENT_NAME', defaultValue: 'Иванов Иван', description: 'ФИО студента')
        choice(name: 'ENVIRONMENT', choices: ['dev', 'staging', 'production'], description: 'Среда')
        booleanParam(name: 'RUN_TESTS', defaultValue: true, description: 'Запускать тесты')
    }
    
    environment {
        DOCKER_IMAGE = "greg2greg/student-app:${BUILD_NUMBER}"
        CONTAINER_NAME = "student-app-${ENVIRONMENT}"
        HOST_PORT = "${params.ENVIRONMENT == 'production' ? '80' : (params.ENVIRONMENT == 'staging' ? '8082' : '8081')}"
    }
    
    stages {
        stage('Checkout') {
            steps {
                git branch: 'main', url: 'https://github.com/grejeq/simple-python-app.git', credentialsId: 'github-credentials'
            }
        }
        
        stage('Tests') {
            when { expression { params.RUN_TESTS } }
            steps {
                sh '''
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                    python -m unittest test_app.py -v
                '''
            }
        }
        
        stage('Build and Push') {
            steps {
                script {
                    docker.withRegistry('', 'docker-hub-credentials') {
                        def customImage = docker.build("${DOCKER_IMAGE}")
                        customImage.push()
                    }
                }
            }
        }
        
        stage('Deploy to Dev/Staging') {
            when { expression { params.ENVIRONMENT != 'production' } }
            steps {
                sh "docker rm -f ${CONTAINER_NAME} || true"
                sh """
                    docker run -d --name ${CONTAINER_NAME} -p ${HOST_PORT}:5000 \
                    -e STUDENT_NAME='${params.STUDENT_NAME}' \
                    ${DOCKER_IMAGE}
                """
            }
        }
        
        stage('Approve Production') {
            when { expression { params.ENVIRONMENT == 'production' } }
            steps {
                input message: "Подтвердите развертывание в PRODUCTION?", ok: "Да, развернуть",
                      parameters:[string(name: 'PROD_VERSION', defaultValue: "v1.0.${BUILD_NUMBER}")]
            }
        }

        stage('Tag Release') {
            when { expression { params.ENVIRONMENT == 'production' } }
            steps {
                withCredentials([usernamePassword(credentialsId: 'github-credentials', passwordVariable: 'GIT_PASS', usernameVariable: 'GIT_USER')]) {
                    sh """
                        git config user.email "jenkins@ci.com"
                        git config user.name "Jenkins CI"
                        git tag -a \${PROD_VERSION} -m "Release \${PROD_VERSION}"
                        git push https://${GIT_USER}:${GIT_PASS}@github.com/${GIT_USER}/simple-python-app.git \${PROD_VERSION}
                    """
                }
            }
        }
        
        stage('Deploy to Production') {
            when { expression { params.ENVIRONMENT == 'production' } }
            steps {
                sh "docker rm -f ${CONTAINER_NAME} || true"
                sh "docker run -d --name ${CONTAINER_NAME} -p ${HOST_PORT}:5000 -e STUDENT_NAME='${params.STUDENT_NAME}' ${DOCKER_IMAGE}"
            }
        }
    }
    
    post {
        always {
            cleanWs()
        }
        success {
            echo " Пайплайн успешно выполнен для окружения ${params.ENVIRONMENT}!"
            
        }
        failure {
            echo " Ошибка пайплайна!"
        }
    }
}
