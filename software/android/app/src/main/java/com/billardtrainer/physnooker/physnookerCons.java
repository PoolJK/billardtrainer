package com.billardtrainer.physnooker;

public class physnookerCons {
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
	final static double tableWidth = 1.778; // x+ (0 = tl)
	final static double DDistance = 0.737;
	final static double DRadius = 0.292;
	final static double blackDistance = 0.324;

	// Ball Params
	final static double ballRadius = 0.02625;
	final static double ballWeight = 0.140;
	final static double uBallCloth = 0.2;
	final static double uBallClothRoll = 0.01;
	final static double uBallBall = 0.06;
	final static double g = 9.81; // m/s^2
	final static double friction_cloth = uBallCloth * g;
	final static double friction_cloth_roll = uBallClothRoll * g;

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

	public static final Vec3[] pockets = { yellowPocket, greenPocket,
			blueLPocket, blueRPocket, blackLPocket, blackRPocket };

	public static double d(double in, double prec) {
		return ((double) Math.round(in * Math.pow(10, prec)))
				/ Math.pow(10, prec);
	}

	public static double length(Vec3 v) {
		return Math.sqrt(v.x * v.x + v.y * v.y + v.z * v.z);
	}

	public static double distance(Vec3 a, Vec3 b) {
		return Math.sqrt(Math.pow(b.x - a.x, 2) + Math.pow(b.y - a.y, 2)
				+ Math.pow(b.z - a.z, 2));
	}

	public static void add(Vec3 a, Vec3 b) {
		a.x += b.x;
		a.y += b.y;
		a.z += b.z;
	}
	
	public static void add(Vec3 a, double b){
		a.x += b;
		a.y += b;
		a.z += b;
	}

	public static void subtract(Vec3 a, Vec3 b) {
		a.x -= b.x;
		a.y -= b.y;
		a.z -= b.z;
	}
	
	public static void subtract(Vec3 a, double b){
		a.x -= b;
		a.y -= b;
		a.z -= b;
	}
	
	public static void multiply(Vec3 a, Vec3 b){
		a.x *= b.x;
		a.y *= b.y;
		a.z *= b.z;
	}

	public static double scalar(Vec3 a, Vec3 b) {
		return a.x * b.x + a.y * b.y + a.z * b.z;
	}

	public static double deltaAngle(Vec3 a, Vec3 b) {
		return Math.acos(scalar(a, b) / (length(a) * length(b)));
	}
	
	public static Vec3 cross(Vec3 a, Vec3 b){
		return new Vec3(a.y*b.z-a.z*b.y, a.z*b.x-a.x*b.z, a.x*b.y-a.y*b.x);
	}

	public static void normalize(Vec3 v) {
		if (v.x == v.y & v.y == v.z & v.z == 0)
			return;
		double l = 1 / length(v);
		v.x *= l;
		v.y *= l;
		v.z *= l;
	}
}
