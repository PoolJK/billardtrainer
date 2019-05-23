package com.billardtrainer;

import android.support.annotation.NonNull;

import java.util.Locale;

import static com.billardtrainer.Cons.*;

class Vec3 {

    double x, y, z;

    Vec3() {
        x = y = z = 0;
    }

    Vec3(double x, double y, double z) {
        this.x = x;
        this.y = y;
        this.z = z;
    }

    double length() {
        return Math.sqrt(x * x + y * y + z * z);
    }

    double distanceTo(Vec3 P) {
        return Math.sqrt(Math.pow(P.x - x, 2) + Math.pow(P.y - y, 2)
                + Math.pow(P.z - z, 2));
    }

    @SuppressWarnings("unused")
    Vec3 add(Vec3 in) {
        return new Vec3(x + in.x, y + in.y, z + in.z);
    }

    Vec3 subtract(Vec3 in) {
        return new Vec3(x - in.x, y - in.y, z - in.z);
    }

    private double scalar(Vec3 in) {
        return x * in.x + y * in.y + z * in.z;
    }

    double deltaAngle(Vec3 in) {
        return Math.acos(this.scalar(in) / (this.length() * in.length()));
    }

    void normalize() {
        double l = 1 / length();
        x *= l;
        y *= l;
        z *= l;
    }

    @NonNull
    public String toString() {
        if (this == yellowPocket)
            return ("yellowPocket");
        if (this == greenPocket)
            return ("greenPocket");
        if (this == blueLPocket)
            return ("blueLPocket");
        if (this == blueRPocket)
            return ("blueRPocket");
        if (this == blackLPocket)
            return ("blackLPocket");
        if (this == blackRPocket)
            return ("blackRPocket");
        return String.format(Locale.ROOT, "{x:%.0f,y:%.0f,z:%.0f}", x, y, z);
    }
}
