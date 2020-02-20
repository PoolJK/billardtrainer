#ifndef _MCP4992_H_
#define _MCP4992_H_

#include <Arduino.h>


/*
    Support for the MCP4922 DA-Converter.
 */

class MCP4922
{
public:
    /* Init DA-Converter support */
    MCP4922();
  
    /* Write values to both channels */
    void writeDac(uint16_t A, uint16_t B);

    static const uint16_t mcp4992_max_val = 4095;
    static const uint16_t mcp4992_min_val = 0;
};

#endif