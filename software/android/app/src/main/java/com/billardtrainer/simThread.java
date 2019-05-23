package com.billardtrainer;

import android.util.Log;

import java.util.ArrayList;

import static com.billardtrainer.Cons.*;

class simThread extends Thread {

    private static final String TAG = "simThread";

    private ArrayList<Ball> ballsOnTable;
    private ArrayList<Double> timesteps;

    simThread(ArrayList<Ball> ballsOnTable) {
        this.ballsOnTable = ballsOnTable;
        timesteps = new ArrayList<>();
        timesteps.add(0d);
    }

    @Override
    public void run() {
        Log.d(TAG, "simThread started");
        // first timestep is [0]->"0.0"
        int timestep = 0;
        double t, new_t;
        boolean moving;
        do {
            moving = false;
            // get next timestep
            t = timesteps.get(timestep);
            // set new_t to arbitrarily high value (depends on whether using s or ms)
            new_t = 10000;
            for (Ball b : ballsOnTable) {
                bNode node = b.getNode(t);
                // if ball is moving at this node
                if (node.state > STATE_STILL) {
                    Log.d(TAG, "this node: " + node);
                    moving = true;
                    // get next node t without collisions
                    new_t = Math.min(new_t, node.getNextInherentT());
                    Log.d(TAG, "new_t: " + new_t);
                    // in testing only cueball has a node, so just add one
                    b.addNode(node.nextNode(new_t));
                }
            }
            // if moving, add next timestep
            if (moving) {
                timesteps.add(t + new_t);
                timestep++;
            }
        } while (timestep < 4 && t < timesteps.get(timesteps.size() - 1));
        Main.handler.obtainMessage(Main.SIM_RESULT, ballsOnTable).sendToTarget();
        Log.d(TAG, "simThread finished");
    }
}

