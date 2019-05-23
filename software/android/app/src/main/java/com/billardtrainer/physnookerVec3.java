package com.physnooker;

import static com.physnooker.Cons.*;

public class physnookerVec3
{

	double x, y, z;
	double time;
	
	public Vec3(){
		x = 0;
		y = 0;
		z = 0;
		time = 0;
	}

	public Vec3(double sx, double sy, double sz)
	{
		x = sx;
		y = sy;
		z = sz;
		time = 0;
	}

	public Vec3(double sx, double sy, double sz, double t)
	{
		x = sx;
		y = sy;
		z = sz;
		time = t;
	}

	public String toString()
	{
		if (this == yellowPocket)
			return("yellowPocket");
		if (this == greenPocket)
			return("greenPocket");
		if (this == blueLPocket)
			return("blueLPocket");
		if (this == blueRPocket)
			return("blueRPocket");
		if (this == blackLPocket)
			return("blackLPocket");
		if (this == blackRPocket)
			return("blackRPocket");

		return "x=" + d(x, 3) + ", y=" + d(y, 3) + ", z=" + d(z, 3);
	}
}
