package com.billardtrainer;

import android.annotation.SuppressLint;
import android.graphics.Canvas;
import android.graphics.Color;
import android.graphics.Paint;
import android.graphics.RectF;
import android.os.Bundle;
import android.support.annotation.NonNull;
import android.support.design.widget.FloatingActionButton;
import android.support.design.widget.NavigationView;
import android.support.design.widget.Snackbar;
import android.support.v4.view.GravityCompat;
import android.support.v4.widget.DrawerLayout;
import android.support.v7.app.ActionBarDrawerToggle;
import android.support.v7.app.AppCompatActivity;
import android.support.v7.widget.Toolbar;
import android.util.Log;
import android.view.Menu;
import android.view.MenuItem;
import android.view.MotionEvent;
import android.view.View;
import android.view.WindowManager;
import android.widget.LinearLayout;

import static com.billardtrainer.Cons.DDistance;
import static com.billardtrainer.Cons.DRadius;
import static com.billardtrainer.Cons.blackSpot;
import static com.billardtrainer.Cons.blueSpot;
import static com.billardtrainer.Cons.brownSpot;
import static com.billardtrainer.Cons.greenSpot;
import static com.billardtrainer.Cons.pinkSpot;
import static com.billardtrainer.Cons.tableLength;
import static com.billardtrainer.Cons.tableWidth;
import static com.billardtrainer.Cons.yellowSpot;

public class DrillSelector extends AppCompatActivity
        implements NavigationView.OnNavigationItemSelectedListener, View.OnTouchListener {

    private static final String TAG = "DrillSelector";

    CustomSurfaceView customSurfaceView = null;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_drill_selector);
        Toolbar toolbar = findViewById(R.id.toolbar);
        setSupportActionBar(toolbar);
        FloatingActionButton fab = findViewById(R.id.fab);
        fab.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                Snackbar.make(view, "Replace with your own action", Snackbar.LENGTH_LONG)
                        .setAction("Action", null).show();
            }
        });
        final DrawerLayout drawer = findViewById(R.id.drawer_layout);
        final NavigationView navigationView = findViewById(R.id.nav_view);
        final ActionBarDrawerToggle toggle = new ActionBarDrawerToggle(
                this, drawer, toolbar, R.string.navigation_drawer_open, R.string.navigation_drawer_close){
            @Override
            public void onDrawerSlide(View drawerView, float slideOffset) {
                super.onDrawerSlide(drawerView, slideOffset);
//                Log.d(TAG, "drawer slide");
//                LinearLayout contentLayout = findViewById(R.id.drill_selector_content);
//                navigationView.bringToFront();
//                navigationView.invalidate();
                drawer.bringChildToFront(navigationView);
//                customSurfaceView.invalidate();
//                contentLayout.invalidate();
//                contentLayout.requestLayout();
                drawer.invalidate();
                drawer.requestLayout();
            }
        };
        drawer.addDrawerListener(toggle);
        toggle.syncState();
        navigationView.setNavigationItemSelectedListener(this);
        // make app fullscreen
        this.getWindow().setFlags(WindowManager.LayoutParams.FLAG_FULLSCREEN, WindowManager.LayoutParams.FLAG_FULLSCREEN);

        LinearLayout contentLayout = findViewById(R.id.drill_selector_content);
        customSurfaceView = new CustomSurfaceView(getBaseContext());
        customSurfaceView.setOnTouchListener(this);
        contentLayout.addView(customSurfaceView);
    }

    @Override
    public void onBackPressed() {
        DrawerLayout drawer = findViewById(R.id.drawer_layout);
        if (drawer.isDrawerOpen(GravityCompat.START)) {
            drawer.closeDrawer(GravityCompat.START);
        } else {
            super.onBackPressed();
        }
    }


    @Override
    public boolean onCreateOptionsMenu(Menu menu) {
        // Inflate the menu; this adds items to the action bar if it is present.
        getMenuInflater().inflate(R.menu.drill_selector, menu);
        draw();
        return true;
    }

    @Override
    public boolean onPrepareOptionsMenu(Menu menu) {
        return super.onPrepareOptionsMenu(menu);
    }

    @Override
    public boolean onOptionsItemSelected(MenuItem item) {
        // Handle action bar item clicks here. The action bar will
        // automatically handle clicks on the Home/Up button, so long
        // as you specify a parent activity in AndroidManifest.xml.
        int id = item.getItemId();

        //noinspection SimplifiableIfStatement
        if (id == R.id.action_settings) {
            return true;
        }

        return super.onOptionsItemSelected(item);
    }

    @SuppressWarnings("StatementWithEmptyBody")
    @Override
    public boolean onNavigationItemSelected(@NonNull MenuItem item) {
        // Handle navigation view item clicks here.
        int id = item.getItemId();

        if (id == R.id.nav_home) {
            // Handle the camera action
        } else if (id == R.id.nav_gallery) {

        } else if (id == R.id.nav_slideshow) {

        } else if (id == R.id.nav_tools) {

        } else if (id == R.id.nav_share) {

        } else if (id == R.id.nav_send) {

        }

        DrawerLayout drawer = findViewById(R.id.drawer_layout);
        drawer.closeDrawer(GravityCompat.START);
        return true;
    }

    @SuppressLint("ClickableViewAccessibility")
    @Override
    public boolean onTouch(View v, MotionEvent event) {
        Log.d(TAG, "onTouch");
        return false;
    }

    void draw() {
        Canvas canvas = customSurfaceView.surfaceHolder.lockCanvas();
        if (canvas == null){
            Log.d(TAG, "draw(): canvas null");
            return;
        }
        Log.d(TAG, "draw()");
        // draw Table
        // cloth
        Paint paint = customSurfaceView.paint;
        paint.setStyle(Paint.Style.FILL);
        //canvas.drawARGB(255, 0, 0, 0);
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
        customSurfaceView.surfaceHolder.unlockCanvasAndPost(canvas);
    }

    float screenX(double x) {
        return (float) (x * customSurfaceView.screenScale + customSurfaceView.screenOffset);
    }

    float screenY(double y) {
        return (float) (y * customSurfaceView.screenScale);
    }

    double rX(float sX) {
        return (sX - customSurfaceView.screenOffset) / customSurfaceView.screenScale;
    }

    double rY(float sY) {
        return (sY - 20) / customSurfaceView.screenScale;
    }
}
