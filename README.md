# snom-pnpserv
fork of http://pnpserv.sourceforge.net/ allowing better configuration of provisioning URL

pnpserv is a python script provided by snom to simplify automatic provisioning of snom ip phones.
unconfigured snom phones broadcast a sip subscribe request, pnpserv.py answers to this request with a provisioning URL.

unfortunately, the original pnpserv.py does not allow for freely configurable URLs, hence this fork.

the "-u" command line parameter is changed, allowing the following template variables:

template string | description       | example
--------------- | ----------------- | -------------------
${model}        | phone model       | snom725
${mac_addr}     | phone mac address | 00041378FFFF
${ip_addr}      | phone ip address  | 192.168.0.10
${fw_version}   | firmware version  | 8.7.5.8.11

call the script e.g. with:
```
python pnpserv.py -u 'http://provisioning-server:8000/snom/provision/${model}/${mac_addr}/config.xml'
```
