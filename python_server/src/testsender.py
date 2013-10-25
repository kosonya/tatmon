import math

import transroute
import json
import socket

homeltd = 55.+45./60.+16.97/3600.
homelng = 37.+38./60.+48.52/3600.


#homelng = 37.+38./60.+52.6/3600.

begining = 55.752361111111114, 37.64678333333333
end = 55.755430555555556, 37.64849722222222
t = transroute.TransRoute(begining, end)

valid_data = {"GPS": {"ltd": homeltd, "lng":homelng, "acc": 3.14}}

closest = t.closest(valid_data)
dist = t.point_to_dist(valid_data)
pos = valid_data['GPS']['ltd'], valid_data['GPS']['lng']
dlat = pos[0] - closest[0]
dlon = pos[1] - closest[1]
err = math.sqrt(dlat*dlat + dlon*dlon)

cool_json = {"GPS": {"ltd": homeltd, "lng":homelng}, "Route":{"ltd": closest[0], "lng": closest[1], "dst": dist, "dstm": dist/8.987202970605459e-06}, "GPSerr":err, "GPSerrm": err/8.987202970605459e-06}


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('', 31416))
s.listen(1)
while True:
	conn, addr = s.accept()
	print "Connected from:", addr
	print json.dumps(cool_json)
	try:
		while True:
			conn.sendall(json.dumps(cool_json)+"\n")
		s.close()
	except Exception as e:	
		print e
