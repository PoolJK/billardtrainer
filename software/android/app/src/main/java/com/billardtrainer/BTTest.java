package com.billardtrainer;

import java.util.Set;
import android.bluetooth.BluetoothAdapter;
import android.bluetooth.BluetoothDevice;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.support.v7.app.AppCompatActivity;

public class BTTest extends AppCompatActivity {

    private final static String TAG = "BTTest";
    private BluetoothAdapter mBluetoothAdapter;
    private BluetoothDevice mDevice;
    private EditText mMessageET;
    private Button mSendBN;
    private BTService btService;

    private void findRaspberry() {
        Set<BluetoothDevice> pairedDevices = mBluetoothAdapter
                .getBondedDevices();
        for (BluetoothDevice device : pairedDevices) {
            if(device.getName().equals("raspberrypi"))
                this.mDevice=device;
        }
    }

    private void initBluetooth() {
        Log.d(TAG, "Checking Bluetooth...");
        if (mBluetoothAdapter == null) {
            Log.d(TAG, "Device does not support Bluetooth");
            mSendBN.setClickable(false);
        } else{
            Log.d(TAG, "Bluetooth supported");
        }
        if (!mBluetoothAdapter.isEnabled()) {
            mSendBN.setClickable(false);
            Log.d(TAG, "Bluetooth not enabled");
        }
        else{
            Log.d(TAG, "Bluetooth enabled");
        }
    }


    public void onSend(View view) {
        String message = mMessageET.getText().toString();
        btService.send(message);
    }

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.bttest);
        mMessageET = findViewById(R.id.message_et);
        mSendBN = findViewById(R.id.send_bn);
        mBluetoothAdapter = BluetoothAdapter.getDefaultAdapter();

        initBluetooth();
        findRaspberry();
        if (mDevice == null)
            mSendBN.setClickable(false);
        btService = new BTService(new Main.mHandler());
        btService.start();
    }
}
