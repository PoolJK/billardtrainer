package com.billardtrainer;

import java.util.*;

class Shot {
    ArrayList<Ball> sBalls = new ArrayList<>();
    Vec3 target, pocket;
    int ballToPot;

    Shot(ArrayList<Ball> b, Vec3 t, Vec3 p, int btp) {
        for (int bi = 0; bi < b.size(); bi++)
            sBalls.add(b.get(bi).cloneBall());
        target = t;
        pocket = p;
        ballToPot = btp;
    }

    int getBallToPot() {
        int bi;
        for (bi = 0; bi < sBalls.size(); bi++)
            if (sBalls.get(bi).id == ballToPot)
                break;
        return bi;
    }

    String getJSONString() {
        StringBuilder res = new StringBuilder();
        Ball cue = sBalls.get(0);
        Ball ballon = sBalls.get(ballToPot);
        // from cueball to target
        res.append(String.format(Locale.ROOT, "\"0\":{\"x1\":%.0f,\"y1\":%.0f,\"x2\":%.0f,\"y2\":%.0f}",
                cue.Pos.x, cue.Pos.y, target.x, target.y));
        // from ball_on to pocket:
        res.append(String.format(Locale.ROOT, ",\"1\":{\"x1\":%.0f,\"y1\":%.0f,\"x2\":%.0f,\"y2\":%.0f}",
                ballon.Pos.x, ballon.Pos.y, pocket.x, pocket.y
        ));
        return res.toString();
    }
}
