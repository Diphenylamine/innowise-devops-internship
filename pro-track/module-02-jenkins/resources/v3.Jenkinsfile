pipeline {
    agent any

    stages {
        stage('Docker Check') {
            steps {
                sh 'docker ps'
            }
        }

        stage('Build Image') {
            steps {
                dir('pro-track/module-02-jenkins/resources/python') {
                    sh 'docker build -t my-app-jenkins:${BUILD_NUMBER} .'
                }
            }
        }
    }
}