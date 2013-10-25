package com.theateam.tatclient;

import java.util.List;
import java.util.LinkedList;

public abstract class DaemonCtrl {
	protected List<DaemonCtrl> children;

	public DaemonCtrl() {
		children = new LinkedList<DaemonCtrl>();

	}
	public void start(){}
	public void stop(){}
	
	protected void startChildren(){
		for(DaemonCtrl d: children){
			d.start();
		}
	}
	protected void stopChildren(){
		for(DaemonCtrl d: children){
			d.stop();
		}
	}
	protected abstract void resume();

	protected abstract void suspend();

	protected abstract boolean canResume();

	public void updateState() {
		if (canResume()) {
			resume();
		} else {
			suspend();
		}
		for (DaemonCtrl d : children) {
			d.updateState();
		}
	}

	public void addChild(DaemonCtrl child) {
		children.add(child);
	}

}
