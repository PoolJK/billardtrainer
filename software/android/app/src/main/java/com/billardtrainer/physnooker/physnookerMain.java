package com.billardtrainer.physnooker;

import android.annotation.SuppressLint;
import android.app.*;
import android.content.*;
import android.graphics.*;
import android.graphics.Paint.*;
import android.graphics.drawable.*;
import android.net.Uri;
import android.os.*;
import android.util.Log;
import android.view.*;
import android.view.ViewGroup.*;
import android.widget.*;
import java.util.*;

import static com.physnooker.Cons.*;

public class physnookerMain extends Activity {

    static boolean first;

    public static void simit() {
        simming = true;
        long t0 = System.nanoTime();
        int n = 0;
        double t, sim_time;
        bNode node;
        Vec3 p, v, w;
        first = true;
        boolean moving;
        sim_time = 0;
        double[] nextT = new double[22];
        do {
            sim_time += 0.001;
            moving = false;
            for (Ball b : ballsOnTable) {
                if (!b.onTable)
                    continue;
                node = b.nodes.get(b.nodes.size() - 1);
                if (node.state == STATE_STILL)
                    continue;
                moving = true;
                // get movement at sim_time
                p = b.getPos(sim_time - node.time);
                v = b.getV(sim_time - node.time);
                w = b.getW(sim_time - node.time);
                if (b.checkCollision(sim_time - node.time))
                    b.addNode(p, v, w, sim_time);
                else if (nextT[b.id] <= sim_time) {
                    nextT[b.id] = node.time
                            + getMaxT(node.P0, node.V0, node.Vc0, node.state, b.id);
                    b.nodes.add(new bNode(p, v, w, sim_time));
                }
            }
        } while (moving && sim_time < 2);
        Log.v("Main", String.format("simtime: %s", sim_time));
        simtime += (System.nanoTime() - t0) / 1E6;
        simcount++;
        simming = false;
        handler.sendEmptyMessage(DRAW);
    }


    public static double getMaxT(Vec3 p0, Vec3 v0, Vec3 vc0, int state,
                                 int ballId) {
        double a, b, c, D, p, q, t, tn;
        double tr1, tr2, tl1, tl2, tb1, tb2, tt1, tt2;
        double tballmin;
        p = -2d / (friction_cloth);
        q = 0;
        D = 0;
        // long t0, t1;
        double[] tball;
        switch (state) {
            case STATE_ROLLING:
                // t0 = System.nanoTime();
                // no coll
                tn = length(v0) / friction_cloth_roll;
                // right cushion
                a = v0.x * 0.5 * friction_cloth_roll / length(v0);
                b = -v0.x;
                c = -(p0.x - tableWidth + ballRadius);
                if (a == 0) {
                    if (b != 0) {
                        tr1 = -c / b;
                        if (tr1 < 0)
                            tr1 = 1000;
                    } else
                        tr1 = 1000;
                } else {
                    p = b / a;
                    q = c / a;
                    D = p * p - 4d * q;
                    if (D >= 0) {
                        tr1 = -p / 2 + Math.sqrt(p * p / 4 - q);
                        tr2 = -p / 2 - Math.sqrt(p * p / 4 - q);
                    } else
                        tr1 = tr2 = 1000;
                    tr1 = tr1 < dprecision ? (tr2 < dprecision ? 1000 : tr2)
                            : (tr2 < dprecision ? tr1 : Math.min(tr1, tr2));
                }
                // left cushion
                c = -(p0.x - ballRadius);
                if (a == 0) {
                    if (b != 0) {
                        tl1 = -c / b;
                        if (tl1 < 0)
                            tl1 = 1000;
                    } else
                        tl1 = 1000;
                } else {
                    p = b / a;
                    q = c / a;
                    D = p * p - 4d * q;
                    if (D >= 0) {
                        tl1 = -p / 2 + Math.sqrt(p * p / 4 - q);
                        tl2 = -p / 2 - Math.sqrt(p * p / 4 - q);
                    } else
                        tl1 = tl2 = 1000;
                    tl1 = tl1 < dprecision ? (tl2 < dprecision ? 1000 : tl2)
                            : (tl2 < dprecision ? tl1 : Math.min(tl1, tl2));
                }
                // bottom cushion
                a = v0.y * 0.5 * friction_cloth_roll / length(v0);
                b = -v0.y;
                c = -(p0.y + tableLength - ballRadius);
                if (a == 0) {
                    if (b != 0) {
                        tb1 = -c / b;
                        if (tb1 < 0)
                            tb1 = 1000;
                    } else
                        tb1 = 1000;
                } else {
                    p = b / a;
                    q = c / a;
                    D = p * p - 4d * q;
                    if (D >= 0) {
                        tb1 = -p / 2 + Math.sqrt(p * p / 4 - q);
                        tb2 = -p / 2 - Math.sqrt(p * p / 4 - q);
                    } else
                        tb1 = tb2 = 1000;
                    tb1 = tb1 < dprecision ? (tb2 < dprecision ? 1000 : tb2)
                            : (tb2 < dprecision ? tb1 : Math.min(tb1, tb2));
                }
                // top cushion
                c = -(p0.y + ballRadius);
                if (a == 0) {
                    if (b != 0) {
                        tt1 = -c / b;
                        if (tt1 < 0)
                            tt1 = 1000;
                    } else
                        tt1 = 1000;
                } else {
                    p = b / a;
                    q = c / a;
                    D = p * p - 4d * q;
                    if (D >= 0) {
                        tt1 = -p / 2 + Math.sqrt(p * p / 4 - q);
                        tt2 = -p / 2 - Math.sqrt(p * p / 4 - q);
                    } else
                        tt1 = tt2 = 1000;
                    tt1 = tt1 < dprecision ? (tt2 < dprecision ? 1000 : tt2)
                            : (tt2 < dprecision ? tt1 : Math.min(tt1, tt2));
                }
                t = Math.min(Math.min(Math.min(Math.min(tt1, tr1), tb1), tl1), tn);
                // t1 = System.nanoTime();
                // toast("calc t = " + (t1 - t0) + "ns");
                break;
            case STATE_SPINNING:
                tn = 2.0 / 7.0 * length(vc0) / friction_cloth;
                // right cushion
                a = vc0.x * 0.5 * friction_cloth / length(vc0);
                b = -v0.x;
                c = -(p0.x - tableWidth + ballRadius);
                if (a == 0) {
                    if (b != 0) {
                        tr1 = -c / b;
                        if (tr1 < 0)
                            tr1 = 1000;
                    } else
                        tr1 = 1000;
                } else {
                    p = b / a;
                    q = c / a;
                    D = p * p - 4d * q;
                    if (D >= 0) {
                        tr1 = -p / 2 + Math.sqrt(p * p / 4 - q);
                        tr2 = -p / 2 - Math.sqrt(p * p / 4 - q);
                    } else
                        tr1 = tr2 = 1000;
                    tr1 = tr1 < dprecision ? (tr2 < dprecision ? 1000 : tr2)
                            : (tr2 < dprecision ? tr1 : Math.min(tr1, tr2));
                }
                t = Math.min(tn, tr1);
                // left cushion
                c = -(p0.x - ballRadius);
                if (a == 0) {
                    if (b != 0) {
                        tl1 = -c / b;
                        if (tl1 < 0)
                            tl1 = 1000;
                    } else
                        tl1 = 1000;
                } else {
                    p = b / a;
                    q = c / a;
                    D = p * p - 4d * q;
                    if (D >= 0) {
                        tl1 = -p / 2 + Math.sqrt(p * p / 4 - q);
                        tl2 = -p / 2 - Math.sqrt(p * p / 4 - q);
                    } else
                        tl1 = tl2 = 1000;
                    tl1 = tl1 < dprecision ? (tl2 < dprecision ? 1000 : tl2)
                            : (tl2 < dprecision ? tl1 : Math.min(tl1, tl2));
                }
                t = Math.min(t, tl1);
                // bottom cushion
                a = vc0.y * 0.5 * friction_cloth / length(vc0);
                b = -v0.y;
                c = -(p0.y + tableLength - ballRadius);
                if (a == 0) {
                    if (b != 0) {
                        tb1 = -c / b;
                        if (tb1 < 0)
                            tb1 = 1000;
                    } else
                        tb1 = 1000;
                } else {
                    p = b / a;
                    q = c / a;
                    D = p * p - 4d * q;
                    if (D >= 0) {
                        tb1 = -p / 2 + Math.sqrt(p * p / 4 - q);
                        tb2 = -p / 2 - Math.sqrt(p * p / 4 - q);
                    } else
                        tb1 = tb2 = 1000;
                    tb1 = tb1 < dprecision ? (tb2 < dprecision ? 1000 : tb2)
                            : (tb2 < dprecision ? tb1 : Math.min(tb1, tb2));
                }
                t = Math.min(t, tb1);
                // top cushion
                c = -(p0.y + ballRadius);
                if (a == 0) {
                    if (b != 0) {
                        tt1 = -c / b;
                        if (tt1 < 0)
                            tt1 = 1000;
                    } else
                        tt1 = 1000;
                } else {
                    p = b / a;
                    q = c / a;
                    D = p * p - 4d * q;
                    if (D >= 0) {
                        tt1 = -p / 2 + Math.sqrt(p * p / 4 - q);
                        tt2 = -p / 2 - Math.sqrt(p * p / 4 - q);
                    } else
                        tt1 = tt2 = 1000;
                    tt1 = tt1 < dprecision ? (tt2 < dprecision ? 1000 : tt2)
                            : (tt2 < dprecision ? tt1 : Math.min(tt1, tt2));
                }
                t = Math.min(t, tt1);
                break;
            default:
                t = 1000;
        }
        // balls
        tballmin = 1000;
        tball = new double[ballsOnTable.size()];
        int bi = 0;
        bNode bn;
        for (Ball testb : ballsOnTable) {
            if (testb.id == ballId | !testb.onTable) {
                bi++;
                continue;
            }
            bn = testb.nodes.get(testb.nodes.size() - 1);
            tball[bi] = getCollisionTime(p0, v0, vc0, state, bn.P0, bn.V0,
                    bn.Vc0, bn.state, t);
            if (tball[bi] < tballmin)
                tballmin = tball[bi];
            bi++;
        }
        t = Math.min(t, tballmin);
        return t;
    }

    public static double getCollisionTime(Vec3 p0a, Vec3 v0a, Vec3 vc0a,
                                          int statea, Vec3 p0b, Vec3 v0b, Vec3 vc0b, int stateb, double tmax) {
        double fax, fbx, fay, fby;
        switch (statea) {
            case STATE_ROLLING:
                fax = 0.5 * friction_cloth_roll * v0a.x / length(v0a);
                fay = 0.5 * friction_cloth_roll * v0a.y / length(v0a);
                break;
            case STATE_SPINNING:
                fax = 0.5 * friction_cloth * vc0a.x / length(vc0a);
                fay = 0.5 * friction_cloth * vc0a.y / length(vc0a);
                break;
            default:
                fax = fay = 0;
        }
        switch (stateb) {
            case STATE_ROLLING:
                fbx = 0.5 * friction_cloth_roll * v0b.x / length(v0b);
                fby = 0.5 * friction_cloth_roll * v0b.y / length(v0b);
                break;
            case STATE_SPINNING:
                fbx = 0.5 * friction_cloth * vc0b.x / length(vc0b);
                fby = 0.5 * friction_cloth * vc0b.y / length(vc0b);
                break;
            default:
                fbx = fby = 0;
        }
        double dt = d(tmax / 100, 6), dist, dx, dy, ttest;
        for (ttest = 0; ttest <= tmax + dt; ttest += dt) {
            dx = p0a.x + ttest * v0a.x - ttest * ttest * fax
                    - (p0b.x + ttest * v0b.x - ttest * ttest * fbx);
            dy = p0a.y + ttest * v0a.y - ttest * ttest * fay
                    - (p0b.y + ttest * v0b.y - ttest * ttest * fby);
            dist = dx * dx + dy * dy;
            if (dist <= 4.0 * ballRadius * ballRadius) {
                dt /= 10.0;
                if (dt <= dprecision)
                    break;
                ttest -= 10.0 * dt;
            }
        }
        return ttest < dprecision ? 1000 : ttest;
    }

    public static void setCueballV() {
        Ball cue = ballsOnTable.get(0);
        cue.nodes.clear();
        double x = speed * Math.sin(Math.toRadians(angle));
        double y = speed * Math.cos(Math.toRadians(angle));
        if (Math.abs(x) < dprecision)
            x = 0;
        if (Math.abs(y) < dprecision)
            y = 0;
        setWx.setText("" + wx);
        setWy.setText("" + wy);
        cue.setW0(wx, wy, 0, 0);
        cue.setV0(x, y, 0, 0);
        cue.addNode(cue.Pos, cue.V0, cue.W0, 0);
    }

    public void draw() {
        long t0 = System.nanoTime();
        drawing = true;
        // draw Table
        // cloth
        paint.setStyle(Style.FILL);
        paint.setTextSize(20);
        canvas.drawARGB(255, 0, 0, 0);
        paint.setColor(Color.rgb(0, 140, 20));
        canvas.drawRect(sX(0), sY(0), sX(tableWidth), sY(-tableLength), paint);
        // lines
        paint.setColor(Color.WHITE);
        paint.setStyle(Paint.Style.STROKE);
        canvas.drawLine(sX(0), sY(-DDistance), sX(tableWidth), sY(-DDistance),
                paint);
        canvas.drawArc(new RectF(sX(yellowSpot.x), sY(yellowSpot.y + DRadius),
                        sX(greenSpot.x), sY(greenSpot.y - DRadius)), 180, 180, false,
                paint);
        // spots
        canvas.drawLine(sX(yellowSpot.x), sY(yellowSpot.y), sX(yellowSpot.x),
                sY(yellowSpot.y + 0.01f), paint);
        canvas.drawLine(sX(greenSpot.x), sY(greenSpot.y), sX(greenSpot.x),
                sY(greenSpot.y + 0.01f), paint);
        canvas.drawLine(sX(brownSpot.x), sY(brownSpot.y - 0.01f),
                sX(brownSpot.x), sY(brownSpot.y + 0.01f), paint);
        canvas.drawLine(sX(blueSpot.x - 0.01f), sY(blueSpot.y),
                sX(blueSpot.x + 0.01f), sY(blueSpot.y), paint);
        canvas.drawLine(sX(blueSpot.x), sY(blueSpot.y - 0.01f), sX(blueSpot.x),
                sY(blueSpot.y + 0.01f), paint);
        canvas.drawLine(sX(pinkSpot.x - 0.01f), sY(pinkSpot.y),
                sX(pinkSpot.x + 0.01f), sY(pinkSpot.y), paint);
        canvas.drawLine(sX(pinkSpot.x), sY(pinkSpot.y - 0.01f), sX(pinkSpot.x),
                sY(pinkSpot.y + 0.01f), paint);
        canvas.drawLine(sX(blackSpot.x - 0.01f), sY(blackSpot.y),
                sX(blackSpot.x + 0.01f), sY(blackSpot.y), paint);
        canvas.drawLine(sX(blackSpot.x), sY(blackSpot.y - 0.01f),
                sX(blackSpot.x), sY(blackSpot.y + 0.01f), paint);
        // angle, speed
        canvas.drawText("Angle = " + d(angle, 4) + "\nSpeed = " + d(speed, 4),
                100f, screenY - 20f, paint);
        // draw Balls
        bNode bn, bn2;
        Vec3 in;
        Path path;
        for (Ball b : ballsOnTable) {
            if (!b.onTable)
                continue;
            // draw ball
            paint.setStyle(Style.FILL);
            paint.setColor(getBallColor(b.value));
            canvas.drawCircle(sX(b.Pos.x), sY(b.Pos.y),
                    (float) (ballRadius * screenscale), paint);
            // draw projected line
            if (!b.nodes.isEmpty() & b.nodes.size() > 1)
                for (int n = 0; n < b.nodes.size() - 1; n++) {
                    bn = b.nodes.get(n);
                    bn2 = b.nodes.get(n + 1);
                    if (bn.state == STATE_ROLLING)
                        canvas.drawLine(sX(bn.P0.x), sY(bn.P0.y), sX(bn2.P0.x),
                                sY(bn2.P0.y), paint);
                    else if (bn.state == STATE_SPINNING) {
                        paint.setStyle(Style.STROKE);
                        path = new Path();
                        path.moveTo(sX(bn.P0.x), sY(bn.P0.y));
                        for (int i = 0; i < quadSimSteps; i++) {
                            in = b.getPos((bn2.time - bn.time) / quadSimSteps * i);
                            path.lineTo(sX(in.x), sY(in.y));
                        }
                        path.lineTo(sX(bn2.P0.x), sY(bn2.P0.y));
                        canvas.drawPath(path, paint);
                    }
                    paint.setColor(Color.RED);
                    paint.setStyle(Style.STROKE);
                    // canvas.drawLine(sX(bn.P0.x),sY(bn.P0.y),sX(bn2.P0.x),sY(bn2.P0.y),paint);
                    canvas.drawCircle(sX(bn2.P0.x), sY(bn2.P0.y),
                            (float) (ballRadius * screenscale), paint);
                    paint.setColor(getBallColor(b.value));

                    // draw node stats
                    /*
                     * canvas.drawText("t=" + d(bn.t, 2) + ", p: " + bn.P0 +
                     * ", state=" + bn.state, 70, 20 + n * 60, paint);
                     * canvas.drawText("v: " + bn.V0 + ", l=" + d(length(bn.V0),
                     * 3), 70, 40 + n * 60, paint); canvas.drawText( "vc0: " +
                     * bn.Vc0 + ", l=" + d(length(bn.Vc0), 3), 70, 60 + n * 60,
                     * paint); if (n == b.nodes.size() - 2) {
                     * canvas.drawText("t=" + d(bn2.t, 2) + ", p: " + bn2.P0
                     * + ", state=" + bn2.state, 70, 80 + n * 60, paint);
                     * canvas.drawText( "v: " + bn2.V0 + ", l=" +
                     * d(length(bn2.V0), 3), 70, 100 + n * 60, paint);
                     * canvas.drawText( "vc0: " + bn2.Vc0 + ", l=" +
                     * d(length(bn2.Vc0), 3), 70, 120 + n * 60, paint); }
                     */
                }
        }
        drawSurface.setBackground(new BitmapDrawable(getResources(), bitmap));
        drawing = false;
        drawTime += (System.nanoTime() - t0) / 1E6;
        drawCount++;
    }

    private static long drawTime = 0, drawCount = 0;

    private static class mHandler extends Handler {
        public mHandler() {
            super();
        }
    }

    public static float sX(double x) {
        if (portrait)
            return (float) (x * screenscale + screenoffset);
        else
            return 0f;
    }

    public static float sY(double y) {
        if (portrait)
            return (float) (-y * screenscale + 20);
        else
            return 0f;
    }

    public static double rX(float sX) {
        if (portrait)
            return (sX - screenoffset) / screenscale;
        else
            return 0f;
    }

    public static double rY(float sY) {
        if (portrait)
            return (sY - 20) / -screenscale;
        else
            return 0f;
    }

    public void fineSwitch(View view) {
        finemove = !finemove;
        fm.setText(finemove ? "fine" : "norm");
    }

    public void aimswitch(View view) {
        aimstate++;
        aimstate = aimstate > 2 ? 0 : aimstate;
        aimButton.setText(aimstate == 0 ? "move" : aimstate == 1 ? "aim"
                : "win");
    }

    public void resetBalls() {
        initTable();
        angle = 83.156;
        speed = 3.4299;
        wx = 0;
        wy = 0;
        setBallsOnTable(new int[] { 0, 7 });
        handler.sendEmptyMessage(SIM);
    }

    public void resetBalls(View view) {
        resetBalls();
    }

    public void removeBall(View view) {
        wx = Double.parseDouble(setWx.getText().toString());
        wy = Double.parseDouble(setWy.getText().toString());
        setCueballV();
        /*
         * if (activeBall == 0) return; for (Ball b : ballsOnTable) if (b.id ==
         * activeBall) { ballsOnTable.remove(b); if (activeBall == ballOn)
         * ballOn = 8; activeBall = 0;
         * tV.setText(Ball.getNameFromId(activeBall)); break; }
         */
        simit();
    }

    public void start(View view) {
        setCueballV();
        simit();
    }

    private static class customCanvas extends View {
        public static final int AIMSTATE_MOVING = 0;
        public static final int AIMSTATE_AIMING = 1;
        private static float startx, starty, oldx, oldy, x, y;
        private static double dx, dy, fact;
        private int newId = -1, bi;
        private boolean moving;
        private static Ball ball;

        public customCanvas(Context context) {
            super(context);
        }

        @Override
        public boolean onTouchEvent(MotionEvent e) {
            switch (e.getActionMasked()) {
                case MotionEvent.ACTION_DOWN:
                    oldx = startx = e.getX();
                    oldy = starty = e.getY();
                    newId = getIdFromPosition(rX(e.getX()), rY(e.getY()));
                    moving = false;
                    return true;
                case MotionEvent.ACTION_MOVE:
                    x = e.getX();
                    y = e.getY();
                    dx = rX(x) - rX(oldx);
                    dy = rY(y) - rY(oldy);
                    oldx = x;
                    oldy = y;
                    if (Math.abs(x - startx) < MIN_MOVEMENT
                            & Math.abs(y - starty) < MIN_MOVEMENT && !finemove
                            & aimstate == 0)
                        return true;
                    else
                        moving = true;
                    fact = finemove ? 0.1 : 1;
                    dx *= fact;
                    dy *= fact;
                    if (aimstate == AIMSTATE_MOVING) { // moving
                        for (bi = 0; bi < ballsOnTable.size(); bi++) {
                            ball = ballsOnTable.get(bi);
                            if (ball.id == activeBall) {
                                if (ball.Pos.x + dx < tableWidth - ballRadius
                                        && ball.Pos.x + dx > ballRadius)
                                    ball.Pos.x += dx;
                                if (ball.Pos.y + dy > -tableLength + ballRadius
                                        && ball.Pos.y + dy < -ballRadius)
                                    ball.Pos.y += dy;
                            }
                        }
                    } else if (aimstate == AIMSTATE_AIMING) { // aiming
                        if (Math.abs(x - startx) > Math.abs(y - starty))
                            angle += Math.toDegrees(dx) * 0.8;
                        else
                            speed += dy * 0.8;
                        if (speed <= 0)
                            speed = 0;
                        if (speed > 40)
                            speed = 40;
                        if (angle > 360)
                            angle -= 360;
                        else if (angle < 0)
                            angle += 360;
                    } else { // w in
                        if (Math.abs(x - startx) > Math.abs(y - starty))
                            wx += dx * 2;
                        else
                            wy += dy * 2;
                    }
                    handler.sendEmptyMessage(SIM);
                    return true;
                case MotionEvent.ACTION_UP:
                    if (moving) {
                        return moving = false;
                    }
                    if (newId != -1) {
                        if (newId == activeBall & activeBall != 0) {
                            // ballOn = activeBall;
                            activeBall = 0;
                            tV.setText(Ball.getNameFromId(activeBall));
                            return false;
                        } else {
                            activeBall = newId;
                            tV.setText(Ball.getNameFromId(activeBall));
                            return false;
                        }
                    }
                    return false;
            }
            return true;
        }
    }

    public static int getIdFromPosition(double x, double y) {
        int id = -1;
        double minDistance = 6 * ballRadius, distance;
        for (int bi = 0; bi < ballsOnTable.size(); bi++) {
            if (!ballsOnTable.get(bi).onTable)
                continue;
            distance = distance(ballsOnTable.get(bi).Pos, new Vec3(x, y,
                    ballRadius));
            if (distance < 5 * ballRadius & distance < minDistance) {
                minDistance = distance;
                id = ballsOnTable.get(bi).id;
            }
        }
        return id;
    }

    public static int getBallColor(int value) {
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

    public void initTable() {
        ballsOnTable.clear();
        // cueball
        ballsOnTable.add(new Ball(yellowSpot.x, blackSpot.y, 0, 0));
        // colors

        ballsOnTable.add(new Ball(yellowSpot.x, yellowSpot.y, 2, 2));
        ballsOnTable.add(new Ball(greenSpot.x, greenSpot.y, 3, 3));
        ballsOnTable.add(new Ball(brownSpot.x, brownSpot.y, 4, 4));
        ballsOnTable.add(new Ball(blueSpot.x, blueSpot.y, 5, 5));
        ballsOnTable.add(new Ball(pinkSpot.x, pinkSpot.y, 6, 6));

        ballsOnTable.add(new Ball(blackSpot.x, blackSpot.y, 7, 7));

        // reds

        double yd = Math.sqrt(3 * ballRadius * ballRadius);
        double yc = pinkSpot.y - precision;
        ballsOnTable.add(new Ball(pinkSpot.x, yc - yd, 1, 8));
        ballsOnTable.add(new Ball(pinkSpot.x - ballRadius, yc - 2 * yd, 1, 9));
        ballsOnTable.add(new Ball(pinkSpot.x + ballRadius, yc - 2 * yd, 1, 10));
        ballsOnTable.add(new Ball(pinkSpot.x - 2 * ballRadius, yc - 3 * yd, 1,
                11));
        ballsOnTable.add(new Ball(pinkSpot.x, yc - 3 * yd, 1, 12));
        ballsOnTable.add(new Ball(pinkSpot.x + 2 * ballRadius, yc - 3 * yd, 1,
                13));
        ballsOnTable.add(new Ball(pinkSpot.x - 3 * ballRadius, yc - 4 * yd, 1,
                14));
        ballsOnTable.add(new Ball(pinkSpot.x - 1 * ballRadius, yc - 4 * yd, 1,
                15));
        ballsOnTable.add(new Ball(pinkSpot.x + 1 * ballRadius, yc - 4 * yd, 1,
                16));
        ballsOnTable.add(new Ball(pinkSpot.x + 3 * ballRadius, yc - 4 * yd, 1,
                17));
        ballsOnTable.add(new Ball(pinkSpot.x - 4 * ballRadius, yc - 5 * yd, 1,
                18));
        ballsOnTable.add(new Ball(pinkSpot.x - 2 * ballRadius, yc - 5 * yd, 1,
                19));
        ballsOnTable.add(new Ball(pinkSpot.x, yc - 5 * yd, 1, 20));
        ballsOnTable.add(new Ball(pinkSpot.x + 2 * ballRadius, yc - 5 * yd, 1,
                21));
        ballsOnTable.add(new Ball(pinkSpot.x + 4 * ballRadius, yc - 5 * yd, 1,
                22));

    }

    public static void setBallsOnTable(int[] which) {
        for (Ball b : ballsOnTable)
            for (int i : which)
                if (b.id == i) {
                    b.onTable = true;
                    break;
                } else
                    b.onTable = false;
    }

    public static void toast(String msg) {
        mToast.setDuration(Toast.LENGTH_SHORT);
        mToast.setText(msg);
        mToast.show();
    }

    public static void toast(String msg, int i) {
        mToast.setDuration(Toast.LENGTH_LONG);
        mToast.setText(msg);
        mToast.show();
    }

    @Override
    public boolean onCreateOptionsMenu(Menu menu) {
        getMenuInflater().inflate(R.menu.main, menu);
        return true;
    }

    @SuppressLint("ShowToast")
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.main);

        tV = (TextView) findViewById(R.id.textView1);
        tV.setText(Ball.getNameFromId(activeBall));
        setWx = (EditText) findViewById(R.id.setWx);
        setWy = (EditText) findViewById(R.id.setWy);
        aimButton = (Button) findViewById(R.id.button3);
        aimButton.setText("aim");
        fm = (Button) findViewById(R.id.button6);
        linlay = (RelativeLayout) findViewById(R.id.linlay);
        ViewTreeObserver vto = linlay.getViewTreeObserver();
        vto.addOnPreDrawListener(new ViewTreeObserver.OnPreDrawListener() {
            @Override
            public boolean onPreDraw() {
                if (!screenSet) {
                    // dimensions of relative Layout View
                    // padding of 20 + 20
                    screenX = linlay.getMeasuredWidth();
                    // Y size - button heights
                    screenY = linlay.getMeasuredHeight();
                    screenscale = Math.min((screenX - 40) / tableWidth,
                            (screenY - 100) / tableLength);
                    screenoffset = (screenX - tableWidth * screenscale) / 2;
                    screenSet = true;
                    bitmap = Bitmap.createBitmap(screenX, screenY,
                            Bitmap.Config.ARGB_8888);
                    canvas = new Canvas(bitmap);
                }
                return true;
            }
        });
        ballsOnTable = new ArrayList<Ball>();
        drawSurface = new customCanvas(this);
        RelativeLayout.LayoutParams params = new RelativeLayout.LayoutParams(
                LayoutParams.WRAP_CONTENT, LayoutParams.WRAP_CONTENT);
        linlay.addView(drawSurface, 0, params);
        drawSurface.requestFocus();
        handler = new mHandler() {
            @Override
            public void handleMessage(Message msg) {
                switch (msg.what) {
                    case TOAST_MESSAGE:
                        toast((String) msg.obj);
                        break;
                    case TOAST_MESSAGE_LONG:
                        toast((String) msg.obj, 1);
                        break;
                    case DRAW:
                        if (!drawing)
                            draw();
                        break;
                    case SIM:
                        if (!simming) {
                            setCueballV();
                            simit();
                        } else
                            System.out.println("already Simming");
                        break;
                }
            }
        };
        paint.setStrokeWidth(0);
        paint.setAntiAlias(true);

        mToast = Toast.makeText(this, "", Toast.LENGTH_LONG);
        mToast.setGravity(Gravity.TOP, 0, 0);
        // ATTENTION: This was auto-generated to handle app links.
        Intent appLinkIntent = getIntent();
        String appLinkAction = appLinkIntent.getAction();
        Uri appLinkData = appLinkIntent.getData();
    }

    @Override
    public void onResume() {
        super.onResume();
        Settings = getSharedPreferences("physnooker", 0);
        for (Ball b : ballsOnTable) {
            b.Pos.x = Settings.getFloat("pxid" + b.id, (float) b.Pos.x);
            b.Pos.y = Settings.getFloat("pyid" + b.id, (float) b.Pos.y);
            b.Pos.z = Settings.getFloat("pzid" + b.id, (float) b.Pos.z);
            b.onTable = Settings.getBoolean("oTid" + b.id, b.onTable);
            if (length(b.Pos) == 0 & b.onTable)
                b.onTable = false;
        }
        angle = Settings.getFloat("angle", 180f);
        speed = Settings.getFloat("speed", 2f);
        resetBalls();
    }

    @Override
    public void onPause() {
        super.onPause();

        ed = Settings.edit();
        for (Ball b : ballsOnTable) {
            ed.putFloat("pxid" + b.id, (float) b.Pos.x);
            ed.putFloat("pyid" + b.id, (float) b.Pos.y);
            ed.putFloat("pzid" + b.id, (float) b.Pos.z);
            ed.putBoolean("oTid" + b.id, b.onTable);
        }
        ed.putFloat("angle", (float) angle);
        ed.putFloat("speed", (float) speed);
        ed.apply();

        // System.out.println("avg simtime=" + simtime / simcount + "ms");
        // System.out.println("avf drawtime=" + drawTime / drawCount + "ms");
        System.exit(0);
    }

    private static final int MIN_MOVEMENT = 4;
    private static final int TOAST_MESSAGE = 0;
    private static final int TOAST_MESSAGE_LONG = 2;
    private static final int DRAW = 1;
    private static final int SIM = 99;

    private static long simcount, simtime;

    private static ArrayList<Ball> ballsOnTable;
    private static int activeBall = 0;

    private static TextView tV;
    private static Toast mToast;
    private static EditText setWx, setWy;
    private static Button aimButton, fm;
    private static RelativeLayout linlay;
    private static customCanvas drawSurface;
    private static int screenX, screenY;
    private static double screenscale;
    private static double screenoffset;
    private static boolean screenSet = false;
    private static int aimstate = 1;
    private static boolean finemove = false;
    private static boolean drawing = false;
    private static boolean simming = false;
    private static boolean portrait = true;
    private static mHandler handler;
    private SharedPreferences Settings;
    private SharedPreferences.Editor ed;
    // private int ballOn = 5;
    private static double angle, speed, wx, wy;

    private static Bitmap bitmap;
    private static Canvas canvas;
    private static Paint paint = new Paint();
}
