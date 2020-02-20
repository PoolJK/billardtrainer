#ifndef _FIGURE_H_
#define _FIGURE_H_

#include <Arduino.h>

/*
Symmetrical figure to show with laser
 */
class figure
{
private:
    /* data */
public:
    figure(const uint16_t* figure, int size, int startA, int startB );

    // pointer to figure data array
    const uint16_t *data;

    // size of data array
    int size;

    // pointer to data for channel A
    volatile const uint16_t *valA;

    // pointer to data for channel B
    volatile const uint16_t *valB;
};

extern figure figSine;
extern figure figRect;
extern figure figCross;

#endif
