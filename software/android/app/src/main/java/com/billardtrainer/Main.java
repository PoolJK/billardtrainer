package com.billardtrainer;

// https://billiards.colostate.edu/technical-proof/

import android.annotation.SuppressLint;
import android.graphics.Bitmap;
import android.graphics.Canvas;
import android.graphics.Color;
import android.graphics.Matrix;
import android.graphics.Paint;
import android.graphics.Paint.Style;
import android.graphics.RectF;
import android.os.Bundle;
import android.os.Handler;
import android.os.Message;
import android.os.SystemClock;
import android.support.v7.app.AppCompatActivity;
import android.util.Log;
import android.view.Menu;
import android.view.MotionEvent;
import android.view.SurfaceHolder;
import android.view.SurfaceView;
import android.view.View;
import android.view.ViewTreeObserver;
import android.widget.Button;
import android.widget.RelativeLayout;
import android.widget.TextView;
import android.widget.Toast;

import org.json.JSONException;
import org.json.JSONObject;

import java.util.ArrayList;
import java.util.Iterator;
import java.util.Locale;

import static com.billardtrainer.Cons.*;
import static com.billardtrainer.Utils.*;

public class Main extends AppCompatActivity {
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

    private static ArrayList<Ball> ballsOnTable;
    private static Ball activeBall;
    private static int currentShot = -1;

    private TextView activeBallView;
    private RelativeLayout linear_layout;
    int screenWidth, screenHeight;
    double screenScale, screenOffset;
    private boolean screenSet;
    static mHandler handler;
    private static int ballOn = 8;
    private static ArrayList<Shot> possibleShots;
    static boolean sim_running = false, drawing = false;

    private Canvas canvas;
    private Bitmap bitmap;
    private SurfaceHolder holder;
    private static final Paint paint = new Paint();
    private static boolean aiming;
    private Button aimButton;

    @SuppressLint({"HandlerLeak", "SetTextI18n", "ClickableViewAccessibility"})
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        screenSet = false;
        setContentView(R.layout.main);

        SurfaceView surfaceView = findViewById(R.id.surface_view);
        holder = surfaceView.getHolder();
        surfaceView.setOnTouchListener(new canvasOnTouchListener());

        activeBallView = findViewById(R.id.active_ball_view);
        activeBallView.setText("Cueball");
        aimButton = findViewById(R.id.button3);
        aimButton.setText(getString(R.string.aimMode_move));
        linear_layout = findViewById(R.id.linlay);
        ViewTreeObserver vto = linear_layout.getViewTreeObserver();
        vto.addOnPreDrawListener(new ViewTreeObserver.OnPreDrawListener() {
            @Override
            public boolean onPreDraw() {
                if (!screenSet) {
                    // dimensions of relative Layout View
                    // padding of 20 + 20
                    screenWidth = linear_layout.getMeasuredWidth();
                    // Y size - button heights
                    screenHeight = linear_layout.getMeasuredHeight();
                    screenScale = Math.min((screenWidth - 40) / tableWidth,
                            (screenHeight - 100) / tableLength);
                    screenOffset = (screenWidth - tableWidth * screenScale) / 2;
                    bitmap = Bitmap.createBitmap(screenWidth, screenHeight, Bitmap.Config.ARGB_8888);
                    canvas = new Canvas();
                    canvas.setBitmap(bitmap);
                    screenSet = true;
                    Log.v(TAG, String.format(Locale.ROOT, "screenW=%d screenH=%d", screenWidth, screenHeight));
                    // calc();
                    handler.sendEmptyMessage(DRAW);
                }
                return true;
            }
        });
        if (ballsOnTable == null) {
            ballsOnTable = new ArrayList<>();
            // initTable();
        }
        if (handler == null) {
            handler = new mHandler() {
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
                        case DRAW:
                            if (!sim_running)
                                draw();
                            break;
                        case DEVICE_READY:
                            device_busy = false;
                            break;
                        case BT_SEND:
                            if (device_busy) {
                                Log.v("Handler", "device busy");
                                // break;
                            }
                            device_busy = true;
                            if (btService != null && btService.isConnected())
                                btService.send(msg.obj.toString());
                            else
                                Log.d(TAG, "bluetooth not ready");
                            break;
                        case BT_RECEIVE:
                            handle_bt_message(msg.obj.toString());
                            break;
                        case BT_CONNECTED:
                            toast("bluetooth connected");
                            device_busy = false;
                            handler.obtainMessage(BT_SEND, getTableAsJSONString()).sendToTarget();
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

        paint.setStrokeWidth(0);
        paint.setAntiAlias(true);

        // ATTENTION: This was auto-generated to handle app links.
//        Intent appLinkIntent = getIntent();
//        String appLinkAction = appLinkIntent.getAction();
//        Uri appLinkData = appLinkIntent.getData();
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

    String index = "";

    private void handle_bt_message(String message) {
        if (message.contains("done")) {
            Log.v("main", "device ready");
            handler.sendEmptyMessage(DEVICE_READY);
            return;
        }
        Log.v(TAG, message);
        if (message.contains("balls")) {
            ballsOnTable.clear();
            JSONObject j;
            try {
                j = new JSONObject(message);
                JSONObject balls = j.getJSONObject("balls");
                index = String.format(Locale.ROOT, "%2d", j.getInt("index"));
                Log.d(TAG, "index = " + index);
                Iterator<String> iter = balls.keys();
                while (iter.hasNext()) {
                    String key = iter.next();
                    JSONObject ball = (JSONObject) balls.get(key);
                    addBallToTable(
                            ball.getDouble("x"),
                            ball.getDouble("y"),
                            ball.getInt("v")
                    );
                }
                calc(null);
                //toast(message);
            } catch (JSONException e) {
                Log.e(TAG, "handle_bt_message: JSONError");
                e.printStackTrace();
            }
        } else {
            toast(message);
            Log.d(TAG, message);
        }
    }

    static class mHandler extends Handler {
        mHandler() {
            super();
        }
    }

    float screenX(double x) {
        return (float) (x * screenScale + screenOffset);
    }

    float screenY(double y) {
        return (float) (y * screenScale + 20);
    }

    double rX(float sX) {
        return (sX - screenOffset) / screenScale;
    }

    double rY(float sY) {
        return (sY - 20) / screenScale;
    }

    private int numposs;
    private int numreach;
    private double ballspread;

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
        ballsOnTable.get(0).getNode().setV0(new Vec3(x, y, 0),
                new Vec3(0, 0, 0)); // [mm/s]
        ((TextView) findViewById(R.id.Angle)).setText(String.format(Locale.ROOT, "%.0f°", angle));
        ((TextView) findViewById(R.id.Speed)).setText(String.format(Locale.ROOT, "%.0f mm/s\u00b2", speed));
    }

    public void resetSim(View view) {
        for (Ball ball : ballsOnTable)
            ball.clearNodes();
        setCueBallV0();
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
        resetSim(view);
        simThread sThread = new simThread(ballsOnTable);
        sim_running = true;
        handler.post(sThread);
    }

//    public void start(View view) {
//        if (simRunning) {
//            simRunning = false;
//            try {
//                sThread.join();
//            } catch (InterruptedException e) {
//                e.printStackTrace();
//            }
//        }
//        sThread = new simThread(ballsOnTable);
//        if (simRunning || currentShot == -1)
//            return;
//        calc();
//        Shot s = possibleShots.get(currentShot);
//        double vx, vy;
//        Ball c = s.sBalls.get(0);
//        vx = (s.target.x - c.Pos.x);
//        vy = (s.target.y - c.Pos.y);
//        double l = 0.8 * Math.sqrt(vx * vx + vy * vy);
//        c.state = 1;
//        c.V.x = vx / l;
//        c.V.y = vy / l;
//        sThread.start();
//    }

    @SuppressWarnings({"unused", "SameParameterValue"})
    void calc(View view) {
        Vec3 pock;
        Ball b, btp;
        Vec3 contactPoint, a;
        numposs = 0;
        numreach = 0;
        ballspread = 0;
        pock = null;
        btp = null;
        if (currentShot > -1) {
            pock = possibleShots.get(currentShot).pocket;
            btp = possibleShots.get(currentShot).ballToPot;
        }
        possibleShots.clear();
        currentShot = -1;
        if (ballsOnTable.isEmpty()) {
            return;
        }
        int bspreadcount = 0;
        for (int bi = 1; bi < ballsOnTable.size(); bi++) {
            b = ballsOnTable.get(bi);
            for (int bia = bi + 1; bia < ballsOnTable.size(); bia++) {
                ballspread += b.Pos.distanceTo(ballsOnTable.get(bia).Pos);
                bspreadcount += 1;
            }
        }
        ballspread /= bspreadcount;
        for (int bi = 1; bi < ballsOnTable.size(); bi++) {
            b = ballsOnTable.get(bi);
            // only balls on
            if ((b.id != ballOn && ballOn < 8) || (ballOn > 7 && b.value != 1))
                continue;
            // all pockets
            for (Vec3 pocket : pockets) {
                if (b.id == 7)
                    Log.d("calc", String.format("pocket: %s", pocket));
                // if obstructed check next
                if (b.getNode().hasNoLineTo(pocket, ballsOnTable, null)) {
                    if (b.id == 7)
                        Log.d("calc", "no line");
                    continue;
                }
                numposs += 1;
                // not obstructed get contact
                contactPoint = b.getNode().contactPoint(pocket);
                // cueball reaches contact
                if (ballsOnTable.get(0).getNode().hasNoLineTo(contactPoint, ballsOnTable, b))
                    continue;
                // angle < 88
                a = contactPoint.subtract(ballsOnTable.get(0).Pos);
                double deltaAngle = Math.toDegrees(a.deltaAngle(pocket
                        .subtract(b.Pos)));
                if (deltaAngle > 88)
                    continue;
                numreach += 1;
                possibleShots.add(new Shot(ballsOnTable, contactPoint, pocket, b));
                // try to select similar shot
                if (b == btp && pocket == pock)
                    currentShot = possibleShots.size() - 1;
            }
        }
        if (!possibleShots.isEmpty()) {
            if (currentShot < 0)
                currentShot = 0;
        } else {
            currentShot = -1;
        }
        handler.sendEmptyMessage(DRAW);
        handler.obtainMessage(BT_SEND, getTableAsJSONString()).sendToTarget();
    }

    private void calcPos() {
        long t0 = System.currentTimeMillis();
        Ball cue;
        Vec3 contactPoint, a;
        numposs = 0;
        numreach = 0;
        ballspread = 0;
        if (ballsOnTable.isEmpty()) {
            return;
        }
        cue = ballsOnTable.get(0);
        //hier startet die x,y schleife
        double oldcuex = cue.Pos.x;
        double oldcuey = cue.Pos.y;
        int fact = 40;
        double nmax = 0;
        double[][] nreach = new double[fact][2 * fact];
        for (Ball ball : ballsOnTable) {
            //if (bi < ballsOnTable.size() - 1)
            // only balls on
            if ((ball.id != ballOn && ballOn < 8) || (ballOn > 7 && ball.value != 1))
                continue;
            // all pockets
            for (Vec3 pocket : pockets) {
                Log.v("main", String.format("pocket: %s", pocket));
                // if obstructed check next
                if (ball.getNode().hasNoLineTo(pocket, ballsOnTable, null)) {
                    Log.v("main", "no line");
                    continue;
                }
                numposs += 1;
                // not obstructed get contact
                contactPoint = ball.getNode().contactPoint(pocket);
                // xy schleife
                for (int x = 0; x < fact; x++)
                    for (int y = 0; y < 2 * fact; y++) {
                        cue.Pos.x = ballRadius + x * tableWidth / fact;
                        cue.Pos.y = -ballRadius - y * tableLength / (2 * fact);
                        if (cue.getNode().hasNoLineTo(contactPoint, ballsOnTable, ball))
                            continue;
                        // angle < 88
                        a = contactPoint.subtract(ballsOnTable.get(0).Pos);
                        double deltaAngle = Math.toDegrees(a.deltaAngle(pocket
                                .subtract(ball.Pos)));
                        if (deltaAngle > 88)
                            continue;
                        //possible shot data
                        double dist1 = ball.Pos.distanceTo(pocket);//ball-pocket
                        double dist2 = cue.Pos.distanceTo(contactPoint);//cue-ball
                        double dist = dist1 + dist2;
                        nreach[x][y] += 0.5 * Math.max(2 - dist / (tableWidth) - deltaAngle / 60, 0);
                        numreach += 1;
                        nmax = Math.max(nmax, nreach[x][y]);
                    }
            }
        }
        float cx, cy, cr = 2;
        for (int x = 0; x < fact; x++)
            for (int y = 0; y < 2 * fact; y++) {
                if (nreach[x][y] == 0)
                    continue;
                cx = screenX(ballRadius + x * tableWidth / fact);
                cy = screenY(-ballRadius - y * tableLength / (2 * fact));
                paint.setStyle(Style.FILL);
                int alp = (int) (200 * nreach[x][y] / nmax + 55);
                paint.setColor(Color.WHITE);
                paint.setAlpha(alp);
                canvas.drawCircle(cx, cy, cr, paint);
		/*
		paint.setStyle(Style.STROKE);
		paint.setColor(Color.BLACK);
		canvas.drawCircle(cx,cy,cr,paint);*/
                //xy schleife
            }
        paint.setAlpha(255);
        //drawSurface.setBackground(new BitmapDrawable(getResources(), bitmap));
        cue.Pos.x = oldcuex;
        cue.Pos.y = oldcuey;
        long t1 = (System.currentTimeMillis() - t0);
        //drawSurface.invalidate();
        // new way
        t0 = System.currentTimeMillis();
        cue = ballsOnTable.get(0);
        //hier startet die x,y schleife
        oldcuex = cue.Pos.x;
        oldcuey = cue.Pos.y;
        fact = 40;
        nmax = 0;
        nreach = new double[fact][2 * fact];
        for (Ball b : ballsOnTable) {
            //if (bi < ballsOnTable.size() - 1)
            // only balls on
            if ((b.id != ballOn && ballOn < 8) || (ballOn > 7 && b.value != 1))
                continue;
            // all pockets
            for (Vec3 pocket : pockets) {
                // if obstructed check next
                if (b.getNode().hasNoLineTo(pocket, ballsOnTable, null))
                    continue;
                numposs += 1;
                // not obstructed get contact
                contactPoint = b.getNode().contactPoint(pocket);
                // xy schleife
                for (int x = 0; x < fact; x++)
                    for (int y = 0; y < 2 * fact; y++) {
                        cue.Pos.x = ballRadius + x * tableWidth / fact;
                        cue.Pos.y = -ballRadius - y * tableLength / (2 * fact);
                        if (cue.getNode().hasNoLineTo(contactPoint, ballsOnTable, b))
                            continue;
                        // angle < 88
                        a = contactPoint.subtract(cue.Pos);
                        double deltaAngle = Math.toDegrees(a.deltaAngle(pocket
                                .subtract(b.Pos)));
                        if (deltaAngle > 88)
                            continue;
                        //possible shot data
                        double dist = b.Pos.distanceTo(pocket) + cue.Pos.distanceTo(contactPoint);
                        nreach[x][y] += 0.5 * Math.max(2 - dist / (tableWidth) - deltaAngle / 60, 0);
                        numreach += 1;
                        if (nreach[x][y] > nmax)
                            nmax = nreach[x][y];
                    }
            }
        }
        cr = 2;
        for (int x = 0; x < fact; x++)
            for (int y = 0; y < 2 * fact; y++) {
                if (nreach[x][y] == 0)
                    continue;
                cx = screenX(ballRadius + x * tableWidth / fact);
                cy = screenY(-ballRadius - y * tableLength / (2 * fact));
                int alp = (int) (220 * nreach[x][y] / nmax + 35);
                paint.setAlpha(alp);
                canvas.drawCircle(cx, cy, cr, paint);
				/*
				 paint.setStyle(Style.STROKE);
				 paint.setColor(Color.BLACK);
				 canvas.drawCircle(cx,cy,cr,paint);*/
                //xy schleife
            }
        paint.setAlpha(255);
        //drawSurface.setBackground(new BitmapDrawable(getResources(), bitmap));
        cue.Pos.x = oldcuex;
        cue.Pos.y = oldcuey;
        Log.d(TAG, "" + numposs + numreach + ballspread);
        toast("old way: " + (double) t1 / 1000 + "new way: " + (double) (System.currentTimeMillis() - t0) / 1000 + "s");
    }

    public void resetBalls(View view) {
        initTable();
        startSim(view);
    }

    public void aimSwitch(View view) {
        aiming = !aiming;
        aimButton.setText(!aiming ? "move" : "aim");
    }

    public void removeBall(View view) {
        if (activeBall.id == 0)
            return;
        for (Ball b : ballsOnTable)
            if (b == activeBall) {
                ballsOnTable.remove(b);
                if (activeBall.id == ballOn)
                    ballOn = 8;
                activeBall = ballsOnTable.get(0);
                activeBallView.setText(activeBall.toString());
                break;
            }
        calc(null);
        calcPos();
    }

    public void device_ready(View view) {
        handler.sendEmptyMessage(DEVICE_READY);
        handler.sendEmptyMessage(DRAW);
    }

    private void cycleShot() {
        if (possibleShots.isEmpty())
            currentShot = -1;
        else {
            currentShot = currentShot < possibleShots.size() - 1 ? currentShot + 1 : 0;
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
                    dx = rX(x) - rX(oldX);
                    dy = rY(y) - rY(oldY);
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
                        calc(null);
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
                        calc(null);
                        startSim(null);
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
                        newBall = getBallFromPosition(rX(x), rY(y), ballsOnTable);
                        if (newBall == null || (newBall == activeBall && ballOn == activeBall.id)) {
                            cycleShot();
                            calc(null);
                            return false;
                        } else {
                            // ball clicked
                            if (newBall == activeBall) {
                                ballOn = activeBall.id;
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
                        startSim(null);
                        moving = false;
                    }
                    return false;
            }
            return true;
        }
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
            all.put("index", String.format(Locale.ROOT, "%2d", index));
            if (balls.length() > 0)
                all.put("balls", balls);
            if (lines.length() > 0)
                all.put("lines", lines);
            if (ghosts.length() > 0)
                all.put("ghosts", ghosts);
        } catch (JSONException e) {
            e.printStackTrace();
            return "";
        }
        Log.v("main", String.format(Locale.ROOT, "JSON took %.0fms to generate",
                (SystemClock.currentThreadTimeMillis() - t0)));
        if (all.length() > 0)
            return all.toString();
        else
            return "";
    }

    private void draw() {
        Log.v(TAG, "draw()");
        double t0 = now();
        // draw Table
        // cloth
        paint.setStyle(Style.FILL);
        canvas.drawARGB(255, 0, 0, 0);
        paint.setColor(Color.rgb(0, 140, 20));
        canvas.drawRect(screenX(0), screenY(0), screenX(tableWidth), screenY(tableLength), paint);
        // lines
        paint.setColor(Color.WHITE);
        paint.setStyle(Paint.Style.STROKE);
        canvas.drawLine(screenX(0), screenY(DDistance), screenX(tableWidth), screenY(DDistance),
                paint);
        canvas.drawArc(new RectF(screenX(yellowSpot.x), screenY(yellowSpot.y - DRadius),
                        screenX(greenSpot.x), screenY(greenSpot.y + DRadius)), 180, 180, false,
                paint);
        // spots
        canvas.drawLine(screenX(yellowSpot.x), screenY(yellowSpot.y), screenX(yellowSpot.x),
                screenY(yellowSpot.y + 0.01f), paint);
        canvas.drawLine(screenX(greenSpot.x), screenY(greenSpot.y), screenX(greenSpot.x),
                screenY(greenSpot.y + 0.01f), paint);
        canvas.drawLine(screenX(brownSpot.x), screenY(brownSpot.y - 0.01f),
                screenX(brownSpot.x), screenY(brownSpot.y + 0.01f), paint);
        canvas.drawLine(screenX(blueSpot.x - 0.01f), screenY(blueSpot.y),
                screenX(blueSpot.x + 0.01f), screenY(blueSpot.y), paint);
        canvas.drawLine(screenX(blueSpot.x), screenY(blueSpot.y - 0.01f), screenX(blueSpot.x),
                screenY(blueSpot.y + 0.01f), paint);
        canvas.drawLine(screenX(pinkSpot.x - 0.01f), screenY(pinkSpot.y),
                screenX(pinkSpot.x + 0.01f), screenY(pinkSpot.y), paint);
        canvas.drawLine(screenX(pinkSpot.x), screenY(pinkSpot.y - 0.01f), screenX(pinkSpot.x),
                screenY(pinkSpot.y + 0.01f), paint);
        canvas.drawLine(screenX(blackSpot.x - 0.01f), screenY(blackSpot.y),
                screenX(blackSpot.x + 0.01f), screenY(blackSpot.y), paint);
        canvas.drawLine(screenX(blackSpot.x), screenY(blackSpot.y - 0.01f),
                screenX(blackSpot.x), screenY(blackSpot.y + 0.01f), paint);
        // draw Balls
        if (ballsOnTable != null && !ballsOnTable.isEmpty()) {
            double t1 = now();
            for (Ball ball : ballsOnTable)
                ball.draw(this, paint, canvas);
            Log.v(TAG, String.format(Locale.ROOT, "draw balls took %.0fms", now() - t1));
            if (currentShot > -1 && !possibleShots.isEmpty()) {
                Shot s = possibleShots.get(currentShot);
                Ball btp = s.ballToPot;
                double da1 = btp.getNode().getTargetAngle(s.pocket);
                double da2 = ballsOnTable.get(0).getNode().getTargetAngle(
                        btp.getNode().contactPoint(s.pocket));
                // draw aim line
                paint.setStyle(Style.STROKE);
                paint.setColor(Color.WHITE);
                canvas.drawLine(screenX(ballsOnTable.get(0).Pos.x),
                        screenY(ballsOnTable.get(0).Pos.y), screenX(s.target.x),
                        screenY(s.target.y), paint);
                // draw target
                canvas.drawCircle(screenX(s.target.x), screenY(s.target.y),
                        (float) (ballRadius * screenScale), paint);
                // draw pocket line
                paint.setColor(getBallColor(btp.value));
                canvas.drawLine(screenX(btp.Pos.x),
                        screenY(btp.Pos.y), screenX(s.pocket.x),
                        screenY(s.pocket.y), paint);
                // draw Stats
                // object ball
                paint.setColor(Color.WHITE);
                paint.setStyle(Style.STROKE);
                double dist = s.pocket.distanceTo(btp.Pos);
                double totdist = dist;
                double dx = screenX(s.pocket.x) - screenX(btp.Pos.x);
                double dy = screenY(s.pocket.y) - screenY(btp.Pos.y);
                double dl = Math.sqrt(dx * dx + dy * dy);
                Vec3 normal = new Vec3(screenX(btp.Pos.x) + dx / 2
                        - 25 * dy / dl, screenY(btp.Pos.y) + dy
                        / 2 - 25 * dx / dl, 0);
                canvas.drawText("d = " + d(dist * 100, 1) + " cm",
                        (float) normal.x, (float) normal.y, paint);
                // cue ball
                dist = ballsOnTable.get(0).Pos.distanceTo(s.target);
                totdist += dist;
                dx = screenX(s.target.x) - screenX(ballsOnTable.get(0).Pos.x);
                dy = screenY(s.target.y) - screenY(ballsOnTable.get(0).Pos.y);
                dl = Math.sqrt(dx * dx + dy * dy);
                normal = new Vec3(screenX(ballsOnTable.get(0).Pos.x) + dx / 2 - 25
                        * dy / dl, screenY(ballsOnTable.get(0).Pos.y) + dy / 2 - 25
                        * dx / dl, 0);
                double da = Math.toDegrees(s.target.subtract(ballsOnTable.get(0).Pos)
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
                float scale = (float) (30 / ballRadius / screenScale);
                canvas.drawCircle(230, screenHeight
                                - (float) (scale * ballRadius * screenScale),
                        (float) (scale * ballRadius * screenScale), paint);
                if (btp.value == 7) {
                    paint.setStyle(Style.STROKE);
                    paint.setColor(Color.WHITE);
                    canvas.drawCircle(230, screenHeight
                                    - (float) (scale * ballRadius * screenScale),
                            (float) (scale * ballRadius * screenScale), paint);
                }

                // helper cueball
                paint.setAlpha(127);
                paint.setStyle(Style.STROKE);
                paint.setColor(Color.WHITE);
                canvas.drawCircle(230 + (float) (Math.sin(da2 - da1) * 2 * scale
                                * ballRadius * screenScale), screenHeight
                                - (float) (scale * ballRadius * screenScale),
                        (float) (scale * ballRadius * screenScale), paint);
                paint.setAlpha(255);
            }
        }

        // simulation
//        if (currentShot > -1 && simRunning) {
//            paint.setStyle(Style.FILL);
//            for (int b = 0; b < possibleShots.get(currentShot).sBalls.size(); b++) {
//                // draw ball
//                paint.setColor(getBallColor(possibleShots.get(currentShot).sBalls
//                        .get(b).value));
//                canvas.drawCircle(
//                        screenX(possibleShots.get(currentShot).sBalls.get(b).Pos.x),
//                        screenY(possibleShots.get(currentShot).sBalls.get(b).Pos.y),
//                        (float) (ballRadius * screenScale), paint);
//            }
//        }
        Log.v(TAG, String.format(Locale.ROOT, "draw before lockCanvas = %.0fms", now() - t0));
        Canvas mCanvas;
        if (android.os.Build.VERSION.SDK_INT >= android.os.Build.VERSION_CODES.O) {
            mCanvas = holder.lockHardwareCanvas();
        } else {
            mCanvas = holder.lockCanvas();
        }
        if (mCanvas != null) {
            mCanvas.drawBitmap(bitmap, new Matrix(), null);
            holder.unlockCanvasAndPost(mCanvas);
        } else
            holder.unlockCanvasAndPost(canvas);
        drawing = false;
        Log.v(TAG, String.format(Locale.ROOT, "draw() took %.0fms", now() - t0));
        if (btService != null && btService.isConnected())
            handler.obtainMessage(BT_SEND, getTableAsJSONString()).sendToTarget();
    }

    void addBallToTable(double x, double y, int value) {
        if (ballsOnTable == null)
            ballsOnTable = new ArrayList<>();
        ballsOnTable.add(new Ball(x, y, value, ballsOnTable.size()));
    }

    private void initTable() {
        ballsOnTable.clear();
        // cueball
        ballsOnTable.add(new Ball(yellowSpot.x, blackSpot.y, 0, 1));
        setCueBallV0();
        activeBall = ballsOnTable.get(0);

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
