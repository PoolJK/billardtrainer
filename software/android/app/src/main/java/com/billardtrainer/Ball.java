package com.billardtrainer;

import java.util.ArrayList;

import android.graphics.Canvas;
import android.graphics.Paint;
import android.support.annotation.NonNull;
import android.util.Log;

import static com.billardtrainer.Cons.*;
import static com.billardtrainer.Utils.*;

class Ball {
    final int value, id;
    int state = 0;
    Vec3 Pos, Rot, V, W, V0, W0, Vc0;

    Ball(double x_position, double y_position, int value, int id) {
        // place on table
        Pos = new Vec3(x_position, y_position, ballRadius);
        Rot = new Vec3(0, 0, 0);
        V = new Vec3(0, 0, 0);
        W = new Vec3(0, 0, 0);
        V0 = new Vec3(0, 0, 0);
        W0 = new Vec3(0, 0, 0);
        Vc0 = new Vec3(0, 0, 0);
        this.value = value;
        this.id = id;
    }

    Vec3 getPos(double t){
        double f = 0.5 * uBallCloth * g * t * t;
        return new Vec3(Pos.x + V0.x * t - f * Vc0.x, Pos.y + V0.y * t - f * Vc0.y, 0, t);
    }

    Vec3 getVel(double t){
        double f = uBallCloth * g * t;
        return new Vec3(V0.x - f * Vc0.x, V0.y - f * Vc0.y, 0);
    }

    Vec3 getW(double t){
        double f = -5 * uBallCloth * g  * t / (2 * ballRadius);
        return new Vec3(W0.x - f * Vc0.y, W0.y + f * Vc0.x, W0.z - uBallCloth * g * t / ballRadius);
    }

    void setW0(Vec3 in){
        W0.x = in.x;
        W0.y = in.y;
        W0.z = in.z;
        W0.time = in.time;
    }

    void setV0(Vec3 in){
        V0.x = in.x;
        V0.y = in.y;
        V0.z = in.z;
        V0.time = in.time;
        Vc0.x = V0.x - ballRadius * W0.y;
        Vc0.y = V0.y + ballRadius * W0.x;
        Vc0.normalize();
        Vc0.time = in.time;
    }

    void move(double time) {
        // m/s -> m/ms * step
        if (state == 0)
            return;
        double tFactor = (double) 1 / 1000 * time;
        Pos.x += V.x * tFactor;
        Pos.y += V.y * tFactor;
        Pos.z += V.z * tFactor;
        Rot.x += W.x * tFactor;
        Rot.y += W.y * tFactor;
        Rot.z += W.z * tFactor;
        // border check
        if (Pos.x <= ballRadius
                || Pos.x >= tableWidth - ballRadius) {
            Pos.x -= V.x * tFactor / 2;
            V.x *= -0.8;
            V.y *= 0.9;
        }
        if (Pos.y >= -ballRadius
                || Pos.y <= -tableLength + ballRadius) {
            Pos.y -= V.y * tFactor / 2;
            V.y *= -0.8;
            V.x *= 0.9;
        }
        // friction
        V.x -= frictionCoeff * V.x / V.length() * tFactor;
        V.y -= frictionCoeff * V.y / V.length() * tFactor;
        if (Math.abs(V.x) < 0.001 && Math.abs(V.y) < 0.001){
            state = 0;
            V.x = 0;
            V.y = 0;
        }
    }

    double getTargetAngle(Vec3 target) {
        double a = new Vec3(0, 1, 0).deltaAngle(new Vec3(target.x - Pos.x,
                target.y - Pos.y, target.z - Pos.z));
        if (target.x - Pos.x < 0)
            a = Math.toRadians(360) - a;
        return a;
    }

    Vec3 contactPoint(Vec3 pocket) {
        Vec3 targetVector = new Vec3(pocket.x - Pos.x, pocket.y - Pos.y,
                pocket.z - Pos.z);
        targetVector.normalize();
        return new Vec3(Pos.x - 2 * ballRadius * targetVector.x, Pos.y - 2
                * ballRadius * targetVector.y, ballRadius);
    }

    boolean hasNoLineTo(Vec3 target, ArrayList<Ball> ballsOnTable, Ball ballOn) {
        // target behind ballOn
        if (ballOn != null && Pos.distanceTo(ballOn.Pos) < Pos.distanceTo(target))
            return true;
        // if no obstructions, return true
        boolean result = true;
        // check against ballsontable
        Ball ball;
        for (int bi = 0; bi < ballsOnTable.size(); bi++) {
            ball = ballsOnTable.get(bi);
            // self collision
            if (ball.equals(this) || ball.equals(ballOn))
                continue;
            if (id == 7 && target == blackRPocket)
                Log.d("main", String.format("distancePointToLine = %f", distancePointToLine(ball.Pos, Pos, new Vec3(target.x - Pos.x,
                        target.y - Pos.y, target.z - Pos.z))));
            // if ball away from targetline
            if (distancePointToLine(ball.Pos, Pos, new Vec3(target.x - Pos.x,
                    target.y - Pos.y, target.z - Pos.z)) > 2 * ballRadius)
                continue;
            // ball within 90deg of target dir
            double deltaAngle = Math.abs(Math.toDegrees(getTargetAngle(target))
                    - Math.toDegrees(getTargetAngle(ball.Pos)));
            if (deltaAngle > 90 && deltaAngle < 270)
                continue;
            // ball "between" pos and target
            if (Pos.distanceTo(ball.Pos) > Pos.distanceTo(target) + 2
                    * ballRadius)
                continue;
            result = false;
            break;
        }
        return !result;
    }

    private double distancePointToLine(Vec3 P, Vec3 Q, Vec3 a) {
        //TODO: returns strange value.
        // in current usage, a is used as difference between two points, check on that first
        return new Vec3((P.y - Q.y) * a.z - (P.z - Q.z) * a.y, (P.z - Q.z)
                * a.x - (P.x - Q.x) * a.z, (P.x - Q.x) * a.y - (P.y - Q.y)
                * a.x).length()
                / a.length();
    }

    void draw(Main app, Paint paint, Canvas canvas) {
        paint.setStyle(Paint.Style.FILL);
        paint.setColor(getBallColor(value));
        canvas.drawCircle(app.screenX(Pos.x), app.screenY(Pos.y),
                (float) (ballRadius * app.screenScale), paint);
//                if (b == 0) {
//                    Ball cue = ballsOnTable.get(b);
//                    float xr = screenX(cue.Pos.x);
//                    float yr = screenY(cue.Pos.y);
//                    xr += Math.cos(1);
//                    yr += Math.cos(2);
//                    paint.setColor(Color.RED);
//                    canvas.drawCircle(xr, yr, 2, paint);
//                }
    }

    Ball cloneBall() {
        Ball b = new Ball(0, 0, value, id);
        b.Pos = new Vec3(Pos.x, Pos.y, Pos.z);
        b.Rot = new Vec3(Rot.x, Rot.y, Rot.z);
        b.state = state;
        b.V = new Vec3(V.x, V.y, V.z);
        b.W = new Vec3(W.x, W.y, W.z);
        return b;
    }

    @Override
    @NonNull
    public String toString() {
        switch (id) {
            case -1:
                return "none";
            case 0:
                return "Cueball";
            case 2:
                return "yellow";
            case 3:
                return "green";
            case 4:
                return "brown";
            case 5:
                return "blue";
            case 6:
                return "pink";
            case 7:
                return "black";
            default:
                return "red";
        }
    }
}
