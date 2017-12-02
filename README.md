## A gist of the application!! ##
Machine learning is one of the fastest-growing and most exciting fields out there, and deep learning represents its true bleeding edge. ChessBrain ​is a web application that leverages deep learning and websockets to accomplish a complete solution for chess enthusiasts. What we are going to accomplish in this project is to build a web platform which will be able to load a game of chess from any given image that might contain a still frame of a chess board. This platform will enable players to set up a chess board without the hassle of moving the pieces and setting it up yourself. Platform will feature a chess engine for a solo play and will also support multiplayer.

## How does it work? ##

The client-side app uploads a snapshot containing chess. The API.... to do here



## Installation Instructions ##

* Go to the 'Setup' directory.
    - Open the Terminal as root user
    
    - Execute the script **install.sh**. This will install the Docker and NodeJs pre-requisites to your system and create an image called 'virtual_machine' inside the Docker. DockerVM may take around 20 to 30 minutes depending on your internet connection.
    
    - Once the Install script executes successfully, copy the folder named 'API' to your desired path.
    
    - Open app.js in the API folder and set the variable values as follows.
    
    	1. **timeout_value**: The time in seconds till which the API should wait for the output of the code before generating an "Execution Timed Out" message.
        2. **port**: The port on which the server will listen, the default port is 80.
        
    - To test the installation, open a new terminal windows, cd to the API folder and type the following command
	```
    $ npm install .
    ```
	to install all needed nodejs modules, followed by
	
    ```
    $ sudo nodejs app.js
    ```
    - If everything has been setup correctly in app.js file, you will see the following message on your terminal
    ```
    Listening at <port_number>
    ```

    - Navigate your browser to http://127.0.0.1/
    
    ## Supported Operating Systems ##
    The CompileBox API has been installed and run succesfully on the following platforms
    - Ubuntu 14.04 LTS
    - Ubuntu 16.04 LTS
    
## Selecting The languages for Installation Inside Docker ##

The default Dockerfile installs the most used languages. To remove/change any, follow these steps

In order to select languages of your own choice you need to make 2 changes.<br>
    	1. <B>Dockerfile</B>: This file contains commands that you would normally give in your terminal to install that language. Add the required commands preceeded by the RUN keyword inside the Dockerfile. Run the "UpdateDocker.sh" script, present in the same folder if you are adding new language to already installed API, execute the Install_*.sh script otherwise, from your terminal after making the changes to your Dockerfile.<br>
        2. <B>Compilers.js</B>: This file is inside the API folder. The compiler name, the source file name and the execution commands to Docker Container are taken from this file. This file only contains an array, which is described in detail inside the file. Add the credentials of the language you are adding to this array.<br>
        
The next time you wish to compile using this language, simply issue the language_id , which is  same as the index of the language in the array present in Compilers.js, along with your code to the NodeJs server.

> Note: Additionally while setting up the API for the first time, you can comment out those languages from the Dockerfile that you do not wish to install, since they can be added later.


> Note:  You should be connected to the Internet when you run UpdateDocker.sh

  [1]: http://compile.remoteinterview.io
  [2]: http://codepad.remoteinterview.io
