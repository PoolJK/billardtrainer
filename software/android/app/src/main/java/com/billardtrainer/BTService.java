package com.billardtrainer;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.io.PrintStream;
import java.util.LinkedList;
import java.util.Queue;
import java.util.Set;
import java.util.UUID;

import android.bluetooth.BluetoothAdapter;
import android.bluetooth.BluetoothDevice;
import android.bluetooth.BluetoothSocket;
import android.util.Log;

class BTService extends Thread {
    // Debug
    private final static String TAG = "BTService";

    // Constants
    private final static String MY_UUID = "00001101-0000-1000-8000-00805f9b34fb";
    private final static int NULL = 0;
    private final static int DISCONNECTED = 1;
    private final static int CONNECTING = 2;
    private final static int CONNECTED = 3;

    // Connection stuff
    private Queue<String> send_queue;
    private BluetoothSocket mSocket = null;
    private BluetoothAdapter mBluetoothAdapter;
    private BluetoothDevice mDevice;
    private int state = NULL;
    private long last_connect_time;
    private connectThread conT;
    private connectedThread connT;

    private Main.mHandler mainHandler;


    BTService(Main.mHandler mainHandler) {
        last_connect_time = System.currentTimeMillis();
        send_queue = new LinkedList<>();
        this.mainHandler = mainHandler;
        mBluetoothAdapter = BluetoothAdapter.getDefaultAdapter();
    }

    synchronized void send(String data) {
        try {
            OutputStream os = mSocket.getOutputStream();
            PrintStream sender = new PrintStream(os);
            sender.print(data);
        } catch (IOException e) {
            e.printStackTrace();
        } catch (NullPointerException e) {
            e.printStackTrace();
            Log.e(TAG, "send called with null Socket");
        }
        Log.v(TAG, String.format("Message sent: %s", data));
        // TODO: use message_queue
        // send_queue.add(data);
        // runQueue();
    }

    public void run() {
        connect();
    }

    void connect() {
        if (state > DISCONNECTED) {
            Log.d(TAG, String.format("connect() called while state = %d", state));
            return;
        }
        try {
            Thread.sleep(Math.max(last_connect_time + 5000 - System.currentTimeMillis(), 0));
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
        last_connect_time = System.currentTimeMillis();
        state = CONNECTING;
        Log.d(TAG, "Checking Bluetooth...");
        if (!mBluetoothAdapter.isEnabled()) {
            Log.d(TAG, "Bluetooth not enabled");
            mBluetoothAdapter.enable();
        } else {
            Log.d(TAG, "Bluetooth enabled");
        }
        Log.d(TAG, "Setting up connection...");
        Set<BluetoothDevice> pairedDevices = mBluetoothAdapter
                .getBondedDevices();
        for (BluetoothDevice device : pairedDevices) {
            if (device.getName().equals("raspberrypi")) {
                mDevice = device;
                break;
            }
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
        conT = new connectThread();
        conT.start();
    }

    private void runQueue() {
        while (!send_queue.isEmpty()) {
            if (state != CONNECTED) {
                Log.d(TAG, "waiting for connection");
                mainHandler.postDelayed(new Runnable() {
                    @Override
                    public void run() {
                        runQueue();
                    }
                }, 5000);
                return;
            }
            String data = send_queue.poll();
            try {
                OutputStream os = mSocket.getOutputStream();
                PrintStream sender = new PrintStream(os);
                sender.print(data);
            } catch (IOException e) {
                e.printStackTrace();
            } catch (NullPointerException e) {
                e.printStackTrace();
                Log.e(TAG, "send called with null Socket");
            }
            Log.d(TAG, "Message sent");
        }
    }

    private class connectThread extends Thread {
        public void run() {
            mBluetoothAdapter.cancelDiscovery();
            try {
                mSocket.connect();
                connT = new connectedThread();
                connT.start();
            } catch (IOException e) {
                Log.e(TAG, "Error in connectThread:");
                e.printStackTrace();
                disconnect();
            } catch (NullPointerException e) {
                e.printStackTrace();
                disconnect();
            }
            Log.d(TAG, "conT exiting");
        }
    }


    private class connectedThread extends Thread {

        private synchronized void read_from_socket(BluetoothSocket socket) throws IOException {
            InputStream is = socket.getInputStream();
            BufferedReader reader = new BufferedReader(new InputStreamReader(is));
            String data;
            state = CONNECTED;
            while (!this.isInterrupted()) {
                try {
                    data = reader.readLine();
                    Log.v(TAG, String.format("Received: \"%s\"", data));
                    mainHandler.obtainMessage(Main.BT_RECEIVE, data).sendToTarget();
                } catch (IOException e) {
                    e.printStackTrace();
                    break;
                }
            }
        }

        public void run() {
            Log.d(TAG, "Connection successful");
            mainHandler.obtainMessage(Main.BT_CONNECTED).sendToTarget();
            try {
                read_from_socket(mSocket);
                mSocket.close();
            } catch (IOException e) {
                Log.e(TAG, "Error in connectedThread:");
                e.printStackTrace();
            }
            disconnect();
        }
    }

    private void disconnect() {
        Log.d(TAG, "disconnecting");
        if (conT.isAlive())
            conT.interrupt();
        if (connT != null && connT.isAlive())
            connT.interrupt();
        if (state > DISCONNECTED) {
            state = DISCONNECTED;
            mainHandler.obtainMessage(Main.BT_DISCONNECTED).sendToTarget();
        }
    }
}
