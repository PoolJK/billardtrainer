#include <Arduino.h>
#include <SPI.h>
#include <TimerOne.h>
#include "figure.h"
#include "mcp4992.h"
#include "remote.h"

//#define LED_PIN 13
MCP4922 mMcp4922;
Remote mRemote;
// figure to draw
figure *actFig;
param_circle *circle_params;
param_rectangle *rect_params;
//param_line *line_params;
param_cross *cross_params;
// resolution of position x,y
const uint16_t posResolution = 1000;
// resolution of figure size
const uint16_t sizeResolution = 100;
// data fetch step size
int data_incr = 4;
// figure data modifiers for isr
// factor for size
uint16_t factor;
// positional offsets
uint16_t offsA;
uint16_t offsB;
// parsed command
char *cmd;
// buffer for debug outputs
char buffer[32];


void timer1_isr()
{
 	mMcp4922.writeDac(
		(uint16_t)(((uint32_t)pgm_read_word_near(actFig->valA) * factor) / sizeResolution + offsA),
		(uint16_t)(((uint32_t)pgm_read_word_near(actFig->valB) * factor) / sizeResolution + offsB));
	// next data, values greate than 1 increase speed, decrease resolution
	actFig->valA += data_incr;
	actFig->valB += data_incr;
	// circle through data arrays
	if (actFig->valA > &actFig->data[actFig->size - 1])
	{
		actFig->valA = actFig->data;
	}

	if (actFig->valB > &actFig->data[actFig->size - 1])
	{
		actFig->valB = actFig->data;
	}
}

void setup()
{
	interrupts();
	//  pinMode(LED_PIN, OUTPUT);
	mMcp4922 = MCP4922();
	mRemote = Remote();
	// set initial figure to draw
	actFig = &figSine;
	// show figure with max size
	factor = sizeResolution;
	offsA = 0;
	offsB = 0;
	// set timer frequency
	Timer1.initialize(140); // 40
	Timer1.attachInterrupt(timer1_isr);
}

void loop()
{
	cmd = NULL;
	mRemote.write(msg_prompt);
	cmd = mRemote.wait_for_cmd();

	if (cmd != NULL)
	{
		if (strcmp(cmd_circle, cmd) == 0)
		{
			circle_params = (param_circle *)mRemote.get_params();
			if(circle_params == NULL)
			{
				mRemote.write(msg_error);
			}
			else
			{
				Timer1.stop();
				/* sprintf_P(buffer,PSTR("circ: %d %d %d\r\n"), circle_params->xpos, circle_params->ypos, circle_params->size);
				mRemote.write(buffer);  */
				// adjust to absolute position from 0 to posResolution
				circle_params->xpos += posResolution / 2;
				circle_params->ypos += posResolution / 2;
				// range check
				if(circle_params->xpos > (int16_t)posResolution)
					circle_params->xpos = posResolution;
				if(circle_params->ypos > (int16_t)posResolution)
					circle_params->ypos = posResolution;
				if(circle_params->size > sizeResolution)
					circle_params->size = sizeResolution;
				// calculate figure offset 
				offsA = (uint16_t) (((uint32_t) mMcp4922.mcp4992_max_val * circle_params->xpos) / posResolution);
				offsB = (uint16_t) (((uint32_t) mMcp4922.mcp4992_max_val * circle_params->ypos) / posResolution);
				factor = circle_params->size;
				actFig = &figSine;
				mRemote.write(msg_success);
				Timer1.start();
			}
		}
		else if (strcmp(cmd_rectangle, cmd) == 0)
		{
			rect_params = (param_rectangle *)mRemote.get_params();
			if(rect_params == NULL)
			{
				mRemote.write(msg_error);
			}
			else
			{
				Timer1.stop();
				/* sprintf_P(buffer,PSTR("rect: %d %d %d\r\n"), circle_params->xpos, circle_params->ypos, circle_params->size);
				mRemote.write(buffer); */
				// adjust to absolute position from 0 to posResolution
				rect_params->xpos += posResolution / 2;
				rect_params->ypos += posResolution / 2;
				// range check
				if(rect_params->xpos > (int16_t)posResolution)
					rect_params->xpos = posResolution;
				if(rect_params->ypos > (int16_t)posResolution)
					rect_params->ypos = posResolution;
				if(rect_params->length > sizeResolution)
					rect_params->length = sizeResolution;

				offsA = (uint16_t) (((uint32_t) mMcp4922.mcp4992_max_val * rect_params->xpos) / posResolution);
				offsB = (uint16_t) (((uint32_t) mMcp4922.mcp4992_max_val * rect_params->ypos) / posResolution);
				factor = rect_params->length;
				actFig = &figRect;
				mRemote.write(msg_success);
				Timer1.start();
			}
		}
		else if (strcmp(cmd_cross, cmd) == 0)
		{
			cross_params = (param_cross *)mRemote.get_params();
			if(cross_params == NULL)
			{
				mRemote.write(msg_error);
			}
			else
			{
				Timer1.stop();
				/* sprintf_P(buffer,PSTR("cross: %d %d %d\r\n"), cross_params->xpos, cross_params->ypos, 
							cross_params->length);
				mRemote.write(buffer); */
				// adjust to absolute position from 0 to posResolution
				cross_params->xpos += posResolution / 2;
				cross_params->ypos += posResolution / 2;
				// range check
				if(cross_params->xpos > (int16_t)posResolution)
					cross_params->xpos = posResolution;
				if(cross_params->ypos > (int16_t)posResolution)
					cross_params->ypos = posResolution;
				if(cross_params->length > sizeResolution)
					cross_params->length = sizeResolution;

				offsA = (uint16_t) (((uint32_t) mMcp4922.mcp4992_max_val * cross_params->xpos) / posResolution);
				offsB = (uint16_t) (((uint32_t) mMcp4922.mcp4992_max_val * cross_params->ypos) / posResolution);
				factor = cross_params->length;
				actFig = &figCross;
				mRemote.write(msg_success);
				Timer1.start();
			}
		}
		else
		{
			mRemote.write(msg_error);
		}
	}
	else
	{
		mRemote.write(msg_error);
	}
}
