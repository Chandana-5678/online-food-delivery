pipeline {
  agent any
  options { disableConcurrentBuilds(); timestamps(); timeout(time: 25, unit: 'MINUTES') }
  parameters {
    string(name: 'PUSH_COMMIT', defaultValue: '')
    string(name: 'DELIVERY_ID', defaultValue: '')
    booleanParam(name: 'REGISTRY_ENABLED', defaultValue: false)
  }
  environment { PATH = "/opt/jenkins-lab/venv/bin:/usr/local/bin:/usr/bin:/bin" }
  stages {
    stage('Project 1 - GitHub checkout and test') {
      steps {
        script {
          if (!(params.PUSH_COMMIT ==~ /[0-9a-f]{40}/)) { error('Expected signed push commit') }
          checkout([$class: 'GitSCM', branches: [[name: params.PUSH_COMMIT]],
            userRemoteConfigs: [[url: 'git@github.com:Chandana-5678/online-food-delivery.git', credentialsId: 'github-read']]])
        }
        sh 'test "$(git rev-parse HEAD)" = "$PUSH_COMMIT"; python -m unittest -v'
      }
    }
    stage('Build candidate image') {
      steps { sh 'python /opt/jenkins-lab/pipeline.py build' }
    }
    stage('Project 2 - Docker secure push') {
      when { expression { params.REGISTRY_ENABLED } }
      steps {
        withCredentials([usernamePassword(credentialsId: 'docker-hub', usernameVariable: 'HUB_USER', passwordVariable: 'HUB_PASSWORD')]) {
          sh 'python /opt/jenkins-lab/pipeline.py publish'
        }
      }
    }
    stage('Project 3 - Automatic staging deployment') {
      steps { sh 'python /opt/jenkins-lab/pipeline.py staging' }
    }
    stage('Project 4 - Ansible EC2 deployment') {
      steps {
        withCredentials([usernamePassword(credentialsId: 'docker-hub', usernameVariable: 'HUB_USER', passwordVariable: 'HUB_PASSWORD')]) {
          sh 'python /opt/jenkins-lab/pipeline.py ansible'
        }
      }
    }
    stage('Live verification') {
      steps { sh 'python /opt/jenkins-lab/pipeline.py verify' }
    }
  }
  post { always { archiveArtifacts artifacts: 'results/*', allowEmptyArchive: true } }
}
