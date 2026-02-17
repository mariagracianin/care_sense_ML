# Elderly Activity Monitoring System — MVP

## Hardware Platform

**Arduino Nano 33 BLE Rev2**

## Overview

This project is a Minimum Viable Product (MVP) of an elderly monitoring system built on the Arduino Nano 33 BLE Rev2 board. It uses onboard IMU sensors and an embedded machine learning model to detect a person’s physical state in real time, classifying whether the user is walking, sitting, lying down, or has experienced a fall.

The system continuously analyzes motion data and recognizes activity patterns. Its goal is to support long-term monitoring by generating useful statistics about daily mobility and behavior. If a fall is detected, the system is intended to trigger an alert to a designated family member or caregiver, enabling rapid response and timely assistance.

## MVP Scope — Included Components

- Sensor data acquisition from the IMU
- Dataset generation and preprocessing
- Predictive model training
- Deployment of a TinyML model on-device
- Real-time inference and state classification on the microcontroller

## Future Extensions for a Production System

- Backend server for centralized processing, storage, and alert management
- Communication layer (BLE / WiFi / mobile gateway) to transmit events
- Frontend dashboard or mobile application to visualize critical data, activity statistics, and real-time alerts for caregivers or relatives
