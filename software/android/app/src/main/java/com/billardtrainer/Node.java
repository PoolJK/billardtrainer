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

import static com.billardtrainer.Constants.*;

class Node {

    private static final String TAG = "Node";

    Vec3 P0, V0, Vc0;
    private Ball ball;
    private Vec3 W0;
    private Node previousNode;
    int state;
    double t, collisionTime, inherentTime;

    Node(Vec3 p, Vec3 v, Vec3 w, double t, Ball ball, Node previousNode) {
        this.previousNode = previousNode;
        this.ball = ball;
        this.t = t;
        collisionTime = -1;
        this.P0 = p;
        setV0(v, w);
    }

    /**
     * Sets initial speeds.
     * Calculates relative speed of contact point between ball and table Vc0.
     * Sets state based on V - R x W
     *
     * @param v0 Initial velocity
     * @param w0 Initial angular velocity
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
        if (ball.value == 0)
            Log.v(TAG, String.format(Locale.ROOT, "V0=%.1f W0=%.1f V0-R*W0=%.1f state=%s",
                    V0.length(), W0.length(), V0.length() - ballRadius * W0.length(), getState()));
    }

    /**
     * Get a new Node at time t
     *
     * @param t Time [ms]
     * @return New Node at time t
     */
    Node nextNode(double t) {
        if (state == STATE_STILL)
            return new Node(P0, V0, W0, t, ball, this);
        else
            // TODO: states
            return new Node(getPos(t), getVel(t), getW(t), this.t + t, ball, this);
    }

    /**
     * Get the next motion inherent state change t, excluding collisions.
     *
     * @return Next state change or time of this node if state == STILL [s]
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
     * @param ballsOnTable Balls on table
     * @return Time of collision or arbitrarily high number [s]
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
                        Log.v("Node", String.format(Locale.ROOT, "balls collide: id1=%d id2=%d coll_t=%.2f", this.ball.id, ball.id, collisionTime));
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

    /**
     * Calculate the actual collision time via the Solver class
     *
     * @param node The node to check against
     * @return Collision time [s] or -1
     */
    private double getCollisionTime(Node node) {
        collisionTime = Solver.getCollisionTime(this, node);
        return collisionTime;
    }

    /**
     * Get position after time t, calculated from this node base
     *
     * @param t Time [s]
     * @return Position at time t
     */
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

    /**
     * Get velocity after time t, calculated from this node base
     *
     * @param t Time [s]
     * @return Velocity at time t
     */
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

    /**
     * Get angular velocity after time t, calculated from this node base
     *
     * @param t Time [s]
     * @return Angular velocity at time t
     */
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

    /**
     * Calculate angle between (0, 1, 0) and the Vec3 to the target.
     *
     * @param target Vec3 to project to
     * @return Angle in radians (I think)
     */
    double getTargetAngle(Vec3 target) {
        double a = new Vec3(0, 1, 0).deltaAngle(new Vec3(target.x - P0.x,
                target.y - P0.y, target.z - P0.z));
        if (target.x - P0.x < 0)
            a = Math.toRadians(360) - a;
        return a;
    }

    /**
     * Calculate the contact point for a given pocket
     *
     * @param pocket Pocket to calculate for
     * @return The contact point as Vec3
     */
    Vec3 contactPoint(Vec3 pocket) {
        Vec3 targetVector = new Vec3(pocket.x - P0.x, pocket.y - P0.y,
                pocket.z - P0.z);
        targetVector.normalize();
        return new Vec3(P0.x - 2 * ballRadius * targetVector.x, P0.y - 2
                * ballRadius * targetVector.y, ballRadius);
    }

    /**
     * Reachable check for simulation.
     *
     * @param target       The ghost ball target
     * @param ballsOnTable Balls on table to check blocks
     * @param ballOn       The ball on
     * @return True if some ball blocks the path to target or target is behind ballon, False otherwise
     */
    boolean hasNoLineTo(Vec3 target, ArrayList<Ball> ballsOnTable, Ball ballOn) {
        // target behind ballOn
        if (ballOn != null && P0.distanceTo(ballOn.Pos) < P0.distanceTo(target))
            return true;
        // assume ball is blocked
        boolean result = true;
        // check against ballsontable
        Ball ball;
        for (int bi = 0; bi < ballsOnTable.size(); bi++) {
            ball = ballsOnTable.get(bi);
            // self collision
            if (ball == this.ball || ball.equals(ballOn))
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
            // nothing is blocking, so ball has a line:
            result = false;
            break;
        }
        return !result;
    }

    /**
     * Calculate the orthogonal distance of a point from a given line vector.
     *
     * @param P weiß nicht
     * @param Q so genau
     * @param a was hier passiert
     * @return denn irgendwas stimmt nicht
     */
    private double distancePointToLine(Vec3 P, Vec3 Q, Vec3 a) {
        //TODO: returns strange value.
        // in current usage, a is used as difference between two points, check on that first
        return new Vec3((P.y - Q.y) * a.z - (P.z - Q.z) * a.y, (P.z - Q.z)
                * a.x - (P.x - Q.x) * a.z, (P.x - Q.x) * a.y - (P.y - Q.y)
                * a.x).length()
                / a.length();
    }

    /**
     * Return a String equivalent of the current ball state
     *
     * @return State as String
     */
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

    /**
     * Draws this Node as ghost with a line from the previous node, if it is not null
     *
     * @param surfaceView    Reference to main surfaceView to be able to draw in UI
     * @param paint  Paint to use
     * @param canvas Canvas to draw on
     */
    void draw(CustomSurfaceView surfaceView, Paint paint, Canvas canvas) {
        // ghost outline
        paint.setStyle(Paint.Style.STROKE);
        paint.setColor(Color.WHITE);
        canvas.drawCircle(surfaceView.screenX(P0.x), surfaceView.screenY(P0.y),
                (float) (ballRadius * surfaceView.screenScale), paint);
        if (previousNode != null) {
            // line from previous
            if (previousNode.state == STATE_ROLLING)
                canvas.drawLine(surfaceView.screenX(previousNode.P0.x), surfaceView.screenY(previousNode.P0.y),
                        surfaceView.screenX(P0.x), surfaceView.screenY(P0.y), paint);
            else if (previousNode.state == STATE_SLIDING) {
                Path path = new Path();
                Vec3 simStep = previousNode.P0;
                path.moveTo(surfaceView.screenX(simStep.x), surfaceView.screenY(simStep.y));
                for (int i = 0; i < quadSimSteps; i++) {
                    simStep = previousNode.getPos((t - previousNode.t) / quadSimSteps * i);
                    path.lineTo(surfaceView.screenX(simStep.x), surfaceView.screenY(simStep.y));
                }
                path.lineTo(surfaceView.screenX(P0.x), surfaceView.screenY(P0.y));
                canvas.drawPath(path, paint);
            }
        }
    }

    /**
     * Add this node with its ghosts and lines to the JSONObjects
     *
     * @param ghosts Ghosts-JSONObject
     * @param lines  Lines-JSONObject
     */
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

    /**
     * String representation of this Node.
     *
     * @return String representation of this Node
     */
    @NonNull
    @Override
    public String toString() {
        return String.format(Locale.ROOT, "state=%s, P=%s, V0=%s, Vc0=%s, W=%s, t=%.2f", getState(), P0, V0, Vc0, W0, t);
    }
}
