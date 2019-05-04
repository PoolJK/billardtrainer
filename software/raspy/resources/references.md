1. coordinate system
   (0,0) = top left = yellow pocket
   (1778,3556) = bottom right = right black pocket
   measured in millimetres

2. position formats
   point: (x,y)
   ball: {value: p}, where value in 0..7, p = point
   line: {l: (p1,p2)}
   circle: {c: (p,r)}, where p = center, r = radius
   rect: {r: (p1,p2)} where p1 = top left, p2 = bottom right
  
3. Table Params
	 tableLength = 3556;
	 tableWidth = 1778;
	 DDistance = 737;
	 DRadius = 292;
	 blackDistance = 324;

4. Ball Params
	 ballRadius = 26.25;

5. Spot Params
   yellowSpot = (tableWidth / 2 - DRadius, DDistance);
	 greenSpot = (tableWidth / 2 + DRadius, DDistance);
	 brownSpot = (tableWidth / 2, DDistance);
   blueSpot = (tableWidth / 2, tableLength / 2);
   pinkSpot = (tableWidth / 2, tableLength / 4 * 3);
	 blackSpot = (tableWidth / 2, tableLength - blackDistance);

   reds: //TODO: y-direction negative, change to positive
   double yd = Math.sqrt(3 * ballRadius * ballRadius);
		double yc = pinkSpot.y - precision;
		ballsOnTable.add(new Ball(pinkSpot.x, yc - yd, 1, 8));
		ballsOnTable.add(new Ball(pinkSpot.x - ballRadius, yc - 2 * yd, 1, 9));
		ballsOnTable.add(new Ball(pinkSpot.x + ballRadius, yc - 2 * yd, 1, 10));
		ballsOnTable.add(new Ball(pinkSpot.x - 2 * ballRadius, yc - 3 * yd, 1,
				11));
		ballsOnTable.add(new Ball(pinkSpot.x, yc - 3 * yd, 1, 12));
		ballsOnTable.add(new Ball(pinkSpot.x + 2 * ballRadius, yc - 3 * yd, 1,
				13));
		ballsOnTable.add(new Ball(pinkSpot.x - 3 * ballRadius, yc - 4 * yd, 1,
				14));
		ballsOnTable.add(new Ball(pinkSpot.x - 1 * ballRadius, yc - 4 * yd, 1,
				15));
		ballsOnTable.add(new Ball(pinkSpot.x + 1 * ballRadius, yc - 4 * yd, 1,
				16));
		ballsOnTable.add(new Ball(pinkSpot.x + 3 * ballRadius, yc - 4 * yd, 1,
				17));
		ballsOnTable.add(new Ball(pinkSpot.x - 4 * ballRadius, yc - 5 * yd, 1,
				18));
		ballsOnTable.add(new Ball(pinkSpot.x - 2 * ballRadius, yc - 5 * yd, 1,
				19));
		ballsOnTable.add(new Ball(pinkSpot.x, yc - 5 * yd, 1, 20));
		ballsOnTable.add(new Ball(pinkSpot.x + 2 * ballRadius, yc - 5 * yd, 1,
				21));
		ballsOnTable.add(new Ball(pinkSpot.x + 4 * ballRadius, yc - 5 * yd, 1,
				22));
