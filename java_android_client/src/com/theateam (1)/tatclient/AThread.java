package com.theateam.tatclient;

public abstract class AThread extends Thread {
	
	protected boolean aThreadWorks = false;
	protected boolean aThreadAlive = true;
	

	synchronized boolean getAThreadWorks(){
		return aThreadWorks;
	}
	synchronized boolean getAThreadAlive(){
		return aThreadAlive;
	}
	
	synchronized void setAThreadWorks(boolean w){
		aThreadWorks = w;
		if(aThreadWorks)
			atResumeCallback();
		else
			atSuspendCallback();
	}
	synchronized void setAThreadAlive(boolean w){
		aThreadAlive = w;
	}
	public void run(){
		while(getAThreadAlive()){
			synchronized (this) {
				// exceptions_text += "O";
				if (!getAThreadWorks()) {
					try {
						this.wait();
					} catch (InterruptedException e) {
						//exceptions_text += e.getMessage();
						//uiSync();
					}
				}

			}
			updateCallback();
			try {
				sleep(1000);
			} catch (InterruptedException e) {
				e.printStackTrace();
			}
		}
	}
	protected abstract void updateCallback();
	protected void atSuspendCallback(){};
	protected void atResumeCallback(){};

}
