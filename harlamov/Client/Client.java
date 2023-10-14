import java.util.List;
import java.net.*;
import java.io.ObjectOutputStream;
import java.io.ByteArrayOutputStream;
class Client {
	public static void main(String[] args){
		int port = 31415;
		try {
			String data = "{\"message\": \"hello|\"}";
			DatagramSocket clientSocket = new DatagramSocket();
			InetAddress ip = InetAddress.getByName("localhost");
			ByteArrayOutputStream bos = new ByteArrayOutputStream();
			ObjectOutputStream ous = new ObjectOutputStream(bos);
			DatagramPacket sendPacket = new DatagramPacket(data.getBytes(), data.length(), ip, port);
			for(int i = 0; i < 10; i++) {
				clientSocket.send(sendPacket);
				System.out.println("Sent: " + data);
			}
		} catch (Exception e) {
			System.out.println(e.getMessage());
		}
	}
}
