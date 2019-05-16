package com.billardtrainer;

import android.graphics.Color;

import java.util.ArrayList;

import static com.billardtrainer.Cons.*;

class Utils {

    static int getBallColor(int value) {
        switch (value) {
            case 0:
                return Color.WHITE;
            case 1:
                return Color.rgb(200, 20, 10);
            case 2:
                return Color.rgb(240, 240, 20);
            case 3:
                return Color.rgb(10, 120, 40);
            case 4:
                return Color.rgb(100, 60, 55);
            case 5:
                return Color.rgb(0, 20, 230);
            case 6:
                return Color.rgb(200, 20, 200);
            case 7:
                return Color.rgb(10, 10, 10);
            default:
                return Color.BLACK;
        }
    }

    static Ball getBallFromPosition(double x, double y, ArrayList<Ball> ballsOnTable) {
        Ball ret = null;
        double minDistance = 6 * ballRadius;
        for (Ball ball : ballsOnTable) {
            double distance = ball.Pos.distanceTo(new Vec3(x, y,
                    ballRadius));
            if (distance < 5 * ballRadius && distance < minDistance) {
                minDistance = distance;
                ret = ball;
            }
        }
        return ret;
    }
}
