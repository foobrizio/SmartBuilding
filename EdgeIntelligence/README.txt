INSTRUCTION FOR RUNNING THE APPLICATION IN IDE

- Run the virtual environment running the following command in a terminal inside the project directory -> " venv/Scripts/activate "
- Inside the virtual environment, it's possible to start the whole application running the _main_.py file, or the single file separately (of course the training has to be executed in order to execute the prediction)
- Before running the training, through the _main_, make sure that in the tfconfig.json file, the key trainingExecutions is set to trainingExecutions



INSTRUCTION FOR BUILDING THE APPLICATION THROUGH DOCKER

- Please note that the first time, will be created an image in which the application is burned. After this, it's possible to run the application through a docker container based on the image
- Open Docker on your pc
- Check the requirements.txt file and modify it based on the comments in it, given the target platform for the application (arm64/amd64)
- Check the Dockerfile and modify it based on the comments in it, given the target platform for the application (arm64/amd64)
- If you want the smartBuildingResources to be accessible from the external of the container, move the folder outside the project directory, it will be mounted later as an external docker volume. Otherwise, leave it inside the directory
- Open a terminal inside the project directory and run the following command: " docker buildx build --platform linux/arm64/v8,linux/amd64 --tag your-username/image-name:tag-name . "
    - EXAMPLE -> docker buildx build --platform linux/arm64/v8,linux/amd64 --tag senjudocker/smartbuilding:version2.1_arm64 .
- When finished, an image will be created and a container could be run with the command: " sudo docker run -it yor-username/image-name:tag-name "
    - EXAMPLE -> docker run -it senjudocker/smartbuilding:version2.1_arm64
- If you want to run the container mounting the virtual environment, run the command: " sudo docker run -it -v "path-of-the-folder/smartBuildingResources":/path-to-be-put-inside-container your-username/image-name:tag-name
    - EXAMPLE -> sudo docker run -it -v "$(pwd)/smartBuildingResources":/app/smartBuildingResources senjudocker/smartbuilding:version2.1_arm64



INSTRUCTION TO RUN UTILIZING THE ALREADY CREATED IMAGE
- Open Docker on yout pc
- Pull the image with the following command: " docker pull senjudocker/smartbuilding:version2.1_arm64 " or " docker pull senjudocker/smartbuilding:version2.1_amd64 " based on the desired platform
- Dowload the smartBuildingResources folder by the following link -> https://drive.google.com/drive/folders/1ErJSDRphtThMJAt3POhbnrl6wBeAjPMA?usp=sharing
- Run the container mounting the virtual environmen: " docker run -it -v "path-of-the-folder/smartBuildingResources":/app/smartBuildingResources senjudocker/smartbuilding:version2.1_arm64 "