package com.billardtrainer;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.io.PrintStream;
import java.util.Set;
import java.util.UUID;

import android.bluetooth.BluetoothAdapter;
import android.bluetooth.BluetoothDevice;
import android.bluetooth.BluetoothSocket;
import android.os.Message;
import android.util.Log;

class BTService extends Thread {
    private Main.mHandler mainHandler;
    private final static String TAG="BTService";
    private final static String MY_UUID ="00001101-0000-1000-8000-00805f9b34fb";
    private BluetoothSocket mSocket=null;
    private String mMessage;
    private BluetoothAdapter mBluetoothAdapter;
    private BluetoothDevice mDevice;


    BTService(Main.mHandler mainHandler) {
        this.mainHandler = mainHandler;
        mBluetoothAdapter = BluetoothAdapter.getDefaultAdapter();
    }

    private synchronized void read_from_socket(BluetoothSocket socket) throws IOException {
        InputStream is = socket.getInputStream();
        BufferedReader reader = new BufferedReader(new InputStreamReader(is));
        String data;
        while (true) {
            data = reader.readLine();
            Log.d(TAG,"Received: " + data);
            Message msg = mainHandler.obtainMessage();
            msg.obj = data;
            msg.what = Main.TOAST_MESSAGE;
            mainHandler.sendMessage(msg);
        }
    }

    void send(String message){
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
        Log.d(TAG, "Checking Bluetooth...");
        if (!mBluetoothAdapter.isEnabled()) {
            Log.d(TAG, "Bluetooth not enabled");
            mBluetoothAdapter.enable();
        }
        else{
            Log.d(TAG, "Bluetooth enabled");
        }
        Log.d(TAG,"Setting up connection...");
        Set<BluetoothDevice> pairedDevices = mBluetoothAdapter
                .getBondedDevices();
        for (BluetoothDevice device : pairedDevices) {
            if(device.getName().equals("raspberrypi"))
                mDevice=device;
        }
        if (mDevice == null) {
            Log.d("BTService", "mDevice is null");
            return;
        }
        try {
            UUID uuid = UUID.fromString(MY_UUID);
            mSocket = mDevice.createRfcommSocketToServiceRecord(uuid);
        } catch (IOException e) {
            e.printStackTrace();
        }
        connectThread cT = new connectThread();
        cT.start();
    }

    private class connectThread extends Thread {
        public void run() {
            mBluetoothAdapter.cancelDiscovery();
            try {
                mSocket.connect();
                connectedThread cT = new connectedThread();
                cT.start();
            } catch (IOException e) {
                Log.d(TAG, "Error in connectThread:");
                e.printStackTrace();
            } catch (NullPointerException e) {
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
