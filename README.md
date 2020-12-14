
<!--
*** Thanks for checking out the Best-README-Template. If you have a suggestion
*** that would make this better, please fork the repo and create a pull request
*** or simply open an issue with the tag "enhancement".
*** Thanks again! Now go create something AMAZING! :D
***
***
***
*** To avoid retyping too much info. Do a search and replace for the following:
*** github_username, repo_name, twitter_handle, email, project_title, project_description
-->



<!-- PROJECT SHIELDS -->
<!--
*** I'm using markdown "reference style" links for readability.
*** Reference links are enclosed in brackets [ ] instead of parentheses ( ).
*** See the bottom of this document for the declaration of the reference variables
*** for contributors-url, forks-url, etc. This is an optional, concise syntax you may use.
*** https://www.markdownguide.org/basic-syntax/#reference-style-links
-->


<!-- TABLE OF CONTENTS -->
<details open="open">
  <summary><h2 style="display: inline-block">Table of Contents</h2></summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## About The Project

The following application records the analog values from numerous DFROBOT steam sensors, as well as, the analog values from DS18B20 temperature sensors in order
to attempt to quantitatively calculate the amount of steam released from a unit under test (UUT). In order to calculate the desired steam accumulation the DFROBOT
steam sensor analog values are multipled by the time elapsed between each sampling and then summed. This sum represents the total steam accumulated during that
single time lapse. To calculate the total steam released throughout the testing process, this is repeated for the entire run. The total steam accumulation is the 
sum of all the sums. In addition the following GUI, plots the recorded data on three graphs: Time vs Steam Accumulation, Time vs Steam Sensor Humidity, and 
Time vs Steam Temperature vs Surrounding Temperature. 


### Built With

### Software 
* []() PyQT5
* []() Python3

### Hardware
* []() 3 DFROBOT Steam Sensors
* []() 2 DS18B20 Sensors
* []() Raspberry Pi 3B
* []() High-Precision AD/DA Board 


<!-- GETTING STARTED -->
## Getting Started

To get a local copy up and running follow these simple steps:
### Setup
* []() Attach the High-Precision AD/DA Board to the Raspberry Pi
* []() Set the Power Supply to 5V: connect the pin 5V and VCC.
* []() Set the Reference Input Voltage to 5V: connect the pin 5V and VREF.
* []() Attach the DFROBOT Steam Sensors to individual analog pins (AD0, AD1, AD2 ...)
* []() Connect the RPi 5V, GND to a breadboard
* []() Connect the DFROBOT Steam Sensors to 5V and GND through the breadboard
* []() Connect P7 to the breadboard and connect the DS18B20 sensors
* []() Clone the repo to a RPi folder
* []() Open steam_Fixture_GUI.py within an IDE and run
* []() Enter the unit's name, function, food load, monitoring time (min), sensor height, sensor threhold, and initial masses
* []() Click start. If an error popup appears fix the error and try again
* []() Once a DFROBOT Steam Sensor's analog value rises above the threshold set the application will begin to record sensor data
* []() The count down will turn green in order to indicate this
* []() When the monitoring time has expired the user may add additional time if the UUT is still releasing steam. If it is not enter 0.
* []() Enter the final masses and click resume
* []() After an initial wait the remaining fields in the application should be filled and an external window with graphs will appear




### Prerequisites
* pip3
  ```sh
  pip3 install PyQt5
  pip3 install pandas
  pip3 install glob3
  pip3 install XlsxWriter
  ```
  
* python
  ```sh
  python -m pip install -U matplotlib
  ```
  
### Installation

1. Clone the repo
   ```sh
   git clone https://github.com/klam2k20/Steam-Fixture.git
   ```




