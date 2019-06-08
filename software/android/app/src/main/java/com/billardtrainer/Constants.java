package com.billardtrainer;

class Constants {

    // prog constants
    static final int STATE_STILL = 0;
    static final int STATE_ROLLING = 1;
    static final int STATE_STUN = 2;
    static final int STATE_SLIDING = 3;
    static final int STATE_COLLISION = 4;
    static final int quadSimSteps = 10;

    // Sim params
    static final double precision = 0.001;

    // Table Params

    final static double tableLength = 3556; // y+(0 = tl)
    static final double tableWidth = 1778; // x+ (0 = tl)
    final static double DDistance = 737;
    final static double DRadius = 292;
    private final static double blackDistance = 324;

    // Ball Params

    // https://www.researchgate.net/publication/228372702_Application_of_high-speed_imaging_to_determine_the_dynamics_of_billiards/download
    final static double ballRadius = 26.25;
    //final static double ballWeight = 0.140; // kg ?
    //final static double uBallBall = 0.06;
    @SuppressWarnings("unused")
    final static double g = 9807; // [mm/s^2]
    final static double frictionClothSpin = 2000; // [mm/s^2]
    final static double frictionClothRoll = 125; // [mm/s^2]

    final static Vec3 yellowSpot = new Vec3(tableWidth / 2 - DRadius,
            DDistance, Constants.ballRadius);
    final static Vec3 greenSpot = new Vec3(tableWidth / 2 + DRadius,
            DDistance, Constants.ballRadius);
    final static Vec3 brownSpot = new Vec3(tableWidth / 2, DDistance,
            Constants.ballRadius);
    final static Vec3 blueSpot = new Vec3(tableWidth / 2, tableLength / 2,
            Constants.ballRadius);
    final static Vec3 pinkSpot = new Vec3(tableWidth / 2, tableLength / 4 * 3,
            Constants.ballRadius);
    final static Vec3 blackSpot = new Vec3(tableWidth / 2, tableLength
            - blackDistance, ballRadius);

    final static Vec3 yellowPocket = new Vec3(ballRadius, ballRadius,
            ballRadius);
    final static Vec3 greenPocket = new Vec3(tableWidth - ballRadius,
            ballRadius, ballRadius);
    final static Vec3 blueLPocket = new Vec3(ballRadius, tableLength / 2,
            ballRadius);
    final static Vec3 blueRPocket = new Vec3(tableWidth - ballRadius,
            tableLength / 2, ballRadius);
    final static Vec3 blackLPocket = new Vec3(ballRadius, tableLength
            - ballRadius, Constants.ballRadius);
    final static Vec3 blackRPocket = new Vec3(tableWidth - ballRadius,
            tableLength - ballRadius, ballRadius);

    static final Vec3[] pockets = {yellowPocket, greenPocket,
            blueLPocket, blueRPocket, blackLPocket, blackRPocket};
}