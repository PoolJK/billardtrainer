package com.billardtrainer;

import java.util.ArrayList;
import java.util.Locale;

import android.graphics.Canvas;
import android.graphics.Paint;
import android.support.annotation.NonNull;

import org.json.JSONException;
import org.json.JSONObject;

import static com.billardtrainer.Cons.*;
import static com.billardtrainer.Utils.*;

class Ball {
    final int value, id;
    private int state = 0;
    private Vec3 V, W, Rot;
    Vec3 Pos;
    private ArrayList<bNode> nodes;

    Ball(double x_position, double y_position, int value, int id) {
        // place on table
        Pos = new Vec3(x_position, y_position, ballRadius);
        Rot = new Vec3(0, 0, 0);
        V = new Vec3(0, 0, 0);
        W = new Vec3(0, 0, 0);
        this.value = value;
        this.id = id;
        nodes = new ArrayList<>();
        addNode();
    }

    void addNode() {
        addNode(new bNode(Pos, V, W, 0, id, null));
    }

    void addNode(bNode node) {
        nodes.add(node);
    }

    bNode getNode() {
        return nodes.get(nodes.size() - 1);
    }

    bNode getNode(double t) {
        bNode lastNode = nodes.get(0);
        for (bNode node : nodes) {
            if (node.t == t)
                return node;
            if (node.t > t)
                return lastNode;
            lastNode = node;
        }
        return lastNode.nextNode(t);
    }

    void clearNodes() {
        nodes.clear();
        addNode();
    }

    @SuppressWarnings("SameParameterValue")
    void draw(Main app, Paint paint, Canvas canvas) {
        paint.setStyle(Paint.Style.FILL);
        paint.setColor(getBallColor(value));
        canvas.drawCircle(app.screenX(Pos.x), app.screenY(Pos.y),
                (float) (ballRadius * app.screenScale), paint);

        for (bNode node : nodes)
            node.draw(app, paint, canvas);
    }

    Ball cloneBall() {
        Ball b = new Ball(0, 0, value, id);
        b.Pos = new Vec3(Pos.x, Pos.y, Pos.z);
        b.Rot = new Vec3(Rot.x, Rot.y, Rot.z);
        b.state = state;
        b.V = new Vec3(V.x, V.y, V.z);
        b.W = new Vec3(W.x, W.y, W.z);
        return b;
    }

    @Override
    @NonNull
    public String toString() {
        switch (value) {
            case -1:
                return "none";
            case 0:
                return "Cueball";
            case 2:
                return "yellow";
            case 3:
                return "green";
            case 4:
                return "brown";
            case 5:
                return "blue";
            case 6:
                return "pink";
            case 7:
                return "black";
            default:
                return "red";
        }
    }

    String getJSONString() {
        JSONObject j = new JSONObject();
        try {
            j.put("x", (int) Pos.x);
            j.put("y", (int) Pos.y);
            j.put("v", value);
        } catch (JSONException e) {
            e.printStackTrace();
            return "";
        }
        return String.format(Locale.ROOT, "\"%d\":%s", id, j.toString());
    }
}
