package com.billardtrainer;

import java.util.*;

class Shot {
    ArrayList<Ball> sBalls = new ArrayList<>();
    Vec3 target, pocket;
    Ball ballToPot;

    Shot(ArrayList<Ball> b, Vec3 t, Vec3 p, Ball btp) {
        for (Ball ball : b)
            sBalls.add(ball.cloneBall());
        target = t;
        pocket = p;
        ballToPot = btp;
    }

    String getJSONString() {
        StringBuilder res = new StringBuilder("\"lines\":{");
        Ball cue = sBalls.get(0);
        Ball ballon = ballToPot;
        // from cueball to target
        res.append(String.format(Locale.ROOT, "\"0\":{\"x1\":%.0f,\"y1\":%.0f,\"x2\":%.0f,\"y2\":%.0f}",
                cue.Pos.x, cue.Pos.y, target.x, target.y));
        // from ball_on to pocket:
        res.append(String.format(Locale.ROOT, ",\"1\":{\"x1\":%.0f,\"y1\":%.0f,\"x2\":%.0f,\"y2\":%.0f}",
                ballon.Pos.x, ballon.Pos.y, pocket.x, pocket.y
        ));
        res.append(String.format(Locale.ROOT, "},\"ghost\":{\"x\":%.0f,\"y\":%.0f}}",
                target.x, target.y));
        return res.toString();
    }
}
