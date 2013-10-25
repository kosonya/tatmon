package com.theateam.tatclient;

public class SharedData {
	/*
	 * GPS
	 */
	protected double gpsLng;
	protected double gpsLtd;
	protected double gpsAcc;
	protected String gsmJSON;
	protected boolean gpsEnabled = false;

	public void setGPS(double lng, double ltd, double acc) {
		synchronized (this) {
			gpsLng = lng;
			gpsLtd = ltd;
			gpsAcc = acc;
		}
	}

	public double getGPSLng() {
		synchronized (this) {
			return gpsLng;
		}
	}

	public double getGPSLtd() {
		synchronized (this) {
			return gpsLtd;
		}
	}

	public double getGPSAcc() {
		synchronized (this) {
			return gpsAcc;
		}
	}

	public boolean isGPSEnabled() {
		synchronized (this) {
			return gpsEnabled;
		}
	}

	public void setGPSEnabled(boolean en) {
		synchronized (this) {
			gpsEnabled = en;
		}
	}
	public void setGSM(String json) {
		synchronized (this) {
			gsmJSON = new String(json);
		}
	}

	public String getGSM() {
		synchronized (this) {
			return new String(gsmJSON);
		}
	}
	
}
