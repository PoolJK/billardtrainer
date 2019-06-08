package com.billardtrainer;

import static com.billardtrainer.Constants.*;

class Solver {
    /**
     * Supposed to return the collision time for any two nodes (in any states...)
     * Needs some Solver like Runge-Kutta etc.
     * check https://introcs.cs.princeton.edu/java/94diffeq/
     * https://softmath.com/tutorials2/java-solve-second-order-differential-equations.html
     *
     * @param node_a First node
     * @param node_b Second node
     * @return The time of collision or arbitrarily high number [s]
     */
    static double getCollisionTime(Node node_a, Node node_b) {
        double fax, fbx, fay, fby;
        double v0a = node_a.V0.length();
        double vc0a = node_a.Vc0.length();
        double v0b = node_b.V0.length();
        double vc0b = node_b.Vc0.length();
        switch (node_a.state) {
            case STATE_ROLLING:
                fax = 0.5 * frictionClothRoll * node_a.V0.x / v0a;
                fay = 0.5 * frictionClothRoll * node_a.V0.y / v0a;
                break;
            case STATE_STUN:
            case STATE_SLIDING:
                fax = 0.5 * frictionClothSpin * node_a.Vc0.x / vc0a;
                fay = 0.5 * frictionClothSpin * node_a.Vc0.y / vc0a;
                break;
            default:
                fax = fay = 0;
        }
        switch (node_b.state) {
            case STATE_ROLLING:
                fbx = 0.5 * frictionClothRoll * node_b.V0.x / v0b;
                fby = 0.5 * frictionClothRoll * node_b.V0.y / v0b;
                break;
            case STATE_STUN:
            case STATE_SLIDING:
                fbx = 0.5 * frictionClothSpin * node_b.Vc0.x / vc0b;
                fby = 0.5 * frictionClothSpin * node_b.Vc0.y / vc0b;
                break;
            default:
                fbx = fby = 0;
        }
        double tmax = 10, dt = tmax / 100, dist, dx, dy, ttest;
        for (ttest = 0; ttest <= tmax + dt; ttest += dt) {
            dx = node_a.P0.x + ttest * node_a.V0.x - ttest * ttest * fax
                    - (node_b.P0.x + ttest * node_b.V0.x - ttest * ttest * fbx);
            dy = node_a.P0.y + ttest * node_a.V0.y - ttest * ttest * fay
                    - (node_b.P0.y + ttest * node_b.V0.y - ttest * ttest * fby);
            dist = dx * dx + dy * dy;
            if (dist <= 4.0 * ballRadius * ballRadius) {
                dt /= 10.0;
                if (dt <= precision)
                    break;
                ttest -= 10.0 * dt;
            }
        }
        return Math.abs(ttest) < precision ? 10000 : ttest;
    }
}