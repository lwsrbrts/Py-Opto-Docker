# Py-Opto-Docker
Python to MQTT for an Opto Isolator attached to a 240v PIR sensor. This is an updated version of the previous PowerShell version that achieved the same thing but this version instead publishes MQTT messages to a broker.

## Opto Isolator circuit

The opto isolator, isolates the mains/line voltage from the Raspberry Pi and is the safest way to detect AC voltage using a Raspberry Pi since the Pi is never in contact with the high AC voltage.

The opto-isolator circuit used was purchased from eBay and is described as:

`240V 220V AC Mains Sensor opto-isolator optoisolator optocoupler 5V 3.3V Arduino`

![ebay seller](https://github.com/lwsrbrts/Pwsh-Opto-Docker/raw/master/ebay-seller.png "ebay seller")


## Pin layouts

The opto-isolator is connected to the Raspberry Pi as follows:

![Pin layout for opto-isolator](https://github.com/lwsrbrts/Pwsh-Opto-Docker/raw/master/Pin-layout.png "Pin layout for opto-isolator")

## Install Docker

Go to `https://get.docker.com/`

or

```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
```

## If you need git on the RaspberryPi

```bash
sudo apt-get install git
```

## Clone the repo & build the image

```bash
git clone https://github.com/lwsrbrts/Py-Opto-Docker.git ~/Py-Opto-Docker/
```

## Build the image

```bash
cd ~/Py-Opto-Docker/

docker build --tag py-opto:1.0 .
```

Builds the image locally and tags it as `py-opto:1.0`

## Environment variables

These environment variables must be passed to the container (PowerShell script ultimately).

* `CLIENT_NAME` - The name of the MQTT topic.
* `ROOT_TOPIC` - The name of the MQTT root topic. Topic becomes eg. "{ROOT_TOPIC}/{CLIENT_NAME}"
* `MQTT_BROKER` - The IP address or host name of hte MQTT broker.
* `MQTT_USER` - The username to be used to connect to the MQTT broker
* `MQTT_PASS` - The password for the MQTT_USER.
* `OPTO_PIN` - The broadcom GPIO pin number the opto-isolator OUT is connected to.
* `PYTHONUNBUFFERED` - Required to ensure that python doesn't buffer stdout so you can see docker logs.

## Example

This is an example docker run command which assumes the image has been built and called `py-opto:1.0`.

### Auto-healing, detached, named

```bash
docker run -d --privileged --name py-opto \
              --restart=unless-stopped \
              -h FRONT \
              -e ROOT_TOPIC=garage \
              -e CLIENT_NAME=FRONT \
              -e MQTT_BROKER=192.168.1.100 \
              -e OPTO_PIN=4 \
              -e MQTT_USER=my-mqtt-user \
              -e MQTT_PASS='Thepassword' \
              -e PYTHONUNBUFFERED=1 \
              py-opto:1.0
```

* `-h` will set the hostname. This isn't used in the script.
* `--privileged` is used to ensure the docker container can access the GPIO pins.

### Review logs from a container

Tail the docker container's logs to see what's going on.

`docker container logs -f py-opto`

### Get inside the docker container

Execute /bin/bash inside the container interactively.

`docker exec -it py-opto /bin/bash`

### Updating the container from GitHub

Basically pull the Dockerfile and script from the GitHub repo and build it again then run once a new image is built.

```bash
docker container stop py-opto

docker container rm py-opto

cd ~/Py-Opto-Docker/

git pull

docker build --tag py-opto:1.0 .
```
