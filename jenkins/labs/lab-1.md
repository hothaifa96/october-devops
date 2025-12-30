# Jenkins assignments

setup:

- If you have created the **Jenkinsfile** on Github , it time to update the Devops Pipeline
- So go to Jenkins and update the Pipeline Definition section , change the Pipeline Script option to Pipeline Script from SCM
- Then select SCM as Git
- Add the Repo Clone HTTPS URL in **Repository URL** section
- For Credentials , Create Username and Password type of credentials with your GitHub email/password
- Update the Branch to Main

# **Task 1 - Jenkins Free Style Job Setup**

Setup the Jenkins Free Style Job to meet the below requirements:

- Create a new Free Style Jenkins Job and name it as **Docker-Verify**.
- Run Shell Command from inside the Jenkins Job to Verify the Docker Version on the Jenkins machine.

Hint:

```jsx
 **docker --version** 
```

# **Task 2 - Jenkins Free Style Job , Cron Setup**

Setup the Jenkins Free Style Job to meet the below requirements:

- Update your Free Style Jenkins Job **Docker-Verify**
- Set the job to run every minute on Jenkins

# **Task 3 - Jenkins Free Style Job , Parameters**

Setup the Jenkins Free Style Job to meet the below requirements:

- Update your Free Style Jenkins Job **Docker-Verify**
- Remove the cron from the job to avoid running it every minute.
- Configure your job as parameterized job , add choice section in your job.
- Under the choices section add two options , **docker** and **python.**
- Then update your execute shell command to get the version of package selected by the user.

# **Task 4 - Jenkins Declarative Pipeline , Docker Verify Stage Setup**

Setup the Jenkins Declarative Pipeline to meet the below requirements:

- Create a new Jenkins job of type **Pipeline**
- Name your Job as **Devops**
- Add single stage named as 'Docker-Verify'
- Setup the command under steps section **'docker --version'**
- Build the Pipeline to print the Docker Version in the output

# **Task 5 - Jenkins Declarative Pipeline -> Git Verify Stage Setup**

- Update your Jenkins Pipeline **Devops.**
- Add a new stage named as 'Git-Verify'
- Setup the command under steps section **'git --version'**
- Build the Pipeline to print the Docker Version and Git Version in the output

# **Task 6 Jenkins Declarative Pipeline -,Docker build**

Setup the GitHub Repo to meet the below requirements:

- Go to GutHub Repo
- Upload the attached Dockerfile onto your GitHub Repo
- Dockerfile:

```docker
From httpd
LABEL name="devops"
```

Setup/Update the Jenkins Declarative Pipeline to meet the below requirements:

- Update your JenkinsFile to add one more stage named as **'Docker-Build'**
- Inside the Steps section of stage **'Docker-Build'** add a **to build the image with environments as names and tag for the image**
- Then Run the DevOps Pipeline after Jenkinsfile is updated

# **Task 7 - Jenkins Declarative Pipeline , Docker Image Verify Stage**

- Update your JenkinsFile to add one more stage named as **'Docker-Image-Verify'**
- Inside the Steps section of stage **'Docker-Image-Verify'** add a command  **to show all the images filtered by the tagname env (the same name we had for the build)**
- Then Run the DevOps Pipeline after Jenkinsfile is updated

# **Task 8 - Jenkins Declarative Pipeline -> Jenkins Pre Defined Variables**

- Inside the Steps section of stage **'Docker-Build'** update the docker build command to use the Jenkins Build Number as tag value, So basically the tag value of our docker image will be always updated.
- Then Run the DevOps Pipeline after Jenkinsfile is updated

# --------------------------------
# **Task 10 - Jenkins Declarative Pipeline , Timeout**

Setup/Update the Jenkins Declarative Pipeline to meet the below requirements:

- Go to GitHub Repo to update the Jenkinsfile
- Inside the Steps section of stage **'Docker-Verify'** update the '**doker --version**' command with '**docker --version**' , basically we need to correct the command.
- Keep the retry value same to 3 Times
- Under the 'Docker-Verify' stage, Add one more section i.e. **timeout** with value 10 seconds and then add a command under the 'timeout' section '**sleep 30**'
- Once Jenkinsfile is updated, run the pipeline

# **Task 11 - Jenkins Declarative Pipeline -> Parallel Stage**

> Task - 18 : Jenkins Declarative Pipeline Setup - Jenkins Parallel (Intermediate Level)
> 

Setup/Update the Jenkins Declarative Pipeline to meet the below requirements:

- Go to GitHub Repo to update the Jenkinsfile
- Remove the timeout section from 'Docker-Verify' Stage
- Its time to shift both the stages 'Docker-Verify' and 'Git-Verify' in parallel
- So create a new stage 'Pre-Checks' and shift 'Docker-Verify' and 'Git-Verify' in parallel under the 'Pre-Checks' Stage
- Once Jenkinsfile is updated, run the pipeline

# **Task 12 - Jenkins Declarative Pipeline -> Options - skipDefaultCheckout**



Setup/Update the Jenkins Declarative Pipeline to meet the below requirements:

- Go to GitHub Repo to update the Jenkinsfile
- Update your Dockerfile and change the **Label name="devops"** value to **Label name="AutoPilot"**
- Add skipDefaultCheckout() at the pipeline level within the options section
- Add one more command within the 'Docker-Build' Stage after the docker build command i.e. **sh "sudo docker inspect ${Docker_Image_Name}:${env.BUILD_NUMBER}"**
- Once Jenkinsfile is updated run the Devops Pipeline

# **Task 13 - Jenkins Declarative Pipeline -> Options - buildDiscarder**



Setup/Update the Jenkins Declarative Pipeline to meet the below requirements:

- Go to GitHub Repo to update the Jenkinsfile
- Remove the skipDefaultCheckout() from the pipeline options section
- Add the '**buildDiscarder**' in the option section at pipeline level, with **numToKeepStr value as 1 ,** as we want to keep logs of only last 1 Build on our system
- Once Jenkinsfile is updated run the Devops Pipeline

# **Task 14 - Jenkins Declarative Pipeline -> When Condition**



Setup/Update the Jenkins Declarative Pipeline to meet the below requirements:

- Go to GitHub Repo to update the Jenkinsfile
- Remove 'sleep 30' command from the 'Docker-Verify' Stage Steps Section
- Add When Condition inside the 'Docker-Build' Stage , if branch name is 'test' then build the docker image else not.
- Use the given when condition:

**when {**

**expression {**

**return env.GIT_BRANCH == "origin/test"**

**}**

**}**

- Once Jenkinsfile is updated run the Devops Pipeline

# **Task 15 - Jenkins Declarative Pipeline -> When Condition**



Setup/Update the Jenkins Declarative Pipeline to meet the below requirements:

- Go to GitHub Repo to update the Jenkinsfile
- Add When Condition inside the 'Docker-Build' Stage , if branch name is 'main' then build the docker image else not.
- Use the given when condition:

**when {**

**expression {**

**return env.GIT_BRANCH == "origin/main"**

**}**

**}**

- Once Jenkinsfile is updated run the Devops Pipeline

# **Task 16 - Jenkins Declarative Pipeline -> Deploy Stage**



Setup/Update the Jenkins Declarative Pipeline to meet the below requirements:

- Go to GitHub Repo to update the Jenkinsfile
- Add a new Stage 'Docker-Deploy'
- Under the steps section add the command **sh "sudo docker run -itd -p 80:80 ${Docker_Image_Name}:${env.BUILD_NUMBER}"**
- Add one more command under the 'Docker-Deploy' stage **sh "sudo docker ps"**
- Once Jenkinsfile is updated run the Devops Pipeline

# **Task 17 - Jenkins Declarative Pipeline -> Add CleanUp Stage Before Deploy**



Setup/Update the Jenkins Declarative Pipeline to meet the below requirements:

- Go to GitHub Repo to update the Jenkinsfile
- Add a new Stage 'Docker-CleanUp' before 'Docker-Deploy' Stage.
- Under the steps section add the command **sh 'sudo docker rm -f \$(sudo docker ps -a -q) 2> /dev/null || true'** to cleanup all the containers from Jenkins Machine before deploying any new container
- Once Jenkinsfile is updated run the Devops Pipeline

# **Task 18 - Jenkins Declarative Pipeline -> Manual Approvals**



Setup/Update the Jenkins Declarative Pipeline to meet the below requirements:

- Go to GitHub Repo to update the Jenkinsfile
- Add a manual approval on 'Docker-Deploy' stage, like it should ask the user if user wants to deploy the docker or not
- Once Jenkinsfile is updated run the Devops Pipeline

Hint: User input inside the stage

input

{

message "Do you want to proceed for deployment ?"

}

# **Task 19 - Jenkins Declarative Pipeline -> Add CleanUp Stage**



Setup/Update the Jenkins Declarative Pipeline to meet the below requirements:

- Go to GitHub Repo to update the Jenkinsfile
- Add a new Stage 'Docker-Images-CleanUp' after 'Docker-Deploy' Stage.
- Under the steps section add the command **sh 'sudo docker image prune -af'** to cleanup all unused docker images from local system
- Once Jenkinsfile is updated run the Devops Pipeline

# **Task 20 - Jenkins Declarative Pipeline -> Post**



Setup/Update the Jenkins Declarative Pipeline to meet the below requirements:

- Go to GitHub Repo to update the Jenkinsfile
- Add a new post section in your pipeline 'always' , so that it must be triggered every time
- Add **sh 'sudo docker images'** , command inside the always post section
- Once Jenkinsfile is updated run the Devops Pipeline

# **Task 21 - Jenkins Declarative Pipeline -> Post**



Setup/Update the Jenkins Declarative Pipeline to meet the below requirements:

- Go to GitHub Repo to update the Jenkinsfile
- Add a new post section in your pipeline 'aborted' , so that it must be triggered if the current Pipeline run has an "aborted" status
- Add **sh 'sudo docker ps'** , command inside the aborted post section
- Once Jenkinsfile is updated run the Devops Pipeline

# **Task 22 - Jenkins Declarative Pipeline -> Post**



Setup/Update the Jenkins Declarative Pipeline to meet the below requirements:

- Go to GitHub Repo to update the Jenkinsfile
- Update your 'Docker-Build' Stage command **"sh sudo docker build -t ${Docker_Image_Name}:${env.BUILD_NUMBER} ."** to the new command **sh "sudo dockers builds -t ${Docker_Image_Name}:${env.BUILD_NUMBER} ."**
- Add a new post section in your pipeline 'failure' , so that it must be triggered if the current Pipeline run has an failed status
- Add **sh 'sudo docker rm -f \$(sudo docker ps -a -q) 2> /dev/null || true'** , command inside the failure post section
- Once Jenkinsfile is updated run the Devops Pipeline

# **Task 23 - Jenkins Declarative Pipeline -> Post**



Setup/Update the Jenkins Declarative Pipeline to meet the below requirements:

- Go to GitHub Repo to update the Jenkinsfile
- Update your 'Docker-Build' Stage command **"sh sudo dockers builds -t ${Docker_Image_Name}:${env.BUILD_NUMBER} ."** to the new command **sh "sudo docker build -t ${Docker_Image_Name}:${env.BUILD_NUMBER} ."**
- Add a new post action in your pipeline 'success' , so that it must be triggered if the current Pipeline run has an success status
- Add **sh 'curl localhost'** , command inside the success post action
- Once Jenkinsfile is updated run the Devops Pipeline

# **Task 24 - Jenkins Declarative Pipeline -> Post**



Setup/Update the Jenkins Declarative Pipeline to meet the below requirements:

- Go to GitHub Repo to update the Jenkinsfile
- Remove the 'Docker-Images-CleanUp' Stage from JenkinsFile
- Add a new post action in your pipeline 'cleanup' , so that it must be triggered after every post action/condition has been evaluated
- Add **sh 'sudo docker image prune -af'** , command inside the cleanup post action
- Once Jenkinsfile is updated run the Devops Pipeline

# **Task 25 - Jenkins Declarative Pipeline -> Setup ECR Repo**


Setup the AWS ECR Repository to meet the below requirements:

- As of now we were saving the docker image on local Jenkins machine , but now we need to Setup a Repo to upload the Docker image to remote Repository.
- Go to AWS Account Console.
- Search for ECR in the search box -> Select Elastic Container Registry
- Click on Get Started under the Create a repository



- Add the name for your repository as "my-jenkins-project"
- Scroll Down and Click on Create Repository

# **Task 26 - Jenkins Declarative Pipeline -> Create AWS IAM Role**



Setup the AWS IAM to meet the below requirements:

- Since we are planning to upload the Docker Image from Jenkins machine to ECR Repo. , we need to design a Role in AWS (basically to allow Jenkins machine to connect with ECR) , so we need to design a role first then we will attach the same on the Jenkins machine in the next question.
- Go to AWS Account Console.
- Search for IAM -> Select IAM
- Select Roles Option from left side menu
- Select Create Role
- Select AWS Service -> Under Use Case -> Select EC2 -> Click on Next


- Search for Permission "AmazonEC2ContainerRegistryFullAccess" , select the permission and click next
- Add Role Name as "Jenkins-ECR-Role" -> Scroll Down and Click on Create Role

# **Task 27 - Jenkins Declarative Pipeline -> Attach AWS IAM Role to EC2**


Setup the AWS EC2 to meet the below requirements:

- Now we need to attach the IAM Role with Jenkins EC2 Machine to allow the machine to access the ECR Repo.
- Go to AWS Account Console.
- Search for EC2 -> Select EC2
- Select Instance from left menu
- Select Jenkins EC2 -> Click on Actions -> Select Security -> Select Modify IAM Role


- Select "Jenkins-ECR-Role" from Drop Down menu , Click on Update IAM Role

# **Task 28 - Jenkins Declarative Pipeline -> Build Stage Integration with ECR**



Setup/Update the Jenkins Declarative Pipeline to meet the below requirements:

- Its time to Integrate the Jenkins Pipeline with ECR Repo.
- Go to AWS Console -> Go to ECR -> Select your Repo. -> Click on View push commands
- Go to GitHub Repo to update the Jenkinsfile
- Update your 'Docker-Build' Stage to ECR Integration with Build Stage
- Remove all commands from '**Docker-Build**' Stage/Steps Section and Add your own push commands , below sample commands I am adding in my **Docker-Build** Stage:
    - **sh 'aws ecr get-login-password --region us-east-1 | sudo docker login --username AWS --password-stdin 719146002784.dkr.ecr.us-east-1.amazonaws.com'**
    - **sh 'sudo docker build -t my-jenkins-project .'**
    - **sh 'sudo docker tag my-jenkins-project:latest 719146002784.dkr.ecr.us-east-1.amazonaws.com/my-jenkins-project:latest'**
    - **sh 'sudo docker push 719146002784.dkr.ecr.us-east-1.amazonaws.com/my-jenkins-project:latest'**
- Make Sure you must add **sudo** while calling docker in the above commands and you must copy your own commands from ECR Push commands section
- Once Jenkinsfile is updated run the Devops Pipeline , it will fail for deployment section which we will cover in the next question

# **Task 29 - Jenkins Declarative Pipeline -> Deploy Stage Integration with ECR**



Setup/Update the Jenkins Declarative Pipeline to meet the below requirements:

- Go to GitHub Repo to update the Jenkinsfile
- Update your 'Docker-Deploy' Stage for ECR Integration with Deploy Stage
- **Remove all commands from 'Docker-Deploy' Stage/Steps Section** and Add below commands in Docker-Deploy Stage:
    - sh "sudo docker run -itd -p 80:80 YOUR_IMAGE_URI"
    - sh "sudo docker ps"
- You can copy your Image URI from ECR Repo -> Click on Project -> Click on Latest Image -> Copy URI
- Once Jenkinsfile is updated run the Devops Pipeline