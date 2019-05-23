package com.billardtrainer;

import android.graphics.Canvas;
import android.graphics.Color;
import android.graphics.Paint;
import android.graphics.Path;
import android.support.annotation.NonNull;
import android.util.Log;

import org.json.JSONException;
import org.json.JSONObject;

import java.util.ArrayList;
import java.util.Locale;

import static com.billardtrainer.Cons.*;

class bNode {

    private static final String TAG = "bNode";

    Vec3 P0, V0, Vc0;
    private Vec3 W0;
    private bNode previousNode;
    private int ballId;
    int state;
    double t, collisionTime, inherentTime;

    bNode(Vec3 p, Vec3 v, Vec3 w, double t, int ballId, bNode previousNode) {
        this.previousNode = previousNode;
        this.ballId = ballId;
        this.t = t;
        collisionTime = -1;
        P0 = p;
        setV0(v, w);
    }

    /**
     * set initial speeds
     *
     * @param v0 velocity
     * @param w0 angular velocity
     */
    void setV0(Vec3 v0, Vec3 w0) {
        V0 = v0;
        W0 = w0;
        // Vc0 according to https://billiards.colostate.edu/technical_proofs/new/TP_A-4.pdf (14)
        Vc0 = new Vec3(V0.x - ballRadius * W0.y, V0.y + ballRadius * W0.x, 0);
        if (Math.abs(Vc0.x) < precision)
            Vc0.x = 0;
        if (Math.abs(Vc0.y) < precision)
            Vc0.y = 0;
        state = Math.abs(V0.length() - ballRadius * W0.length()) > precision ? STATE_SLIDING
                : V0.length() > precision ? STATE_ROLLING : STATE_STILL;
        // log for cueball
        if (ballId == 1 && Main.sim_running)
            Log.v(TAG, String.format(Locale.ROOT, "V0=%.1f W0=%.1f V0-R*W0=%.1f state=%s",
                    V0.length(), W0.length(), V0.length() - ballRadius * W0.length(), getState()));
    }

    bNode nextNode(double t) {
        if (state == STATE_STILL)
            return new bNode(P0, V0, W0, t, ballId, this);
        else
            // TODO: states
            return new bNode(getPos(t), getVel(t), getW(t), this.t + t, ballId, this);
    }

    /**
     * Get the next state change t, excluding collisions
     * reference: https://billiards.colostate.edu/technical_proofs/TP_4-1.pdf
     *
     * @return double t = next state change [s]
     */
    double getNextInherentT() {
        switch (state) {
            case STATE_ROLLING:
                // return t when ball comes to rest
                // roll shot: w = v / R
                inherentTime = V0.length() / (frictionClothRoll);
                break;
            case STATE_STUN:
                // return t when ball starts to roll
                // TODO: stun shot ts: check if w0 <= 0 (stun will develop)
                // stun or draw: w <= v / R
                // for a stun shot w = 0, this would be 0
                // for a follow shot w > v / R, stun will not develop
                // 2 * R * (-w) / (5 * u * g)
                // TODO: for now, go to sliding...
            case STATE_SLIDING:
                // https://billiards.colostate.edu/technical_proofs/new/TP_A-4.pdf (20)
                // return t when starting to roll TODO: stun
                // TODO: test: can be positive or negative (large W0)?
                // 2 * vc / (7*u*g)
                inherentTime = 2 * Vc0.length() / (7 * frictionClothSpin);
                break;
            default:
                // state_still
                inherentTime = t;
        }
        return inherentTime;
    }

    /**
     * Get time of next collision if any
     *
     * @param ballsOnTable balls on table
     * @return time [s]
     */
    double getNextCollisionT(ArrayList<Ball> ballsOnTable) {
        switch (state) {
            case STATE_ROLLING:
                for (Ball ball : ballsOnTable) {
                    if (ball.getNode(t).equals(this))
                        continue;
                    double cT = ball.getNode(t).getCollisionTime(this);
                    if (cT > 0) {
                        collisionTime = cT;
                        Log.v("bNode", String.format(Locale.ROOT, "balls collide: id1=%d id2=%d coll_t=%.2f", this.ballId, ball.id, collisionTime));
                    }
                }
                break;
            case STATE_STUN:
            case STATE_SLIDING:
            default:
                return t + 10000;
        }
        return collisionTime;
    }

    private double getCollisionTime(bNode node) {
        collisionTime = Solver.getCollisionTime(this, node);
        return collisionTime;
    }

    private Vec3 getPos(double t) {
        double vc0 = Vc0.length();
        double v0 = V0.length();
        double f;
        switch (state) {
            case STATE_ROLLING:
                f = v0 == 0 ? 0 : 0.5 * frictionClothRoll * t * t / v0;
                return new Vec3(P0.x + V0.x * t - f * V0.x,
                        P0.y + V0.y * t - f * V0.y, P0.z);
            case STATE_STUN:
                // TODO
            case STATE_SLIDING:
                f = vc0 == 0 ? 0 : 0.5 * frictionClothSpin * t * t / vc0;
                return new Vec3(P0.x + V0.x * t - f * Vc0.x,
                        P0.y + V0.y * t - f * Vc0.y, P0.z);
            default:
                return P0;
        }
    }

    private Vec3 getVel(double t) {
        double v0 = V0.length();
        double vc0 = Vc0.length();
        double f;
        switch (state) {
            case STATE_ROLLING:
                f = v0 == 0 ? 0 : frictionClothRoll * t / v0;
                return new Vec3(V0.x - f * V0.x, V0.y - f * V0.y, 0);
            case STATE_STUN:
                // TODO
            case STATE_SLIDING:
                f = vc0 == 0 ? 0 : frictionClothSpin * t / vc0; // [mm/s^2*s/(mm/s)] = []
                return new Vec3(V0.x - f * Vc0.x, V0.y - f * Vc0.y, 0);
            default:
                return V0;
        }
    }

    private Vec3 getW(double t) {
        // https://billiards.colostate.edu/technical_proofs/new/TP_A-4.pdf
        double w0 = W0.length();
        double vc0 = Vc0.length();
        double f;
        switch (state) {
            case STATE_ROLLING:
                f = frictionClothRoll * t / (w0 * ballRadius);
                return new Vec3(W0.x - f * W0.x, W0.y - f * W0.y, W0.z - f * W0.z);
            case STATE_STUN:
                // TODO
            case STATE_SLIDING:
                f = vc0 == 0 ? 0 : -5f / 2f * frictionClothSpin * t / (ballRadius * vc0);
                // TODO: W.z?!?
                return new Vec3(W0.x - f * Vc0.y, W0.y - f * Vc0.x, W0.z - f * W0.z);
            default:
                return W0;
        }
    }

    double getTargetAngle(Vec3 target) {
        double a = new Vec3(0, 1, 0).deltaAngle(new Vec3(target.x - P0.x,
                target.y - P0.y, target.z - P0.z));
        if (target.x - P0.x < 0)
            a = Math.toRadians(360) - a;
        return a;
    }

    Vec3 contactPoint(Vec3 pocket) {
        Vec3 targetVector = new Vec3(pocket.x - P0.x, pocket.y - P0.y,
                pocket.z - P0.z);
        targetVector.normalize();
        return new Vec3(P0.x - 2 * ballRadius * targetVector.x, P0.y - 2
                * ballRadius * targetVector.y, ballRadius);
    }

    boolean hasNoLineTo(Vec3 target, ArrayList<Ball> ballsOnTable, Ball ballOn) {
        // target behind ballOn
        if (ballOn != null && P0.distanceTo(ballOn.Pos) < P0.distanceTo(target))
            return true;
        // if no obstructions, return true
        boolean result = true;
        // check against ballsontable
        Ball ball;
        for (int bi = 0; bi < ballsOnTable.size(); bi++) {
            ball = ballsOnTable.get(bi);
            // self collision
            if (ball.id == this.ballId || ball.equals(ballOn))
                continue;
            // if ball away from targetline
            if (distancePointToLine(ball.Pos, P0, new Vec3(target.x - P0.x,
                    target.y - P0.y, target.z - P0.z)) > 2 * ballRadius)
                continue;
            // ball within 90deg of target dir
            double deltaAngle = Math.abs(Math.toDegrees(getTargetAngle(target))
                    - Math.toDegrees(getTargetAngle(ball.Pos)));
            if (deltaAngle > 90 && deltaAngle < 270)
                continue;
            // ball "between" pos and target
            if (P0.distanceTo(ball.Pos) > P0.distanceTo(target) + 2
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

    private String getState() {
        switch (state) {
            case STATE_STILL:
                return "still";
            case STATE_ROLLING:
                return "rolling";
            case STATE_STUN:
                return "stun";
            case STATE_SLIDING:
                return "sliding";
            default:
                return "none";
        }
    }

    void draw(Main app, Paint paint, Canvas canvas) {
        // ghost outline
        paint.setStyle(Paint.Style.STROKE);
        paint.setColor(Color.WHITE);
        canvas.drawCircle(app.screenX(P0.x), app.screenY(P0.y),
                (float) (ballRadius * app.screenScale), paint);
        if (previousNode != null) {
            // line from previous
            if (previousNode.state == STATE_ROLLING)
                canvas.drawLine(app.screenX(previousNode.P0.x), app.screenY(previousNode.P0.y),
                        app.screenX(P0.x), app.screenY(P0.y), paint);
            else if (previousNode.state == STATE_SLIDING) {
                Path path = new Path();
                Vec3 simStep = previousNode.P0;
                path.moveTo(app.screenX(simStep.x), app.screenY(simStep.y));
                for (int i = 0; i < quadSimSteps; i++) {
                    simStep = previousNode.getPos((t - previousNode.t) / quadSimSteps * i);
                    path.lineTo(app.screenX(simStep.x), app.screenY(simStep.y));
                }
                path.lineTo(app.screenX(P0.x), app.screenY(P0.y));
                canvas.drawPath(path, paint);
            }
        }
    }

    void addJSON(JSONObject ghosts, JSONObject lines) {
        JSONObject n = new JSONObject();
        try {
            n.put("x", (int) P0.x);
            n.put("y", (int) P0.y);
            ghosts.put(String.format(Locale.ROOT, "%d", ghosts.length()), n);
            if (previousNode != null) {
                //TODO: curveball
                JSONObject l = new JSONObject();
                l.put("x1", (int) previousNode.P0.x);
                l.put("y1", (int) previousNode.P0.y);
                l.put("x2", (int) P0.x);
                l.put("y2", (int) P0.y);
                lines.put(String.format(Locale.ROOT, "%d", lines.length()), l);
            }
        } catch (JSONException e) {
            e.printStackTrace();
        }
    }

    @NonNull
    @Override
    public String toString() {
        return String.format(Locale.ROOT, "state=%s, P=%s, V0=%s, Vc0=%s, W=%s, t=%.2f", getState(), P0, V0, Vc0, W0, t);
    }
}
