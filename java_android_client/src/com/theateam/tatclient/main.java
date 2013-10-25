package com.theateam.tatclient;

import com.theateam.tatclient.R;

import com.theateam.tatlib.*;

import android.app.Activity;
import android.content.Context;
import android.location.Location;
import android.location.LocationListener;
import android.location.LocationManager;
import android.os.Bundle; //import android.os.Handler;
//import android.os.Looper;
//import android.os.Message;
//import android.os.AsyncTask;
import android.util.Log;
import android.telephony.NeighboringCellInfo;
import android.telephony.TelephonyManager; //import android.util.Log;
import android.view.View;
import android.view.View.OnClickListener;
import android.widget.CompoundButton;
import android.widget.CompoundButton.OnCheckedChangeListener;
import android.widget.Button;
import android.widget.CheckBox;
import android.widget.EditText;
import android.widget.TextView;

//import java.lang.Void;
import java.util.List;
import java.net.*;
import java.io.ObjectOutputStream;
import java.io.ByteArrayOutputStream;

public class main extends Activity {

	// private static final String TAG = "ThreadMessaging";
	private TextView exceptions_TextView, gps_TextView, gsm_TextView;
	private EditText did_EditText;
	private Button start_Button;
	private CheckBox sendGpsCheckBox;
	private CheckBox inetCheckBox;

	private LocationManager locMan;
	private TelephonyManager telephonyManager;
	private LocationListener gpsListener;

	private GPSDaemon gpsDaemon;
	private InetDaemon inetDaemon;
	private DataManagerDaemon dmDaemon;

	private SharedData sharedData;

	private String host = "vkphoto.auditory.ru";
	private int port = 31415;
	private int did = 1;
	static private boolean started = false;

	// private Object dataManagerSync;
	class InetManager extends AThread {
		private static final String TAG = "InetManager";
		DatagramSocket clientSocket = null;
		String exceptions_text = "";

		protected void syncUI() {
			runOnUiThread(new Runnable() {
				public void run() {
					if (exceptions_text != "") {
						exceptions_TextView.setText(exceptions_text);
						exceptions_text = "";
					}
				}
			});
		}

		@Override
		protected void atResumeCallback() {
			try {
				if (clientSocket == null)
					clientSocket = new DatagramSocket();
			} catch (Exception e) {
				exceptions_text = e.getMessage();
				syncUI();
			}
			Log.d(TAG, "atResumeCallback");
		}

		@Override
		protected void updateCallback() {
			try {

				InetAddress ip = InetAddress.getByName(host);
				byte[] sendData = new byte[1024]; // FIXME !!

				String out_data = "{}";
				String gpsjson = "{}";
				String gsmjson =  "{}";
				
				Packet p = new Packet();
				p.setGPS(sharedData.getGPSLng(), sharedData.getGPSLtd(),
						sharedData.getGPSAcc());

				ByteArrayOutputStream bos = new ByteArrayOutputStream();
				ObjectOutputStream ous = new ObjectOutputStream(bos);

				ous.writeObject(p);
				Log.d(TAG, bos.toString());
				// sendData = "Lol".getBytes();
				if(sharedData.isGPSEnabled())
				{
					gpsjson = "{\"lng\":" + Double.toString(sharedData.getGPSLng()) +
							", \"ltd\":" + Double.toString(sharedData.getGPSLtd()) +
							", \"acc\":" + Double.toString(sharedData.getGPSAcc()) + "}";
				}
				else
				{
					gpsjson = "{}";
				}
				
				try {
					gsmjson = sharedData.getGSM();
				} catch (Exception e){
					exceptions_text = "from getGSM: " + e.getMessage();
					gsmjson = "{}";
				}
				
				out_data = "{\"GSM\":" + gsmjson + ", \"GPS\":" + gpsjson + "}\n";
								
/*				DatagramPacket sendPacket = new DatagramPacket(bos
						.toByteArray(), bos.size(), ip, port);
*/
				DatagramPacket sendPacket = new DatagramPacket(
						out_data.getBytes(), out_data.length(), ip, port);
				clientSocket.send(sendPacket);
				// exceptions_text = "send";
				// syncUI();
				Log.d(TAG, "Send");
			} catch (Exception e) {
				exceptions_text = e.getMessage();
				syncUI();
				Log.e(TAG, e.getMessage());
			}
		}

		@Override
		protected void atSuspendCallback() {
			if (clientSocket != null) {
				clientSocket.close();
				clientSocket = null;
			}
			Log.d(TAG, "atSuspendCallback");
		}
	}

	class DataManager extends AThread {

		protected String exceptions_text, gsm_text;		
		
		synchronized protected void updateUI() {
			runOnUiThread(new Runnable() {
				public void run() {
					if (exceptions_text != "") {
						exceptions_TextView.setText(exceptions_text);
						exceptions_text = "";
					}
					if (gsm_text != "") {
						gsm_TextView.setText(gsm_text);
					}
				}
			});
		}

		protected void updateCallback() {
			String info = "";
			String gsmjson = "{}";
			boolean first = true;
			sharedData.setGSM("{}");
			try {

				List<NeighboringCellInfo> neighboringCells = telephonyManager
						.getNeighboringCellInfo();
				gsmjson = "{\"cellcount\":" + Integer.toString(neighboringCells.size()) +
						", \"cells\":[";
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
					if(first) first = false;
					else gsmjson += ", ";
					gsmjson += "{\"CID\":" + Integer.toString(cell.getCid()) +
							", \"Psc\":" + Integer.toString(cell.getPsc()) +
							", \"RSSI\":" + Integer.toString(cell.getRssi()) +
							", \"type\":";
					switch (networktype) {
					case TelephonyManager.NETWORK_TYPE_GPRS:
						info += "CID: " + Integer.toHexString(cell.getCid())
								+ " Signal: " + rssi + " type: GPRS\n";
						gsmjson += "\"GPRS\"";
						break;
					case TelephonyManager.NETWORK_TYPE_EDGE:
						info += "CID: " + Integer.toHexString(cell.getCid())
								+ " Signal: " + rssi + " type: EDGE\n";
						gsmjson += "\"EDGE\"";
						break;
					case TelephonyManager.NETWORK_TYPE_UMTS:
						info += "Psc: " + Integer.toHexString(cell.getPsc())
								+ " Signal " + rssi + " type: UMTS\n";
						gsmjson += "\"UMTS\"";
						break;
					default:
						info += "CID: " + Integer.toHexString(cell.getCid())
								+ " Psc: " + Integer.toHexString(cell.getPsc())
								+ " Signal " + rssi + " type: " + networktype
								+ "\n";
						gsmjson += "\"UNKNOWN\"";
					}
					gsmjson += "}";
				}
				gsmjson += "]}";
			} catch (Exception e) {
				exceptions_text += e.getMessage();

			}
			gsm_text = info;
			try {
				sharedData.setGSM(gsmjson);
			} catch (Exception e) {
				exceptions_text += "from setGSM: " + e.getMessage();
			}
			updateUI();
		}

	}

	class GPSDaemon extends DaemonCtrl {

		@Override
		protected boolean canResume() {
			return started && sendGpsCheckBox.isChecked();
		}

		@Override
		protected void resume() {
			locMan.requestLocationUpdates(LocationManager.GPS_PROVIDER, 0, 0,
					gpsListener);
			sharedData.setGPSEnabled(true);
		}

		@Override
		protected void suspend() {
			locMan.removeUpdates(gpsListener);
			sharedData.setGPSEnabled(false);
		}
	}

	class InetDaemon extends DaemonCtrl {
		private InetManager inetManager;

		public InetDaemon() {
			super();
			inetManager = new InetManager();
		}

		@Override
		public void start() {
			inetManager.start();
		}

		@Override
		public void stop() {
			inetManager.setAThreadAlive(false);
		}

		@Override
		protected boolean canResume() {
			return started && inetCheckBox.isChecked();
		}

		@Override
		protected void resume() {
			synchronized (inetManager) {
				inetManager.setAThreadWorks(true);
				inetManager.notify();
			}
		}

		@Override
		protected void suspend() {
			inetManager.setAThreadWorks(false);
		}
	}

	class DataManagerDaemon extends DaemonCtrl {
		private DataManager dataManager;

		public DataManagerDaemon() {
			dataManager = new DataManager();
		}

		// Fuck
		public boolean getDataManagerWorks() {
			boolean w;
			synchronized (dataManager) {
				w = dataManager.getAThreadWorks();
			}
			return w;
		}

		@Override
		public void start() {
			dataManager.start();
			startChildren();
		}

		@Override
		public void stop() {
			stopChildren();
			dataManager.setAThreadAlive(false);
		}

		@Override
		protected boolean canResume() {
			return started;
		}

		@Override
		protected void resume() {
			synchronized (dataManager) {
				dataManager.setAThreadWorks(true);
				dataManager.notify();
			}
		}

		@Override
		protected void suspend() {
			dataManager.setAThreadWorks(false);
		}

		// gpsStartStop();

		// inetStartStop();
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

		inetCheckBox = (CheckBox) findViewById(R.id.inet_checkBox);
		inetCheckBox.setOnCheckedChangeListener(new OnCheckedChangeListener() {
			@Override
			public void onCheckedChanged(CompoundButton buttonView,
					boolean isChecked) {
				inetDaemon.updateState();
			}
		});
		gpsListener = new LocationListener() {
			public void onLocationChanged(Location location) {
				double lng = 0.0, ltd = 0.0, acc = 0.0;
				ltd = location.getLatitude();
				lng = location.getLongitude();
				acc = location.getAccuracy();
				String lat = "" + ltd;
				String lon = "" + lng;
				String a = "" + acc;
				gps_TextView.setText("Latitide: " + lat + "\nLongtotude: "
						+ lon + "\nAccuracy: " + a);
				sharedData.setGPS(lng, ltd, acc);

			}

			public void onProviderDisabled(String provider) {
				gps_TextView.setText("GPS provider disabled");

			}

			public void onProviderEnabled(String provider) {
			}

			public void onStatusChanged(String provider, int status,
					Bundle extras) {
			}
		};
		sendGpsCheckBox = (CheckBox) findViewById(R.id.gps_checkBox);
		sendGpsCheckBox
				.setOnCheckedChangeListener(new OnCheckedChangeListener() {
					@Override
					public void onCheckedChanged(CompoundButton buttonView,
							boolean isChecked) {
						gpsDaemon.updateState();
					}

				});

		start_Button = (Button) findViewById(R.id.button1);
		start_Button.setOnClickListener(new OnClickListener() {

			@Override
			public void onClick(View v) {
				boolean w = dmDaemon.getDataManagerWorks();

				// dataManager.setAThreadWorks(!dataManager.getAThreadWorks());
				start_Button.setText(!w ? "Stop" : "Start");
				started = !started;
				dmDaemon.updateState();

				if (!started) {
					gps_TextView.setText("-");
					gsm_TextView.setText("-");
				}

			}

		});

		// dataManager.dataManagerWorks = false;

		sharedData = new SharedData();
		inetDaemon = new InetDaemon();
		gpsDaemon = new GPSDaemon();
		dmDaemon = new DataManagerDaemon();
		dmDaemon.addChild(inetDaemon);
		dmDaemon.addChild(gpsDaemon);

		dmDaemon.start();
		Log.d("onCreate", "EE");

	}

	@Override
	protected void onDestroy() {

		dmDaemon.stop();

		super.onDestroy();
	}

}