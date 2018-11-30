# Experimental software-defined radio using a serial port

This project creates an experimental radio-frequency transmitter from a modern serial port that uses a USB-UART bridge. These bridges allow very fast baud rates, allowing fundamental frequencies into the low MHz region to be generated.  The TTL-level output of some of the commonly available ICs has very fast edges, producing harmonics into the VHF region.

See the [full project on hackaday.io](https://hackaday.io/project/162477-serial-port-sdr).

## CW Frequency Generation

The square_wave.py program generates a square wave on the TX line of a serial port.

```
usage: square_wave.py [-h] port frequency

Generate square wave from serial port

positional arguments:
  port        serial port device name
  frequency   output frequency (Hz)

optional arguments:
  -h, --help  show this help message and exit
```
## AM Audio Transmission

The serial_sdr_tx.py program will generate an amplitude-modulated signal from an audio file.

```
usage: serial_sdr_tx.py [-h] [-p PORT] [-s START_OFFSET] [-e END_OFFSET]
                        [-r AUDIO_RATE] -f FREQUENCY [-m {pdm,ds1bit,dsmulti}]
                        [-l] [-d DELAY] [-o OUTPUT_FILE]
                        input_file

Transmit AM-modulated RF using serial port

positional arguments:
  input_file            audio file (wav format) to transmit

optional arguments:
  -h, --help            show this help message and exit
  -p PORT, --port PORT  serial port device name
  -s START_OFFSET, --start_offset START_OFFSET
                        audio start point (seconds)
  -e END_OFFSET, --end_offset END_OFFSET
                        audio end point (seconds)
  -r AUDIO_RATE, --rate AUDIO_RATE
                        audio resample rate
  -f FREQUENCY, --frequency FREQUENCY
                        fundamental frequency
  -m {pdm,ds1bit,dsmulti}, --method {pdm,ds1bit,dsmulti}
                        modulation method
  -l, --loop            transmit continuously
  -d DELAY, --delay DELAY
                        delay between loops
  -o OUTPUT_FILE, --output_file OUTPUT_FILE
                        output file
```

### Copying to serial ports directly

For large audio files, transmitting the audio directly from the python code can cause some clicks and pops.  The root cause of this is unknown, but the issue can be avoided by writing the data stream to a file, then copying this file to the serial port.  The following applies to linux systems.

First, create the AM modulated data and save it to a file, in this case, called 'test.dat':

    ./serial_sdr_tx.py sample.wav -f 1e6 -m dsmulti -o test.dat
    
Next, set the serial port to 8N1 with the appropriate baud rate.  Note that the baud rate is *twice* the fundamental frequency.

    stty --file=/dev/ttyUSB0 2000000 -parenb cs8 -cstopb
    
Finally, send the data to the serial port. This will play the audio once.

    cat test.dat >/dev/ttyUSB0
    
To play the audio in a loop:

    while true; do cat test.dat >/dev/ttyUSB0; done
