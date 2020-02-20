#include <SPI.h>
#include "mcp4992.h"

const uint8_t PIN_SS = 10;
const uint8_t PIN_LDAC  = 9;

MCP4922::MCP4922()
{
    // set the slaveSelectPin as an output high
    digitalWrite(PIN_SS, HIGH);
    pinMode(PIN_SS, OUTPUT);
    // set the LDAC pin as output high
    digitalWrite(PIN_LDAC, LOW);
    pinMode(PIN_LDAC, OUTPUT);
    // initialize SPI:
    SPI.begin();
    SPI.beginTransaction(SPISettings(4000000, MSBFIRST, SPI_MODE0));
}

void MCP4922::writeDac(uint16_t A, uint16_t B)
{
    // A = uint16_t((float)A / (float)1.2);
    // B = uint16_t((float)B / (float)1.2);
    // setup highest bits for each channel value
    //Bit 0: 0 for channel A, 1 for B
    //Bit 1: 1 means VREF is buffered (can use simple voltage divider)
    //Bit 2: 1 means G = 1 , 0 means G = 2, so that VOUT = 0 .. 2*VREF
    //Bit 3: 0 means shutdown, no output
    // avoid mirroring on to high values
    if(A > 4095) A = 4095;
    if(B > 4095) B = 4095;
    A &= 0x0FFF;
    A |= 0x7000;
    B &= 0x0FFF;
    B |= 0xF000;
    // write channel A value
    digitalWrite(PIN_SS, LOW);
    SPI.transfer16(A);
    digitalWrite(PIN_SS, HIGH);
    delayMicroseconds(1);
    // write channel B value
    digitalWrite(PIN_SS, LOW);
    SPI.transfer16(B);
    digitalWrite(PIN_SS, HIGH);
}