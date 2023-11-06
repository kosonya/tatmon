package com.theateam.tatclient;
/*
import android.widget.TextView;
import android.telephony.*;
import java.util.List;

import android.app.Activity;
import android.os.AsyncTask;
import android.os.Bundle;
import android.telephony.PhoneStateListener;
import android.telephony.TelephonyManager;
import android.telephony.gsm.GsmCellLocation;

import java.lang.Integer;

public class CellSignal extends AsyncTask<Object, String, Void>{
	TextView m_TextView;
	String info = "";
	TelephonyManager telephonyManager;
	PhoneStateListener listener;
	@Override
	protected Void doInBackground(Object... params) {
		m_TextView = (TextView) params[0];
//		telephonyManager = (TelephonyManager) params[1];
//		publishProgress("telephony manager created");
		List<NeighboringCellInfo> neighboringCells = (List<NeighboringCellInfo>) params[1]; 
//		publishProgress("list created");
		for(NeighboringCellInfo cell: neighboringCells)
		{
			publishProgress("Psc: " + Integer.toHexString(cell.getPsc()) + " signal level: " + cell.getRssi() + " type: " + cell.getNetworkType());
		}
		return null;
	}
	
    protected void onProgressUpdate(String... progress) {
        info += '\n' + progress[0];
        m_TextView.setText(info);
    }

}
*/