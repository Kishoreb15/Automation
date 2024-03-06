pipeline {
    agent any

    triggers {
        cron('50 6,19 * * *')  // Schedule for 6:50 AM and 7:00 PM every day
    }

    stages {
        stage('Run Script') {
            steps {
                script {
                    sh 'python main.py'  // Use the correct command to run your Python script
                }
            }
        }
    }
}
