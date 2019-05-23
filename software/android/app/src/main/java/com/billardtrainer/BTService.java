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
import android.util.Log;

class BTService extends Thread {
    // Debug
    private final static String TAG = "BTService";

    // Constants
    private final static String MY_UUID = "00001101-0000-1000-8000-00805f9b34fb";
    private final static int EXITING = -1;
    private final static int NULL = 0;
    private final static int DISCONNECTED = 1;
    private final static int CONNECTING = 2;
    private final static int CONNECTED = 3;

    // Connection stuff
    private int BTState = NULL;
    private BluetoothSocket mSocket = null;
    private BluetoothAdapter mBluetoothAdapter;
    private BluetoothDevice mDevice;

    private long last_connect_time;
    private connectThread conT;
    private connectedThread connT;

    private Main.mHandler mainHandler;

    boolean isConnected() {
        return BTState == CONNECTED;
    }

    BTService(Main.mHandler mainHandler) {
        last_connect_time = System.currentTimeMillis() - 5000;
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
        if (BTState > DISCONNECTED) {
            Log.d(TAG, String.format("connect() called while BTState = %d", BTState));
            return;
        }
        Log.v(TAG, "connecting");
        try {
            Thread.sleep(Math.max(last_connect_time + 5000 - System.currentTimeMillis(), 0));
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
        last_connect_time = System.currentTimeMillis();
        BTState = CONNECTING;
        if (!mBluetoothAdapter.isEnabled()) {
            mBluetoothAdapter.enable();
        }
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
            BTState = DISCONNECTED;
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

    private class connectThread extends Thread {
        public void run() {
            mBluetoothAdapter.cancelDiscovery();
            try {
                mSocket.connect();
                connT = new connectedThread();
                connT.start();
            } catch (IOException e) {
                Log.d(TAG, "Connection failed");
                if (!this.isInterrupted())
                    disconnect();
            } catch (NullPointerException e) {
                e.printStackTrace();
            }
        }
    }


    private class connectedThread extends Thread {

        private synchronized void read_from_socket(BluetoothSocket socket) throws IOException {
            InputStream is = socket.getInputStream();
            BufferedReader reader = new BufferedReader(new InputStreamReader(is));
            String data;
            while (!this.isInterrupted()) {
                data = reader.readLine();
                Log.v(TAG, String.format("Received: \"%s\"", data));
                mainHandler.obtainMessage(Main.BT_RECEIVE, data).sendToTarget();
            }
        }

        public void run() {
            Log.d(TAG, "Connection successful");
            BTState = CONNECTED;
            mainHandler.obtainMessage(Main.BT_CONNECTED).sendToTarget();
            try {
                read_from_socket(mSocket);
                mSocket.close();
            } catch (IOException e) {
                Log.d(TAG, "Connection lost");
            } catch (NullPointerException e) {
                Log.v(TAG, "Socket null");
            }
            if (BTState != EXITING)
                disconnect();
        }
    }

    private void disconnect() {
        Log.v(TAG, "disconnecting");
        if (conT != null && conT.isAlive())
            conT.interrupt();
        if (connT != null && connT.isAlive())
            connT.interrupt();
        if (BTState > DISCONNECTED) {
            BTState = DISCONNECTED;
            mainHandler.obtainMessage(Main.BT_DISCONNECTED).sendToTarget();
            mainHandler.sendEmptyMessage(Main.DEVICE_READY);
        }
    }

    void stopAll() {
        BTState = EXITING;
        disconnect();
        try {
            mSocket.close();
            mSocket = null;
            if (conT != null) {
                if (conT.isAlive()) {
                    conT.interrupt();
                    conT.join();
                }
                conT = null;
            }
            if (connT != null) {
                if (connT.isAlive()) {
                    connT.interrupt();
                    connT.join();
                }
                connT = null;
            }
        } catch (InterruptedException e) {
            Log.d(TAG, "Thread already interrupted");
        } catch (IOException e) {
            Log.d(TAG, "IOException closing socket");
        } catch (NullPointerException e) {
            Log.e(TAG, "socket was null you asshole!");
        }
        Log.v(TAG, "stopped all, bye");
    }
}
