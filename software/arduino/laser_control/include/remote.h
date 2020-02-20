#ifndef _REMOTE_H_
#define _REMOTE_H_

#include <Arduino.h>

#define RECBUF_SIZE 64

const char msg_delimiter[] = ";";
const char msg_prompt[] = ":";
const char msg_success[] = "ok\r\n";
const char msg_error[] = "err\r\n";


/** Command for drawing circle */
const char cmd_circle[] = "circ";
struct param_circle
{
    /** postion of x axis from -500 to 500 */
    int16_t xpos;
    /** postion of x axis from -500 to 500 */
    int16_t ypos;
    /** size of circle from 0 to 100 */
    uint16_t size;
};

const char cmd_rectangle[] = "rect";
struct param_rectangle
{
    /** postion of x axis from -500 to 500 */
    int16_t xpos;
    /** postion of x axis from -500 to 500 */
    int16_t ypos;
    /** size of sides length from 0 to 100 */
    uint16_t length;
};

const char cmd_cross[] = "cross";
struct param_cross
{
    /** postion of x axis from -500 to 500 */
    int16_t xpos;
    /** postion of x axis from -500 to 500 */
    int16_t ypos;
    /** size of line lengths from 0 to 100 */
    uint16_t length;
};

const char cmd_line[] = "line";
struct param_line
{
    int xpos1;
    int ypos1;
    int xpos2;
    int ypos2;
};


class Remote
{
public:
    Remote();

    /**
     * Wait for next command.
     * 
     * @return {char*}  : name of receive command
     */
    char* wait_for_cmd();

    /**
     * Parse parameters of command
     * @return {void*} : pointer to structure with parameters
     */
    void* get_params();

    /* write message to remote device */
    void write(const char* msg);

private:
    char recMsg[RECBUF_SIZE];
    char *tokptr;
    int recChar;
    int charCnt;
    param_rectangle params_rect;
    param_circle params_circ;
    param_line params_line;
    param_cross params_cross;
};

#endif