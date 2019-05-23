package com.billardtrainer;

import org.json.JSONObject;

import java.util.*;

class Shot {
    private ArrayList<Ball> sBalls = new ArrayList<>();
    Vec3 target, pocket;
    Ball ballToPot;

    Shot(ArrayList<Ball> b, Vec3 t, Vec3 p, Ball btp) {
        for (Ball ball : b)
            sBalls.add(ball.cloneBall());
        target = t;
        pocket = p;
        ballToPot = btp;
    }

    @SuppressWarnings("unused")
    void addJSON(JSONObject lines, JSONObject ghosts) {
        for (Ball ball : sBalls)
            System.out.println("x");
    }
}
