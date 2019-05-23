package com.billardtrainer.physnooker;

import java.util.*;

import static com.physnooker.Cons.*;

public class physnookerBall {
	int value, id;
	int state = 0;
	boolean onTable = false;
	Vec3 Pos, Rot, V0, W0, Vc0;
	ArrayList<bNode> nodes = new ArrayList<bNode>();

	public Ball(double x, double y, int v, int i) {
		// place on table
		onTable = true;
		Pos = new Vec3(x, y, ballRadius);
		Rot = new Vec3(0, 0, 0);
		V0 = new Vec3(0, 0, 0);
		W0 = new Vec3(0, 0, 0);
		Vc0 = new Vec3(0, 0, 0);
		value = v;
		id = i;
		addCurrentNode(0);
	}

	void addCurrentNode(double t) {
		nodes.add(new bNode(Pos, V0, W0, t));
	}

	public void addNode(Vec3 pos, Vec3 V0, Vec3 w0, double t) {
		nodes.add(new bNode(pos, V0, w0, t));
	}

	public void setW0(double inx, double iny, double inz, double it) {
		W0.x = inx;
		W0.y = iny;
		W0.z = inz;
		W0.time = it;
	}

	public void setV0(double inx, double iny, double inz, double it) {
		V0.x = inx;
		V0.y = iny;
		V0.z = inz;
		V0.time = it;
		Vc0.x = V0.x - ballRadius * W0.y;
		Vc0.y = V0.y - ballRadius * W0.x;
		state = length(Vc0) > 0.001 ? STATE_SPINNING
				: length(V0) > 0.001 ? STATE_ROLLING : STATE_STILL;
		Vc0.time = it;
	}

	public static String getNameFromId(int id) {
		switch (id) {
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

	@Override
	public String toString() {
		return getNameFromId(id);
	}

	boolean checkCollision(double t) {
		// right cushion
		if (Math.abs(Pos.x - tableWidth + ballRadius) < precision) {
			V0.x *= -0.98;
			W0.y *= -0.7;
			return true;
		}
		// bottom cushion
		if (Math.abs(Pos.y + tableLength - ballRadius) < precision) {
			V0.y *= -0.98;
			W0.x *= -0.7;
			return true;
		}
		// left cushion
		if (Math.abs(Pos.x - ballRadius) < precision) {
			V0.x *= -0.98;
			W0.y *= -0.7;
			return true;
		}
		// top cushion
		if (Math.abs(Pos.y + ballRadius) < precision) {
			V0.y *= -0.98;
			W0.x *= -0.7;
			return true;
		}
		// balls

		// double dist;
		// for (Ball b : ballsOnTable)
		// if (b.onTable & id != b.id) {
		// dist = distance(p, b.Pos);
		// // TODO: wrong Pos, use nodes instead
		// if (dist <= ballRadius * 2.0 + precision)
		// // TODO: use relative velocities
		// {
		// Vec3 vrel = new Vec3(v.x, v.y, v.z);
		// add(vrel, b.V0);
		// Vec3 n = new Vec3(b.Pos.x, b.Pos.y, b.Pos.z);
		// subtract(n, p);
		// normalize(n);
		// multiply(vrel, n);
		// subtract(v, vrel);
		// add(b.V0, vrel);
		// if (first) {
		// Message.obtain(handler, TOAST_MESSAGE_LONG,
		// "vrel: " + vrel + "\nn: " + n).sendToTarget();
		// first = false;
		// }
		// // b.onTable = false;
		// return true;
		// }
		// }
		return false;
	}

	Vec3 getPos(double t) {
		double factor;
		switch (state) {
			case STATE_ROLLING:
				factor = 0.5 * friction_cloth_roll * t * t / length(V0);
				return new Vec3(Pos.x + V0.x * t - factor * V0.x, Pos.y + V0.y * t
						- factor * V0.y, Pos.z);
			case STATE_SPINNING:
				factor = 0.5 * friction_cloth * t * t / length(Vc0);
				return new Vec3(Pos.x + V0.x * t - factor * Vc0.x, Pos.y + V0.y * t
						- factor * Vc0.y, Pos.z);
			default:
				return new Vec3(0, 0, 0);
		}
	}

	Vec3 getV(double t) {
		double factor;
		switch (state) {
			case STATE_ROLLING:
				factor = friction_cloth_roll * t / length(V0);
				return new Vec3(V0.x - factor * V0.x, V0.y - factor * V0.y, 0);
			case STATE_SPINNING:
				factor = friction_cloth * t / length(Vc0);
				return new Vec3(V0.x - factor * Vc0.x, V0.y - factor * Vc0.y, 0);
			default:
				return new Vec3(0, 0, 0);
		}
	}

	Vec3 getW(double t) {
		double factor;
		switch (state) {
			case STATE_ROLLING:
				factor = friction_cloth_roll * t / (length(W0) * ballRadius);
				return new Vec3(W0.x - factor * W0.x, W0.y - factor * W0.y, 0);
			case STATE_SPINNING:
				factor = (-5.0 / 2.0) * friction_cloth * t / (length(Vc0) * ballRadius);
				return new Vec3(W0.x - factor * Vc0.y, W0.y - factor * Vc0.x, 0);
			default:
				return new Vec3(0, 0, 0);
		}
	}
}
