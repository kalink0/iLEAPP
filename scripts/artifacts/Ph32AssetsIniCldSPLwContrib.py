# Photos.sqlite
# Author:  Scott Koenig, assisted by past contributors
# Version: 2.0
#
#   Description:
#   Parses Assets in iCloud Shared Photo Library with contributor information from PhotoData-Photos.sqlite ZSHARE Table
#   and supports iOS 16-18. Parses basic asset data and iCloud SPL and contributor information.
#   If you are attempting to match SPL count with results please check hidden, trashed, and burst assets.
#   This parser is based on research and SQLite Queries written by Scott Koenig
#   This is very large query and script, I recommend opening the TSV generated report with Zimmerman's Tools
#   https://ericzimmerman.github.io/#!index.md TimelineExplorer to view, search and filter the results.
#   https://theforensicscooter.com/ and queries found at https://github.com/ScottKjr3347
#

import os
import scripts.artifacts.artGlobals
from packaging import version
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, kmlgen, is_platform_windows, media_to_html, open_sqlite_db_readonly


def get_ph32icldsplassetsphdapsql(files_found, report_folder, seeker, wrap_text, timezone_offset):
    for file_found in files_found:
        file_found = str(file_found)
        
        if file_found.endswith('.sqlite'):
            break
      
    if report_folder.endswith('-') or report_folder.endswith('\\'):
        report_folder = report_folder[:-1]
    iosversion = scripts.artifacts.artGlobals.versionf
    if version.parse(iosversion) <= version.parse("15.8.2"):
        logfunc("Unsupported version for iCloud Shared Photo Library assets from PhotoData-Photos.sqlite"
                " from iOS " + iosversion)
    if (version.parse(iosversion) >= version.parse("16")) & (version.parse(iosversion) < version.parse("18")):
        file_found = str(files_found[0])
        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()

        cursor.execute("""
        SELECT
        DateTime(zAsset.ZDATECREATED + 978307200, 'UNIXEPOCH') AS 'zAsset-Date Created',
        CASE zAsset.ZACTIVELIBRARYSCOPEPARTICIPATIONSTATE
            WHEN 0 THEN '0-Asset-Not-In-Active-SPL-0'
            WHEN 1 THEN '1-Asset-In-Active-SPL-1'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZACTIVELIBRARYSCOPEPARTICIPATIONSTATE || ''
        END AS 'zAsset-Active Library Scope Participation State',
        zAsset.Z_PK AS 'zAsset-zPK',
        zAsset.ZDIRECTORY AS 'zAsset-Directory-Path',
        zAsset.ZFILENAME AS 'zAsset-Filename',
        zAddAssetAttr.ZORIGINALFILENAME AS 'zAddAssetAttr- Original Filename',
        zCldMast.ZORIGINALFILENAME AS 'zCldMast- Original Filename',
        zAddAssetAttr.ZSYNDICATIONIDENTIFIER AS 'zAddAssetAttr- Syndication Identifier-SWY-Files',
        CASE zAsset.ZSYNDICATIONSTATE
            WHEN 0 THEN '0-PhDaPs-NA_or_SyndPs-Received-SWY_Synd_Asset-0'
            WHEN 1 THEN '1-SyndPs-Sent-SWY_Synd_Asset-1'
            WHEN 2 THEN '2-SyndPs-Manually-Saved_SWY_Synd_Asset-2'
            WHEN 3 THEN '3-SyndPs-STILLTESTING_Sent-SWY-3'
            WHEN 8 THEN '8-SyndPs-Linked_Asset_was_Visible_On-Device_User_Deleted_Link-8'
            WHEN 9 THEN '9-SyndPs-STILLTESTING_Sent_SWY-9'
            WHEN 10 THEN '10-SyndPs-Manually-Saved_SWY_Synd_Asset_User_Deleted_From_LPL-10'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZSYNDICATIONSTATE || ''
        END AS 'zAsset-Syndication State',
        CASE zAsset.ZBUNDLESCOPE
            WHEN 0 THEN '0-iCldPhtos-ON-AssetNotInSharedAlbum_or_iCldPhtos-OFF-AssetOnLocalDevice-0'
            WHEN 1 THEN '1-SharediCldLink_CldMastMomentAsset-1'
            WHEN 2 THEN '2-iCldPhtos-ON-AssetInCloudSharedAlbum-2'
            WHEN 3 THEN '3-iCldPhtos-ON-AssetIsInSWYConversation-3'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZBUNDLESCOPE || ''
        END AS 'zAsset-Bundle Scope',
        CASE zAddAssetAttr.ZIMPORTEDBY
            WHEN 0 THEN '0-Cloud-Other-0'
            WHEN 1 THEN '1-Native-Back-Camera-1'
            WHEN 2 THEN '2-Native-Front-Camera-2'
            WHEN 3 THEN '3-Third-Party-App-3'
            WHEN 4 THEN '4-StillTesting-4'
            WHEN 5 THEN '5-PhotoBooth_PL-Asset-5'
            WHEN 6 THEN '6-Third-Party-App-6'
            WHEN 7 THEN '7-iCloud_Share_Link-CMMAsset-7'
            WHEN 8 THEN '8-System-Package-App-8'
            WHEN 9 THEN '9-Native-App-9'
            WHEN 10 THEN '10-StillTesting-10'
            WHEN 11 THEN '11-StillTesting-11'
            WHEN 12 THEN '12-SWY_Syndication_PL-12'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZIMPORTEDBY || ''
        END AS 'zAddAssetAttr-Imported by',
        zExtAttr.ZCAMERAMAKE AS 'zExtAttr-Camera Make',
        zExtAttr.ZCAMERAMODEL AS 'zExtAttr-Camera Model',
        zAddAssetAttr.ZIMPORTEDBYBUNDLEIDENTIFIER AS 'zAddAssetAttr- Imported by Bundle Identifier',
        zAddAssetAttr.ZIMPORTEDBYDISPLAYNAME AS 'zAddAssetAttr- Imported By Display Name',
        CASE zAsset.ZVISIBILITYSTATE
            WHEN 0 THEN '0-Visible-PL-CameraRoll-0'
            WHEN 2 THEN '2-Not-Visible-PL-CameraRoll-2'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZVISIBILITYSTATE || ''
        END AS 'zAsset-Visibility State',
        CASE zAsset.ZSAVEDASSETTYPE
            WHEN 0 THEN '0-Saved-via-other-source-0'
            WHEN 1 THEN '1-StillTesting-1'
            WHEN 2 THEN '2-StillTesting-2'
            WHEN 3 THEN '3-PhDaPs-Asset_or_SyndPs-Asset_NoAuto-Display-3'
            WHEN 4 THEN '4-Photo-Cloud-Sharing-Data-Asset-4'
            WHEN 5 THEN '5-PhotoBooth_Photo-Library-Asset-5'
            WHEN 6 THEN '6-Cloud-Photo-Library-Asset-6'
            WHEN 7 THEN '7-StillTesting-7'
            WHEN 8 THEN '8-iCloudLink_CloudMasterMomentAsset-8'
            WHEN 12 THEN '12-SyndPs-SWY-Asset_Auto-Display_In_CameraRoll-12'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZSAVEDASSETTYPE || ''
        END AS 'zAsset-Saved Asset Type',
        CASE zAddAssetAttr.ZSHARETYPE
            WHEN 0 THEN '0-Not_Shared-or-Shared_via_Phy_Device_StillTesting-0'
            WHEN 1 THEN '1-Shared_via_iCldPhotos_Web-or-Other_Device_StillTesting-1'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZSHARETYPE || ''
        END AS 'zAddAssetAttr-Share Type',
        DateTime(zAsset.ZSORTTOKEN + 978307200, 'UNIXEPOCH') AS 'zAsset- SortToken -CameraRoll',
        DateTime(zAsset.ZADDEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Added Date',        
        DateTime(zCldMast.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'zCldMast-Creation Date',
        zAddAssetAttr.ZTIMEZONENAME AS 'zAddAssetAttr-Time Zone Name',
        zAddAssetAttr.ZEXIFTIMESTAMPSTRING AS 'zAddAssetAttr-EXIF-String',
        DateTime(zAsset.ZMODIFICATIONDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Modification Date',
        DateTime(zAsset.ZLASTSHAREDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Last Shared Date',
        CASE zAsset.ZHIDDEN
            WHEN 0 THEN '0-Asset Not Hidden-0'
            WHEN 1 THEN '1-Asset Hidden-1'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZHIDDEN || ''
        END AS 'zAsset-Hidden',
        CASE zAsset.ZAVALANCHEPICKTYPE
            WHEN 0 THEN '0-NA-Single_Asset_Burst_UUID-0_RT'
            WHEN 2 THEN '2-Burst_Asset_Not_Selected-2_RT'
            WHEN 4 THEN '4-Burst_Asset_PhotosApp_Picked_KeyImage-4_RT'
            WHEN 8 THEN '8-Burst_Asset_Selected_for_LPL-8_RT'
            WHEN 16 THEN '16-Top_Burst_Asset_inStack_KeyImage-16_RT'
            WHEN 32 THEN '32-StillTesting-32_RT'
            WHEN 52 THEN '52-Burst_Asset_Visible_LPL-52'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZAVALANCHEPICKTYPE || ''
        END AS 'zAsset-Avalanche_Pick_Type-BurstAsset',
        CASE zAddAssetAttr.ZCLOUDAVALANCHEPICKTYPE
            WHEN 0 THEN '0-NA-Single_Asset_Burst_UUID-0_RT'
            WHEN 2 THEN '2-Burst_Asset_Not_Selected-2_RT'
            WHEN 4 THEN '4-Burst_Asset_PhotosApp_Picked_KeyImage-4_RT'
            WHEN 8 THEN '8-Burst_Asset_Selected_for_LPL-8_RT'
            WHEN 16 THEN '16-Top_Burst_Asset_inStack_KeyImage-16_RT'
            WHEN 32 THEN '32-StillTesting-32_RT'
            WHEN 52 THEN '52-Burst_Asset_Visible_LPL-52'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZCLOUDAVALANCHEPICKTYPE || ''
        END AS 'zAddAssetAttr-Cloud_Avalanche_Pick_Type-BurstAsset',
        CASE zAsset.ZTRASHEDSTATE
            WHEN 0 THEN '0-Asset Not In Trash-Recently Deleted-0'
            WHEN 1 THEN '1-Asset In Trash-Recently Deleted-1'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZTRASHEDSTATE || ''
        END AS 'zAsset-Trashed State-LocalAssetRecentlyDeleted',
        DateTime(zAsset.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Trashed Date',
        zAsset.ZTRASHEDBYPARTICIPANT AS 'zAsset-Trashed by Participant= zShareParticipant_zPK',
        CASE zAddAssetAttr.ZSHARETYPE
            WHEN 0 THEN '0-Not_Shared-or-Shared_via_Phy_Device_StillTesting-0'
            WHEN 1 THEN '1-Shared_via_iCldPhotos_Web-or-Other_Device_StillTesting-1'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZSHARETYPE || ''
        END AS 'zAddAssetAttr-Share Type',
        zAddAssetAttr.Z_PK AS 'zAddAssetAttr-zPK',
        zAsset.ZUUID AS 'zAsset-UUID = store.cloudphotodb',
        zAddAssetAttr.ZMASTERFINGERPRINT AS 'zAddAssetAttr-Master Fingerprint',
        zAddAssetAttr.ZADJUSTEDFINGERPRINT AS 'zAddAssetAttr.Adjusted Fingerprint',
        CASE SPLzSharePartic.ZISCURRENTUSER
            WHEN 0 THEN '0-Participant-Not_This_User-0'
            WHEN 1 THEN '1-Participant-Is_This_User-1'
            ELSE 'Unknown-New-Value!: ' || SPLzSharePartic.ZISCURRENTUSER || ''
        END AS 'SPLzSharePartic-Is Current User',
        CASE SPLzSharePartic.ZROLE
            WHEN 1 THEN '1-Participant-is-Owner-Role-1'
            WHEN 2 THEN '2-Participant-is-Invitee-Role-2'
            ELSE 'Unknown-New-Value!: ' || SPLzSharePartic.ZROLE || ''
        END AS 'SPLzSharePartic-Role',
        zAssetContrib.ZPARTICIPANT AS 'zAsstContrib-Participant= zSharePartic-zPK',
        SPLzSharePartic.ZEMAILADDRESS AS 'SPLzSharePartic-Email Address',
        SPLzSharePartic.ZPHONENUMBER AS 'SPLzSharePartic-Phone Number',        
        SPLzShare.ZTITLE AS 'SPLzShare-Title-SPL',
        SPLzShare.ZSHAREURL AS 'SPLzShare-Share URL-SPL',
        SPLzShare.ZSCOPEIDENTIFIER AS 'SPLzShare-Scope ID-SPL',
        DateTime(SPLzShare.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'SPLzShare-Creation Date-SPL',
        DateTime(SPLzShare.ZEXPIRYDATE + 978307200, 'UNIXEPOCH') AS 'SPLzShare-Expiry Date-SPL',
        SPLzShare.ZCLOUDPHOTOCOUNT AS 'SPLzShare-Cloud Photo Count-SPL',
        SPLzShare.ZCOUNTOFASSETSADDEDBYCAMERASMARTSHARING AS 'SPLzShare-Assets AddedByCamera SmartSharing',
        SPLzShare.ZCLOUDVIDEOCOUNT AS 'SPLzShare-Cloud Video Count-SPL',
        CASE SPLzSharePartic.Z54_SHARE
            WHEN 55 THEN '55-SPL-Entity-55'
            WHEN 56 THEN '56-CMM-iCloud-Link-Entity-56'
            WHEN 63 THEN '63-SPL-Active-Participant-iOS18-63'
            WHEN 64 THEN '64-CMM-iCloud-Link-iOS18-64'
            ELSE 'Unknown-New-Value!: ' || SPLzSharePartic.Z54_SHARE || ''
        END AS 'SPLzSharePartic-z54SHARE',
        CASE SPLzShare.ZSTATUS
            WHEN 1 THEN '1-Active_Share-CMM_or_SPL-1'
            WHEN 3 THEN '3-SPL-Actively-Sharing-3'
            ELSE 'Unknown-New-Value!: ' || SPLzShare.ZSTATUS || ''
        END AS 'SPLzShare-Status',
        CASE SPLzShare.ZSCOPETYPE
            WHEN 2 THEN '2-iCloudLink-CMMoment-2'
            WHEN 4 THEN '4-iCld-Shared-Photo-Library-SPL-4'
            WHEN 5 THEN '5-SPL-Active-Participant-5'
            ELSE 'Unknown-New-Value!: ' || SPLzShare.ZSCOPETYPE || ''
        END AS 'SPLzShare-Scope Type'
        FROM ZASSET zAsset
          LEFT JOIN ZADDITIONALASSETATTRIBUTES zAddAssetAttr ON zAddAssetAttr.Z_PK = zAsset.ZADDITIONALATTRIBUTES
          LEFT JOIN ZEXTENDEDATTRIBUTES zExtAttr ON zExtAttr.Z_PK = zAsset.ZEXTENDEDATTRIBUTES
          LEFT JOIN ZCLOUDMASTER zCldMast ON zAsset.ZMASTER = zCldMast.Z_PK
          LEFT JOIN ZSHARE SPLzShare ON SPLzShare.Z_PK = zAsset.ZLIBRARYSCOPE
          LEFT JOIN ZASSETCONTRIBUTOR zAssetContrib ON zAssetContrib.Z3LIBRARYSCOPEASSETCONTRIBUTORS = zAsset.Z_PK
          LEFT JOIN ZSHAREPARTICIPANT SPLzSharePartic ON SPLzSharePartic.Z_PK = zAssetContrib.ZPARTICIPANT
        WHERE zAsset.ZACTIVELIBRARYSCOPEPARTICIPATIONSTATE = 1
        ORDER BY zAsset.ZDATECREATED     
        """)

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        data_list = []
        counter = 0
        if usageentries > 0:
            for row in all_rows:
                data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9],
                                  row[10], row[11], row[12], row[13], row[14], row[15], row[16], row[17], row[18],
                                  row[19], row[20], row[21], row[22], row[23], row[24], row[25], row[26], row[27],
                                  row[28], row[29], row[30], row[31], row[32], row[33], row[34], row[35], row[36],
                                  row[37], row[38], row[39], row[40], row[41], row[42], row[43], row[44], row[45],
                                  row[46], row[47], row[48], row[49], row[50], row[51]))

                counter += 1

            description = 'Parses Assets in iCloud Shared Photo Library with contributor information from' \
                          ' PhotoData-Photos.sqlite ZSHARE Table and supports iOS 16-17.' \
                          ' Parses basic asset data and iCloud SPL and contributor information.' \
                          ' If you are attempting to match SPL count with results please check' \
                          ' hidden, trashed, and burst assets.'
            report = ArtifactHtmlReport('Ph32-iCld Shared Photo Lib Assets-PhDaPsql')
            report.start_artifact_report(report_folder, 'Ph32-iCld Shared Photo Lib Assets-PhDaPsql', description)
            report.add_script()
            data_headers = ('zAsset-Date Created-0',
                            'zAsset-Active Library Scope Participation State-1',
                            'zAsset-zPK-2',
                            'zAsset-Directory-Path-3',
                            'zAsset-Filename-4',
                            'zAddAssetAttr- Original Filename-5',
                            'zCldMast- Original Filename-6',
                            'zAddAssetAttr- Syndication Identifier-SWY-Files-7',
                            'zAsset-Syndication State-8',
                            'zAsset-Bundle Scope-9',
                            'zAddAssetAttr-Imported by-10',
                            'zExtAttr-Camera Make-11',
                            'zExtAttr-Camera Model-12',
                            'zAddAssetAttr.Imported by Bundle Identifier-13',
                            'zAddAssetAttr-Imported By Display Name-14',
                            'zAsset-Visibility State-15',
                            'zAsset-Saved Asset Type-16',
                            'zAddAssetAttr-Share Type-17',
                            'zAsset- SortToken -CameraRoll-18',
                            'zAsset-Added Date-19',
                            'zCldMast-Creation Date-20',
                            'zAddAssetAttr-Time Zone Name-21',
                            'zAddAssetAttr-EXIF-String-22',
                            'zAsset-Modification Date-23',
                            'zAsset-Last Shared Date-24',
                            'zAsset-Hidden-25',
                            'zAsset-Avalanche_Pick_Type-BurstAsset-26',
                            'zAddAssetAttr-Cloud_Avalanche_Pick_Type-BurstAsset-27',
                            'zAsset-Trashed State-LocalAssetRecentlyDeleted-28',
                            'zAsset-Trashed Date-29',
                            'zAsset-Trashed by Participant= zShareParticipant_zPK-30',
                            'zAddAssetAttr-Share Type-31',
                            'zAddAssetAttr-zPK-32',
                            'zAsset-UUID = store.cloudphotodb-33',
                            'zAddAssetAttr-Master Fingerprint-34',
                            'zAddAssetAttr.Adjusted Fingerprint-35',
                            'SPLzSharePartic-Is Current User-36',
                            'SPLzSharePartic-Role-37',
                            'zAsstContrib-Participant= zSharePartic-zPK-38',
                            'SPLzSharePartic-Email Address-39',
                            'SPLzSharePartic-Phone Number-10',
                            'SPLzShare-Title-SPL-41',
                            'SPLzShare-Share URL-SPL-42',
                            'SPLzShare-Scope ID-SPL-43',
                            'SPLzShare-Creation Date-SPL-44',
                            'SPLzShare-Expiry Date-SPL-45',
                            'SPLzShare-Cloud Photo Count-SPL-46',
                            'SPLzShare-Assets AddedByCamera SmartSharing-47',
                            'SPLzShare-Cloud Video Count-SPL-48',
                            'SPLzSharePartic-z54SHARE-49',
                            'SPLzShare-Status-50',
                            'SPLzShare-Scope Type-51')
            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()

            tsvname = 'Ph32-iCld Shared Photo Lib Assets-PhDaPsql'
            tsv(report_folder, data_headers, data_list, tsvname)

            tlactivity = 'Ph32-iCld Shared Photo Lib Assets-PhDaPsql'
            timeline(report_folder, tlactivity, data_list, data_headers)

        else:
            logfunc('No assets in iCloud Shared Photo Library found in PhotoData-Photos.sqlite ZSHARE table')

        db.close()
        return

    elif version.parse(iosversion) >= version.parse("18"):
        file_found = str(files_found[0])
        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()

        cursor.execute("""
        SELECT
        DateTime(zAsset.ZDATECREATED + 978307200, 'UNIXEPOCH') AS 'zAsset-Date Created',
        CASE zAsset.ZACTIVELIBRARYSCOPEPARTICIPATIONSTATE
            WHEN 0 THEN '0-Asset-Not-In-Active-SPL-0'
            WHEN 1 THEN '1-Asset-In-Active-SPL-1'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZACTIVELIBRARYSCOPEPARTICIPATIONSTATE || ''
        END AS 'zAsset-Active Library Scope Participation State',
        zAsset.Z_PK AS 'zAsset-zPK',
        zAsset.ZDIRECTORY AS 'zAsset-Directory-Path',
        zAsset.ZFILENAME AS 'zAsset-Filename',
        zAddAssetAttr.ZORIGINALFILENAME AS 'zAddAssetAttr- Original Filename',
        zCldMast.ZORIGINALFILENAME AS 'zCldMast- Original Filename',
        zAddAssetAttr.ZSYNDICATIONIDENTIFIER AS 'zAddAssetAttr- Syndication Identifier-SWY-Files',
        CASE zAsset.ZSYNDICATIONSTATE
            WHEN 0 THEN '0-PhDaPs-NA_or_SyndPs-Received-SWY_Synd_Asset-0'
            WHEN 1 THEN '1-SyndPs-Sent-SWY_Synd_Asset-1'
            WHEN 2 THEN '2-SyndPs-Manually-Saved_SWY_Synd_Asset-2'
            WHEN 3 THEN '3-SyndPs-STILLTESTING_Sent-SWY-3'
            WHEN 8 THEN '8-SyndPs-Linked_Asset_was_Visible_On-Device_User_Deleted_Link-8'
            WHEN 9 THEN '9-SyndPs-STILLTESTING_Sent_SWY-9'
            WHEN 10 THEN '10-SyndPs-Manually-Saved_SWY_Synd_Asset_User_Deleted_From_LPL-10'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZSYNDICATIONSTATE || ''
        END AS 'zAsset-Syndication State',
        CASE zAsset.ZBUNDLESCOPE
            WHEN 0 THEN '0-iCldPhtos-ON-AssetNotInSharedAlbum_or_iCldPhtos-OFF-AssetOnLocalDevice-0'
            WHEN 1 THEN '1-SharediCldLink_CldMastMomentAsset-1'
            WHEN 2 THEN '2-iCldPhtos-ON-AssetInCloudSharedAlbum-2'
            WHEN 3 THEN '3-iCldPhtos-ON-AssetIsInSWYConversation-3'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZBUNDLESCOPE || ''
        END AS 'zAsset-Bundle Scope',
        CASE zAddAssetAttr.ZIMPORTEDBY
            WHEN 0 THEN '0-Cloud-Other-0'
            WHEN 1 THEN '1-Native-Back-Camera-1'
            WHEN 2 THEN '2-Native-Front-Camera-2'
            WHEN 3 THEN '3-Third-Party-App-3'
            WHEN 4 THEN '4-StillTesting-4'
            WHEN 5 THEN '5-PhotoBooth_PL-Asset-5'
            WHEN 6 THEN '6-Third-Party-App-6'
            WHEN 7 THEN '7-iCloud_Share_Link-CMMAsset-7'
            WHEN 8 THEN '8-System-Package-App-8'
            WHEN 9 THEN '9-Native-App-9'
            WHEN 10 THEN '10-StillTesting-10'
            WHEN 11 THEN '11-StillTesting-11'
            WHEN 12 THEN '12-SWY_Syndication_PL-12'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZIMPORTEDBY || ''
        END AS 'zAddAssetAttr-Imported by',
        zExtAttr.ZCAMERAMAKE AS 'zExtAttr-Camera Make',
        zExtAttr.ZCAMERAMODEL AS 'zExtAttr-Camera Model',
        zAddAssetAttr.ZIMPORTEDBYBUNDLEIDENTIFIER AS 'zAddAssetAttr- Imported by Bundle Identifier',
        zAddAssetAttr.ZIMPORTEDBYDISPLAYNAME AS 'zAddAssetAttr- Imported By Display Name',
        CASE zAsset.ZVISIBILITYSTATE
            WHEN 0 THEN '0-Visible-PL-CameraRoll-0'
            WHEN 2 THEN '2-Not-Visible-PL-CameraRoll-2'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZVISIBILITYSTATE || ''
        END AS 'zAsset-Visibility State',
        CASE zAsset.ZISRECENTLYSAVED
            WHEN 0 THEN '0-Not_Recently_Saved iOS18_Still_Testing-0'
            WHEN 1 THEN '1-Recently_Saved iOS18_Still_Testing-1'	
            ELSE 'Unknown-New-Value!: ' || zAsset.ZISRECENTLYSAVED || ''
        END AS 'zAsset-Is_Recently_Saved-iOS18',
        CASE zAsset.ZSAVEDASSETTYPE
            WHEN 0 THEN '0-Saved-via-other-source-0'
            WHEN 1 THEN '1-StillTesting-1'
            WHEN 2 THEN '2-StillTesting-2'
            WHEN 3 THEN '3-PhDaPs-Asset_or_SyndPs-Asset_NoAuto-Display-3'
            WHEN 4 THEN '4-Photo-Cloud-Sharing-Data-Asset-4'
            WHEN 5 THEN '5-PhotoBooth_Photo-Library-Asset-5'
            WHEN 6 THEN '6-Cloud-Photo-Library-Asset-6'
            WHEN 7 THEN '7-StillTesting-7'
            WHEN 8 THEN '8-iCloudLink_CloudMasterMomentAsset-8'
            WHEN 12 THEN '12-SyndPs-SWY-Asset_Auto-Display_In_CameraRoll-12'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZSAVEDASSETTYPE || ''
        END AS 'zAsset-Saved Asset Type',
        CASE zAddAssetAttr.ZSHARETYPE
            WHEN 0 THEN '0-Not_Shared-or-Shared_via_Phy_Device_StillTesting-0'
            WHEN 1 THEN '1-Shared_via_iCldPhotos_Web-or-Other_Device_StillTesting-1'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZSHARETYPE || ''
        END AS 'zAddAssetAttr-Share Type',
        DateTime(zAsset.ZSORTTOKEN + 978307200, 'UNIXEPOCH') AS 'zAsset- SortToken -CameraRoll',
        DateTime(zAsset.ZADDEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Added Date',        
        DateTime(zCldMast.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'zCldMast-Creation Date',
        zAddAssetAttr.ZTIMEZONENAME AS 'zAddAssetAttr-Time Zone Name',
        zAddAssetAttr.ZEXIFTIMESTAMPSTRING AS 'zAddAssetAttr-EXIF-String',
        DateTime(zAsset.ZMODIFICATIONDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Modification Date',
        DateTime(zAsset.ZLASTSHAREDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Last Shared Date',
        CASE zAsset.ZISDETECTEDSCREENSHOT
            WHEN 0 THEN '0-Not_Detected_Screenshot iOS18_Still_Testing-0'
            WHEN 1 THEN '1-Detected_Screenshot iOS18_Still_Testing-1'	
            ELSE 'Unknown-New-Value!: ' || zAsset.ZISDETECTEDSCREENSHOT || ''
        END AS 'zAsset-Is_Detected_Screenshot-iOS18',
        CASE zAsset.ZHIDDEN
            WHEN 0 THEN '0-Asset Not Hidden-0'
            WHEN 1 THEN '1-Asset Hidden-1'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZHIDDEN || ''
        END AS 'zAsset-Hidden',
        CASE zAsset.ZADJUSTMENTSSTATE
            WHEN 0 THEN '0-No-Adjustments-0'
            WHEN 2 THEN '2-Yes-Adjustments iOS18_needs_update_Decoding-2'
            WHEN 3 THEN '3-Yes-Adjustments iOS18_needs_update_Decoding-3'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZADJUSTMENTSSTATE || ''
        END AS 'zAsset-Adjustments_State-Camera-Effects-Filters-iOS18',
        CASE zAsset.ZAVALANCHEKIND
            WHEN 0 THEN '0-No_Avalanche iOS18_Still_Testing-0'
            WHEN 1 THEN '1-Is_Avalanche iOS18_Still_Testing-1'	
            ELSE 'Unknown-New-Value!: ' || zAsset.ZAVALANCHEKIND || ''
        END AS 'zAsset-Avalanche_Kind-iOS18',
        CASE zAsset.ZAVALANCHEPICKTYPE
            WHEN 0 THEN '0-NA-Single_Asset_Burst_UUID-0_RT'
            WHEN 2 THEN '2-Burst_Asset_Not_Selected-2_RT'
            WHEN 4 THEN '4-Burst_Asset_PhotosApp_Picked_KeyImage-4_RT'
            WHEN 8 THEN '8-Burst_Asset_Selected_for_LPL-8_RT'
            WHEN 16 THEN '16-Top_Burst_Asset_inStack_KeyImage-16_RT'
            WHEN 32 THEN '32-StillTesting-32_RT'
            WHEN 52 THEN '52-Burst_Asset_Visible_LPL-52'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZAVALANCHEPICKTYPE || ''
        END AS 'zAsset-Avalanche_Pick_Type-BurstAsset',
        CASE zAddAssetAttr.ZCLOUDAVALANCHEPICKTYPE
            WHEN 0 THEN '0-NA-Single_Asset_Burst_UUID-0_RT'
            WHEN 2 THEN '2-Burst_Asset_Not_Selected-2_RT'
            WHEN 4 THEN '4-Burst_Asset_PhotosApp_Picked_KeyImage-4_RT'
            WHEN 8 THEN '8-Burst_Asset_Selected_for_LPL-8_RT'
            WHEN 16 THEN '16-Top_Burst_Asset_inStack_KeyImage-16_RT'
            WHEN 32 THEN '32-StillTesting-32_RT'
            WHEN 52 THEN '52-Burst_Asset_Visible_LPL-52'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZCLOUDAVALANCHEPICKTYPE || ''
        END AS 'zAddAssetAttr-Cloud_Avalanche_Pick_Type-BurstAsset',
        CASE zAsset.ZTRASHEDSTATE
            WHEN 0 THEN '0-Asset Not In Trash-Recently Deleted-0'
            WHEN 1 THEN '1-Asset In Trash-Recently Deleted-1'
            ELSE 'Unknown-New-Value!: ' || zAsset.ZTRASHEDSTATE || ''
        END AS 'zAsset-Trashed State-LocalAssetRecentlyDeleted',
        DateTime(zAsset.ZTRASHEDDATE + 978307200, 'UNIXEPOCH') AS 'zAsset-Trashed Date',
        zAsset.ZTRASHEDBYPARTICIPANT AS 'zAsset-Trashed by Participant= zShareParticipant_zPK',
        CASE zAddAssetAttr.ZSHARETYPE
            WHEN 0 THEN '0-Not_Shared-or-Shared_via_Phy_Device_StillTesting-0'
            WHEN 1 THEN '1-Shared_via_iCldPhotos_Web-or-Other_Device_StillTesting-1'
            ELSE 'Unknown-New-Value!: ' || zAddAssetAttr.ZSHARETYPE || ''
        END AS 'zAddAssetAttr-Share Type',
        zAddAssetAttr.Z_PK AS 'zAddAssetAttr-zPK',
        zAsset.ZUUID AS 'zAsset-UUID = store.cloudphotodb',
        zAddAssetAttr.ZORIGINALSTABLEHASH AS 'zAddAssetAttr-Original Stable Hash-iOS18',
        zAddAssetAttr.ZADJUSTEDSTABLEHASH AS 'zAddAssetAttr.Adjusted Stable Hash-iOS18',
        CASE SPLzSharePartic.ZISCURRENTUSER
            WHEN 0 THEN '0-Participant-Not_This_User-0'
            WHEN 1 THEN '1-Participant-Is_This_User-1'
            ELSE 'Unknown-New-Value!: ' || SPLzSharePartic.ZISCURRENTUSER || ''
        END AS 'SPLzSharePartic-Is Current User',
        CASE SPLzSharePartic.ZROLE
            WHEN 1 THEN '1-Participant-is-Owner-Role-1'
            WHEN 2 THEN '2-Participant-is-Invitee-Role-2'
            ELSE 'Unknown-New-Value!: ' || SPLzSharePartic.ZROLE || ''
        END AS 'SPLzSharePartic-Role',
        zAssetContrib.ZPARTICIPANT AS 'zAsstContrib-Participant= zSharePartic-zPK',
        SPLzSharePartic.ZEMAILADDRESS AS 'SPLzSharePartic-Email Address',
        SPLzSharePartic.ZPHONENUMBER AS 'SPLzSharePartic-Phone Number',        
        SPLzShare.ZTITLE AS 'SPLzShare-Title-SPL',
        SPLzShare.ZSHAREURL AS 'SPLzShare-Share URL-SPL',
        SPLzShare.ZSCOPEIDENTIFIER AS 'SPLzShare-Scope ID-SPL',
        DateTime(SPLzShare.ZCREATIONDATE + 978307200, 'UNIXEPOCH') AS 'SPLzShare-Creation Date-SPL',
        DateTime(SPLzShare.ZEXPIRYDATE + 978307200, 'UNIXEPOCH') AS 'SPLzShare-Expiry Date-SPL',
        SPLzShare.ZCLOUDPHOTOCOUNT AS 'SPLzShare-Cloud Photo Count-SPL',
        SPLzShare.ZCOUNTOFASSETSADDEDBYCAMERASMARTSHARING AS 'SPLzShare-Assets AddedByCamera SmartSharing',
        SPLzShare.ZCLOUDVIDEOCOUNT AS 'SPLzShare-Cloud Video Count-SPL',        
        CASE zExtAttr.ZGENERATIVEAITYPE 
            WHEN 0 THEN '0-Not_Generative_AI iOS18_Still_Testing-0'
            ELSE 'Unknown-New-Value!: ' || zExtAttr.ZGENERATIVEAITYPE || ''
        END AS 'zExtAttr-Generative_AI_Type-iOS18',
        zExtAttr.ZCREDIT AS 'zExtAttr-Credit-iOS18'
        FROM ZASSET zAsset
          LEFT JOIN ZADDITIONALASSETATTRIBUTES zAddAssetAttr ON zAddAssetAttr.Z_PK = zAsset.ZADDITIONALATTRIBUTES
          LEFT JOIN ZEXTENDEDATTRIBUTES zExtAttr ON zExtAttr.Z_PK = zAsset.ZEXTENDEDATTRIBUTES
          LEFT JOIN ZCLOUDMASTER zCldMast ON zAsset.ZMASTER = zCldMast.Z_PK
          LEFT JOIN ZSHARE SPLzShare ON SPLzShare.Z_PK = zAsset.ZLIBRARYSCOPE
          LEFT JOIN ZASSETCONTRIBUTOR zAssetContrib ON zAssetContrib.Z3LIBRARYSCOPEASSETCONTRIBUTORS = zAsset.Z_PK
          LEFT JOIN ZSHAREPARTICIPANT SPLzSharePartic ON SPLzSharePartic.Z_PK = zAssetContrib.ZPARTICIPANT
        WHERE zAsset.ZACTIVELIBRARYSCOPEPARTICIPATIONSTATE = 1
        ORDER BY zAsset.ZDATECREATED     
        """)

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        data_list = []
        counter = 0
        if usageentries > 0:
            for row in all_rows:
                data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9],
                                  row[10], row[11], row[12], row[13], row[14], row[15], row[16], row[17], row[18],
                                  row[19], row[20], row[21], row[22], row[23], row[24], row[25], row[26], row[27],
                                  row[28], row[29], row[30], row[31], row[32], row[33], row[34], row[35], row[36],
                                  row[37], row[38], row[39], row[40], row[41], row[42], row[43], row[44], row[45],
                                  row[46], row[47], row[48], row[49], row[50], row[51], row[52], row[53], row[54]))

                counter += 1

            description = 'Parses Assets in iCloud Shared Photo Library with contributor information from' \
                          ' PhotoData-Photos.sqlite ZSHARE Table and supports iOS 18.' \
                          ' Parses basic asset data and iCloud SPL and contributor information.' \
                          ' If you are attempting to match SPL count with results please check' \
                          ' hidden, trashed, and burst assets.'
            report = ArtifactHtmlReport('Ph32-iCld Shared Photo Lib Assets-PhDaPsql')
            report.start_artifact_report(report_folder, 'Ph32-iCld Shared Photo Lib Assets-PhDaPsql', description)
            report.add_script()
            data_headers = ('zAsset-Date Created-0',
                            'zAsset-Active Library Scope Participation State-1',
                            'zAsset-zPK-2',
                            'zAsset-Directory-Path-3',
                            'zAsset-Filename-4',
                            'zAddAssetAttr- Original Filename-5',
                            'zCldMast- Original Filename-6',
                            'zAddAssetAttr- Syndication Identifier-SWY-Files-7',
                            'zAsset-Syndication State-8',
                            'zAsset-Bundle Scope-9',
                            'zAddAssetAttr-Imported by-10',
                            'zExtAttr-Camera Make-11',
                            'zExtAttr-Camera Model-12',
                            'zAddAssetAttr- Imported by Bundle Identifier-13',
                            'zAddAssetAttr- Imported By Display Name-14',
                            'zAsset-Visibility State-15',
                            'zAsset-Is_Recently_Saved-iOS18-16',
                            'zAsset-Saved Asset Type-17',
                            'zAddAssetAttr-Share Type-18',
                            'zAsset- SortToken -CameraRoll-19',
                            'zAsset-Added Date-20',
                            'zCldMast-Creation Date-21',
                            'zAddAssetAttr-Time Zone Name-22',
                            'zAddAssetAttr-EXIF-String-23',
                            'zAsset-Modification Date-24',
                            'zAsset-Last Shared Date-25',
                            'zAsset-Is_Detected_Screenshot-iOS18-26',
                            'zAsset-Hidden-27',
                            'zAsset-Adjustments_State-Camera-Effects-Filters-iOS18-28',
                            'zAsset-Avalanche_Kind-iOS18-29',
                            'zAsset-Avalanche_Pick_Type-BurstAsset-30',
                            'zAddAssetAttr-Cloud_Avalanche_Pick_Type-BurstAsset-31',
                            'zAsset-Trashed State-LocalAssetRecentlyDeleted-32',
                            'zAsset-Trashed Date-33',
                            'zAsset-Trashed by Participant= zShareParticipant_zPK-34',
                            'zAddAssetAttr-Share Type-35',
                            'zAddAssetAttr-zPK-36',
                            'zAsset-UUID = store.cloudphotodb-37',
                            'zAddAssetAttr-Original Stable Hash-iOS18-38',
                            'zAddAssetAttr.Adjusted Stable Hash-iOS18-39',
                            'SPLzSharePartic-Is Current User-40',
                            'SPLzSharePartic-Role-41',
                            'zAsstContrib-Participant= zSharePartic-zPK-42',
                            'SPLzSharePartic-Email Address-43',
                            'SPLzSharePartic-Phone Number-44',
                            'SPLzShare-Title-SPL-45',
                            'SPLzShare-Share URL-SPL-46',
                            'SPLzShare-Scope ID-SPL-47',
                            'SPLzShare-Creation Date-SPL-48',
                            'SPLzShare-Expiry Date-SPL-49',
                            'SPLzShare-Cloud Photo Count-SPL-50',
                            'SPLzShare-Assets AddedByCamera SmartSharing-51',
                            'SPLzShare-Cloud Video Count-SPL-52',
                            'zExtAttr-Generative_AI_Type-iOS18-53',
                            'zExtAttr-Credit-iOS18-54')
            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()

            tsvname = 'Ph32-iCld Shared Photo Lib Assets-PhDaPsql'
            tsv(report_folder, data_headers, data_list, tsvname)

            tlactivity = 'Ph32-iCld Shared Photo Lib Assets-PhDaPsql'
            timeline(report_folder, tlactivity, data_list, data_headers)

        else:
            logfunc('No assets in iCloud Shared Photo Library found in PhotoData-Photos.sqlite ZSHARE table')

        db.close()
        return


__artifacts_v2__ = {
    'Ph32-iCloud SPL Assets with Contributor-PhDaPsql': {
        'name': 'PhDaPL Photos.sqlite Ph32 iCld Shared Photo Library Assets with Contributor',
        'description': 'Parses Assets in iCloud Shared Photo Library with contributor information from'
                       ' PhotoData-Photos.sqlite ZSHARE Table and supports iOS 16-18.'
                       ' Parses basic asset data and iCloud SPL and contributor information.'
                       ' If you are attempting to match SPL count with results please check'
                       ' hidden, trashed, and burst assets.',
        'author': 'Scott Koenig https://theforensicscooter.com/',
        'version': '2.0',
        'date': '2024-06-13',
        'requirements': 'Acquisition that contains PhotoData-Photos.sqlite',
        'category': 'Photos.sqlite-F-Cloud_Shared_Methods',
        'notes': '',
        'paths': '*/PhotoData/Photos.sqlite*',
        'function': 'get_ph32icldsplassetsphdapsql'
    }
}
