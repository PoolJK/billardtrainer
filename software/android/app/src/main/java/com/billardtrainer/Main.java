package com.billardtrainer;

import java.util.ArrayList;

import android.content.Context;
import android.content.Intent;
import android.graphics.Bitmap;
import android.graphics.Canvas;
import android.graphics.Color;
import android.graphics.Paint;
import android.graphics.Paint.Style;
import android.graphics.RectF;
import android.graphics.drawable.BitmapDrawable;
import android.net.Uri;
import android.os.Bundle;
import android.os.Handler;
import android.os.Message;
import android.support.v7.app.AppCompatActivity;
import android.util.Log;
import android.view.Menu;
import android.view.MotionEvent;
import android.view.View;
import android.view.ViewGroup.LayoutParams;
import android.view.ViewTreeObserver;
import android.widget.Button;
import android.widget.RelativeLayout;
import android.widget.TextView;
import android.widget.Toast;
import static com.billardtrainer.Cons.*;
import static com.billardtrainer.Utils.*;

public class Main extends AppCompatActivity {

    // Bluetooth
    private BTService btService;

    private final int TOAST_MESSAGE = 0;
    private final int DRAW = 1;
    private ArrayList<Ball> ballsOnTable;
    private int activeBall = 0;
    private int currentShot = -1;

    private TextView activeBallView;
    private Button fineSwitchButton;
    private RelativeLayout linear_layout;
    private customCanvas drawSurface;
    int screenWidth, screenHeight;
    double screenScale, screenOffset;
    private boolean screenSet = false;
    private boolean fineMove = false;
    private static mHandler handler;
    private int ballOn = 8;
    private ArrayList<Shot> possibleShots;
    private boolean simRunning, calcRunning;
    private simThread sThread;

    private Bitmap bitmap;
    private Canvas canvas;
    private final Paint paint = new Paint();
    private boolean aiming;
    private Button aimButton;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.main);

        activeBallView = findViewById(R.id.active_ball_view);
        activeBallView.setText("Cueball");
        aimButton = findViewById(R.id.button3);
        aimButton.setText(getString(R.string.aimMode_move));
        fineSwitchButton = findViewById(R.id.button6);
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
                    screenSet = true;
                    bitmap = Bitmap.createBitmap(screenWidth, screenHeight,
                            Bitmap.Config.ARGB_8888);
                    canvas = new Canvas(bitmap);
                    calc();
                }
                return true;
            }
        });
        ballsOnTable = new ArrayList<>();
        initTable();
        drawSurface = new customCanvas(this);
        RelativeLayout.LayoutParams params = new RelativeLayout.LayoutParams(
                LayoutParams.WRAP_CONTENT, LayoutParams.WRAP_CONTENT);
        linear_layout.addView(drawSurface, 0, params);

        handler = new mHandler() {
            @Override
            public void handleMessage(Message msg) {
                Log.d("mHandler", msg.toString());
                switch (msg.what) {
                    case TOAST_MESSAGE:
                        toast((String) msg.obj);
                        break;
                    case DRAW:
                        draw();
                        break;
                }
            }
        };
        sThread = new simThread();
        possibleShots = new ArrayList<>();
        paint.setStrokeWidth(0);
        paint.setAntiAlias(true);
        angle = 180;
        speed = 3;

        // Test case to simulate data from bluetooth:
        btService = new BTService(handler);
        btService.start();



        // ATTENTION: This was auto-generated to handle app links.
        Intent appLinkIntent = getIntent();
        String appLinkAction = appLinkIntent.getAction();
        Uri appLinkData = appLinkIntent.getData();
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
        return (float) (-y * screenScale + 20);
    }

    double rX(float sX) {
        return (sX - screenOffset) / screenScale;
    }

    double rY(float sY) {
        return (sY - 20) / -screenScale;
    }

    private int numposs = 0;
    private int numreach = 0;
    private int nummpossprev = 0;
    private double ballspread = 0;

    private void calc() {
        Vec3 pock;
        int btp;
        Ball b;
        Vec3 contactPoint, a;
        numposs = 0;
        numreach = 0;
        ballspread = 0;
        pock = null;
        btp = -1;
        calcRunning = true;
        if (currentShot > -1) {
            pock = possibleShots.get(currentShot).pocket;
            btp = possibleShots.get(currentShot).ballToPot;
        }
        possibleShots.clear();
        currentShot = -1;
        if (ballsOnTable.isEmpty()) {
            calcRunning = false;
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
            if (bi < ballsOnTable.size() - 1)
                // only balls on
                if ((b.id != ballOn && ballOn < 8) || (ballOn > 7 && b.value != 1))
                    continue;
            // all pockets
            for (Vec3 pocket : pockets) {
                if (b.id == 7)
                    Log.d("main", String.format("pocket: %s", pocket));
                // if obstructed check next
                if (b.hasNoLineTo(pocket, ballsOnTable, null)) {
                    if (b.id == 7)
                        Log.d("main", "no line");
                    continue;
                }
                numposs += 1;
                // not obstructed get contact
                contactPoint = b.contactPoint(pocket);
                // cueball reaches contact
                if (ballsOnTable.get(0).hasNoLineTo(contactPoint, ballsOnTable, b))
                    continue;
                // angle < 88
                a = contactPoint.subtract(ballsOnTable.get(0).Pos);
                double deltaAngle = Math.toDegrees(a.deltaAngle(pocket
                        .subtract(b.Pos)));
                if (deltaAngle > 88)
                    continue;
                numreach += 1;
                possibleShots.add(new Shot(ballsOnTable, contactPoint, pocket, b.id,
                        possibleShots.size() + 1));
                // try to select similar shot
                if (b.id == btp && pocket == pock)
                    currentShot = possibleShots.size() - 1;
            }
        }

        if (!possibleShots.isEmpty() && currentShot == -1)
            currentShot = 0;
        calcRunning = false;
        handler.sendEmptyMessage(DRAW);
    }

    private void calcPos() {
        long t0 = System.currentTimeMillis();
        Ball cue;
        Vec3 contactPoint, a;
        numposs = 0;
        numreach = 0;
        ballspread = 0;
        calcRunning = true;
        if (ballsOnTable.isEmpty()) {
            calcRunning = false;
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
                Log.d("main", String.format("pocket: %s", pocket));
                // if obstructed check next
                if (ball.hasNoLineTo(pocket, ballsOnTable, null)) {
                    Log.d("main", "no line");
                    continue;
                }
                numposs += 1;
                // not obstructed get contact
                contactPoint = ball.contactPoint(pocket);
                // xy schleife
                for (int x = 0; x < fact; x++)
                    for (int y = 0; y < 2 * fact; y++) {
                        cue.Pos.x = ballRadius + x * tableWidth / fact;
                        cue.Pos.y = -ballRadius - y * tableLength / (2 * fact);
                        if (cue.hasNoLineTo(contactPoint, ballsOnTable, ball))
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
        drawSurface.setBackground(new BitmapDrawable(getResources(), bitmap));
        cue.Pos.x = oldcuex;
        cue.Pos.y = oldcuey;
        calcRunning = false;
        long t1 = (System.currentTimeMillis() - t0);
        drawSurface.invalidate();
        // new way
        calcRunning = true;
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
                pocket = pocket;
                // if obstructed check next
                if (b.hasNoLineTo(pocket, ballsOnTable, null))
                    continue;
                numposs += 1;
                // not obstructed get contact
                contactPoint = b.contactPoint(pocket);
                // xy schleife
                for (int x = 0; x < fact; x++)
                    for (int y = 0; y < 2 * fact; y++) {
                        cue.Pos.x = ballRadius + x * tableWidth / fact;
                        cue.Pos.y = -ballRadius - y * tableLength / (2 * fact);
                        if (cue.hasNoLineTo(contactPoint, ballsOnTable, b))
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
        calcRunning = false;

        toast("old way: " + (double) t1 / 1000 + "new way: " + (double) (System.currentTimeMillis() - t0) / 1000 + "s");

    }

    class simThread extends Thread {
        @Override
        public void run() {
            if (currentShot == -1)
                return;
            simRunning = true;
            long fps = 25;
            long time = System.currentTimeMillis();
            long tStart = time;
            long showInterval = 1000 / fps;
            long lastShowTime = tStart;
            double simcounter = 0;
            Message msg;
            Ball b1 = possibleShots.get(currentShot).sBalls.get(0);
            Ball b2 = possibleShots.get(currentShot).sBalls.get(4);
//			double f = 0.5 * uBallCloth * g * t * t;
//			new Vec3(Pos.x + V0.x * t - f * Vc0.x, Pos.y + V0.y * t - f * Vc0.y, 0, t);
            // x:
            // (b2.V0x - b1.V0x) * t - 0.5*uBallCloth*g*(b2.Vc0.x - b1.Vc0.x) * t^2 + (b2.Pos.x - b1.Pos.x) - 2 * ballRadius = 0
            b1.setV0(b1.V);
            double a = 0.5 * uBallCloth * g * (b2.Vc0.x - b1.Vc0.x);
            double B = (b2.V0.x - b1.V0.x);
            double c = b2.Pos.x - b1.Pos.x - 4 * ballRadius * ballRadius;
            double D = B * B - 4 * a * c;
            if (D >= 0) {
                double t1 = 0.5 * (-B + Math.sqrt(D)) / a;
                double t2 = 0.5 * (-B - Math.sqrt(D)) / a;
                msg = handler.obtainMessage();
                msg.obj = "t1 = " + d(t1, 4) + ", t2 = " + d(t2, 4);
                handler.sendMessage(msg);
            }
            while (ballsMoving() && simRunning) {
                time = System.currentTimeMillis();
                // sim stuff
                simcounter++;
                // move
                for (Ball b : possibleShots.get(currentShot).sBalls) {
                    if (b.state == 0)
                        continue;
                    // move time simcounter - lastAction
                    b.move(1);
                }
                // check Collision
                Ball ball1, ball2;
                for (int index1 = 0; index1 < possibleShots.get(currentShot).sBalls
                        .size(); index1++) {
                    ball1 = possibleShots.get(currentShot).sBalls.get(index1);
                    if (ball1.state == 0)
                        continue;
                    for (int index2 = 0; index2 < possibleShots
                            .get(currentShot).sBalls.size(); index2++) {
                        // no self collision
                        if (index1 == index2)
                            continue;
                        ball2 = possibleShots.get(currentShot).sBalls
                                .get(index2);
                        // check for collision
                        // movement smaller than distanceTo
                        double distance = ball1.Pos.distanceTo(ball2.Pos) - 2
                                * ballRadius;
                        if (ball1.V.length() / 1000 < distance)
                            continue;
                        Vec3 normal = ball1.V.cloneVec3();
                        normal.normalize();
                        Vec3 C = ball2.Pos.subtract(ball1.Pos);
                        D = normal.scalar(C);
                        // not moving towards
                        if (D <= 0)
                            continue;
                        double lC = C.length();
                        double F = (lC * lC) - (D * D);
                        // doesn't get close enough
                        double sumRadii = Math.pow(2 * ballRadius, 2);
                        if (F >= sumRadii)
                            continue;
                        double T = sumRadii - F;
                        if (T < 0)
                            continue;
                        distance = D - Math.sqrt(T);
                        if (ball1.V.length() / 1000 < distance)
                            continue;
                        // collide
                        double dx = ball2.Pos.x - ball1.Pos.x;
                        double dy = ball2.Pos.y - ball1.Pos.y;
                        D = Math.sqrt(dx * dx + dy * dy);
                        Vec3 n = new Vec3(dx / D, dy / D, 0);
                        double dp = (n.scalar(ball1.V) - n.scalar(ball2.V));
                        dx = dp * n.x;
                        dy = dp * n.y;
                        ball2.V.x += dx;
                        ball2.V.y += dy;
                        ball1.V.x -= dx;
                        ball1.V.y -= dy;
                        ball2.state = 1;
                        ball1.move(0.5);
                        ball2.move(0.5);
                    }
                }
                if (simcounter % showInterval == 0) {
                    if (time - lastShowTime < showInterval)
                        try {
                            sleep(Math.max(showInterval
                                    - (time - lastShowTime + 1), 0));
                        } catch (InterruptedException e) {
                            e.printStackTrace();
                        }
                    lastShowTime = time;
                    handler.sendEmptyMessage(DRAW);
                }
            }
            ballsOnTable = possibleShots.get(currentShot).sBalls;
            simRunning = false;
            calc();
        }

        private boolean ballsMoving() {
            if (currentShot == -1)
                return false;
            for (int b = 0; b < possibleShots.get(currentShot).sBalls.size(); b++)
                if (possibleShots.get(currentShot).sBalls.get(b).state > 0)
                    return true;
            return false;
        }
    }

    public void fineSwitch(View view) {
        fineMove = !fineMove;
        fineSwitchButton.setText(fineMove ? "fine" : "norm");
    }

    public void aimSwitch(View view) {
        aiming = !aiming;
        aimButton.setText(!aiming ? "move" : "aim");
        calcPos();
    }

    public void resetBalls(View view) {
        //ballsOnTable = oldBalls;
        //calc();
        toast("ballspread = " + d(ballspread * 100, 1) + "cm, numposspock = " + numposs + ", numcuereach = " + numreach);
    }

    public void removeBall(View view) {
        if (activeBall == 0)
            return;
        for (Ball b : ballsOnTable)
            if (b.id == activeBall) {
                ballsOnTable.remove(b);
                if (activeBall == ballOn)
                    ballOn = 8;
                activeBall = 0;
                activeBallView.setText(ballsOnTable.get(activeBall).toString());
                break;
            }
        calc();
    }

    public void start(View view) {
        if (simRunning) {
            simRunning = false;
            try {
                sThread.join();
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
        }
        sThread = new simThread();
        if (simRunning || currentShot == -1)
            return;
        calc();
        Shot s = possibleShots.get(currentShot);
        double vx, vy;
        Ball c = s.sBalls.get(0);
        vx = (s.target.x - c.Pos.x);
        vy = (s.target.y - c.Pos.y);
        double l = 0.8 * Math.sqrt(vx * vx + vy * vy);
        c.state = 1;
        c.V.x = vx / l;
        c.V.y = vy / l;
        sThread.start();
    }

    private void cycleShot() {
        if (possibleShots.isEmpty())
            currentShot = -1;
        else {
            currentShot = currentShot < possibleShots.size() - 1 ? currentShot + 1
                    : 0;
            handler.sendEmptyMessage(DRAW);
        }
    }

    private void setCueballV() {
        ballsOnTable.get(0).V0.x = speed * Math.cos(Math.toRadians(angle));
        ballsOnTable.get(0).V0.y = speed * Math.sin(Math.toRadians(angle));
    }

    private double angle;
    private double speed;

    private class customCanvas extends View {

        private float startX, startY, oldX, oldY;
        private double dx, dy;
        private int newId = -1;
        private boolean moving;
        private Ball ball;

        public customCanvas(Context context) {
            super(context);
        }

        @Override
        public boolean onTouchEvent(MotionEvent e) {
            int MIN_MOVEMENT = 4;
            aiming = false;
            switch (e.getActionMasked()) {
                case MotionEvent.ACTION_DOWN:
                    oldX = startX = e.getX();
                    oldY = startY = e.getY();
                    newId = getIdFromPosition(rX(e.getX()), rY(e.getY()), ballsOnTable);
                    moving = false;
                    return true;
                case MotionEvent.ACTION_MOVE:
                    dx = rX(e.getX()) - rX(oldX);
                    dy = rY(e.getY()) - rY(oldY);
                    oldX = e.getX();
                    oldY = e.getY();
                    if (Math.abs(e.getX() - startX) < MIN_MOVEMENT
                            && Math.abs(e.getY() - startY) < MIN_MOVEMENT
                            && !fineMove
                            && !aiming)
                        return true;
                    else
                        moving = true;
                    double fact = fineMove ? 0.5 : 1;
                    dx *= fact;
                    dy *= fact;
                    if (!aiming) { // moving
                        for (int bi = 0; bi < ballsOnTable.size(); bi++) {
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
                    } else { // aiming
                        //TODO
                        angle += dx;
                        speed += dy * 0.1;
                        setCueballV();
                        handler.sendEmptyMessage(DRAW);
                        return true;
                    }
                    if (!simRunning && !calcRunning) {
                        calc();
                    }
                    return true;
                case MotionEvent.ACTION_UP:
                    Log.d("main", String.format("Cueball position: x=%f y=%f",
                            ballsOnTable.get(0).Pos.x,
                            ballsOnTable.get(0).Pos.y));
                    if (moving)
                        return false;
                    // else
                    //TODO kann glaub ich weg
                    if (simRunning) {
                        simRunning = false;
                        try {
                            sThread.join();
                        } catch (InterruptedException ex) {
                            ex.printStackTrace();
                        }
                        calc();
                        return false;
                    }
                    // "click"-event:
                    // first: no ball clicked:
                    if (newId == -1)
                        cycleShot();
                    else {
                        // ball clicked
                        if (newId == activeBall && activeBall != 0) {
                            ballOn = activeBall;
                            activeBall = 0;
                            activeBallView.setText(ballsOnTable.get(activeBall).toString());
                            calc();
                            return false;
                        } else {
                            activeBall = newId;
                            activeBallView.setText(ballsOnTable.get(activeBall).toString());
                            return false;
                        }
                    }
                    return false;
            }
            return true;
        }

        @Override
        public boolean performClick() {
            Log.w("click", "click");
            return super.performClick();
        }
    }

    private void draw() {
        if (calcRunning) {
            return;
        }
        // draw Table
        // cloth
        paint.setStyle(Style.FILL);
        canvas.drawARGB(255, 0, 0, 0);
        paint.setColor(Color.rgb(0, 140, 20));
        canvas.drawRect(screenX(0), screenY(0), screenX(tableWidth), screenY(-tableLength), paint);
        // lines
        paint.setColor(Color.WHITE);
        paint.setStyle(Paint.Style.STROKE);
        canvas.drawLine(screenX(0), screenY(-DDistance), screenX(tableWidth), screenY(-DDistance),
                paint);
        canvas.drawArc(new RectF(screenX(yellowSpot.x), screenY(yellowSpot.y + DRadius),
                        screenX(greenSpot.x), screenY(greenSpot.y - DRadius)), 180, 180, false,
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
        if (ballsOnTable == null || ballsOnTable.isEmpty()) {
            return;
        }
        if (!simRunning) {
            for (Ball ball : ballsOnTable)
                ball.draw(this, paint, canvas);
        }
        if (currentShot > -1 && !possibleShots.isEmpty()) {
            Shot s = possibleShots.get(currentShot);
            int btp = s.getBallToPot();
            double da1 = ballsOnTable.get(btp).getTargetAngle(s.pocket);
            double da2 = ballsOnTable.get(0).getTargetAngle(
                    ballsOnTable.get(btp).contactPoint(s.pocket));
            if (!simRunning) {
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
                paint.setColor(getBallColor(ballsOnTable.get(btp).value));
                canvas.drawLine(screenX(ballsOnTable.get(btp).Pos.x),
                        screenY(ballsOnTable.get(btp).Pos.y), screenX(s.pocket.x),
                        screenY(s.pocket.y), paint);
                // draw Stats
                // object ball
                paint.setColor(Color.WHITE);
                paint.setStyle(Style.STROKE);
                double dist = s.pocket.distanceTo(ballsOnTable.get(btp).Pos);
                double totdist = dist;
                double dx = screenX(s.pocket.x) - screenX(ballsOnTable.get(btp).Pos.x);
                double dy = screenY(s.pocket.y) - screenY(ballsOnTable.get(btp).Pos.y);
                double dl = Math.sqrt(dx * dx + dy * dy);
                Vec3 normal = new Vec3(screenX(ballsOnTable.get(btp).Pos.x) + dx / 2
                        - 25 * dy / dl, screenY(ballsOnTable.get(btp).Pos.y) + dy
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
                                s.pocket.subtract(ballsOnTable.get(btp).Pos)));
                paint.setTextSize(15);
                canvas.drawText("ang = " + d(da, 2) + " deg", (float) normal.x,
                        (float) normal.y, paint);
                canvas.drawText("dist = " + d(dist * 100, 1) + " cm",
                        (float) normal.x, (float) normal.y + 20, paint);
                canvas.drawText("tot = " + d(totdist * 100, 1) + " cm",
                        (float) normal.x, (float) normal.y + 40, paint);
            }
            // draw helper ballOn
            paint.setStyle(Style.FILL);
            paint.setColor(getBallColor(ballsOnTable.get(btp).value));
            float scale = (float) (30 / ballRadius / screenScale);
            canvas.drawCircle(230, screenHeight
                            - (float) (scale * ballRadius * screenScale),
                    (float) (scale * ballRadius * screenScale), paint);
            if (ballsOnTable.get(btp).value == 7) {
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

        // simulation
        if (currentShot > -1 && simRunning) {
            paint.setStyle(Style.FILL);
            for (int b = 0; b < possibleShots.get(currentShot).sBalls.size(); b++) {
                // draw ball
                paint.setColor(getBallColor(possibleShots.get(currentShot).sBalls
                        .get(b).value));
                canvas.drawCircle(
                        screenX(possibleShots.get(currentShot).sBalls.get(b).Pos.x),
                        screenY(possibleShots.get(currentShot).sBalls.get(b).Pos.y),
                        (float) (ballRadius * screenScale), paint);
            }
        }
        drawSurface.setBackground(new BitmapDrawable(getResources(), bitmap));
    }

    private void initTable() {
        // cueball

        ballsOnTable.add(new Ball((brownSpot.x + greenSpot.x) / 2, brownSpot.y,
                0, 0));

        // colors

        ballsOnTable.add(new Ball(yellowSpot.x, yellowSpot.y, 2, 2));
        ballsOnTable.add(new Ball(greenSpot.x, greenSpot.y, 3, 3));
        ballsOnTable.add(new Ball(brownSpot.x, brownSpot.y, 4, 4));
        ballsOnTable.add(new Ball(blueSpot.x, blueSpot.y, 5, 5));
        ballsOnTable.add(new Ball(pinkSpot.x, pinkSpot.y, 6, 6));
        ballsOnTable.add(new Ball(blackSpot.x, blackSpot.y, 7, 7));

        // reds

        double yd = Math.sqrt(3 * ballRadius * ballRadius);
        double yc = pinkSpot.y - 0.001;
        ballsOnTable.add(new Ball(pinkSpot.x, yc - yd, 1, 8));
        ballsOnTable.add(new Ball(pinkSpot.x - ballRadius, yc - 2 * yd, 1, 9));
        ballsOnTable.add(new Ball(pinkSpot.x + ballRadius, yc - 2 * yd, 1, 10));
        ballsOnTable.add(new Ball(pinkSpot.x - 2 * ballRadius, yc - 3 * yd, 1, 11));
        ballsOnTable.add(new Ball(pinkSpot.x, yc - 3 * yd, 1, 12));
        ballsOnTable.add(new Ball(pinkSpot.x + 2 * ballRadius, yc - 3 * yd, 1, 13));
        ballsOnTable.add(new Ball(pinkSpot.x - 3 * ballRadius, yc - 4 * yd, 1, 14));
        ballsOnTable.add(new Ball(pinkSpot.x - 1 * ballRadius, yc - 4 * yd, 1, 15));
        ballsOnTable.add(new Ball(pinkSpot.x + 1 * ballRadius, yc - 4 * yd, 1, 16));
        ballsOnTable.add(new Ball(pinkSpot.x + 3 * ballRadius, yc - 4 * yd, 1, 17));
        ballsOnTable.add(new Ball(pinkSpot.x - 4 * ballRadius, yc - 5 * yd, 1, 18));
        ballsOnTable.add(new Ball(pinkSpot.x - 2 * ballRadius, yc - 5 * yd, 1, 19));
        ballsOnTable.add(new Ball(pinkSpot.x, yc - 5 * yd, 1, 20));
        ballsOnTable.add(new Ball(pinkSpot.x + 2 * ballRadius, yc - 5 * yd, 1, 21));
        ballsOnTable.add(new Ball(pinkSpot.x + 4 * ballRadius, yc - 5 * yd, 1, 22));
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
