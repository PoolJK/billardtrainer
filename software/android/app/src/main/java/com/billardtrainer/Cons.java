package com.billardtrainer;

import android.graphics.Color;

class Cons {

	// prog constants
	static final int STATE_STILL = 0;
	static final int STATE_ROLLING = 1;
	static final int STATE_SPINNING = 2;
	static final int quadSimSteps = 10;

	// Sim params
	static final double precision = 0.001;
	static final double dprecision = 0.000001;

	// Table Params

	final static double tableLength = 3.556; // y+(0 = tl)
	static final double tableWidth = 1.778; // x+ (0 = tl)
	final static double DDistance = 0.737;
	final static double DRadius = 0.292;
	final static double blackDistance = 0.324;

	// Ball Params

	final static double ballRadius = 0.02625;
	final static double ballWeight = 0.140;
	final static double uBallCloth = 0.01;
	final static double uBallBall = 0.06;
	final static double g = 9.81; // m/s^2
	final static double frictionCoeff = uBallCloth * g;

	final static Vec3 yellowSpot = new Vec3(tableWidth / 2 - DRadius,
			-DDistance, Cons.ballRadius);
	final static Vec3 greenSpot = new Vec3(tableWidth / 2 + DRadius,
			-DDistance, Cons.ballRadius);
	final static Vec3 brownSpot = new Vec3(tableWidth / 2, -DDistance,
			Cons.ballRadius);
	final static Vec3 blueSpot = new Vec3(tableWidth / 2, -tableLength / 2,
			Cons.ballRadius);
	final static Vec3 pinkSpot = new Vec3(tableWidth / 2, -tableLength / 4 * 3,
			Cons.ballRadius);
	final static Vec3 blackSpot = new Vec3(tableWidth / 2, -tableLength
			+ blackDistance, ballRadius);

	final static Vec3 yellowPocket = new Vec3(ballRadius, -ballRadius,
			ballRadius);
	final static Vec3 greenPocket = new Vec3(tableWidth - ballRadius,
			-ballRadius, ballRadius);
	final static Vec3 blueLPocket = new Vec3(ballRadius, -tableLength / 2,
			ballRadius);
	final static Vec3 blueRPocket = new Vec3(tableWidth - ballRadius,
			-tableLength / 2, ballRadius);
	final static Vec3 blackLPocket = new Vec3(ballRadius, -tableLength
			+ ballRadius, Cons.ballRadius);
	final static Vec3 blackRPocket = new Vec3(tableWidth - ballRadius,
			-tableLength + ballRadius, ballRadius);

	static final Vec3[] pockets = { yellowPocket, greenPocket,
			blueLPocket, blueRPocket, blackLPocket, blackRPocket };
}
