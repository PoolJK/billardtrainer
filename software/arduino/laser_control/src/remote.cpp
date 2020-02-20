#include "remote.h"


Remote::Remote()
{
	//Serial.setTimeout(10000);
	Serial.begin(9600);
	while (!Serial);
}

char *Remote::wait_for_cmd()
{
	// clear old message
	memset(recMsg, 0 , sizeof(recMsg));
	charCnt = 0;
	do
	{
		recChar = (char)Serial.read();
		if ((recChar != -1) && (recChar != '\r') && (recChar != '\n'))
			recMsg[charCnt++] = recChar;
	} while ((recChar != '\r') && (charCnt < RECBUF_SIZE));

	// return first substring, identifying the command
	tokptr = strtok(recMsg, msg_delimiter);
	return tokptr;
}


void *Remote::get_params()
{	
	//write(tokptr);
	// parse circle command parameters
	if (strcmp(cmd_circle, tokptr) == 0)
	{
		tokptr = strtok(NULL, msg_delimiter);
		if (tokptr != NULL)
		{
			params_circ.xpos = (uint16_t)strtol(tokptr, NULL, 10);
			//Serial.print(params_circ.xpos, DEC);
		}
		else 
		{
			return NULL;
		}
		tokptr = strtok(NULL, msg_delimiter);
		if (tokptr != NULL)
		{
			params_circ.ypos = (int16_t)strtol(tokptr, NULL, 10);
			//Serial.print(params_circ.ypos, DEC);
		}
		else 
		{
			return NULL;
		}
		tokptr = strtok(NULL, msg_delimiter);
		if (tokptr != NULL)
		{
			params_circ.size = (int16_t)strtol(tokptr, NULL, 10);
			//Serial.print(params_circ.size, DEC);
		}
		else 
		{
			return NULL;
		}

		return &params_circ;
	}
	// parse rectangle command parameters
	else if (strcmp(cmd_rectangle, tokptr) == 0)
	{
		tokptr = strtok(NULL, msg_delimiter);
		if (tokptr != NULL)
		{
			params_rect.xpos = (uint16_t)strtol(tokptr, NULL, 10);
			//Serial.print(params_circ.xpos, DEC);
		}
		else 
		{
			return NULL;
		}
		tokptr = strtok(NULL, msg_delimiter);
		if (tokptr != NULL)
		{
			params_rect.ypos = (uint16_t)strtol(tokptr, NULL, 10);
			//Serial.print(params_circ.ypos, DEC);
		}
		else 
		{
			return NULL;
		}

		tokptr = strtok(NULL, msg_delimiter);
		if (tokptr != NULL)
		{
			params_rect.length = (uint16_t)strtol(tokptr, NULL, 10);
			//Serial.print(params_circ.size, DEC);
		}
		else 
		{
			return NULL;
		}	

		return &params_rect;
	}
	// parse cross command parameters
	else if (strcmp(cmd_cross, tokptr) == 0)
	{
		tokptr = strtok(NULL, msg_delimiter);
		if (tokptr != NULL)
		{
			params_cross.xpos = (uint16_t)strtol(tokptr, NULL, 10);
		}
		else 
		{
			return NULL;
		}
		tokptr = strtok(NULL, msg_delimiter);
		if (tokptr != NULL)
		{
			params_cross.ypos = (uint16_t)strtol(tokptr, NULL, 10);
		}
		else 
		{
			return NULL;
		}

		tokptr = strtok(NULL, msg_delimiter);
		if (tokptr != NULL)
		{
			params_cross.length = (uint16_t)strtol(tokptr, NULL, 10);
		}
		else 
		{
			return NULL;
		}	
		return &params_cross;
	}
	// line not implemented yet
	else if (strcmp(cmd_line, tokptr) == 0)
	{
		return NULL;
	}

	return NULL;
}

void Remote::write(const char *msg)
{
	Serial.print(msg);
}
