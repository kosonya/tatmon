package ru.auditory.sometest;

//import com.theateam.tatclient.R;

import android.app.Activity;
import android.content.Context;
import android.location.Location;
import android.location.LocationListener;
import android.location.LocationManager;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.os.Message;
import android.os.AsyncTask;
import android.telephony.NeighboringCellInfo;
import android.telephony.TelephonyManager;
import android.util.Log;
import android.view.View;
import android.view.View.OnClickListener;
import android.widget.CompoundButton;
import android.widget.CompoundButton.OnCheckedChangeListener;
import android.widget.Button;
import android.widget.CheckBox;
import android.widget.EditText;
import android.widget.TextView;

import java.lang.Void;
import java.util.List;

public class SomeTest extends Activity {

	// private static final String TAG = "ThreadMessaging";
	private TextView exceptions_TextView, gps_TextView, gsm_TextView;
	private EditText did_EditText;

	private LocationManager locMan;
	private TelephonyManager telephonyManager;

	private String host = "vkphoto.auditory.ru";
	private int port = 31415;
	private int did = 1;
	static private DataManager dataManager;
	static private Object dataManagerLock;

	// private Object dataManagerSync;

	class DataManager extends Thread {
		public boolean dataManagerWorks = false;
		public boolean dataManagerAlive = true;

		public boolean dataManagerGPS = false;

		protected String exceptions_text, gps_text, gsm_text;
		// private Handler gsmHandler;
		private LocationListener gpsListener = null;
		private double lng = 0.0, ltd = 0.0, acc = 0.0;

		synchronized public void die() {
			dataManagerAlive = false;
		}

		synchronized protected void uiSync() {
			runOnUiThread(new Runnable() {
				public void run() {
					if (exceptions_text != "") {
						exceptions_TextView.setText(exceptions_text);
					}
					if (gps_text != "") {
						gps_TextView.setText(gps_text);
					}
					if (gsm_text != "") {
						gsm_TextView.setText(gsm_text);
					}
				}
			});
		}

		private void updateGSM() {
			String info = "";
			try {

				List<NeighboringCellInfo> neighboringCells = telephonyManager
						.getNeighboringCellInfo();

				info = "Stations count: " + neighboringCells.size() + "\n";
				for (NeighboringCellInfo cell : neighboringCells) {
					int networktype = cell.getNetworkType();
					int Rssi = cell.getRssi();
					String rssi = "";
					if (Rssi == NeighboringCellInfo.UNKNOWN_RSSI) {
						rssi = "UNKNOWN";
					} else {
						rssi = Integer.toString(Rssi);
					}
					switch (networktype) {
					case TelephonyManager.NETWORK_TYPE_GPRS:
						info += "CID: " + Integer.toHexString(cell.getCid())
								+ " Signal: " + rssi + " type: GPRS\n";
						break;
					case TelephonyManager.NETWORK_TYPE_EDGE:
						info += "CID: " + Integer.toHexString(cell.getCid())
								+ " Signal: " + rssi + " type: EDGE\n";
						break;
					case TelephonyManager.NETWORK_TYPE_UMTS:
						info += "Psc: " + Integer.toHexString(cell.getPsc())
								+ " Signal " + rssi + " type: UMTS\n";
						break;
					default:
						info += "CID: " + Integer.toHexString(cell.getCid())
								+ " Psc: " + Integer.toHexString(cell.getPsc())
								+ " Signal " + rssi + " type: " + networktype
								+ "\n";
					}

				}
			} catch (Exception e) {
				exceptions_text += e.getMessage();

			}
			gsm_text = info;
		}

		public void run() {

			// boolean works = false;
			boolean alive = true;
			// int r = 0; // It don't want to work with Void O_o
			//exceptions_text = "Started";
			uiSync();
			while (alive) {
				// gps_text = Integer.toHexString(r);
				// r++;
				synchronized (dataManager) {
					// exceptions_text += "O";
					if (!dataManagerWorks) {
						try {
							dataManager.wait();
						} catch (InterruptedException e) {
							exceptions_text += e.getMessage();
							uiSync();
						}
					}

				}

				synchronized (dataManager) {
					if (dataManagerGPS && gpsListener == null) {
						gps_text = "GPS starting...";
						uiSync();
						gpsListener = new LocationListener() {
							public void onLocationChanged(Location location) {
								ltd = location.getLatitude();
								lng = location.getLongitude();
								acc = location.getAccuracy();
								String lat = "" + ltd;
								String lon = "" + lng;
								String a = "" + acc;
								gps_text = "Latitide: " + lat
										+ "\nLongtotude: " + lon
										+ "\nAccuracy: " + a;
								uiSync();
							}

							public void onProviderDisabled(String provider) {
								gps_text = "GPS provider disabled";
								uiSync();
							}

							public void onProviderEnabled(String provider) {
							}

							public void onStatusChanged(String provider,
									int status, Bundle extras) {
							}
						};
					} else if (!dataManagerGPS && gpsListener != null) {
						gpsListener = null;
					}
				}
				updateGSM();
				uiSync();

				try {
					sleep(1000);
				} catch (InterruptedException e) {
					e.printStackTrace();
				}
				synchronized (dataManager) {
					alive = dataManagerAlive;
				}

			}
		}

	}

	/** Called when the activity is first created. */
	@Override
	public void onCreate(Bundle savedInstanceState) {
		super.onCreate(savedInstanceState);
		setContentView(R.layout.main);
		// mTextView = (TextView)findViewById(R.id.text);
		gsm_TextView = (TextView) findViewById(R.id.gsm_TextView);
		gps_TextView = (TextView) findViewById(R.id.gps_TextView);
		exceptions_TextView = (TextView) findViewById(R.id.exceptions_TextView);
		did_EditText = (EditText) findViewById(R.id.did_EditText);
		locMan = (LocationManager) getSystemService(Context.LOCATION_SERVICE);
		telephonyManager = (TelephonyManager) getSystemService(Context.TELEPHONY_SERVICE);

		CheckBox sendGpsCheckBox = (CheckBox) findViewById(R.id.gps_checkBox);
		sendGpsCheckBox
				.setOnCheckedChangeListener(new OnCheckedChangeListener() {
					@Override
					public void onCheckedChanged(CompoundButton buttonView,
							boolean isChecked) {
						dataManager.dataManagerGPS = isChecked;

					}

				});

		Button button = (Button) findViewById(R.id.button1);
		button.setOnClickListener(new OnClickListener() {

			@Override
			public void onClick(View v) {
				// new DataManagerTask().execute();
				// new Thread(new DataManager()).start();

				synchronized (dataManager) {
					dataManager.dataManagerWorks = !dataManager.dataManagerWorks;
					if (dataManager.dataManagerWorks)
						dataManager.notify();
					else {
						gps_TextView.setText("-");
						gsm_TextView.setText("-");
					}

				}

			}

		});

		dataManager = new DataManager();
		dataManager.dataManagerWorks = false;
		dataManager.start();
	}

	@Override
	protected void onDestroy() {

		dataManager.die();
		super.onDestroy();
	}

}