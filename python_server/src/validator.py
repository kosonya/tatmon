# -*- coding: utf8 -*-

def validator(raw_data):
	if not raw_data:
		return None
	if not raw_data.has_key('GPS') or not raw_data.has_key('GSM'):
		return None
	if not raw_data['GPS'] or not raw_data['GSM']:
		return None
	if not all (k in raw_data['GPS'] for k in ['acc', 'lng', 'ltd']):
		return None
	if not all (k in raw_data['GSM'] for k in ['cellcount', 'cells']):
		return None
	if raw_data['GPS']['acc'] == 0.0:
		return None
		
	new_cells = []
	for cell in raw_data['GSM']['cells']:
		if not all (k in cell for k in ['CID', 'RSSI', 'type']):
			continue
		cid = int(cell['CID'])
		rssi = int(cell['RSSI'])
		if not (0 <= rssi <= 31):
			continue
		if cell['type'] not in ['EDGE', 'GPRS']:
			continue
		new_cells.append({"CID": cid, "RSSI": rssi, "type": cell['type']} )
	if len(new_cells) == 0:
		return 0
	raw_data['GSM']['cellcount'] = len(new_cells)
	raw_data['GSM']['cells'] = new_cells
	raw_data['GPS']['lng'], raw_data['GPS']['ltd'] = raw_data['GPS']['ltd'], raw_data['GPS']['lng']
	return raw_data
