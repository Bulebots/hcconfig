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

That will try to connect with your Bluetooth device at ``/dev/ttyUSB0`` with
the baudrate set to 38400. If you want to use other non-default configuration,
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
