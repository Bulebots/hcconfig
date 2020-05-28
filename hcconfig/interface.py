from collections import namedtuple
from enum import Enum
import os
import sys
from pathlib import Path
import re

import cmd
import click
import serial
from serial import Serial
from serial.tools.miniterm import ask_for_port


def suggest_completions(string, completions):
    """
    Suggest string completions.
    """
    if not string:
        return completions
    return [c for c in completions if c.startswith(string)]


class Parity(Enum):
    """
    Class to define the UART parity.
    """
    none = 0
    odd = 1
    even = 2

    def __repr__(self):
        return self.name


UARTConfiguration = namedtuple('UARTConfig', 'baudrate stopbits parity')

VALID = {
    'parity': [p.name for p in Parity],
    'stopbits': ['1', '2'],
    'baudrate': ['4800', '9600', '19200', '38400', '57600', '115200',
                 '230400', '460800', '921600', '1382400', '1843200',
                 '2764800', '3686400'],
    'role': ['slave', 'master', 'master-loop'],
    'cmode': ['specific address', 'any address', 'slave-loop'],
}


class Interface(cmd.Cmd):
    prompt = '(hcconfig) '

    def configure(self, device, baudrate):
        """
        Configure the interface with the appropriate serial parameters.
        """
        while True:
            try:
                self.serial = Serial(device, baudrate=baudrate, timeout=.25)
            except serial.SerialException as e:
                sys.stderr.write(f'could not open port {device}: {e}\n')
                device = ask_for_port()
            else:
                break

    def cmdloop(self, intro=None):
        """
        Modified cmdloop() to handle keyboard interruptions.
        """
        while True:
            try:
                super().cmdloop()
                self.postloop()
                break
            except KeyboardInterrupt:
                print('^C')

    def emptyline(self):
        """
        On empty line, make sure to do nothing instead of repeating last
        command (which is the default behavior).
        """
        pass

    def get_response(self, field: str = None) -> str:
        """
        Get a response from the serial port.

        The `field` parameter is used to match the field to retrieve from the
        response.
        """
        response = self.serial.read(200)
        if not response:
            return 'No response!'
        response = response.decode('ascii').split('\n')[0]
        if 'ERROR' in response:
            print(response)
        if not field:
            return response
        match = re.search(r'(?<={})[^\s]+'.format(field), response)
        if not match:
            return 'Invalid response: {}'.format(response)
        return match.group(0)

    def send(self, message):
        """
        Send a message through the serial port.
        """
        self.serial.write(message.encode('ascii'))

    def get_uart_configuration(self) -> UARTConfiguration:
        """
        Get the UART configuration.
        """
        self.send('AT+UART?\r\n')
        response = self.get_response('UART:')
        response = response.split(',')
        if len(response) != 3:
            return UARTConfiguration(None, None, None)
        baudrate, stopbits, parity = response
        baudrate = int(baudrate)
        stopbits = int(stopbits) + 1
        parity = Parity(int(parity))
        return UARTConfiguration(
            baudrate=baudrate, stopbits=stopbits, parity=parity)

    def set_uart_configuration(self, baudrate=None, stopbits=None, parity=None):
        """
        Set the UART configuration.
        """
        current = self.get_uart_configuration()
        if baudrate is not None:
            if not baudrate in VALID['baudrate']:
                print('Invalid value! Use one of {}'.format(VALID['baudrate']))
                return
            current = current._replace(baudrate=int(baudrate))
        if stopbits is not None:
            if not stopbits in VALID['stopbits']:
                print('Invalid value! Use one of {}'.format(VALID['stopbits']))
                return
            current = current._replace(stopbits=int(stopbits))
        if parity is not None:
            if not parity in VALID['parity']:
                print('Invalid value! Use one of {}'.format(VALID['parity']))
                return
            current = current._replace(parity=Parity[parity])
        self.send('AT+UART={},{},{}\r\n'.format(
            current.baudrate, current.stopbits - 1, current.parity.value))
        self.get_response()

    def do_exit(self, arg=None):
        """
        Exit shell
        """
        exit()
        return True

    def do_EOF(self, arg=None):
        """
        Exit on end-of-file.
        """
        print('')
        self.do_exit()

    def do_clear(self, arg):
        """
        Clear the screen.
        """
        os.system('clear')

    def do_version(self, arg=None):
        """
        Get firmware version.
        """
        self.send('AT+VERSION?\r\n')
        print(self.get_response('VERSION:'))

    def do_info(self, arg=None):
        """
        Get Device summary.
        """

        self.send('AT\r\n')
        response = self.get_response().strip()
        if not response == 'OK':
            print('Please connect a module set to command mode')
            return

        self.send('AT+NAME?\r\n')
        name = self.get_response('NAME:')
        print(f'      Name: {name}')

        self.send('AT+UART?\r\n')
        uart = self.get_response('UART:').strip()
        uart_parts = uart.split(',')
        stop_bits = VALID['stopbits'][int(uart_parts[1])]
        parity = VALID['parity'][int(uart_parts[2])]
        print(f'  Baudrate: {uart_parts[0]}')
        print(f' Stop Bits: {stop_bits}')
        print(f'    Parity: {parity}')

        self.send('AT+PSWD?\r\n')
        password = self.get_response('')  # inconsistent response across modules
        print(f'  Password: {password}')

        self.send('AT+ADDR?\r\n')
        address = self.get_response('ADDR:')
        print(f'   Address: {address}')

        self.send('AT+VERSION?\r\n')
        version = self.get_response('VERSION:')
        print(f'   Version: {version}')

        self.send('AT+ROLE?\r\n')
        role = self.get_response('ROLE:')
        role = VALID['role'][int(role)]
        print(f'      Role: {role}')

        self.send('AT+CMODE?\r\n')
        mode = self.get_response('CMODE:')
        mode = VALID['cmode'][int(mode)]
        print(f'      Mode: {mode}')

    def do_address(self, arg=None):
        """
        Get module address.
        """
        self.send('AT+ADDR?\r\n')
        print(self.get_response('ADDR:'))

    def do_name(self, name=None):
        """
        Get or set the module name.
        """
        if name:
            self.send('AT+NAME="{}"\r\n'.format(name))
            self.get_response()
        self.send('AT+NAME?\r\n')
        print(self.get_response('NAME:'))

    def do_baudrate(self, baudrate=None):
        """
        Get or set the serial baudrate.
        """
        if baudrate:
            self.set_uart_configuration(baudrate=baudrate)
        print(self.get_uart_configuration())

    def do_stopbits(self, stopbits=None):
        """
        Get or set the serial stopbits.
        """
        if stopbits:
            self.set_uart_configuration(stopbits=stopbits)
        print(self.get_uart_configuration())

    def do_pin(self, pin=None):
        """
        Get or set the serial connection pin number.
        """
        if pin:
            self.send('AT+PSWD="{}"\r\n'.format(pin))
            self.get_response()
        self.send('AT+PSWD?\r\n')
        print(self.get_response())

    def do_parity(self, parity=None):
        """
        Get or set the serial parity.
        """
        if parity:
            self.set_uart_configuration(parity=parity)
        print(self.get_uart_configuration())

    def complete_baudrate(self, text, line, begidx, endidx):
        return suggest_completions(text, VALID['baudrate'])

    def complete_stopbits(self, text, line, begidx, endidx):
        return suggest_completions(text, VALID['stopbits'])

    def complete_parity(self, text, line, begidx, endidx):
        return suggest_completions(text, VALID['parity'])


@click.command()
@click.argument('device', type=click.Path(readable=False), required=False)
@click.option('-b', '--baud-rate', type=int, default=38400, help='Baud rate')
def run(device, baud_rate):
    cli = Interface()
    if device is None:
        try:
            device = ask_for_port()
        except KeyboardInterrupt:
            sys.stderr.write(' User Abort\n')
            sys.exit(1)
    cli.configure(device=device, baudrate=baud_rate)
    cli.do_info()
    cli.cmdloop()


if __name__ == '__main__':
    run()
