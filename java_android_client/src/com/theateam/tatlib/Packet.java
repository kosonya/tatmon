package com.theateam.tatlib;

import java.io.Serializable;

public class Packet implements Serializable {
	/* $Rev: 41 $ */
	static final long serialVersionUID = 2L;

	protected int did;
	protected double gpsLng;
	protected double gpsLtd;
	protected double gpsAcc;
	

	public void setGPS(double lng, double ltd, double acc) {
		gpsLng = lng;
		gpsLtd = ltd;
		gpsAcc = acc;
	}

	public double getGPSLng() {
		return gpsLng;
	}

	public double getGPSLtd() {
		return gpsLtd;
	}

	public double getGPSAcc() {
		return gpsAcc;
	}
	
}
