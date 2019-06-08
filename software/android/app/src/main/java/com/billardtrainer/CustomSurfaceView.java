package com.billardtrainer;

import android.content.Context;
import android.graphics.Color;
import android.graphics.Paint;
import android.graphics.PixelFormat;
import android.util.Log;
import android.view.SurfaceHolder;
import android.view.SurfaceView;

import java.util.Locale;

import static com.billardtrainer.Cons.*;
import static java.lang.String.format;

class CustomSurfaceView extends SurfaceView implements SurfaceHolder.Callback {

    SurfaceHolder surfaceHolder = null;
    Paint paint = null;
    int screenWidth, screenHeight;
    double screenScale, screenOffset;
    private static final String TAG = "CustomSurfaceView";

    CustomSurfaceView(Context context) {
        super(context);

        setFocusable(true);

        if (surfaceHolder == null) {
            // Get surfaceHolder object.
            surfaceHolder = getHolder();
            // Add this as surfaceHolder callback object.
            surfaceHolder.addCallback(this);
        }

        if (paint == null) {
            paint = new Paint();
        }

        // Set the parent view background color.
        this.setBackgroundColor(Color.TRANSPARENT);
        surfaceHolder.setFormat(PixelFormat.TRANSLUCENT);
    }

    @Override
    public void surfaceCreated(SurfaceHolder surfaceHolder) {
        Log.d(TAG, "surfaceCreated");
        // dimensions of relative Layout View
        // left right padding of 20 + 20
        // top bottom padding ??
        // Y size - button heights ???
        screenWidth = this.getWidth();
        screenHeight = this.getHeight();
        screenScale = Math.min((screenWidth - 40) / tableWidth,
                (screenHeight - 100) / tableLength);
        screenOffset = (screenWidth - tableWidth * screenScale) / 2;
        Log.d(TAG, format(Locale.ROOT, "screenW=%d screenH=%d screenScale=%1.2f screenOffset=%1.2f", screenWidth, screenHeight, screenScale, screenOffset));
    }

    @Override
    public void surfaceChanged(SurfaceHolder surfaceHolder, int i, int i1, int i2) {
        Log.d(TAG, "surfaceChanged");
    }

    @Override
    public void surfaceDestroyed(SurfaceHolder surfaceHolder) {
        Log.d(TAG, "surfaceDestroyed");
    }
}
