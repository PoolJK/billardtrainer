package com.billardtrainer;

import org.json.JSONException;
import org.json.JSONObject;

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

    void addJSON(JSONObject lines, JSONObject ghosts) {
        JSONObject n = new JSONObject();
        try {
            // target ghost
            n.put("x", (int) target.x);
            n.put("y", (int) target.y);
            ghosts.put(String.format(Locale.ROOT, "%d", ghosts.length()), n);

            // cue to target line
            Ball cue = sBalls.get(0);
            for (Ball b : sBalls)
                if (b.value == 0) {
                    cue = b;
                    break;
                }
            JSONObject l = new JSONObject();
            l.put("x1", (int) cue.Pos.x);
            l.put("y1", (int) cue.Pos.y);
            l.put("x2", (int) target.x);
            l.put("y2", (int) target.y);
            lines.put(String.format(Locale.ROOT, "%d", lines.length()), l);

            // ball on to pocket line
            l = new JSONObject();
            l.put("x1", (int) ballToPot.Pos.x);
            l.put("y1", (int) ballToPot.Pos.y);
            l.put("x2", (int) pocket.x);
            l.put("y2", (int) pocket.y);
            lines.put(String.format(Locale.ROOT, "%d", lines.length()), l);
        } catch (JSONException e) {
            e.printStackTrace();
        }
    }
}
