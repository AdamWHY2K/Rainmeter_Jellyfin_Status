# Rainmeter_Jellyfin_Status
Author: AdamWHY2K

## Description

https://user-images.githubusercontent.com/68286215/218041739-2b3a643b-c759-4f06-b267-5eef9b548472.mp4

A rainmeter skin that displays the sessions your Jellyfin media server is currently operating.

Currently capable of displaying:

* [User#Name] 		- Returns user's name
* [User#Playing]		- Returns name of the file user is playing, or "Online" if they're not playing anything
* [User#Client]		- Returns the client that user is viewing from
* [User#Transcoding]	- Returns (T) if user is transcoding, or (D) if direct playing
* [User#MinutesLeft]	- Returns # min, ## sec
* [User#AltMinutesLeft]	- Returns #:##
* [User#PercentageDone]	- Returns 100.00 - 0.00
* [User#PlayStatus]	- Returns [>] if playing, [II] if paused, or [X] if not playing anything
* [User#DeviceName]	- Returns name of device user is playing from
* [NumberOfSessions]	- Returns the total number of sessions

# Requirements
* Rainmeter v4.5.17.3700 or later
* Jellyfin server

# Installation
* Download a [release](https://github.com/AdamWHY2K/Rainmeter_Jellyfin_Status/releases).
* Run the .rmskin.
* Edit skin
* Replace IP with your Jellyfin server's IP
* Replace API with your API key generated from Jellyfin Admin Account > Dashboard > Advanced > API Keys

# Disclaimer
If you have any issues please first check `JF_Status.log`, then open an [issue](https://github.com/AdamWHY2K/Rainmeter_Jellyfin_Status/issues/new).
