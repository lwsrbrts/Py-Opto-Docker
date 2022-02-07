# Py-Opto-Docker
Python to MQTT for an Opto Isolator attached to a 240v PIR sensor. This is an updated version of the previous PowerShell version that achieved the same thing but this version instead publishes MQTT messages to a broker.

## Opto Isolator circuit

The opto isolator, isolates the mains/line voltage from the Raspberry Pi and is the safest way to detect AC voltage using a Raspberry Pi since the Pi is never in contact with the high AC voltage.

The opto-isolator circuit used was purchased from eBay and is described as:

`240V 220V AC Mains Sensor opto-isolator optoisolator optocoupler 5V 3.3V Arduino`

![ebay seller](https://github.com/lwsrbrts/Pwsh-Opto-Docker/raw/master/ebay-seller.png "ebay seller")


## Pin layout

The opto-isolator is connected to the Raspberry Pi as follows:

![Pin layout for opto-isolator](https://github.com/lwsrbrts/Pwsh-Opto-Docker/raw/master/Pin-layout.png "Pin layout for opto-isolator")

PowerShell uses WiringPi pin numbering so the opto-isolator `OUT` is connected to physical pin `7` on the Raspberry Pi's GPIO, which is also WiringPi pin `7`. If you are not using physical pin `7`, the WiringPi pin is (obviously) different. For example, physical pin `26` on the Raspberry Pi GPIO is WiringPi pin `11` as far as the PowerShell IoT module is concerned.

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

* `CLIENT_NAME` - The name of the MQTT topic to be appended to /garage/.
* `MQTT_BROKER` - The IP address or host name of hte MQTT broker.
* `MQTT_USER` - The username to be used ot connect ot the MQTT broker
* `MQTT_PASS` - The password for the MQTT_USER.
* `OPTO_PIN` - The GPIO pin number the opto isolator is connected to.
* `PYTHONUNBUFFERED` - Required to ensure that python doesn't buffer stdout so you can see docker logs.

## Example

This is an example docker run command which assumes the image has been built and called `py-opto:1.0`.

### Auto-healing, detached, named

```bash
docker run -d --privileged --name py-opto \
              --restart=unless-stopped \
              -h FRONT \
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

Redirect standard and error logs to a file.

`docker container logs -f py-opto`

### Updating the container from GitHub

Basically pull the Dockerfile and script from the GitHub repo and build it again then run once a new image is built.

```powershell
docker container stop py-opto

docker container rm py-opto

cd ~/Py-Opto-Docker/

git pull

docker build --tag py-opto:1.0 .
```
