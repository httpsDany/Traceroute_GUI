# Tracre-route-but-in-GUI
Traceroute (or tracert on Windows) is a command-line tool that helps you track how packets hop from your router to the final destination. 
However, the output is in IP addresses, and to get physical locations, you often need external websites like IP address lookup tools.

In this mini project i will be using a globe made using data from [NaturalEarth](https://www.naturalearthdata.com/) website to get data and country boundry and names 
The data from NaturalErath was maped into a 3d sphere to give a globe illusion and was displayed in web interface using flask.

A input box on top right is where we need to write a public ip address and traceroute will run in backend.
Then all the ipaddr goes to [ip-api](https://ip-api.com/) to fetch geo location.

NOTE:
    1]It dosen't work on Windows, made for Linux(and macOS) only (if running locally).

    2]'traceroute' must be installed.

    3]NaturalEarth files must be installed.

Finally, the results are visualized on the globe, providing a simplified yet detailed view of the packet path.
This project was created as a mini experiment and also intended for use in my DevOps pipeline with Jenkins in a real-world project.
