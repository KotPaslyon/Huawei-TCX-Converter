<img align="left" width="80" height="80" src="./Development Tools/icon.png" alt="Huawei TCX Converter icon">

# Huawei TCX Converter
A makeshift python tool that generates TCX files from Huawei HiTrack files.

Users of Huawei Watches/Bands sync their fitness data with the Huawei Health App. It is [notoriously difficult](https://uk.community.huawei.com/software-17/huawei-health-integration-with-other-services-1198/index3.html) to get the data out of this app, but [through some cunning](https://forum.xda-developers.com/smartwatch/huawei-watch/huawei-watch-gt-export-data-health-t3874330) you can find `HiTrack` files which seem to contain some run data. This program allows you to take these files and generate `.TCX` files for use in your tracking app of choice (e.g. Strava). The outputted `.TCX` files will contain timestamped GPS, altitude, heart-rate, and cadence data where available.

## How to get the HiTrack Files

**This section needs to be updated. Please use the info in the release notes from version 3.0 build 1910.0301** 

- Open the Huawei Health app and open the exercise that you want to convert to view it's trajectory. This ensures that its HiTrack file is generated.

If you have a **rooted** phone you can simply navigate to: `data/data/com.huawei.health/files/` where you should find a number of files prefixed `HiTrack`.

If you have an **unrooted** phone then:
- Download the [Huawei Backup App](https://play.google.com/store/apps/details?id=com.huawei.KoBackup&hl=en_GB) onto your phone.
- Start a new **unencrypted** backup of the Huawei Health app data to your external storage (SD Card)
- Navigate to `Huawei/Backup/***/backupFiles/***/` and copy `com.huawei.health.tar` to your computer.
- Unzip the file and navigate to `com.huawei.health/files/` and you should should see a number of `HiTrack` files.

## How to use the Huawei TCX Converter
You need [`python 3`](https://www.python.org/downloads/) to use this tool.

Download the [Huawei TCX Converter](https://raw.githubusercontent.com/aricooperdavis/Huawei-TCX-Converter/master/Huawei-TCX-Converter.py) and save it as a Python script in the same folder as your HiTrack file.

### Command Line Arguments Overview
>usage: Huawei-TCX-Converter.py [-h] [-f FILE]
>                     [-s {Walk,Run,Cycle,Swim_Pool,Swim_Open_Water}] [-j JSON]
>                     [-t TAR] [--from_date FROM_DATE]
>                     [--pool_length POOL_LENGTH] [--output_dir OUTPUT_DIR]
>                     [--output_file_prefix OUTPUT_FILE_PREFIX]
>                     [--validate_xml] [--log_level {INFO,DEBUG}]
>

>optional arguments:
>>  -h, --help            show this help message and exit

>>  --log_level {INFO,DEBUG}
>>                        Set the logging level.

>FILE options:
>>  -f FILE, --file FILE  The filename of a single HiTrack file to convert.
>
>> -s {Walk,Run,Cycle,Swim_Pool,Swim_Open_Water}, --sport {Walk,Run,Cycle,Swim_Pool,Swim_Open_Water}
>>                        Force sport for the conversion. Sport will be auto-
>>                        detected when this option is not used.

>JSON options:
>>  -j JSON, --json JSON  The filename of a Huawei Cloud JSON file containing
>>                        the motion path detail data.

>TAR options:
>>  -t TAR, --tar TAR     The filename of an (unencrypted) tarball with HiTrack
>>                        files to convert.

>DATE options:
>>  --from_date FROM_DATE
>>                        Applicable to --json and --tar options only. Only
>>                        convert HiTrack information from the JSON file or from
>>                        HiTrack files in the tarball if the activity started
>>                        on FROM_DATE or later. Format YYYY-MM-DD

>SWIM options:
>>  --pool_length POOL_LENGTH
>>                        The pool length in meters to use for swimming
>>                        activities. If the option is not set, the estimated
>>                        pool length derived from the available speed data in
>>                        the HiTrack file will be used. Note that the available
>>                        speed data has a minimum resolution of 1 dm/s.

>OUTPUT options:
>>  --output_dir OUTPUT_DIR
>>                        The path to the directory to store the output files.
>>                        The default directory is ./output.

>>  --output_file_prefix OUTPUT_FILE_PREFIX
>>                        Adds the strftime representation of this argument as a
>>                        prefix to the generated TCX XML file(s). E.g. use
>>                        %Y-%m-%d- to add human readable year-month-day
>>                        information in the name of the generated TCX file.

>>  --validate_xml        Validate generated TCX XML file(s). NOTE: requires
>>                        xmlschema library and an internet connection to
>>                        retrieve the TCX XSD.
                     
### Usage Examples

#### JSON file conversion example
USe the command below to convert all activities available in the motion path JSON file from the requested Huawei Privacy data that were started
on October, 3rd, 2019 or later. Source HiTrack files and converted TCX files will be generated in folder /my_output_dir/json 

>python Huawei-TCX-Converter --json "motion path detail data.json" --from_date 2019-10-03 --output_dir /my_output_dir/json

#### Single file conversion examples
The example below converts extracted file HiTrack_12345678901212345678912 to HiTrack_12345678901212345678912.tcx in 
the ./output directory

>python Huawei-TCX-Converter --file HiTrack_12345678901212345678912

The next example converts extracted file HiTrack_12345678901212345678912 to HiTrack_12345678901212345678912.tcx in 
the /my_output_dir directory. The program logging level is set to display debug messages. The converted file is validated against the TCX XSD schema (requires installed xmlschema 
library and an intenet connection). 

>python Huawei-TCX-Converter --file HiTrack_12345678901212345678912 --output_dir /my_output_dir --validate_xml --log_level DEBUG

The following example converts an extracted file HiTrack_12345678901212345678912 to HiTrack_12345678901212345678912.tcx 
in the /my_output_dir directory and forces the sport to walking. 

>python Huawei-TCX-Converter --file HiTrack_12345678901212345678912 --sport Walk

The next example converts an indoor swimming activity in an extracted file HiTrack_12345678901212345678912 to 
HiTrack_12345678901212345678912.tcx. The length of the pool in meters is specified to have a more accurate swimming data
calculation.  

>python Huawei-TCX-Converter --file HiTrack_12345678901212345678912 --pool_length 25

#### Direct tar file conversion examples
The first example extracts and converts any HiTrack file found in tar file com.huawei.health.tar into the ./output 
directory. The output directory will contain both the extracted HiTrack file and the converted TCX XML file. 

>python Huawei-TCX-Converter --tar com.huawei.health.tar

In the example below, only activities in the com.huawei.health.tar tarball that were started on August 20th, 2019 or 
later will be extracted and converted to the ./output directory.

>python Huawei-TCX-Converter --tar com.huawei.health.tar --from_date 20190820
 

### Illustration
I have copied the `Huawei-TCX-Converter.py` file to the directory containing my HiTrack file (`HiTrack_1551732120000155173259000030001` ). Now I can run the tool as follows:

    python Huawei-TCX-Converter.py --file HiTrack_1551732120000155173259000030001

I've included both the HiTrack file and the resultant TCX file in the Examples folder for you to have a go with. You can also [visualise the data online](https://www.mygpsfiles.com/app/#3gcQ1H3M).

## Release Notes
### Version 3.0 Build 1910.0301
#### New features and changes
<li>It is now possible to (mass) convert activity data from the JSON file with the motion path detail data available in
the Privacy Data zip file that you can request in the Huawei Health app. Use the new --json command line option and
specify your extracted "motion path detail data.json" file.
To be able to request your data in the Huawei Health app, a prerequisite is to have an enabled Huawei account in the app.
To request your data, tap the "Me" button in the lower right-hand corner, then tap on your account name on top of 
the screen. Next, tap on 'Privacy Center' (one but last option just above 'Settings'). You can now request ALL your
Huawei Health app data in a zip file by tapping 'Request Your Data'. You will receive a mail with a link to download
the zip file. Once downloaded, open the zip file and go to the "data/Motion path detail data & description" folder.
Extract the file "motion path detail data.json" from the zip file. Use this file in the --json command line option.  
This will generate both the original HiTrack files and the converted TCX files. Closes #37.</li>

#### Known Limitations
<li>The JSON file from the Huawei Privacy export contains other interesting data and information which is currently not
used (yet).</li>

### Version 2.3 Build 1909.2401
#### Solved issues
<li>Program would error out when trying to convert without the --validate_xml option when the xmlschema library wasn't 
installed. Closes #36.</li>

#### Known Limitations
<li>Since the latest version of Huawei Backup (10.0.0.360_OVE) and more importantly Huawei Health (10.0.0.533), the
program is ( / might be, see #35) defunct in its current state. Last version of Huawei Helath app seems to disallow
backups through its properties. Huawei Backup release notes state that encryption of the backup is required.</li>

### Version 2.3 Build 1909.1501
#### New features and changes
<li>Added **--output_file_prefix** command line argument option. You can now add the strftime representation of this argument 
as a prefix to the generated TCX XML file(s). E.g. use %Y-%m-%d- to add human readable year-month-day information in 
the name of the generated TCX file.</li>
<li>Reworked auto-detection of activity types. This was needed for the detection and distinction between pool swimming 
and open water swimming [see also FEATURE #28]. Added internal auto-distinction between walking and running based on
research in https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5435734. For validation purposes, both types will still be
converted as 'Run' in the TCX file (for now) to comply with the Garmin TCX XSD. Closes #31. Closes #24.</li>
<li>The --sport command line argument now disables auto-detection of the type of sport of the activity and also enforces 
the selected type of sport for the conversion.</li>
<li>The values of --sport command line argument have been changed. 'Swim' has been replaced by 'Swim_Pool' or 
'Swim_Open_water'. Please adapt your script(s) or remove the command line argument and try the (improved) auto-detection.</li>
<li>
[FEATURE #28] Alpha support for open water swimming activities. Tested on a single activity file only. SWOLF and speed
data were found to be unreliable / unusable. The conversion relies on the GPS data for this type of activity. We welcome
your feedback if you have any problems or remarks using this feature. Closes #28. 
</li>

#### Solved issues
<li>Bug solved in swimming lap generation that could cause each lap to be generated twice (probably since V2.0 B1908.3101).</li>
<li>Bug solved that could cause the --sport command line argument to get overruled by auto-detection. Closes #30.</li>

#### Known Limitations
<li>Distance calculation during long(er) pause periods can be off due to continuing speed data records
during the pause in the HiTrack file. If you suspect a converted activity to have a wrong distance, you can 
try to recalculate the distance from the activity details screen in Strava for now.</li>

### Version 2.2 Build 1909.0801
#### New features and changes
<li>[FEATURE #21] Conversion of Walking, Running ad Cycling activities without any GPS data is supported. You can now convert 
activities that were recorded using a fitness band only (that has no GPS) without using your phone during the 
activity. Distance calculation is an estimated distance and may differ from the real distance because calculation is
based on (average) speed data during a period of seconds (typically 5 seconds) with a resolution of 1 dm/s. Closes #21.</li>

#### Solved issues

<li>[BUG #27] Solved conversion error due to improper segment handling in some cases of GPS loss and/or pause.</li>
<li>Solved potential conversion error due to improper distance calculation in case the HiTrack file would not contain 
an explicit stop record.</li>

#### Known Limitations
<li>
[FEATURE #28] Open water swimming activities were not and are not supported (yet).
</li>

### Version 2.1 Build 1909.0701
#### New features and changes
<li>More accurate distance calculation in case of GPS loss during an activity is now supported for walking, running and 
cycling activities. The real-time speed data in the Hitrack file is used to determine the distance during GPS loss.
See also #21.</li>

#### Known Limitations
<li>Walking, Running and Cycling activities without any GPS data at all can't be converted (yet) and the conversion will
fail with an error. This might be related to issue #18 (O m distance) reported in pre-version 2. Possible use-case: 
You use your fitness band (that has no GPS) without your phone during an activity. To be solved in a future update.</li>

### Version 2.0 Build 1908.3101
#### Solved issues

<li>[BUG #26] Solved issue causing only a part of the activity to be converted. It was detected in a case where the
activity track contained multiple loops over the same track (and/or on some devices, the records in the Hitrack
file are not in chronological order).</li>

### Version 2.0 Build 1908.2901
#### New features and changes
<li>Changed the auto-detected activity type from 'Walk' to 'Run' for walking or running activities. Please note that the
known limitation from the previous version still exists: no auto-distinction between walking and running activities,
they both are detected as running activities.</li>

#### Solved issues

<li>[BUG #25] Error parsing altitude data from tp=alti records in Hitrack file</li>

### Version 2.0 Build 1908.2201
#### New features and changes
<li><u>Support for swimming activities.</u> In this version duration and distances are supported. SWOLF data is available 
from the HiTrack files but is not exported (yet) since we don't have the information how to pass it in the TCX 
format or if Strava supports it natively.</li>
<li><u>Direct conversion from tarball.</u> It is now possible to convert activities directly from the tarball without the 
need to extract them.</li>
<li><u>Auto activity type detection.</u> Auto detection of running, cycling or swimming activities. There is no auto 
distinction (yet) between walking and running activities. For now, walking activities will be detected as running. The 
activity type can be changed in Strava directly after importing the file.</li>
<li><u>Extended program logging.</u> Ability to log only information messages or to have a more extensive debug logging.</li>
<li><u>Restructured and new command line options.</u> This includes new options for direct tarball processing (--tar and 
--from_date), file processing (--file), forcing the sport type (--sport), setting the pool length for swim
activities (--pool_length) and general options to set the directory for extracted and converted files 
(--output_dir), the logging detail (--log_level) and the optional validation of converted TCX XML files 
(--validate_xml)</li>
<li>The source code underwent a restructuring to facilitate the new features.</li>

#### Solved issues
<li>Step frequency corrected.<br>Strava displays steps/minute in app but reads the value in the imported file as 
strides/minute. As a consequence, imported step frequency information from previous versions was 2 times the real value.</li>

#### Known Limitations
<li>Auto distinction between walking and running activities is not included in this version.</li>
<li>For walking and swimming activities, in this version the correct sport type must be manually changed in Strava directly 
after importing the TCX file.</li>
<li>Distance calculation may be incorrect in this version when GPS signal is lost during a longer period or there is no
GPS signal at all.</li>
<li>Due to the very nature of the available speed data (minimum resolution is 1 dm/s) for swimming activities, swimming
distances are an estimation (unless the --pool_length option is used) and there might be a second difference in the
actual lap times versus the ones shown in the Huawei Health app.</li>
<li>There is no direct upload functionality to upload the converted activities to Strava in this version.</li>
<li>This program is dependent on the availability of the temporary/intermediate 'HiTrack' files in the Huawei Health app.</li>
<li>This program is dependent on the Huawei Backup to take an unencrypted backup of the Huawei Health app data.</li>
<li>This program was not tested on Python versions prior to version 3.7.3.</li>

## Comparison
This is an image of the GPS trace from the .tcx file. The command line output above also lists the start time as 2019-03-04 20:42:00, the distance as 1.70km, and the duration as 00:07:49.

![Map of example route](https://raw.githubusercontent.com/aricooperdavis/Huawei-TCX-Converter/master/Examples/Route.PNG)

For comparison, below is the data visable on the Huawei Health App. You can see that the distance is off by about 80m, and the duration off by 1 second, but the GPS trace is spot on.

![Huawei Health App example route](https://raw.githubusercontent.com/aricooperdavis/Huawei-TCX-Converter/master/Examples/Huawei_Health.png)

## Contributing
This is a very early alpha version of this tool, so please help me by making it better! There are some scripts in the Development Tools folder that I find useful for debugging. I'll accept any improvements, but if you're looking for inspiration you could start with this to-do list:
* ~~Remove reliance on using the original filename~~
* ~~Enable changing sport type from running (default) to biking~~
* ~~Read timestamped heart-rate, cadence, and altitude data where available~~
* ~~See if we really need to add the unused data elements (e.g. Calories) to the TCX (edit: we do as there is no minOccurs in the schema)~~
* Add a GUI to make life easier for users who aren't familiar with the command line
* Build for common platforms so that users don't need to install python independently (Android?)
* Work with API's (i.e. Strava/Garmin) for automating tcx upload
* Check that this works for files other than those generated using the Huawei Band 2 Pro:
  * Confirmed working on a [file from a Huawei Watch GT](https://forum.xda-developers.com/smartwatch/huawei-watch/huawei-watch-gt-export-data-health-t3874330#post79042345)
  * Confirmed working on a [file from a Huawei Band 3 Pro](https://github.com/aricooperdavis/Huawei-TCX-Converter/pull/5)
  * Confirmed working on a [file from a Honor Watch Magic](https://forum.xda-developers.com/showpost.php?p=79468704&postcount=35)
  * Confirmed working on a file from a Honor Band 4
* Improve the distance measurement method (currently using [Viscenty's Formulae](https://en.wikipedia.org/wiki/Vincenty%27s_formulae))
* Try and work out what `tp=b-p-m` is
* Add interpolated heart-rate/pace/average speed data to each location element
* ~~Work on splitting data into `Laps`/`Tracks` rather than shoving it all into one~~
* Try to call on an open API to get altitude data for location points that don't have it
* Inspect other files in `com.huawei.health` to see if we can get any more relevant data out of them
  * iOS users may have some success looking at the [SQLite databases included in backups](https://forum.xda-developers.com/showpost.php?p=79445408&postcount=34) from their devices.
