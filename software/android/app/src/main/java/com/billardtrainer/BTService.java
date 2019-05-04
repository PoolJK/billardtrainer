package com.billardtrainer;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.io.PrintStream;
import java.util.UUID;

import android.bluetooth.BluetoothAdapter;
import android.bluetooth.BluetoothDevice;
import android.bluetooth.BluetoothSocket;
import android.util.Log;

public class BTService extends Thread {
    private final static String TAG="BTService";
    private final static String MY_UUID ="00001101-0000-1000-8000-00805f9b34fb";
    private BluetoothSocket mSocket=null;
    private String mMessage;


    BTService(BluetoothDevice device) {
        Log.d(TAG,"Setting up connection...");
        try {
            UUID uuid = UUID.fromString(MY_UUID);
            mSocket = device.createRfcommSocketToServiceRecord(uuid);
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    private synchronized void read_from_socket(BluetoothSocket socket) throws IOException {
        InputStream is = socket.getInputStream();
        BufferedReader reader = new BufferedReader(new InputStreamReader(is));
        String data;
        while (true) {
            data = reader.readLine();
            Log.d(TAG,"Received: " + data);
            mMessage = data;
        }
    }

    public void send(String message){
        try {
            OutputStream os = mSocket.getOutputStream();
            PrintStream sender = new PrintStream(os);
            sender.print(message);
        } catch (IOException e) {
            e.printStackTrace();
        }
        Log.d(TAG,"Message sent");
    }

    public void run() {
        connectThread cT = new connectThread();
        cT.start();
    }

    private class connectThread extends Thread {
        public void run() {
            BluetoothAdapter.getDefaultAdapter().cancelDiscovery();
            try {
                mSocket.connect();
                connectedThread cT = new connectedThread();
                cT.start();
            } catch (IOException e) {
                Log.d(TAG, "Error in connectThread:");
                e.printStackTrace();
            }
        }
    }

    private class connectedThread extends Thread {
        public void run() {
            Log.d(TAG,"Connection successful");
            try {
                read_from_socket(mSocket);
                mSocket.close();
            } catch (IOException e) {
                Log.d(TAG, "Error in connectedThread:");
                e.printStackTrace();
            }
        }
    }
}
