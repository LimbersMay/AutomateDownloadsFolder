
# AutomateDownloadsFolder
> A python script to automate the cleaning of the Downloads folder

## Table of contents
* [General info](#general-info)
* [Technologies](#technologies)
* [Prerequisites](#prerequisites)
* [Setup](#setup)
* [Usage](#usage)
* [Settings](#settings)
* [Future features](#future-features)

## General Info
This project is a python script to automate the cleaning of the Downloads folder or any other folder you want. 
In my daily life, I downloaded a lot of files and my Downloads folder was always a mess,
so I decided to start this project.

This is not just a simple script, it has a lot of features and settings that you can customize, like:
* Move files to folders based on their extensions
* Create folders based on the extensions found in settings
* Indicate how many days the files will be kept in the sorted folder before being deleted
* Decide if you want to delete the files or send them to the trash
* Set the maximum size of the files that will be moved

## Technologies
* Python 3.x

## Prerequisites
* Python 3.x
* pip

## Setup
1. Clone the repository:
   ```sh
   git clone https://github.com/LimbersMay/AutomateDownloadsFolder.git
   ```

2. Create a virtual environment (optional):
   ```sh
   python -m venv venv
   ```

3. Activate the virtual environment (optional):
   ```sh
   source venv/bin/activate
   ```

4. Install the requirements:
   ```sh
    pip install -r requirements.txt
    ```
   
5. Rename the `settings.example.json` file to `settings.json` located in the folder data/settings.example.json.\
   
## Usage
There are several ways to use this script, for example:
* Run the script manually
* Create a cron job
* Start the script when the computer starts

Here, I will show you how to start the script when the computer starts.

### Linux
1. Create a new systemd user service called `automate_downloads_folder.service` in the `/lib/systemd/user` directory:
   ```sh
   touch /lib/systemd/user/automate_downloads_folder.service
   ```

2. Open the file with your favorite text editor and paste the following code:
   ```
   [Unit]
   Description=My Script
   
   [Service]
   Type=simple
   ExecStart=/usr/bin/python /home/limbers/Documents/PersonalProjects/automateDownloadsFolde>
   WorkingDirectory=/home/limbers/Documents/PersonalProjects/automateDownloadsFolder
   
   [Install]
   WantedBy=default.target
    ```
   
3. Reload the systemd daemon:
   ```sh
   systemctl --user daemon-reload
   ```
   
4. Enable the service:
   ```sh
    systemctl --user enable automate_downloads_folder.service
    ```

Remember to change the `ExecStart` field to the path where the script is located.

**Note:**
If you are using a virtual environment,
you must use the path to the python executable inside the virtual environment instead of `/usr/bin/python`.
The path to the python executable inside the virtual environment is usually `/path/to/venv/bin/python`.

### Windows
1. Open the Run window by pressing the Windows key + R.

2. Type `shell:startup` and press Enter.

3. Create a shortcut to the script in the folder that opens.

## Settings
The settings are in the `settings.json` file, located in `data/settings.json`.

These settings are:
* `extensions`: List of extensions that will be used to create the folders and move the files.
* `daysToKeep`: Number of days that the files will be kept in the sorted folder before being deleted.
* `sendToTrash`: If `true`, the files will be sent to the trash. If `false`, the files will be deleted from the system.
* `maxSizeInMb`: Maximum size of the files that will be moved to the sorted folder.
* `paths`: List of paths that will be used to search for files to be moved.

Feel free to change the names of the extensions, 
the program will create the folders with the names you put in the settings.

## Future features
* Make possible to have multiple source folders where the files will be searched.
* Make possible to have multiple destination folders where the files will be moved.
* Use sqlite3 to store all the data instead of using a json file. (The change from json to sqlite3 wouldn't be hard to do, because I used the repository pattern to separate the data layer from the business layer, so I just need to create a new repository that uses sqlite3 instead of json)