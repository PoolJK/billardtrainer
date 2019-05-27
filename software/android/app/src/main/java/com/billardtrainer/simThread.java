package com.billardtrainer;

import android.util.Log;

import java.util.ArrayList;
import java.util.Locale;

import static com.billardtrainer.Cons.*;
import static com.billardtrainer.Utils.*;

class simThread extends Thread {

    private static final String TAG = "simThread";

    private ArrayList<Ball> ballsOnTable;
    private ArrayList<Double> timeSteps;

    /**
     * Initialize a new simThread
     * @param ballsOnTable balls on table
     */
    simThread(ArrayList<Ball> ballsOnTable) {
        this.ballsOnTable = ballsOnTable;
        timeSteps = new ArrayList<>();
        timeSteps.add(0d);
    }

    /**
     * The actual simulation runnable
     */
    @Override
    public void run() {
        Log.v(TAG, "simThread started");
        double t0 = now();
        // first timeStep is [0]->"0.0"
        int timestep = 0;
        double t, new_t, coll_t;
        boolean moving, collision;
        do {
            moving = collision = false;
            // get next timeStep
            t = timeSteps.get(timestep);
            // set new_t to arbitrarily high value (depends on whether using s or ms)
            new_t = 10000;
            for (Ball b : ballsOnTable) {
                bNode node = b.getNode(t);
                // if ball is moving at this node
                if (node.state > STATE_STILL) {
                    Log.v(TAG, "this node: " + node);
                    moving = true;
                    // get next node t without collisions
                    new_t = Math.min(new_t, node.getNextInherentT());
                    coll_t = node.getNextCollisionT(ballsOnTable);
                    if (t < coll_t && coll_t < new_t) {
                        new_t = coll_t;
                        // TODO: add collision something...
                        collision = true;
                    }
                    Log.v(TAG, String.format(Locale.ROOT, "new_t: %.2f", new_t));
                }
            }
            if (collision)
                solveCollisions(ballsOnTable, t, new_t);
            // if moving, add next timeStep and nodes
            if (moving) {
                for (Ball ball : ballsOnTable) {
                    if (ball.getNode(t).inherentTime == new_t) {
                        ball.addNode(ball.getNode(t).nextNode(new_t));
                    }
                }
                timeSteps.add(t + new_t);
                timestep++;
            }
        } while (timestep < 4 && t < timeSteps.get(timeSteps.size() - 1));
        Main.handler.obtainMessage(Main.SIM_RESULT, ballsOnTable).sendToTarget();
        Log.v(TAG, String.format(Locale.ROOT, "simThread took %.0fms", now() - t0));
    }

    /**
     * Solve all collisions and set states accordingly
     *
     * @param ballsOnTable balls on the table
     * @param t            last node time [s]
     * @param new_t        new node time [s]
     */
    private void solveCollisions(ArrayList<Ball> ballsOnTable, double t, double new_t) {
        for (Ball ball : ballsOnTable)
            if (ball.getNode(t).collisionTime >= t && ball.getNode(t).collisionTime <= new_t) {
                Log.v(TAG, String.format(Locale.ROOT, "Ball %d: solving collision @%.2fs", ball.id, ball.getNode(t).collisionTime));
                ball.addNode(ball.getNode(t).nextNode(new_t));
            }
    }
}

