hcconfig
========

This tool allows you to easily configure HC-05, HC-06 and other Bluetooth
modules easily through the serial port.

Installation
------------

You need Python 3.5+ to use it.

Install ``hcconfig`` with::

   pip3 install hcconfig

Command line interface
----------------------

Run it with::

   hcconfig


You will be asked to select a serial port that you will use to connect with the Bluetooth module.

The default baudrate is 38400 which should be correct for most BT modules.

Both the port and the baud rate can be optionally provided on the command line if you prefer. For example,
you can::

    hcconfig --baud-rate 9600 /dev/ttyUSB1

See the currently available commands with::

   (hcconfig) help

See help for a given command::

   (hcconfig) help baudrate

To change the baudrate, for example::

   (hcconfig) baudrate 115200
   UART(baudrate=115200, stopbits=1, parity=none)

You can use ``TAB`` for autocompletion and to see the allowed values for any
command.
