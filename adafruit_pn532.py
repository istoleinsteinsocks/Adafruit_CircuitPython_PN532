# Adafruit PN532 NFC/RFID control library.
# Author: Tony DiCola
# Copyright (c) 2015-2018 Adafruit Industries
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

#import binascii
#from functools import reduce
#import logging
import time
import adafruit_bus_device.i2c_device as i2c_device
import adafruit_bus_device.spi_device as spi_device

from micropython import const


PN532_PREAMBLE                      = const(0x00)
PN532_STARTCODE1                    = const(0x00)
PN532_STARTCODE2                    = const(0xFF)
PN532_POSTAMBLE                     = const(0x00)

PN532_HOSTTOPN532                   = const(0xD4)
PN532_PN532TOHOST                   = const(0xD5)

# PN532 Commands
PN532_COMMAND_DIAGNOSE              = const(0x00)
PN532_COMMAND_GETFIRMWAREVERSION    = const(0x02)
PN532_COMMAND_GETGENERALSTATUS      = const(0x04)
PN532_COMMAND_READREGISTER          = const(0x06)
PN532_COMMAND_WRITEREGISTER         = const(0x08)
PN532_COMMAND_READGPIO              = const(0x0C)
PN532_COMMAND_WRITEGPIO             = const(0x0E)
PN532_COMMAND_SETSERIALBAUDRATE     = const(0x10)
PN532_COMMAND_SETPARAMETERS         = const(0x12)
PN532_COMMAND_SAMCONFIGURATION      = const(0x14)
PN532_COMMAND_POWERDOWN             = const(0x16)
PN532_COMMAND_RFCONFIGURATION       = const(0x32)
PN532_COMMAND_RFREGULATIONTEST      = const(0x58)
PN532_COMMAND_INJUMPFORDEP          = const(0x56)
PN532_COMMAND_INJUMPFORPSL          = const(0x46)
PN532_COMMAND_INLISTPASSIVETARGET   = const(0x4A)
PN532_COMMAND_INATR                 = const(0x50)
PN532_COMMAND_INPSL                 = const(0x4E)
PN532_COMMAND_INDATAEXCHANGE        = const(0x40)
PN532_COMMAND_INCOMMUNICATETHRU     = const(0x42)
PN532_COMMAND_INDESELECT            = const(0x44)
PN532_COMMAND_INRELEASE             = const(0x52)
PN532_COMMAND_INSELECT              = const(0x54)
PN532_COMMAND_INAUTOPOLL            = const(0x60)
PN532_COMMAND_TGINITASTARGET        = const(0x8C)
PN532_COMMAND_TGSETGENERALBYTES     = const(0x92)
PN532_COMMAND_TGGETDATA             = const(0x86)
PN532_COMMAND_TGSETDATA             = const(0x8E)
PN532_COMMAND_TGSETMETADATA         = const(0x94)
PN532_COMMAND_TGGETINITIATORCOMMAND = const(0x88)
PN532_COMMAND_TGRESPONSETOINITIATOR = const(0x90)
PN532_COMMAND_TGGETTARGETSTATUS     = const(0x8A)

PN532_RESPONSE_INDATAEXCHANGE       = const(0x41)
PN532_RESPONSE_INLISTPASSIVETARGET  = const(0x4B)

PN532_WAKEUP                        = const(0x55)

PN532_SPI_STATREAD                  = const(0x02)
PN532_SPI_DATAWRITE                 = const(0x01)
PN532_SPI_DATAREAD                  = const(0x03)
PN532_SPI_READY                     = const(0x01)

PN532_I2C_ADDRESS                   = const(0x24)

PN532_MIFARE_ISO14443A              = 0x00

# Mifare Commands
MIFARE_CMD_AUTH_A                   = const(0x60)
MIFARE_CMD_AUTH_B                   = const(0x61)
MIFARE_CMD_READ                     = const(0x30)
MIFARE_CMD_WRITE                    = const(0xA0)
MIFARE_CMD_TRANSFER                 = const(0xB0)
MIFARE_CMD_DECREMENT                = const(0xC0)
MIFARE_CMD_INCREMENT                = const(0xC1)
MIFARE_CMD_STORE                    = const(0xC2)
MIFARE_ULTRALIGHT_CMD_WRITE         = const(0xA2)

# Prefixes for NDEF Records (to identify record type)
NDEF_URIPREFIX_NONE                 = const(0x00)
NDEF_URIPREFIX_HTTP_WWWDOT          = const(0x01)
NDEF_URIPREFIX_HTTPS_WWWDOT         = const(0x02)
NDEF_URIPREFIX_HTTP                 = const(0x03)
NDEF_URIPREFIX_HTTPS                = const(0x04)
NDEF_URIPREFIX_TEL                  = const(0x05)
NDEF_URIPREFIX_MAILTO               = const(0x06)
NDEF_URIPREFIX_FTP_ANONAT           = const(0x07)
NDEF_URIPREFIX_FTP_FTPDOT           = const(0x08)
NDEF_URIPREFIX_FTPS                 = const(0x09)
NDEF_URIPREFIX_SFTP                 = const(0x0A)
NDEF_URIPREFIX_SMB                  = const(0x0B)
NDEF_URIPREFIX_NFS                  = const(0x0C)
NDEF_URIPREFIX_FTP                  = const(0x0D)
NDEF_URIPREFIX_DAV                  = const(0x0E)
NDEF_URIPREFIX_NEWS                 = const(0x0F)
NDEF_URIPREFIX_TELNET               = const(0x10)
NDEF_URIPREFIX_IMAP                 = const(0x11)
NDEF_URIPREFIX_RTSP                 = const(0x12)
NDEF_URIPREFIX_URN                  = const(0x13)
NDEF_URIPREFIX_POP                  = const(0x14)
NDEF_URIPREFIX_SIP                  = const(0x15)
NDEF_URIPREFIX_SIPS                 = const(0x16)
NDEF_URIPREFIX_TFTP                 = const(0x17)
NDEF_URIPREFIX_BTSPP                = const(0x18)
NDEF_URIPREFIX_BTL2CAP              = const(0x19)
NDEF_URIPREFIX_BTGOEP               = const(0x1A)
NDEF_URIPREFIX_TCPOBEX              = const(0x1B)
NDEF_URIPREFIX_IRDAOBEX             = const(0x1C)
NDEF_URIPREFIX_FILE                 = const(0x1D)
NDEF_URIPREFIX_URN_EPC_ID           = const(0x1E)
NDEF_URIPREFIX_URN_EPC_TAG          = const(0x1F)
NDEF_URIPREFIX_URN_EPC_PAT          = const(0x20)
NDEF_URIPREFIX_URN_EPC_RAW          = const(0x21)
NDEF_URIPREFIX_URN_EPC              = const(0x22)
NDEF_URIPREFIX_URN_NFC              = const(0x23)

PN532_GPIO_VALIDATIONBIT            = 0x80
PN532_GPIO_P30                      = 0
PN532_GPIO_P31                      = 1
PN532_GPIO_P32                      = 2
PN532_GPIO_P33                      = 3
PN532_GPIO_P34                      = 4
PN532_GPIO_P35                      = 5

PN532_ACK                           = b'\x01\x00\x00\xFF\x00\xFF\x00'
PN532_FRAME_START                   = b'\x01\x00\x00\xFF'


class PN532_I2C(object):
    """PN532 breakout board representation.  Requires a SPI connection to the
    breakout board.  A software SPI connection is recommended as the hardware
    SPI on the Raspberry Pi has some issues with the LSB first mode used by the
    PN532 (see: http://www.raspberrypi.org/forums/viewtopic.php?f=32&t=98070&p=720659#p720659)
    """

    def __init__(self, i2c, irq=None, *, debug=False):
        """Create an instance of the PN532 class using either software SPI (if
        the sclk, mosi, and miso pins are specified) or hardware SPI if a
        spi parameter is passed.  The cs pin must be a digital GPIO pin.
        Optionally specify a GPIO controller to override the default that uses
        the board's GPIO pins.
        """
        self.debug = debug
        self._i2c = i2c_device.I2CDevice(i2c, PN532_I2C_ADDRESS)
        self._irq = irq
        self.get_firmware_version()

    def _write_frame(self, data):
        """Write a frame to the PN532 with the specified data bytearray."""
        assert data is not None and 0 < len(data) < 255, 'Data must be array of 1 to 255 bytes.'
        # Build frame to send as:
        # - Preamble (0x00)
        # - Start code  (0x00, 0xFF)
        # - Command length (1 byte)
        # - Command length checksum
        # - Command bytes
        # - Checksum
        # - Postamble (0x00)
        length = len(data)
        frame = bytearray(length+8)
        frame[0] = PN532_PREAMBLE
        frame[1] = PN532_STARTCODE1
        frame[2] = PN532_STARTCODE2
        checksum = sum(frame[0:3])
        frame[3] = length & 0xFF
        frame[4] = (~length + 1) & 0xFF
        frame[5:-2] = data
        checksum += sum(data)
        frame[-2] = ~checksum & 0xFF
        frame[-1] = PN532_POSTAMBLE
        # Send frame.
        if self.debug:
            print('Write frame: ', [hex(i) for i in frame])
        with self._i2c:
            self._i2c.write(bytes(frame))

    def _read_data(self, count):
        """Read a specified count of bytes from the PN532."""
        # Build a read request frame.
        frame = bytearray(count)
        with self._i2c:
            self._i2c.readinto(frame)
        if self.debug:
            print("Reading: ", [hex(i) for i in frame])
        return frame

    def _read_frame(self, length):
        """Read a response frame from the PN532 of at most length bytes in size.
        Returns the data inside the frame if found, otherwise raises an exception
        if there is an error parsing the frame.  Note that less than length bytes
        might be returned!
        """
        # Read frame with expected length of data.
        response = self._read_data(length+8)
        if self.debug:
            print('Read frame:', [hex(i) for i in response])
        # Check frame starts with 0x01 and then has 0x00FF (preceeded by optional
        # zeros).
        if response[0] != 0x01:
            raise RuntimeError('Response frame does not start with 0x01!')
        # Swallow all the 0x00 values that preceed 0xFF.
        offset = 1
        while response[offset] == 0x00:
            offset += 1
            if offset >= len(response):
                raise RuntimeError('Response frame preamble does not contain 0x00FF!')
        if response[offset] != 0xFF:
            raise RuntimeError('Response frame preamble does not contain 0x00FF!')
        offset += 1
        if offset >= len(response):
                raise RuntimeError('Response contains no data!')
        # Check length & length checksum match.
        frame_len = response[offset]
        if (frame_len + response[offset+1]) & 0xFF != 0:
            raise RuntimeError('Response length checksum did not match length!')
        # Check frame checksum value matches bytes.
        checksum = sum(response[offset+2:offset+2+frame_len+1]) & 0xFF
        if checksum != 0:
            raise RuntimeError('Response checksum did not match expected value: ', checksum)
        # Return frame data.
        return response[offset+2:offset+2+frame_len]

    def _wait_ready(self, timeout=1):
        if self._irq:
            print("TODO IRQ")
        else:
            time.sleep(timeout)
        return True

    def call_function(self, command, response_length=0, params=[], timeout=1):
        """Send specified command to the PN532 and expect up to response_length
        bytes back in a response.  Note that less than the expected bytes might
        be returned!  Params can optionally specify an array of bytes to send as
        parameters to the function call.  Will wait up to timeout seconds
        for a response and return a bytearray of response bytes, or None if no
        response is available within the timeout.
        """
        # Build frame data with command and parameters.
        data = bytearray(2+len(params))
        data[0]  = PN532_HOSTTOPN532
        data[1]  = command & 0xFF
        for i in range(len(params)):
            data[2+i] = params[i]
        # Send frame and wait for response.
        self._write_frame(data)
        if not self._wait_ready(timeout):
            return None
        # Verify ACK response and wait to be ready for function response.
        if not PN532_ACK == self._read_data(len(PN532_ACK)):
            raise RuntimeError('Did not receive expected ACK from PN532!')
        if not self._wait_ready(timeout):
            return None
        # Read response bytes.
        response = self._read_frame(response_length+2)
        # Check that response is for the called function.
        if not (response[0] == PN532_PN532TOHOST and response[1] == (command+1)):
            raise RuntimeError('Received unexpected command response!')
        # Return response data.
        return response[2:]

    def get_firmware_version(self):
        """Call PN532 GetFirmwareVersion function and return a tuple with the IC,
        Ver, Rev, and Support values.
        """
        response = self.call_function(PN532_COMMAND_GETFIRMWAREVERSION, 4, timeout=0.1)
        if response is None:
            raise RuntimeError('Failed to detect the PN532')
        return (response[0], response[1], response[2], response[3])

    def SAM_configuration(self):
        """Configure the PN532 to read MiFare cards."""
        # Send SAM configuration command with configuration for:
        # - 0x01, normal mode
        # - 0x14, timeout 50ms * 20 = 1 second
        # - 0x01, use IRQ pin
        # Note that no other verification is necessary as call_function will
        # check the command was executed as expected.
        self.call_function(PN532_COMMAND_SAMCONFIGURATION, params=[0x01, 0x14, 0x01])

    def read_passive_target(self, card_baud=PN532_MIFARE_ISO14443A, timeout=1):
        """Wait for a MiFare card to be available and return its UID when found.
        Will wait up to timeout seconds and return None if no card is found,
        otherwise a bytearray with the UID of the found card is returned.
        """
        # Send passive read command for 1 card.  Expect at most a 7 byte UUID.
        response = self.call_function(PN532_COMMAND_INLISTPASSIVETARGET,
                                      params=[0x01, card_baud],
                                      response_length=17)
        # If no response is available return None to indicate no card is present.
        if response is None:
            return None
        # Check only 1 card with up to a 7 byte UID is present.
        if response[0] != 0x01:
            raise RuntimeError('More than one card detected!')
        if response[5] > 7:
            raise RuntimeError('Found card with unexpectedly long UID!')
        # Return UID of card.
        return response[6:6+response[5]]

    def mifare_classic_authenticate_block(self, uid, block_number, key_number, key):
        """Authenticate specified block number for a MiFare classic card.  Uid
        should be a byte array with the UID of the card, block number should be
        the block to authenticate, key number should be the key type (like
        MIFARE_CMD_AUTH_A or MIFARE_CMD_AUTH_B), and key should be a byte array
        with the key data.  Returns True if the block was authenticated, or False
        if not authenticated.
        """
        # Build parameters for InDataExchange command to authenticate MiFare card.
        uidlen = len(uid)
        keylen = len(key)
        params = bytearray(3+uidlen+keylen)
        params[0] = 0x01  # Max card numbers
        params[1] = key_number & 0xFF
        params[2] = block_number & 0xFF
        params[3:3+keylen] = key
        params[3+keylen:]  = uid
        # Send InDataExchange request and verify response is 0x00.
        response = self.call_function(PN532_COMMAND_INDATAEXCHANGE,
                                      params=params,
                                      response_length=1)
        return response[0] == 0x00

    def mifare_classic_read_block(self, block_number):
        """Read a block of data from the card.  Block number should be the block
        to read.  If the block is successfully read a bytearray of length 16 with
        data starting at the specified block will be returned.  If the block is
        not read then None will be returned.
        """
        # Send InDataExchange request to read block of MiFare data.
        response = self.call_function(PN532_COMMAND_INDATAEXCHANGE,
                                      params=[0x01, MIFARE_CMD_READ, block_number & 0xFF],
                                      response_length=17)
        # Check first response is 0x00 to show success.
        if response[0] != 0x00:
            return None
        # Return first 4 bytes since 16 bytes are always returned.
        return response[1:]

    def mifare_classic_write_block(self, block_number, data):
        """Write a block of data to the card.  Block number should be the block
        to write and data should be a byte array of length 16 with the data to
        write.  If the data is successfully written then True is returned,
        otherwise False is returned.
        """
        assert data is not None and len(data) == 16, 'Data must be an array of 16 bytes!'
        # Build parameters for InDataExchange command to do MiFare classic write.
        params = bytearray(19)
        params[0] = 0x01  # Max card numbers
        params[1] = MIFARE_CMD_WRITE
        params[2] = block_number & 0xFF
        params[3:] = data
        # Send InDataExchange request.
        response = self.call_function(PN532_COMMAND_INDATAEXCHANGE,
                                      params=params,
                                      response_length=1)
        return response[0] == 0x00
