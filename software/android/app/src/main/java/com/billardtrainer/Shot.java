package com.billardtrainer;

import java.util.*;

class Shot
{
	ArrayList<Ball> sBalls = new ArrayList<>();
	Vec3 target, pocket;
	int ballToPot, id;

	Shot(ArrayList<Ball> b, Vec3 t, Vec3 p, int btp, int i) {
		for (int bi = 0; bi < b.size(); bi++)
			sBalls.add(b.get(bi).cloneBall());
		target = t;
		pocket = p;
		ballToPot = btp;
		id = i;
	}

	int getBallToPot() {
		int bi;
		for (bi = 0; bi < sBalls.size(); bi++)
			if (sBalls.get(bi).id == ballToPot)
				break;
		return bi;
	}
}
