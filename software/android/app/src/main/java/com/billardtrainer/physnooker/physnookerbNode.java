package com.billardtrainer.physnooker;

import com.billardtrainer.Vec3;

import static com.billardtrainer.Cons.*;

public class physnookerbNode {
	Vec3 P0, V0, W0, Vc0;
	int state;
	double time;

	public physnookerbNode(Vec3 p, Vec3 v, Vec3 w, double t) {
		P0 = p;
		V0 = v;
		W0 = w;
		Vc0 = new Vec3();
		Vc0.x = V0.x - ballRadius * W0.y;
		Vc0.y = V0.y - ballRadius * W0.x;
		if (Math.abs(Vc0.x) < precision)
			Vc0.x = 0;
		if (Math.abs(Vc0.y) < precision)
			Vc0.y = 0;
		state = length(Vc0) > precision ? STATE_SLIDING
				: length(V0) > precision ? STATE_ROLLING : STATE_STILL;
		time = t;
	}
}
