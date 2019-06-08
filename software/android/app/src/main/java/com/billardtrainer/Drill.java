package com.billardtrainer;

// https://billiards.colostate.edu/technical-proof/

import android.annotation.SuppressLint;
import android.graphics.Canvas;
import android.graphics.Color;
import android.graphics.Paint;
import android.graphics.Paint.Style;
import android.graphics.RectF;
import android.os.Handler;
import android.os.Message;
import android.os.SystemClock;
import android.support.v4.app.FragmentActivity;
import android.util.Log;
import android.view.Menu;
import android.view.MotionEvent;
import android.view.View;
import android.widget.Button;
import android.widget.TextView;
import android.widget.Toast;

import org.json.JSONException;
import org.json.JSONObject;

import java.util.ArrayList;
import java.util.Iterator;
import java.util.Locale;

import static com.billardtrainer.Constants.DDistance;
import static com.billardtrainer.Constants.DRadius;
import static com.billardtrainer.Constants.ballRadius;
import static com.billardtrainer.Constants.blackSpot;
import static com.billardtrainer.Constants.blueSpot;
import static com.billardtrainer.Constants.brownSpot;
import static com.billardtrainer.Constants.greenSpot;
import static com.billardtrainer.Constants.pinkSpot;
import static com.billardtrainer.Constants.pockets;
import static com.billardtrainer.Constants.precision;
import static com.billardtrainer.Constants.tableLength;
import static com.billardtrainer.Constants.tableWidth;
import static com.billardtrainer.Constants.yellowSpot;
import static com.billardtrainer.Utils.getBallColor;
import static com.billardtrainer.Utils.getBallFromPosition;
import static com.billardtrainer.Utils.now;
import static java.lang.String.format;

@SuppressLint("Registered")
public class Drill extends FragmentActivity {
    // Debug
    private final String TAG = "Main";
    // private final boolean debug = BuildConfig.DEBUG;

    // Bluetooth
    private static BTService btService;

    // Handler Constants
    static final int TOAST_MESSAGE = 0;
    static final int DRAW = 1;
    static final int BT_SEND = 2;
    static final int BT_RECEIVE = 3;
    static final int BT_CONNECTED = 4;
    static final int BT_DISCONNECTED = 5;
    static final int DEVICE_READY = 6;
    static final int SIM_RESULT = 7;
    static final int CALC = 8;

    private static ArrayList<Ball> ballsOnTable = new ArrayList<>();
    private static Ball activeBall;
    private static int currentShot = -1;

    private TextView activeBallView;
    static Handler handler;
    private static int ballOn = 1;
    private static ArrayList<Shot> possibleShots;
    static boolean sim_running = false, drawing = false, calcing = false;

    private static boolean aiming;
    private Button aimButton;
    CustomSurfaceView surfaceView;

    @SuppressLint({"ClickableViewAccessibility", "HandlerLeak", "SetTextI18n"})
    Drill(CustomSurfaceView surfaceView) {
        surfaceView.setOnTouchListener(new canvasOnTouchListener());
        this.surfaceView = surfaceView;

        activeBallView = findViewById(R.id.active_ball_view);
        activeBallView.setText("Cueball");
        aimButton = findViewById(R.id.button3);
        aimButton.setText(getString(R.string.aimMode_move));

        if (ballsOnTable == null)
            ballsOnTable = new ArrayList<>();
        initTable();
        handler.sendEmptyMessage(CALC);
        if (handler == null) {
            handler = new Handler() {
                private boolean device_busy = false;

                @SuppressWarnings("unchecked")
                @Override
                public void handleMessage(Message msg) {
                    // Log.v(TAG, String.format("mHandler: %s", msg.toString()));
                    switch (msg.what) {
                        case SIM_RESULT:
                            ballsOnTable = (ArrayList<Ball>) msg.obj;
                            sim_running = false;
                            this.sendEmptyMessage(DRAW);
                            break;
                        case TOAST_MESSAGE:
                            toast((String) msg.obj);
                            break;
                        case CALC:
                            if (!sim_running)
                                calc(null);
                            break;
                        case DRAW:
                            if (!sim_running)
                                draw();
                            break;
                        case DEVICE_READY:
                            device_busy = false;
                            break;
                        case BT_SEND:
                            if (device_busy) {
                                toast("device busy");
                                Log.v("Handler", "device busy");
                                break;
                            }
                            device_busy = true;
                            if (btService != null && btService.isConnected())
                                btService.send(msg.obj.toString());
                            else
                                Log.d(TAG, "bluetooth not ready");
                            break;
                        case BT_RECEIVE:
                            handle_bt_message(msg.obj.toString());
                            // toast(msg.obj.toString());
                            break;
                        case BT_CONNECTED:
                            toast("bluetooth connected");
                            device_busy = false;
                            //handler.obtainMessage(BT_SEND, getTableAsJSONString()).sendToTarget();
                            break;
                        case BT_DISCONNECTED:
                            toast("bluetooth disconnected");
                            ballsOnTable.clear();
                            this.sendEmptyMessage(DRAW);
                            btService.connect();
                            break;
                        default:
                            super.handleMessage(msg);
                    }
                }
            };
        }
        if (possibleShots == null)
            possibleShots = new ArrayList<>();
    }

    @Override
    protected void onResume() {
        super.onResume();
        // Test case for physics sim
        // startSim(null);
        // Test case to simulate data from bluetooth:
        if (btService == null) {
            Log.d(TAG, "btService is null");
            btService = new BTService(handler);
        }
        btService.start();
    }

    @Override
    protected void onPause() {
        if (btService != null)
            btService.stopAll();
        btService = null;
        super.onPause();
    }

    int index = -1;

    private void handle_bt_message(String message) {
        if (message.contains("done")) {
            Log.v("main", "device ready");
            handler.sendEmptyMessage(DEVICE_READY);
            return;
        }
        if (message.contains("balls")) {
            ballsOnTable.clear();
            JSONObject j;
            try {
                j = new JSONObject(message);
                JSONObject balls = j.getJSONObject("balls");
                index = j.getInt("index");
                Log.d(TAG, "index = " + index);
                Iterator<String> iter = balls.keys();
                while (iter.hasNext()) {
                    String key = iter.next();
                    JSONObject ball = (JSONObject) balls.get(key);
                    addBallToTable(
                            ball.getDouble("x"),
                            ball.getDouble("y"),
                            key.equals("1") ? 7 : 0,
                            Integer.parseInt(key)
                    );
                }
                calc(null);
            } catch (JSONException e) {
                Log.e(TAG, "handle_bt_message: JSONError");
                e.printStackTrace();
            }
        } else {
            handler.obtainMessage(TOAST_MESSAGE, message).sendToTarget();
            Log.d(TAG, message);
        }
    }

    private double angle = 95; // [deg]
    private double speed = 1000; // [mm/s]

    @SuppressLint("SetTextI18n")
    private void setCueBallV0() {
        double x = speed * Math.sin(Math.toRadians(angle));
        double y = speed * Math.cos(Math.toRadians(angle));
        if (Math.abs(x) < precision)
            x = 0;
        if (Math.abs(y) < precision)
            y = 0;
        // get cueball
        Ball cue = ballsOnTable.get(0);
        for (Ball b : ballsOnTable)
            if (b.value == 0)
                cue = b;
        cue.getNode().setV0(new Vec3(x, y, 0),
                new Vec3(0, 0, 0)); // [mm/s]
        ((TextView) findViewById(R.id.Angle)).setText(format(Locale.ROOT, "%.0f°", angle));
        ((TextView) findViewById(R.id.Speed)).setText(format(Locale.ROOT, "%.0f mm/s\u00b2", speed));
    }

    @SuppressLint("SetTextI18n")
    private void setCueBallV0(double vx, double vy) {
        angle = Math.toDegrees(Math.atan(vx / vy));
        speed = new Vec3(vx, vy, 0).length() * 2;
        // get cueball
        Ball cue = ballsOnTable.get(0);
        for (Ball b : ballsOnTable)
            if (b.value == 0)
                cue = b;
        cue.getNode().setV0(new Vec3(vx, vy, 0),
                new Vec3(0, 0, 0)); // [mm/s]
        ((TextView) findViewById(R.id.Angle)).setText(format(Locale.ROOT, "%.0f°", angle));
        ((TextView) findViewById(R.id.Speed)).setText(format(Locale.ROOT, "%.0f mm/s\u00b2", speed));
    }

    public void resetSim(View view) {
        for (Ball ball : ballsOnTable)
            ball.clearNodes();
    }

    public void startSim(View view) {
        if (ballsOnTable.isEmpty()) {
            Log.d(TAG, "startSim: no balls on table");
            return;
        }
        if (sim_running) {
            Log.v(TAG, "startSim: sim running, start cancelled");
            return;
        }
        resetSim(null);
        SimThread sThread = new SimThread(ballsOnTable);
        sim_running = true;
        handler.post(sThread);
    }

    @SuppressWarnings({"unused", "SameParameterValue"})
    public void calc(View view) {
        if (calcing) {
            Log.d(TAG, "calc() while still calcing, returning.");
            return;
        }
        calcing = true;
        Log.d(TAG, "calc() start");
        long t0 = System.currentTimeMillis();
        Ball b, btp, cue;
        Vec3 contactPoint, a;
        if (ballsOnTable.isEmpty()) {
            Log.d(TAG, "ballsOnTable empty");
            handler.obtainMessage(TOAST_MESSAGE, "ballsOnTable empty").sendToTarget();
            return;
        }
        // get cueball
        cue = ballsOnTable.get(0);
        if (cue.value != 0)
            for (Ball ball : ballsOnTable)
                if (ball.value == 0) {
                    cue = ball;
                    Log.d(TAG, "cueball has id = " + cue.id + ", val = " + cue.value);
                    break;
                }
        // calculate possible shots
        btp = null;
        if (currentShot > -1) {
            btp = possibleShots.get(currentShot).ballToPot;
        }
        possibleShots.clear();
        currentShot = -1;
        for (int bi = 0; bi < ballsOnTable.size(); bi++) {
            b = ballsOnTable.get(bi);
            if (b == cue)
                // obviously, man
                continue;
            Log.d(TAG, "ball: " + b.toString());
            // only balls on
            if ((b.value != ballOn && ballOn < 8) || (ballOn > 7 && b.value != 1)) {
                Log.d(TAG, String.format(Locale.ROOT, "b.val=%d ballOn=%d, next ball", b.value, ballOn));
                continue;
            }
            // all pockets
            for (Vec3 pocket : pockets) {
                // if obstructed check next
                if (b.getNode().hasNoLineTo(pocket, ballsOnTable, null)) {
                    Log.d("calc", format("no line to %s", pocket.toString()));
                    continue;
                }
                // not obstructed get contact
                contactPoint = b.getNode().contactPoint(pocket);
                // cueball reaches contact
                if (cue.getNode().hasNoLineTo(contactPoint, ballsOnTable, b)) {
                    Log.d(TAG, format("pocket %s: cueball has no line to target point", pocket.toString()));
                    continue;
                }
                // angle < 88
                // angle calculated strangely sometimes?!?
                a = contactPoint.subtract(ballsOnTable.get(0).Pos);
                double deltaAngle = Math.toDegrees(a.deltaAngle(pocket
                        .subtract(b.Pos)));
                if (deltaAngle > 88) {
                    Log.d(TAG, format("pocket %s: angle to high: %f", pocket.toString(), deltaAngle));
                    // commented out while angle calculation is wrong
                    //continue;
                }
                possibleShots.add(new Shot(ballsOnTable, contactPoint, pocket, b));
                Log.d(TAG, format("shot to %s added", pocket.toString()));
                // try to select similar shot
                if (b == btp)
                    currentShot = possibleShots.size() - 1;
            }
        }
        if (!possibleShots.isEmpty()) {
            if (currentShot < 0) {
                currentShot = 0;
                Log.d(TAG, format("shot selected: %d", currentShot));
            }
            double vx = possibleShots.get(currentShot).target.x - possibleShots.get(currentShot).sBalls.get(0).Pos.x;
            double vy = possibleShots.get(currentShot).target.y - possibleShots.get(currentShot).sBalls.get(0).Pos.y;
            Log.d(TAG, format("vx=%f vy=%f", vx, vy));
            setCueBallV0(vx, vy);
        } else {
            // no available shot
            currentShot = -1;
            Log.d(TAG, "no shot found, trying once more");
        }
        // startSim(null);
        calcing = false;
        Log.d(TAG, format("calc() finished in %dms", System.currentTimeMillis() - t0));
        draw();
        //Log.d(TAG, format("calc() finished in %dms, calling handler: draw()", System.currentTimeMillis() - t0));
        //handler.sendEmptyMessage(DRAW);
    }

    public void resetBalls(View view) {
        initTable();
        startSim(view);
    }

    public void aimSwitch(View view) {
        aiming = !aiming;
        aimButton.setText(!aiming ? "move" : "aim");
    }

    public void device_ready(View view) {
        handler.sendEmptyMessage(DEVICE_READY);
        handler.sendEmptyMessage(DRAW);
    }

    private void cycleShot() {
        if (possibleShots.isEmpty())
            currentShot = -1;
        else {
            int old = currentShot;
            currentShot = currentShot < possibleShots.size() - 1 ? currentShot + 1 : 0;
            handler.obtainMessage(TOAST_MESSAGE, "old = " + old + " new = " + currentShot).sendToTarget();
            Log.d(TAG, "old = " + old + " new = " + currentShot);
            handler.sendEmptyMessage(DRAW);
        }
    }

    private class canvasOnTouchListener implements View.OnTouchListener {

        private float startX, startY, oldX, oldY, x, y;
        private double dx, dy;
        private Ball newBall;
        private boolean moving;

        @SuppressLint("ClickableViewAccessibility")
        @Override
        public boolean onTouch(View v, MotionEvent e) {
            if (ballsOnTable.size() > 0 && ballsOnTable.get(0).nodeCount() > 1)
                resetSim(null);
            int MIN_MOVEMENT = 4;
            x = e.getX();
            y = e.getY();
            switch (e.getActionMasked()) {
                case MotionEvent.ACTION_DOWN:
                    //Log.i("Main", "ACTION_DOWN moving=" + moving);
                    oldX = startX = x;
                    oldY = startY = y;
                    moving = false;
                    return true;
                case MotionEvent.ACTION_MOVE:
                    //Log.i("Main", "ACTION_MOVE moving=" + moving);
                    dx = surfaceView.rX(x) - surfaceView.rX(oldX);
                    dy = surfaceView.rY(y) - surfaceView.rY(oldY);
                    oldX = x;
                    oldY = y;
                    if (Math.abs(x - startX) < MIN_MOVEMENT
                            && Math.abs(y - startY) < MIN_MOVEMENT)
                        // movement too small, return
                        return true;
                    else
                        moving = true;
                    if (aiming) {
                        double fact = 0.001;
                        dx *= fact;
                        // update values of cueball then call sim
                        if (Math.abs(x - startX) > Math.abs(y - startY))
                            angle -= Math.toDegrees(dx);
                        else
                            speed -= dy;
                        if (speed <= 0)
                            speed = 0;
                        if (speed > 2000)
                            speed = 2000;
                        if (angle > 360)
                            angle -= 360;
                        else if (angle < 0)
                            angle += 360;
                        startSim(null);
                        return true;
                    }
                    if (activeBall != null) { // move active Ball
                        if (activeBall.Pos.x + dx < tableWidth - ballRadius
                                && activeBall.Pos.x + dx > ballRadius)
                            activeBall.Pos.x += dx;
                        if (activeBall.Pos.y + dy < tableLength - ballRadius
                                && activeBall.Pos.y + dy > ballRadius)
                            activeBall.Pos.y += dy;
                        // if moving cueball, update angle and speed
                        if (activeBall.value == 0)
                            setCueBallV0();
                        calc(null);
                        //startSim(null);
                    } else {
                        // activeBall = null, no moving
                        moving = false;
                        return true;
                    }
                    return true;
                case MotionEvent.ACTION_UP:
                    //Log.i("Main", "ACTION_UP moving=" + moving);
                    if (!moving) {
                        // not moving, "click"-event:
                        newBall = getBallFromPosition(surfaceView.rX(x), surfaceView.rY(y), ballsOnTable);
                        if (newBall == null || (newBall == activeBall && ballOn == activeBall.id)) {
                            cycleShot();
                            calc(null);
                            return false;
                        } else {
                            // ball clicked
                            if (newBall == activeBall) {
                                ballOn = activeBall.value;
                            } else {
                                activeBall = newBall;
                                activeBallView.setText(activeBall.toString());
                            }
                            calc(null);
                            return false;
                        }
                    } else {
                        // movement ended
                        calc(null);
                        //startSim(null);
                        moving = false;
                    }
                    return false;
            }
            return true;
        }
    }

    public void detect(View view) {
        JSONObject j = new JSONObject();
        try {
            j.put("what", "detect");
        } catch (JSONException e) {
            e.printStackTrace();
        }
        handler.obtainMessage(BT_SEND, j.toString()).sendToTarget();
    }

    @SuppressLint("DefaultLocale")
    private String getTableAsJSONString() {
        double t0 = now();
        JSONObject balls = new JSONObject();
        JSONObject lines = new JSONObject();
        JSONObject ghosts = new JSONObject();
        JSONObject all = new JSONObject();
        try {
            for (Ball ball : ballsOnTable)
                ball.addJSON(balls, lines, ghosts);
            if (possibleShots.size() > 0 && currentShot > -1)
                possibleShots.get(currentShot).addJSON(lines, ghosts);
            all.put("what", "show");
            all.put("index", 0);
            all.put("balls", balls);
            all.put("lines", lines);
            all.put("ghosts", ghosts);
        } catch (JSONException e) {
            e.printStackTrace();
            return "";
        }
        Log.v("main", format(Locale.ROOT, "JSON took %.0fms to generate",
                (SystemClock.currentThreadTimeMillis() - t0)));
        if (all.length() > 0)
            return all.toString();
        else
            return "";
    }

    void draw() {
        Canvas canvas;
        if (android.os.Build.VERSION.SDK_INT >= android.os.Build.VERSION_CODES.O) {
            canvas = surfaceView.surfaceHolder.lockHardwareCanvas();
        } else {
            canvas = surfaceView.surfaceHolder.lockCanvas();
        }
        if (canvas == null) {
            Log.d(TAG, "draw(): canvas null");
            return;
        }
        Paint paint = surfaceView.paint;
        Log.d(TAG, "draw()");
        if (drawing) {
            Log.d(TAG, "already drawing, returning");
            return;
        }
        drawing = true;
        double t0 = now();
        // draw Table
        // cloth
        paint.setStyle(Style.FILL);
        canvas.drawARGB(255, 0, 0, 0);
        paint.setColor(Color.rgb(0, 140, 20));
        canvas.drawRect(surfaceView.screenX(0), surfaceView.screenY(0), surfaceView.screenX(tableWidth), surfaceView.screenY(tableLength), paint);
        // lines
        paint.setColor(Color.WHITE);
        paint.setStyle(Style.STROKE);
        canvas.drawLine(surfaceView.screenX(0), surfaceView.screenY(DDistance), surfaceView.screenX(tableWidth), surfaceView.screenY(DDistance),
                paint);
        canvas.drawArc(new RectF(surfaceView.screenX(yellowSpot.x), surfaceView.screenY(yellowSpot.y - DRadius),
                        surfaceView.screenX(greenSpot.x), surfaceView.screenY(greenSpot.y + DRadius)), 180, 180, false,
                paint);
        // spots
        canvas.drawLine(surfaceView.screenX(yellowSpot.x), surfaceView.screenY(yellowSpot.y), surfaceView.screenX(yellowSpot.x),
                surfaceView.screenY(yellowSpot.y + 0.01f), paint);
        canvas.drawLine(surfaceView.screenX(greenSpot.x), surfaceView.screenY(greenSpot.y), surfaceView.screenX(greenSpot.x),
                surfaceView.screenY(greenSpot.y + 0.01f), paint);
        canvas.drawLine(surfaceView.screenX(brownSpot.x), surfaceView.screenY(brownSpot.y - 0.01f),
                surfaceView.screenX(brownSpot.x), surfaceView.screenY(brownSpot.y + 0.01f), paint);
        canvas.drawLine(surfaceView.screenX(blueSpot.x - 0.01f), surfaceView.screenY(blueSpot.y),
                surfaceView.screenX(blueSpot.x + 0.01f), surfaceView.screenY(blueSpot.y), paint);
        canvas.drawLine(surfaceView.screenX(blueSpot.x), surfaceView.screenY(blueSpot.y - 0.01f), surfaceView.screenX(blueSpot.x),
                surfaceView.screenY(blueSpot.y + 0.01f), paint);
        canvas.drawLine(surfaceView.screenX(pinkSpot.x - 0.01f), surfaceView.screenY(pinkSpot.y),
                surfaceView.screenX(pinkSpot.x + 0.01f), surfaceView.screenY(pinkSpot.y), paint);
        canvas.drawLine(surfaceView.screenX(pinkSpot.x), surfaceView.screenY(pinkSpot.y - 0.01f), surfaceView.screenX(pinkSpot.x),
                surfaceView.screenY(pinkSpot.y + 0.01f), paint);
        canvas.drawLine(surfaceView.screenX(blackSpot.x - 0.01f), surfaceView.screenY(blackSpot.y),
                surfaceView.screenX(blackSpot.x + 0.01f), surfaceView.screenY(blackSpot.y), paint);
        canvas.drawLine(surfaceView.screenX(blackSpot.x), surfaceView.screenY(blackSpot.y - 0.01f),
                surfaceView.screenX(blackSpot.x), surfaceView.screenY(blackSpot.y + 0.01f), paint);
        // draw Balls
        if (ballsOnTable != null && !ballsOnTable.isEmpty()) {
            double t1 = now();
            for (Ball ball : ballsOnTable)
                ball.draw(surfaceView, paint, canvas);
            Log.v(TAG, format(Locale.ROOT, "draw balls took %.0fms", now() - t1));
            // draw current shot info
            if (currentShot > -1 && !possibleShots.isEmpty()) {
                Shot s = possibleShots.get(currentShot);
                for (Ball ball : s.sBalls)
                    ball.draw(surfaceView, paint, canvas);
                Ball btp = s.ballToPot;
                // get cueball from value
                Ball cue = s.sBalls.get(0);
                if (cue.value != 0)
                    for (Ball b : s.sBalls)
                        if (b.value == 0) {
                            cue = b;
                            Log.v(TAG, format("cueball selected: id = %d value = %d", cue.id, cue.value));
                            break;
                        }
                double da1 = btp.getNode().getTargetAngle(s.pocket);
                double da2 = cue.getNode().getTargetAngle(
                        btp.getNode().contactPoint(s.pocket));
                //TODO: why is cuenode = 0, 0, 26?...
                Log.i(TAG, format("da1= %1.1f=%1.1f° da2= %1.1f=%1.1f° cuenodePos:%s", da1, Math.toDegrees(da1), da2, Math.toDegrees(da2), cue.getNode().P0.toString()));
                // draw aim line
                paint.setStyle(Style.STROKE);
                paint.setColor(Color.WHITE);
                canvas.drawLine(surfaceView.screenX(cue.Pos.x),
                        surfaceView.screenY(cue.Pos.y), surfaceView.screenX(s.target.x),
                        surfaceView.screenY(s.target.y), paint);
                // draw target
                canvas.drawCircle(surfaceView.screenX(s.target.x), surfaceView.screenY(s.target.y),
                        (float) (ballRadius * surfaceView.screenScale), paint);
                // draw pocket line
                paint.setColor(getBallColor(btp.value));
                canvas.drawLine(surfaceView.screenX(btp.Pos.x),
                        surfaceView.screenY(btp.Pos.y), surfaceView.screenX(s.pocket.x),
                        surfaceView.screenY(s.pocket.y), paint);
                // draw Stats
                // object ball
                paint.setColor(Color.WHITE);
                paint.setStyle(Style.STROKE);
                double dist = s.pocket.distanceTo(btp.Pos);
                double totdist = dist;
                double dx = surfaceView.screenX(s.pocket.x) - surfaceView.screenX(btp.Pos.x);
                double dy = surfaceView.screenY(s.pocket.y) - surfaceView.screenY(btp.Pos.y);
                double dl = Math.sqrt(dx * dx + dy * dy);
                Vec3 normal = new Vec3(surfaceView.screenX(btp.Pos.x) + dx / 2
                        - 25 * dy / dl, surfaceView.screenY(btp.Pos.y) + dy
                        / 2 - 25 * dx / dl, 0);
                canvas.drawText("d = " + d(dist * 100, 1) + " cm",
                        (float) normal.x, (float) normal.y, paint);
                // cue ball
                dist = cue.Pos.distanceTo(s.target);
                totdist += dist;
                dx = surfaceView.screenX(s.target.x) - surfaceView.screenX(cue.Pos.x);
                dy = surfaceView.screenY(s.target.y) - surfaceView.screenY(cue.Pos.y);
                dl = Math.sqrt(dx * dx + dy * dy);
                normal = new Vec3(surfaceView.screenX(cue.Pos.x) + dx / 2 - 25
                        * dy / dl, surfaceView.screenY(cue.Pos.y) + dy / 2 - 25
                        * dx / dl, 0);
                double da = Math.toDegrees(s.target.subtract(cue.Pos)
                        .deltaAngle(
                                s.pocket.subtract(btp.Pos)));
                paint.setTextSize(15);
                canvas.drawText("ang = " + d(da, 2) + " deg", (float) normal.x,
                        (float) normal.y, paint);
                canvas.drawText("dist = " + d(dist * 100, 1) + " cm",
                        (float) normal.x, (float) normal.y + 20, paint);
                canvas.drawText("tot = " + d(totdist * 100, 1) + " cm",
                        (float) normal.x, (float) normal.y + 40, paint);
                // draw helper ballOn
                paint.setStyle(Style.FILL);
                paint.setColor(getBallColor(btp.value));
                float scale = (float) (30 / ballRadius / surfaceView.screenScale);
                canvas.drawCircle(230, surfaceView.screenHeight
                                - (float) (scale * ballRadius * surfaceView.screenScale),
                        (float) (scale * ballRadius * surfaceView.screenScale), paint);
                if (btp.value == 7) {
                    paint.setStyle(Style.STROKE);
                    paint.setColor(Color.WHITE);
                    canvas.drawCircle(230, surfaceView.screenHeight
                                    - (float) (scale * ballRadius * surfaceView.screenScale),
                            (float) (scale * ballRadius * surfaceView.screenScale), paint);
                }

                // helper cueball
                paint.setStyle(Style.FILL);
                paint.setAlpha(127);
                paint.setColor(Color.WHITE);
                canvas.drawCircle(230 + (float) (Math.sin(da2 - da1) * 2 * scale
                                * ballRadius * surfaceView.screenScale), surfaceView.screenHeight
                                - (float) (scale * ballRadius * surfaceView.screenScale),
                        (float) (scale * ballRadius * surfaceView.screenScale), paint);
                paint.setAlpha(255);
            }
        }
//
//        // simulation
//        if (currentShot > -1) {
//            paint.setStyle(Style.FILL);
//            for (int b = 0; b < possibleShots.get(currentShot).sBalls.size(); b++) {
//                // draw ball
//                paint.setColor(getBallColor(possibleShots.get(currentShot).sBalls
//                        .get(b).value));
//                canvas.drawCircle(
//                        surfaceView.screenX(possibleShots.get(currentShot).sBalls.get(b).Pos.x),
//                        surfaceView.screenY(possibleShots.get(currentShot).sBalls.get(b).Pos.y),
//                        (float) (ballRadius * surfaceView.screenScale), paint);
//            }
//        }
        surfaceView.surfaceHolder.unlockCanvasAndPost(canvas);
        drawing = false;
        Log.d(TAG, format(Locale.ROOT, "draw() took %.0fms", now() - t0));
        if (btService != null && btService.isConnected())
            handler.obtainMessage(BT_SEND, getTableAsJSONString()).sendToTarget();
    }

    void addBallToTable(double x, double y, int value, int id) {
        if (ballsOnTable == null)
            ballsOnTable = new ArrayList<>();
        ballsOnTable.add(new Ball(x, y, value, id));
    }

    public void switchBalls(View view) {
        int va1 = ballsOnTable.get(0).value;
        ballsOnTable.get(0).value = ballsOnTable.get(1).value;
        ballsOnTable.get(1).value = va1;
        calc(null);
    }

    private void initTable() {
        ballsOnTable.clear();
        // setup initial practice exercise
        // cueball
        ballsOnTable.add(new Ball((brownSpot.x + greenSpot.x) / 2, blackSpot.y - 100, 0, 1));
        setCueBallV0();
        activeBall = ballsOnTable.get(0);
        ballOn = 7;

        // colors
        ballsOnTable.add(new Ball(yellowSpot.x, yellowSpot.y, 2, 2));
        ballsOnTable.add(new Ball(greenSpot.x, greenSpot.y, 3, 3));
        ballsOnTable.add(new Ball(brownSpot.x, brownSpot.y, 4, 4));
        ballsOnTable.add(new Ball(blueSpot.x, blueSpot.y, 5, 5));
        ballsOnTable.add(new Ball(pinkSpot.x, pinkSpot.y, 6, 6));
        ballsOnTable.add(new Ball(blackSpot.x, blackSpot.y, 7, 7));

        // reds
        double red_row_dist = Math.sqrt(3 * ballRadius * ballRadius);
        double first_red = pinkSpot.y + 0.00 + 2 * ballRadius;
        ballsOnTable.add(new Ball(pinkSpot.x, first_red, 1, 8));
        ballsOnTable.add(new Ball(pinkSpot.x - ballRadius, first_red + red_row_dist, 1, 9));
        ballsOnTable.add(new Ball(pinkSpot.x + ballRadius, first_red + red_row_dist, 1, 10));
        ballsOnTable.add(new Ball(pinkSpot.x - 2 * ballRadius, first_red + 2 * red_row_dist, 1, 11));
        ballsOnTable.add(new Ball(pinkSpot.x, first_red + 2 * red_row_dist, 1, 12));
        ballsOnTable.add(new Ball(pinkSpot.x + 2 * ballRadius, first_red + 2 * red_row_dist, 1, 13));
        ballsOnTable.add(new Ball(pinkSpot.x - 3 * ballRadius, first_red + 3 * red_row_dist, 1, 14));
        ballsOnTable.add(new Ball(pinkSpot.x - 1 * ballRadius, first_red + 3 * red_row_dist, 1, 15));
        ballsOnTable.add(new Ball(pinkSpot.x + 1 * ballRadius, first_red + 3 * red_row_dist, 1, 16));
        ballsOnTable.add(new Ball(pinkSpot.x + 3 * ballRadius, first_red + 3 * red_row_dist, 1, 17));
        ballsOnTable.add(new Ball(pinkSpot.x - 4 * ballRadius, first_red + 4 * red_row_dist, 1, 18));
        ballsOnTable.add(new Ball(pinkSpot.x - 2 * ballRadius, first_red + 4 * red_row_dist, 1, 19));
        ballsOnTable.add(new Ball(pinkSpot.x, first_red + 4 * red_row_dist, 1, 20));
        ballsOnTable.add(new Ball(pinkSpot.x + 2 * ballRadius, first_red + 4 * red_row_dist, 1, 21));
        ballsOnTable.add(new Ball(pinkSpot.x + 4 * ballRadius, first_red + 4 * red_row_dist, 1, 22));
    }

    private void toast(String msg) {
        Toast.makeText(getApplicationContext(), msg, Toast.LENGTH_SHORT).show();
    }

    @Override
    public boolean onCreateOptionsMenu(Menu menu) {
        getMenuInflater().inflate(R.menu.main, menu);
        return true;
    }

    private double d(double value, int precision) {
        return Math.round(value * Math.pow(10, precision)) / Math.pow(10, precision);
    }
}
