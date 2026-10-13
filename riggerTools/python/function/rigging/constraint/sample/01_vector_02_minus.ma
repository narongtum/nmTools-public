//Maya ASCII 2018 scene
//Name: 01_vector_02_minus.ma
//Last modified: Tue, Mar 22, 2022 11:32:38 AM
//Codeset: 1252
file -rdi 1 -ns "learning_vector_object" -rfn "learning_vector_objectRN" -op
		 "v=0;" -typ "mayaAscii" "C:/Users/Noman/Documents/maya/projects/default//assets/learning_vector_object.ma";
file -r -ns "learning_vector_object" -dr 1 -rfn "learning_vector_objectRN" -op "v=0;"
		 -typ "mayaAscii" "C:/Users/Noman/Documents/maya/projects/default//assets/learning_vector_object.ma";
requires maya "2018";
requires "stereoCamera" "10.0";
currentUnit -l centimeter -a degree -t ntsc;
fileInfo "application" "maya";
fileInfo "product" "Maya 2018";
fileInfo "version" "2018";
fileInfo "cutIdentifier" "201706261615-f9658c4cfc";
fileInfo "osv" "Microsoft Windows 8 Business Edition, 64-bit  (Build 9200)\n";
createNode transform -s -n "persp";
	rename -uid "2F9C86DA-4019-58CB-A400-5AB727126B75";
	setAttr ".v" no;
	setAttr ".t" -type "double3" 28 21 28 ;
	setAttr ".r" -type "double3" -27.938352729602379 44.999999999999972 -5.172681101354183e-14 ;
createNode camera -s -n "perspShape" -p "persp";
	rename -uid "472E6A0A-4015-ABD9-CBBD-48905917C32E";
	setAttr -k off ".v" no;
	setAttr ".fl" 34.999999999999993;
	setAttr ".coi" 44.82186966202994;
	setAttr ".imn" -type "string" "persp";
	setAttr ".den" -type "string" "persp_depth";
	setAttr ".man" -type "string" "persp_mask";
	setAttr ".hc" -type "string" "viewSet -p %camera";
createNode transform -s -n "top";
	rename -uid "0B4DC99C-4027-CA66-F849-A89D17242530";
	setAttr ".v" no;
	setAttr ".t" -type "double3" 0 1000.1 0 ;
	setAttr ".r" -type "double3" -89.999999999999986 0 0 ;
createNode camera -s -n "topShape" -p "top";
	rename -uid "41703269-4543-881F-9E4E-EEBC721C2BA7";
	setAttr -k off ".v" no;
	setAttr ".rnd" no;
	setAttr ".coi" 1000.1;
	setAttr ".ow" 30;
	setAttr ".imn" -type "string" "top";
	setAttr ".den" -type "string" "top_depth";
	setAttr ".man" -type "string" "top_mask";
	setAttr ".hc" -type "string" "viewSet -t %camera";
	setAttr ".o" yes;
createNode transform -s -n "front";
	rename -uid "91492E65-49F1-6788-C7B4-77A7A02E8E48";
	setAttr ".v" no;
	setAttr ".t" -type "double3" -3.0723232694474802 5.7972031196012894 1000.1204609747821 ;
createNode camera -s -n "frontShape" -p "front";
	rename -uid "F624C5FF-4A0A-3E3B-E29C-F1AF879E7905";
	setAttr -k off ".v" no;
	setAttr ".rnd" no;
	setAttr ".coi" 1000.0373298645673;
	setAttr ".ow" 51.916567326481754;
	setAttr ".imn" -type "string" "front";
	setAttr ".den" -type "string" "front_depth";
	setAttr ".man" -type "string" "front_mask";
	setAttr ".tp" -type "double3" 6.6949574165439234 0.90032654410614654 0.08313111021487396 ;
	setAttr ".hc" -type "string" "viewSet -f %camera";
	setAttr ".o" yes;
createNode transform -s -n "side";
	rename -uid "409B13E3-4273-CAEB-A0B1-E59E5C31135B";
	setAttr ".v" no;
	setAttr ".t" -type "double3" 1000.1 0 0 ;
	setAttr ".r" -type "double3" 0 89.999999999999986 0 ;
createNode camera -s -n "sideShape" -p "side";
	rename -uid "A93FC658-4C8A-C8F6-8407-37914E07EA7D";
	setAttr -k off ".v" no;
	setAttr ".rnd" no;
	setAttr ".coi" 1000.1;
	setAttr ".ow" 30;
	setAttr ".imn" -type "string" "side";
	setAttr ".den" -type "string" "side_depth";
	setAttr ".man" -type "string" "side_mask";
	setAttr ".hc" -type "string" "viewSet -s %camera";
	setAttr ".o" yes;
createNode transform -n "point_a";
	rename -uid "8FCA9B0C-4703-1EDE-6EA4-63A1FBA1F9DE";
	setAttr ".t" -type "double3" -19.336748859467821 21.655117182116808 0 ;
createNode locator -n "point_aShape" -p "point_a";
	rename -uid "69EABB91-4A9D-61EC-8D9B-FEB2EE02EB4C";
	setAttr -k off ".v";
createNode transform -n "point_b";
	rename -uid "3F1C3421-44B0-6547-876A-B6AFB558EDDD";
	setAttr ".t" -type "double3" -2.3287263853868669 5.2156435699676864 0 ;
createNode locator -n "point_bShape" -p "point_b";
	rename -uid "19D310D5-443A-3F81-C670-DA8366B8B676";
	setAttr -k off ".v";
createNode lightLinker -s -n "lightLinker1";
	rename -uid "49791BD5-4D2C-4AB7-0CDF-12826A4D0B31";
	setAttr -s 6 ".lnk";
	setAttr -s 6 ".slnk";
createNode shapeEditorManager -n "shapeEditorManager";
	rename -uid "0E8C8CE9-444E-8539-1444-A198BEB60F2A";
createNode poseInterpolatorManager -n "poseInterpolatorManager";
	rename -uid "0E6C9596-4127-D18E-F73F-79893F4E176C";
createNode displayLayerManager -n "layerManager";
	rename -uid "C7959084-4891-9659-95FC-D6BB21D66004";
createNode displayLayer -n "defaultLayer";
	rename -uid "A5596BA0-4CEF-818C-BF7E-15A6777B6746";
createNode renderLayerManager -n "renderLayerManager";
	rename -uid "90EBADBD-4361-A6F5-5561-7087B4BB3B0F";
createNode renderLayer -n "defaultRenderLayer";
	rename -uid "1213B285-4768-AB83-E4B6-14B998260FA1";
	setAttr ".g" yes;
createNode script -n "sceneConfigurationScriptNode";
	rename -uid "259BD32F-4928-151F-D87B-7AB806FA7934";
	setAttr ".b" -type "string" "playbackOptions -min 1 -max 120 -ast 1 -aet 200 ";
	setAttr ".st" 6;
createNode plusMinusAverage -n "plusMinusAverage1";
	rename -uid "A2C693D9-4BCD-206D-C88D-8DB34DF420AB";
	setAttr ".op" 2;
	setAttr -s 2 ".i3";
	setAttr -s 2 ".i3";
createNode reference -n "learning_vector_objectRN";
	rename -uid "F3CCD617-42A3-02F3-97A8-3E8566A27FFD";
	setAttr -s 71 ".phl";
	setAttr ".phl[1]" 0;
	setAttr ".phl[2]" 0;
	setAttr ".phl[3]" 0;
	setAttr ".phl[4]" 0;
	setAttr ".phl[5]" 0;
	setAttr ".phl[6]" 0;
	setAttr ".phl[7]" 0;
	setAttr ".phl[8]" 0;
	setAttr ".phl[9]" 0;
	setAttr ".phl[10]" 0;
	setAttr ".phl[11]" 0;
	setAttr ".phl[12]" 0;
	setAttr ".phl[13]" 0;
	setAttr ".phl[14]" 0;
	setAttr ".phl[15]" 0;
	setAttr ".phl[16]" 0;
	setAttr ".phl[17]" 0;
	setAttr ".phl[18]" 0;
	setAttr ".phl[19]" 0;
	setAttr ".phl[20]" 0;
	setAttr ".phl[21]" 0;
	setAttr ".phl[22]" 0;
	setAttr ".phl[23]" 0;
	setAttr ".phl[24]" 0;
	setAttr ".phl[25]" 0;
	setAttr ".phl[26]" 0;
	setAttr ".phl[27]" 0;
	setAttr ".phl[28]" 0;
	setAttr ".phl[29]" 0;
	setAttr ".phl[30]" 0;
	setAttr ".phl[31]" 0;
	setAttr ".phl[32]" 0;
	setAttr ".phl[33]" 0;
	setAttr ".phl[34]" 0;
	setAttr ".phl[35]" 0;
	setAttr ".phl[36]" 0;
	setAttr ".phl[37]" 0;
	setAttr ".phl[38]" 0;
	setAttr ".phl[39]" 0;
	setAttr ".phl[40]" 0;
	setAttr ".phl[41]" 0;
	setAttr ".phl[42]" 0;
	setAttr ".phl[43]" 0;
	setAttr ".phl[44]" 0;
	setAttr ".phl[45]" 0;
	setAttr ".phl[46]" 0;
	setAttr ".phl[47]" 0;
	setAttr ".phl[48]" 0;
	setAttr ".phl[49]" 0;
	setAttr ".phl[50]" 0;
	setAttr ".phl[51]" 0;
	setAttr ".phl[52]" 0;
	setAttr ".phl[53]" 0;
	setAttr ".phl[54]" 0;
	setAttr ".phl[55]" 0;
	setAttr ".phl[56]" 0;
	setAttr ".phl[57]" 0;
	setAttr ".phl[58]" 0;
	setAttr ".phl[59]" 0;
	setAttr ".phl[60]" 0;
	setAttr ".phl[61]" 0;
	setAttr ".phl[62]" 0;
	setAttr ".phl[63]" 0;
	setAttr ".phl[64]" 0;
	setAttr ".phl[65]" 0;
	setAttr ".phl[66]" 0;
	setAttr ".phl[67]" 0;
	setAttr ".phl[68]" 0;
	setAttr ".phl[69]" 0;
	setAttr ".phl[70]" 0;
	setAttr ".phl[71]" 0;
	setAttr ".ed" -type "dataReferenceEdits" 
		"learning_vector_objectRN"
		"learning_vector_objectRN" 0
		"learning_vector_objectRN" 72
		2 "|learning_vector_object:vector_grp|learning_vector_object:geo_grp|learning_vector_object:vector_blue_ply" 
		"inheritsTransform" " 0"
		5 3 "learning_vector_objectRN" "|learning_vector_object:vector_grp.message" 
		"learning_vector_objectRN.placeHolderList[1]" ""
		5 4 "learning_vector_objectRN" "|learning_vector_object:vector_grp.translate" 
		"learning_vector_objectRN.placeHolderList[2]" ""
		5 3 "learning_vector_objectRN" "|learning_vector_object:vector_grp|learning_vector_object:jnt_grp.message" 
		"learning_vector_objectRN.placeHolderList[3]" ""
		5 3 "learning_vector_objectRN" "|learning_vector_object:vector_grp|learning_vector_object:jnt_grp|learning_vector_object:tail.message" 
		"learning_vector_objectRN.placeHolderList[4]" ""
		5 3 "learning_vector_objectRN" "|learning_vector_object:vector_grp|learning_vector_object:jnt_grp|learning_vector_object:tail|learning_vector_object:tail_parCons.message" 
		"learning_vector_objectRN.placeHolderList[5]" ""
		5 3 "learning_vector_objectRN" "|learning_vector_object:vector_grp|learning_vector_object:jnt_grp|learning_vector_object:tail|learning_vector_object:tail_scalCons.message" 
		"learning_vector_objectRN.placeHolderList[6]" ""
		5 3 "learning_vector_objectRN" "|learning_vector_object:vector_grp|learning_vector_object:jnt_grp|learning_vector_object:head.message" 
		"learning_vector_objectRN.placeHolderList[7]" ""
		5 3 "learning_vector_objectRN" "|learning_vector_object:vector_grp|learning_vector_object:jnt_grp|learning_vector_object:head|learning_vector_object:head_parCons.message" 
		"learning_vector_objectRN.placeHolderList[8]" ""
		5 3 "learning_vector_objectRN" "|learning_vector_object:vector_grp|learning_vector_object:jnt_grp|learning_vector_object:head|learning_vector_object:head_scalCons.message" 
		"learning_vector_objectRN.placeHolderList[9]" ""
		5 3 "learning_vector_objectRN" "|learning_vector_object:vector_grp|learning_vector_object:master_ctrl.message" 
		"learning_vector_objectRN.placeHolderList[10]" ""
		5 3 "learning_vector_objectRN" "|learning_vector_object:vector_grp|learning_vector_object:master_ctrl|learning_vector_object:master_ctrlShape.message" 
		"learning_vector_objectRN.placeHolderList[11]" ""
		5 3 "learning_vector_objectRN" "|learning_vector_object:vector_grp|learning_vector_object:master_ctrl|learning_vector_object:headZro_grp.message" 
		"learning_vector_objectRN.placeHolderList[12]" ""
		5 3 "learning_vector_objectRN" "|learning_vector_object:vector_grp|learning_vector_object:master_ctrl|learning_vector_object:headZro_grp|learning_vector_object:headOffset_grp.message" 
		"learning_vector_objectRN.placeHolderList[13]" ""
		5 4 "learning_vector_objectRN" "|learning_vector_object:vector_grp|learning_vector_object:master_ctrl|learning_vector_object:headZro_grp|learning_vector_object:headOffset_grp|learning_vector_object:head_ctrl.translate" 
		"learning_vector_objectRN.placeHolderList[14]" ""
		5 3 "learning_vector_objectRN" "|learning_vector_object:vector_grp|learning_vector_object:master_ctrl|learning_vector_object:headZro_grp|learning_vector_object:headOffset_grp|learning_vector_object:head_ctrl.message" 
		"learning_vector_objectRN.placeHolderList[15]" ""
		5 3 "learning_vector_objectRN" "|learning_vector_object:vector_grp|learning_vector_object:master_ctrl|learning_vector_object:headZro_grp|learning_vector_object:headOffset_grp|learning_vector_object:head_ctrl|learning_vector_object:head_ctrlShape.message" 
		"learning_vector_objectRN.placeHolderList[16]" ""
		5 3 "learning_vector_objectRN" "|learning_vector_object:vector_grp|learning_vector_object:master_ctrl|learning_vector_object:headZro_grp|learning_vector_object:headOffset_grp|learning_vector_object:head_ctrl|learning_vector_object:head_gmbCtrl.message" 
		"learning_vector_objectRN.placeHolderList[17]" ""
		5 3 "learning_vector_objectRN" "|learning_vector_object:vector_grp|learning_vector_object:master_ctrl|learning_vector_object:headZro_grp|learning_vector_object:headOffset_grp|learning_vector_object:head_ctrl|learning_vector_object:head_gmbCtrl|learning_vector_object:head_gmbCtrlShape.message" 
		"learning_vector_objectRN.placeHolderList[18]" ""
		5 3 "learning_vector_objectRN" "|learning_vector_object:vector_grp|learning_vector_object:master_ctrl|learning_vector_object:headZro_grp|learning_vector_object:headOffset_grp|learning_vector_object:head_ctrl|learning_vector_object:annotationLocator1.message" 
		"learning_vector_objectRN.placeHolderList[19]" ""
		5 3 "learning_vector_objectRN" "|learning_vector_object:vector_grp|learning_vector_object:master_ctrl|learning_vector_object:headZro_grp|learning_vector_object:headOffset_grp|learning_vector_object:head_ctrl|learning_vector_object:annotationLocator1|learning_vector_object:annotationLocator1Shape.message" 
		"learning_vector_objectRN.placeHolderList[20]" ""
		5 3 "learning_vector_objectRN" "|learning_vector_object:vector_grp|learning_vector_object:master_ctrl|learning_vector_object:headZro_grp|learning_vector_object:headOffset_grp|learning_vector_object:head_ctrl|learning_vector_object:annotationLocator1|learning_vector_object:annotation1.message" 
		"learning_vector_objectRN.placeHolderList[21]" ""
		5 3 "learning_vector_objectRN" "|learning_vector_object:vector_grp|learning_vector_object:master_ctrl|learning_vector_object:headZro_grp|learning_vector_object:headOffset_grp|learning_vector_object:head_ctrl|learning_vector_object:annotationLocator1|learning_vector_object:annotation1|learning_vector_object:annotationShape1.message" 
		"learning_vector_objectRN.placeHolderList[22]" ""
		5 3 "learning_vector_objectRN" "|learning_vector_object:vector_grp|learning_vector_object:master_ctrl|learning_vector_object:tailZro_grp.message" 
		"learning_vector_objectRN.placeHolderList[23]" ""
		5 3 "learning_vector_objectRN" "|learning_vector_object:vector_grp|learning_vector_object:master_ctrl|learning_vector_object:tailZro_grp|learning_vector_object:tailOffset_grp.message" 
		"learning_vector_objectRN.placeHolderList[24]" ""
		5 3 "learning_vector_objectRN" "|learning_vector_object:vector_grp|learning_vector_object:master_ctrl|learning_vector_object:tailZro_grp|learning_vector_object:tailOffset_grp|learning_vector_object:tail_ctrl.message" 
		"learning_vector_objectRN.placeHolderList[25]" ""
		5 3 "learning_vector_objectRN" "|learning_vector_object:vector_grp|learning_vector_object:master_ctrl|learning_vector_object:tailZro_grp|learning_vector_object:tailOffset_grp|learning_vector_object:tail_ctrl|learning_vector_object:tail_ctrlShape.message" 
		"learning_vector_objectRN.placeHolderList[26]" ""
		5 3 "learning_vector_objectRN" "|learning_vector_object:vector_grp|learning_vector_object:master_ctrl|learning_vector_object:tailZro_grp|learning_vector_object:tailOffset_grp|learning_vector_object:tail_ctrl|learning_vector_object:tail_gmbCtrl.message" 
		"learning_vector_objectRN.placeHolderList[27]" ""
		5 3 "learning_vector_objectRN" "|learning_vector_object:vector_grp|learning_vector_object:master_ctrl|learning_vector_object:tailZro_grp|learning_vector_object:tailOffset_grp|learning_vector_object:tail_ctrl|learning_vector_object:tail_gmbCtrl|learning_vector_object:tail_gmbCtrlShape.message" 
		"learning_vector_objectRN.placeHolderList[28]" ""
		5 3 "learning_vector_objectRN" "|learning_vector_object:vector_grp|learning_vector_object:geo_grp.message" 
		"learning_vector_objectRN.placeHolderList[29]" ""
		5 3 "learning_vector_objectRN" "|learning_vector_object:vector_grp|learning_vector_object:geo_grp|learning_vector_object:vector_yellow_ply.message" 
		"learning_vector_objectRN.placeHolderList[30]" ""
		5 3 "learning_vector_objectRN" "|learning_vector_object:vector_grp|learning_vector_object:geo_grp|learning_vector_object:vector_yellow_ply|learning_vector_object:vector_yellow_plyShape.message" 
		"learning_vector_objectRN.placeHolderList[31]" ""
		5 3 "learning_vector_objectRN" "|learning_vector_object:vector_grp|learning_vector_object:geo_grp|learning_vector_object:vector_yellow_ply|learning_vector_object:vector_yellow_plyShapeOrig.message" 
		"learning_vector_objectRN.placeHolderList[32]" ""
		5 3 "learning_vector_objectRN" "|learning_vector_object:vector_grp|learning_vector_object:geo_grp|learning_vector_object:vector_blue_ply.message" 
		"learning_vector_objectRN.placeHolderList[33]" ""
		5 3 "learning_vector_objectRN" "|learning_vector_object:vector_grp|learning_vector_object:geo_grp|learning_vector_object:vector_blue_ply|learning_vector_object:vector_blue_plyShape.message" 
		"learning_vector_objectRN.placeHolderList[34]" ""
		5 3 "learning_vector_objectRN" "|learning_vector_object:vector_grp|learning_vector_object:geo_grp|learning_vector_object:vector_blue_ply|learning_vector_object:vector_blue_plyShapeOrig.message" 
		"learning_vector_objectRN.placeHolderList[35]" ""
		5 3 "learning_vector_objectRN" "|learning_vector_object:vector_grp|learning_vector_object:geo_grp|learning_vector_object:vector_blue_ply|learning_vector_object:vector_blue_plyShapeOrig1.message" 
		"learning_vector_objectRN.placeHolderList[36]" ""
		5 3 "learning_vector_objectRN" "|learning_vector_object:vector_grp|learning_vector_object:geo_grp|learning_vector_object:vector_red_ply.message" 
		"learning_vector_objectRN.placeHolderList[37]" ""
		5 3 "learning_vector_objectRN" "|learning_vector_object:vector_grp|learning_vector_object:geo_grp|learning_vector_object:vector_red_ply|learning_vector_object:vector_red_plyShape.message" 
		"learning_vector_objectRN.placeHolderList[38]" ""
		5 3 "learning_vector_objectRN" "|learning_vector_object:vector_grp|learning_vector_object:geo_grp|learning_vector_object:vector_red_ply|learning_vector_object:vector_red_plyShapeOrig.message" 
		"learning_vector_objectRN.placeHolderList[39]" ""
		5 3 "learning_vector_objectRN" "|learning_vector_object:vector_grp|learning_vector_object:geo_grp|learning_vector_object:vector_red_ply|learning_vector_object:vector_red_plyShapeOrig1.message" 
		"learning_vector_objectRN.placeHolderList[40]" ""
		5 3 "learning_vector_objectRN" "learning_vector_object:shapeEditorManager.message" 
		"learning_vector_objectRN.placeHolderList[41]" ""
		5 3 "learning_vector_objectRN" "learning_vector_object:poseInterpolatorManager.message" 
		"learning_vector_objectRN.placeHolderList[42]" ""
		5 3 "learning_vector_objectRN" "learning_vector_object:layerManager.message" 
		"learning_vector_objectRN.placeHolderList[43]" ""
		5 3 "learning_vector_objectRN" "learning_vector_object:defaultLayer.message" 
		"learning_vector_objectRN.placeHolderList[44]" ""
		5 3 "learning_vector_objectRN" "learning_vector_object:defaultRenderLayer.message" 
		"learning_vector_objectRN.placeHolderList[45]" ""
		5 3 "learning_vector_objectRN" "learning_vector_object:sceneConfigurationScriptNode.message" 
		"learning_vector_objectRN.placeHolderList[46]" ""
		5 3 "learning_vector_objectRN" "learning_vector_object:rampShader1.message" 
		"learning_vector_objectRN.placeHolderList[47]" ""
		5 3 "learning_vector_objectRN" "learning_vector_object:rampShader1SG.message" 
		"learning_vector_objectRN.placeHolderList[48]" ""
		5 3 "learning_vector_objectRN" "learning_vector_object:yellow_mat.message" 
		"learning_vector_objectRN.placeHolderList[49]" ""
		5 3 "learning_vector_objectRN" "learning_vector_object:surfaceShader1SG.message" 
		"learning_vector_objectRN.placeHolderList[50]" ""
		5 3 "learning_vector_objectRN" "learning_vector_object:vector_head.message" 
		"learning_vector_objectRN.placeHolderList[51]" ""
		5 3 "learning_vector_objectRN" "learning_vector_object:bindPose2.message" 
		"learning_vector_objectRN.placeHolderList[52]" ""
		5 3 "learning_vector_objectRN" "learning_vector_object:skinCluster1.message" 
		"learning_vector_objectRN.placeHolderList[53]" ""
		5 3 "learning_vector_objectRN" "learning_vector_object:skinCluster1Set.message" 
		"learning_vector_objectRN.placeHolderList[54]" ""
		5 3 "learning_vector_objectRN" "learning_vector_object:tweak1.message" 
		"learning_vector_objectRN.placeHolderList[55]" ""
		5 3 "learning_vector_objectRN" "learning_vector_object:tweakSet1.message" 
		"learning_vector_objectRN.placeHolderList[56]" ""
		5 3 "learning_vector_objectRN" "learning_vector_object:surfaceShader2.message" 
		"learning_vector_objectRN.placeHolderList[57]" ""
		5 3 "learning_vector_objectRN" "learning_vector_object:surfaceShader2SG.message" 
		"learning_vector_objectRN.placeHolderList[58]" ""
		5 3 "learning_vector_objectRN" "learning_vector_object:surfaceShader3.message" 
		"learning_vector_objectRN.placeHolderList[59]" ""
		5 3 "learning_vector_objectRN" "learning_vector_object:surfaceShader3SG.message" 
		"learning_vector_objectRN.placeHolderList[60]" ""
		5 3 "learning_vector_objectRN" "learning_vector_object:yellow_cnd.message" 
		"learning_vector_objectRN.placeHolderList[61]" ""
		5 3 "learning_vector_objectRN" "learning_vector_object:blue_cnd.message" 
		"learning_vector_objectRN.placeHolderList[62]" ""
		5 3 "learning_vector_objectRN" "learning_vector_object:red_cnd.message" 
		"learning_vector_objectRN.placeHolderList[63]" ""
		5 3 "learning_vector_objectRN" "learning_vector_object:skinCluster2.message" 
		"learning_vector_objectRN.placeHolderList[64]" ""
		5 3 "learning_vector_objectRN" "learning_vector_object:tweak2.message" 
		"learning_vector_objectRN.placeHolderList[65]" ""
		5 3 "learning_vector_objectRN" "learning_vector_object:skinCluster2Set.message" 
		"learning_vector_objectRN.placeHolderList[66]" ""
		5 3 "learning_vector_objectRN" "learning_vector_object:tweakSet2.message" 
		"learning_vector_objectRN.placeHolderList[67]" ""
		5 3 "learning_vector_objectRN" "learning_vector_object:skinCluster3.message" 
		"learning_vector_objectRN.placeHolderList[68]" ""
		5 3 "learning_vector_objectRN" "learning_vector_object:tweak3.message" 
		"learning_vector_objectRN.placeHolderList[69]" ""
		5 3 "learning_vector_objectRN" "learning_vector_object:skinCluster3Set.message" 
		"learning_vector_objectRN.placeHolderList[70]" ""
		5 3 "learning_vector_objectRN" "learning_vector_object:tweakSet3.message" 
		"learning_vector_objectRN.placeHolderList[71]" "";
	setAttr ".ptag" -type "string" "";
lockNode -l 1 ;
createNode plusMinusAverage -n "plusMinusAverage3";
	rename -uid "F4DEB2A6-477B-BBDC-2593-47AFC25B8EDA";
	setAttr -s 2 ".i3[1]" -type "float3"  0 0 0;
createNode multiplyDivide -n "multiplyDivide1";
	rename -uid "4699E01D-4A05-BC81-DA91-B4BD3386158B";
	setAttr ".i2" -type "float3" 0.5 0.5 0.5 ;
createNode nodeGraphEditorInfo -n "MayaNodeEditorSavedTabsInfo";
	rename -uid "6654063D-497A-3677-42EC-61A9DA10DFFD";
	setAttr ".pee" yes;
	setAttr ".tgi[0].tn" -type "string" "Untitled_1";
	setAttr ".tgi[0].vl" -type "double2" 824.02937247506122 -485.37369466540963 ;
	setAttr ".tgi[0].vh" -type "double2" 2134.8508141087905 754.14286347056441 ;
	setAttr -s 75 ".tgi[0].ni";
	setAttr ".tgi[0].ni[0].x" 1715.7142333984375;
	setAttr ".tgi[0].ni[0].y" 2820;
	setAttr ".tgi[0].ni[0].nvs" 18304;
	setAttr ".tgi[0].ni[1].x" 1408.5714111328125;
	setAttr ".tgi[0].ni[1].y" 1545.7142333984375;
	setAttr ".tgi[0].ni[1].nvs" 18304;
	setAttr ".tgi[0].ni[2].x" 487.14285278320313;
	setAttr ".tgi[0].ni[2].y" 2820;
	setAttr ".tgi[0].ni[2].nvs" 18304;
	setAttr ".tgi[0].ni[3].x" 794.28570556640625;
	setAttr ".tgi[0].ni[3].y" 2848.571533203125;
	setAttr ".tgi[0].ni[3].nvs" 18304;
	setAttr ".tgi[0].ni[4].x" 1408.5714111328125;
	setAttr ".tgi[0].ni[4].y" 2881.428466796875;
	setAttr ".tgi[0].ni[4].nvs" 18304;
	setAttr ".tgi[0].ni[5].x" 487.14285278320313;
	setAttr ".tgi[0].ni[5].y" 2468.571533203125;
	setAttr ".tgi[0].ni[5].nvs" 18304;
	setAttr ".tgi[0].ni[6].x" 1715.7142333984375;
	setAttr ".tgi[0].ni[6].y" 2517.142822265625;
	setAttr ".tgi[0].ni[6].nvs" 18304;
	setAttr ".tgi[0].ni[7].x" 794.28570556640625;
	setAttr ".tgi[0].ni[7].y" 2668.571533203125;
	setAttr ".tgi[0].ni[7].nvs" 18304;
	setAttr ".tgi[0].ni[8].x" 794.28570556640625;
	setAttr ".tgi[0].ni[8].y" 2185.71435546875;
	setAttr ".tgi[0].ni[8].nvs" 18304;
	setAttr ".tgi[0].ni[9].x" 1408.5714111328125;
	setAttr ".tgi[0].ni[9].y" 1300;
	setAttr ".tgi[0].ni[9].nvs" 18304;
	setAttr ".tgi[0].ni[10].x" 794.28570556640625;
	setAttr ".tgi[0].ni[10].y" 2545.71435546875;
	setAttr ".tgi[0].ni[10].nvs" 18304;
	setAttr ".tgi[0].ni[11].x" 1408.5714111328125;
	setAttr ".tgi[0].ni[11].y" 2218.571533203125;
	setAttr ".tgi[0].ni[11].nvs" 18304;
	setAttr ".tgi[0].ni[12].x" 1408.5714111328125;
	setAttr ".tgi[0].ni[12].y" 1422.857177734375;
	setAttr ".tgi[0].ni[12].nvs" 18304;
	setAttr ".tgi[0].ni[13].x" 1408.5714111328125;
	setAttr ".tgi[0].ni[13].y" 2701.428466796875;
	setAttr ".tgi[0].ni[13].nvs" 18304;
	setAttr ".tgi[0].ni[14].x" 1067.308837890625;
	setAttr ".tgi[0].ni[14].y" 561.82781982421875;
	setAttr ".tgi[0].ni[14].nvs" 18306;
	setAttr ".tgi[0].ni[15].x" 576.4542236328125;
	setAttr ".tgi[0].ni[15].y" -107.62625885009766;
	setAttr ".tgi[0].ni[15].nvs" 18306;
	setAttr ".tgi[0].ni[16].x" 1715.7142333984375;
	setAttr ".tgi[0].ni[16].y" -2305.71435546875;
	setAttr ".tgi[0].ni[16].nvs" 18304;
	setAttr ".tgi[0].ni[17].x" 1408.5714111328125;
	setAttr ".tgi[0].ni[17].y" 571.4285888671875;
	setAttr ".tgi[0].ni[17].nvs" 18304;
	setAttr ".tgi[0].ni[18].x" 1715.7142333984375;
	setAttr ".tgi[0].ni[18].y" -2154.28564453125;
	setAttr ".tgi[0].ni[18].nvs" 18304;
	setAttr ".tgi[0].ni[19].x" 1101.4285888671875;
	setAttr ".tgi[0].ni[19].y" 1265.7142333984375;
	setAttr ".tgi[0].ni[19].nvs" 18304;
	setAttr ".tgi[0].ni[20].x" 487.14285278320313;
	setAttr ".tgi[0].ni[20].y" 2254.28564453125;
	setAttr ".tgi[0].ni[20].nvs" 18304;
	setAttr ".tgi[0].ni[21].x" 1101.4285888671875;
	setAttr ".tgi[0].ni[21].y" 2271.428466796875;
	setAttr ".tgi[0].ni[21].nvs" 18304;
	setAttr ".tgi[0].ni[22].x" 1715.7142333984375;
	setAttr ".tgi[0].ni[22].y" -2002.857177734375;
	setAttr ".tgi[0].ni[22].nvs" 18304;
	setAttr ".tgi[0].ni[23].x" 1715.7142333984375;
	setAttr ".tgi[0].ni[23].y" -1851.4285888671875;
	setAttr ".tgi[0].ni[23].nvs" 18304;
	setAttr ".tgi[0].ni[24].x" 1715.7142333984375;
	setAttr ".tgi[0].ni[24].y" -1700;
	setAttr ".tgi[0].ni[24].nvs" 18304;
	setAttr ".tgi[0].ni[25].x" 1715.7142333984375;
	setAttr ".tgi[0].ni[25].y" 1545.7142333984375;
	setAttr ".tgi[0].ni[25].nvs" 18304;
	setAttr ".tgi[0].ni[26].x" 1101.4285888671875;
	setAttr ".tgi[0].ni[26].y" 2742.857177734375;
	setAttr ".tgi[0].ni[26].nvs" 18304;
	setAttr ".tgi[0].ni[27].x" 1101.4285888671875;
	setAttr ".tgi[0].ni[27].y" 2394.28564453125;
	setAttr ".tgi[0].ni[27].nvs" 18304;
	setAttr ".tgi[0].ni[28].x" 1715.7142333984375;
	setAttr ".tgi[0].ni[28].y" -1548.5714111328125;
	setAttr ".tgi[0].ni[28].nvs" 18304;
	setAttr ".tgi[0].ni[29].x" 1715.7142333984375;
	setAttr ".tgi[0].ni[29].y" 1422.857177734375;
	setAttr ".tgi[0].ni[29].nvs" 18304;
	setAttr ".tgi[0].ni[30].x" 1715.7142333984375;
	setAttr ".tgi[0].ni[30].y" -1397.142822265625;
	setAttr ".tgi[0].ni[30].nvs" 18304;
	setAttr ".tgi[0].ni[31].x" 1715.7142333984375;
	setAttr ".tgi[0].ni[31].y" -1245.7142333984375;
	setAttr ".tgi[0].ni[31].nvs" 18304;
	setAttr ".tgi[0].ni[32].x" 1715.7142333984375;
	setAttr ".tgi[0].ni[32].y" 722.85711669921875;
	setAttr ".tgi[0].ni[32].nvs" 18304;
	setAttr ".tgi[0].ni[33].x" 1715.7142333984375;
	setAttr ".tgi[0].ni[33].y" -1094.2857666015625;
	setAttr ".tgi[0].ni[33].nvs" 18304;
	setAttr ".tgi[0].ni[34].x" 1695.7142333984375;
	setAttr ".tgi[0].ni[34].y" 420;
	setAttr ".tgi[0].ni[34].nvs" 18304;
	setAttr ".tgi[0].ni[35].x" 1715.7142333984375;
	setAttr ".tgi[0].ni[35].y" -942.85711669921875;
	setAttr ".tgi[0].ni[35].nvs" 18304;
	setAttr ".tgi[0].ni[36].x" 1715.7142333984375;
	setAttr ".tgi[0].ni[36].y" 874.28570556640625;
	setAttr ".tgi[0].ni[36].nvs" 18304;
	setAttr ".tgi[0].ni[37].x" 1715.7142333984375;
	setAttr ".tgi[0].ni[37].y" -791.4285888671875;
	setAttr ".tgi[0].ni[37].nvs" 18304;
	setAttr ".tgi[0].ni[38].x" 1715.7142333984375;
	setAttr ".tgi[0].ni[38].y" 571.4285888671875;
	setAttr ".tgi[0].ni[38].nvs" 18304;
	setAttr ".tgi[0].ni[39].x" 1715.7142333984375;
	setAttr ".tgi[0].ni[39].y" 1300;
	setAttr ".tgi[0].ni[39].nvs" 18304;
	setAttr ".tgi[0].ni[40].x" 1408.5714111328125;
	setAttr ".tgi[0].ni[40].y" 1025.7142333984375;
	setAttr ".tgi[0].ni[40].nvs" 18304;
	setAttr ".tgi[0].ni[41].x" 1408.5714111328125;
	setAttr ".tgi[0].ni[41].y" 874.28570556640625;
	setAttr ".tgi[0].ni[41].nvs" 18304;
	setAttr ".tgi[0].ni[42].x" 1408.5714111328125;
	setAttr ".tgi[0].ni[42].y" 2398.571533203125;
	setAttr ".tgi[0].ni[42].nvs" 18304;
	setAttr ".tgi[0].ni[43].x" 1715.7142333984375;
	setAttr ".tgi[0].ni[43].y" 2337.142822265625;
	setAttr ".tgi[0].ni[43].nvs" 18304;
	setAttr ".tgi[0].ni[44].x" 1715.7142333984375;
	setAttr ".tgi[0].ni[44].y" -640;
	setAttr ".tgi[0].ni[44].nvs" 18304;
	setAttr ".tgi[0].ni[45].x" -741.4285888671875;
	setAttr ".tgi[0].ni[45].y" 2421.428466796875;
	setAttr ".tgi[0].ni[45].nvs" 18304;
	setAttr ".tgi[0].ni[46].x" 1408.5714111328125;
	setAttr ".tgi[0].ni[46].y" 722.85711669921875;
	setAttr ".tgi[0].ni[46].nvs" 18304;
	setAttr ".tgi[0].ni[47].x" 1715.7142333984375;
	setAttr ".tgi[0].ni[47].y" -488.57144165039063;
	setAttr ".tgi[0].ni[47].nvs" 18304;
	setAttr ".tgi[0].ni[48].x" 1715.7142333984375;
	setAttr ".tgi[0].ni[48].y" 1025.7142333984375;
	setAttr ".tgi[0].ni[48].nvs" 18304;
	setAttr ".tgi[0].ni[49].x" 180;
	setAttr ".tgi[0].ni[49].y" 2554.28564453125;
	setAttr ".tgi[0].ni[49].nvs" 18304;
	setAttr ".tgi[0].ni[50].x" 794.28570556640625;
	setAttr ".tgi[0].ni[50].y" 2308.571533203125;
	setAttr ".tgi[0].ni[50].nvs" 18304;
	setAttr ".tgi[0].ni[51].x" 794.28570556640625;
	setAttr ".tgi[0].ni[51].y" 2005.7142333984375;
	setAttr ".tgi[0].ni[51].nvs" 18304;
	setAttr ".tgi[0].ni[52].x" 1408.5714111328125;
	setAttr ".tgi[0].ni[52].y" 2095.71435546875;
	setAttr ".tgi[0].ni[52].nvs" 18304;
	setAttr ".tgi[0].ni[53].x" -72.290878295898438;
	setAttr ".tgi[0].ni[53].y" 593.50677490234375;
	setAttr ".tgi[0].ni[53].nvs" 18306;
	setAttr ".tgi[0].ni[54].x" 585.31024169921875;
	setAttr ".tgi[0].ni[54].y" 382.05419921875;
	setAttr ".tgi[0].ni[54].nvs" 18306;
	setAttr ".tgi[0].ni[55].x" 1408.5714111328125;
	setAttr ".tgi[0].ni[55].y" 2578.571533203125;
	setAttr ".tgi[0].ni[55].nvs" 18304;
	setAttr ".tgi[0].ni[56].x" 70.71282958984375;
	setAttr ".tgi[0].ni[56].y" -7.7021493911743164;
	setAttr ".tgi[0].ni[56].nvs" 18306;
	setAttr ".tgi[0].ni[57].x" 944.8072509765625;
	setAttr ".tgi[0].ni[57].y" 39.926895141601563;
	setAttr ".tgi[0].ni[57].nvs" 18306;
	setAttr ".tgi[0].ni[58].x" -434.28570556640625;
	setAttr ".tgi[0].ni[58].y" 2542.857177734375;
	setAttr ".tgi[0].ni[58].nvs" 18304;
	setAttr ".tgi[0].ni[59].x" 1715.7142333984375;
	setAttr ".tgi[0].ni[59].y" -337.14285278320313;
	setAttr ".tgi[0].ni[59].nvs" 18304;
	setAttr ".tgi[0].ni[60].x" 1715.7142333984375;
	setAttr ".tgi[0].ni[60].y" -185.71427917480469;
	setAttr ".tgi[0].ni[60].nvs" 18304;
	setAttr ".tgi[0].ni[61].x" 1372.133544921875;
	setAttr ".tgi[0].ni[61].y" 270.726318359375;
	setAttr ".tgi[0].ni[61].nvs" 18306;
	setAttr ".tgi[0].ni[62].x" 1408.5714111328125;
	setAttr ".tgi[0].ni[62].y" 1971.4285888671875;
	setAttr ".tgi[0].ni[62].nvs" 18304;
	setAttr ".tgi[0].ni[63].x" -127.14286041259766;
	setAttr ".tgi[0].ni[63].y" 2728.571533203125;
	setAttr ".tgi[0].ni[63].nvs" 18304;
	setAttr ".tgi[0].ni[64].x" -127.14286041259766;
	setAttr ".tgi[0].ni[64].y" 2360;
	setAttr ".tgi[0].ni[64].nvs" 18304;
	setAttr ".tgi[0].ni[65].x" 1715.7142333984375;
	setAttr ".tgi[0].ni[65].y" -34.285713195800781;
	setAttr ".tgi[0].ni[65].nvs" 18304;
	setAttr ".tgi[0].ni[66].x" 1715.7142333984375;
	setAttr ".tgi[0].ni[66].y" 117.14286041259766;
	setAttr ".tgi[0].ni[66].nvs" 18304;
	setAttr ".tgi[0].ni[67].x" 1408.5714111328125;
	setAttr ".tgi[0].ni[67].y" 1177.142822265625;
	setAttr ".tgi[0].ni[67].nvs" 18304;
	setAttr ".tgi[0].ni[68].x" -741.4285888671875;
	setAttr ".tgi[0].ni[68].y" 2298.571533203125;
	setAttr ".tgi[0].ni[68].nvs" 18304;
	setAttr ".tgi[0].ni[69].x" 1715.7142333984375;
	setAttr ".tgi[0].ni[69].y" 1177.142822265625;
	setAttr ".tgi[0].ni[69].nvs" 18304;
	setAttr ".tgi[0].ni[70].x" 1715.7142333984375;
	setAttr ".tgi[0].ni[70].y" 268.57144165039063;
	setAttr ".tgi[0].ni[70].nvs" 18304;
	setAttr ".tgi[0].ni[71].x" 1715.7142333984375;
	setAttr ".tgi[0].ni[71].y" -2457.142822265625;
	setAttr ".tgi[0].ni[71].nvs" 18304;
	setAttr ".tgi[0].ni[72].x" -434.28570556640625;
	setAttr ".tgi[0].ni[72].y" 2420;
	setAttr ".tgi[0].ni[72].nvs" 18304;
	setAttr ".tgi[0].ni[73].x" -127.14286041259766;
	setAttr ".tgi[0].ni[73].y" 2482.857177734375;
	setAttr ".tgi[0].ni[73].nvs" 18304;
	setAttr ".tgi[0].ni[74].x" 1408.5714111328125;
	setAttr ".tgi[0].ni[74].y" 1695.7142333984375;
	setAttr ".tgi[0].ni[74].nvs" 18304;
select -ne :time1;
	setAttr ".o" 1;
	setAttr ".unw" 1;
select -ne :hardwareRenderingGlobals;
	setAttr ".otfna" -type "stringArray" 22 "NURBS Curves" "NURBS Surfaces" "Polygons" "Subdiv Surface" "Particles" "Particle Instance" "Fluids" "Strokes" "Image Planes" "UI" "Lights" "Cameras" "Locators" "Joints" "IK Handles" "Deformers" "Motion Trails" "Components" "Hair Systems" "Follicles" "Misc. UI" "Ornaments"  ;
	setAttr ".otfva" -type "Int32Array" 22 0 1 1 1 1 1
		 1 1 1 0 0 0 0 0 0 0 0 0
		 0 0 0 0 ;
	setAttr ".fprt" yes;
select -ne :renderPartition;
	setAttr -s 6 ".st";
select -ne :renderGlobalsList1;
select -ne :defaultShaderList1;
	setAttr -s 8 ".s";
select -ne :postProcessList1;
	setAttr -s 2 ".p";
select -ne :defaultRenderUtilityList1;
	setAttr -s 7 ".u";
select -ne :defaultRenderingList1;
	setAttr -s 2 ".r";
select -ne :initialShadingGroup;
	setAttr ".ro" yes;
select -ne :initialParticleSE;
	setAttr ".ro" yes;
select -ne :defaultRenderGlobals;
	setAttr ".fs" 1;
	setAttr ".ef" 10;
select -ne :defaultResolution;
	setAttr ".pa" 1;
select -ne :hardwareRenderGlobals;
	setAttr ".ctrs" 256;
	setAttr ".btrs" 512;
connectAttr "learning_vector_objectRN.phl[1]" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[57].dn"
		;
connectAttr "plusMinusAverage3.o3" "learning_vector_objectRN.phl[2]";
connectAttr "learning_vector_objectRN.phl[3]" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[63].dn"
		;
connectAttr "learning_vector_objectRN.phl[4]" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[73].dn"
		;
connectAttr "learning_vector_objectRN.phl[5]" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[72].dn"
		;
connectAttr "learning_vector_objectRN.phl[6]" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[62].dn"
		;
connectAttr "learning_vector_objectRN.phl[7]" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[64].dn"
		;
connectAttr "learning_vector_objectRN.phl[8]" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[74].dn"
		;
connectAttr "learning_vector_objectRN.phl[9]" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[58].dn"
		;
connectAttr "learning_vector_objectRN.phl[10]" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[59].dn"
		;
connectAttr "learning_vector_objectRN.phl[11]" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[60].dn"
		;
connectAttr "learning_vector_objectRN.phl[12]" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[65].dn"
		;
connectAttr "learning_vector_objectRN.phl[13]" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[66].dn"
		;
connectAttr "multiplyDivide1.o" "learning_vector_objectRN.phl[14]";
connectAttr "learning_vector_objectRN.phl[15]" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[61].dn"
		;
connectAttr "learning_vector_objectRN.phl[16]" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[67].dn"
		;
connectAttr "learning_vector_objectRN.phl[17]" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[68].dn"
		;
connectAttr "learning_vector_objectRN.phl[18]" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[69].dn"
		;
connectAttr "learning_vector_objectRN.phl[19]" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[70].dn"
		;
connectAttr "learning_vector_objectRN.phl[20]" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[17].dn"
		;
connectAttr "learning_vector_objectRN.phl[21]" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[16].dn"
		;
connectAttr "learning_vector_objectRN.phl[22]" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[38].dn"
		;
connectAttr "learning_vector_objectRN.phl[23]" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[47].dn"
		;
connectAttr "learning_vector_objectRN.phl[24]" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[24].dn"
		;
connectAttr "learning_vector_objectRN.phl[25]" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[35].dn"
		;
connectAttr "learning_vector_objectRN.phl[26]" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[41].dn"
		;
connectAttr "learning_vector_objectRN.phl[27]" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[45].dn"
		;
connectAttr "learning_vector_objectRN.phl[28]" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[36].dn"
		;
connectAttr "learning_vector_objectRN.phl[29]" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[37].dn"
		;
connectAttr "learning_vector_objectRN.phl[30]" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[29].dn"
		;
connectAttr "learning_vector_objectRN.phl[31]" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[21].dn"
		;
connectAttr "learning_vector_objectRN.phl[32]" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[18].dn"
		;
connectAttr "learning_vector_objectRN.phl[33]" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[25].dn"
		;
connectAttr "learning_vector_objectRN.phl[34]" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[26].dn"
		;
connectAttr "learning_vector_objectRN.phl[35]" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[44].dn"
		;
connectAttr "learning_vector_objectRN.phl[36]" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[23].dn"
		;
connectAttr "learning_vector_objectRN.phl[37]" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[39].dn"
		;
connectAttr "learning_vector_objectRN.phl[38]" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[27].dn"
		;
connectAttr "learning_vector_objectRN.phl[39]" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[22].dn"
		;
connectAttr "learning_vector_objectRN.phl[40]" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[28].dn"
		;
connectAttr "learning_vector_objectRN.phl[41]" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[30].dn"
		;
connectAttr "learning_vector_objectRN.phl[42]" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[31].dn"
		;
connectAttr "learning_vector_objectRN.phl[43]" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[46].dn"
		;
connectAttr "learning_vector_objectRN.phl[44]" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[32].dn"
		;
connectAttr "learning_vector_objectRN.phl[45]" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[33].dn"
		;
connectAttr "learning_vector_objectRN.phl[46]" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[34].dn"
		;
connectAttr "learning_vector_objectRN.phl[47]" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[40].dn"
		;
connectAttr "learning_vector_objectRN.phl[48]" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[48].dn"
		;
connectAttr "learning_vector_objectRN.phl[49]" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[42].dn"
		;
connectAttr "learning_vector_objectRN.phl[50]" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[43].dn"
		;
connectAttr "learning_vector_objectRN.phl[51]" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[19].dn"
		;
connectAttr "learning_vector_objectRN.phl[52]" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[49].dn"
		;
connectAttr "learning_vector_objectRN.phl[53]" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[20].dn"
		;
connectAttr "learning_vector_objectRN.phl[54]" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[50].dn"
		;
connectAttr "learning_vector_objectRN.phl[55]" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[51].dn"
		;
connectAttr "learning_vector_objectRN.phl[56]" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[52].dn"
		;
connectAttr "learning_vector_objectRN.phl[57]" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[55].dn"
		;
connectAttr "learning_vector_objectRN.phl[58]" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[6].dn"
		;
connectAttr "learning_vector_objectRN.phl[59]" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[4].dn"
		;
connectAttr "learning_vector_objectRN.phl[60]" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[0].dn"
		;
connectAttr "learning_vector_objectRN.phl[61]" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[12].dn"
		;
connectAttr "learning_vector_objectRN.phl[62]" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[1].dn"
		;
connectAttr "learning_vector_objectRN.phl[63]" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[9].dn"
		;
connectAttr "learning_vector_objectRN.phl[64]" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[7].dn"
		;
connectAttr "learning_vector_objectRN.phl[65]" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[2].dn"
		;
connectAttr "learning_vector_objectRN.phl[66]" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[13].dn"
		;
connectAttr "learning_vector_objectRN.phl[67]" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[3].dn"
		;
connectAttr "learning_vector_objectRN.phl[68]" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[5].dn"
		;
connectAttr "learning_vector_objectRN.phl[69]" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[8].dn"
		;
connectAttr "learning_vector_objectRN.phl[70]" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[10].dn"
		;
connectAttr "learning_vector_objectRN.phl[71]" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[11].dn"
		;
relationship "link" ":lightLinker1" ":initialShadingGroup.message" ":defaultLightSet.message";
relationship "link" ":lightLinker1" ":initialParticleSE.message" ":defaultLightSet.message";
relationship "shadowLink" ":lightLinker1" ":initialShadingGroup.message" ":defaultLightSet.message";
relationship "shadowLink" ":lightLinker1" ":initialParticleSE.message" ":defaultLightSet.message";
connectAttr "layerManager.dli[0]" "defaultLayer.id";
connectAttr "renderLayerManager.rlmi[0]" "defaultRenderLayer.rlid";
connectAttr "point_b.t" "plusMinusAverage1.i3[0]";
connectAttr "point_a.t" "plusMinusAverage1.i3[1]";
connectAttr "point_a.t" "plusMinusAverage3.i3[0]";
connectAttr "plusMinusAverage1.o3" "multiplyDivide1.i1";
connectAttr "multiplyDivide1.msg" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[14].dn"
		;
connectAttr "plusMinusAverage3.msg" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[15].dn"
		;
connectAttr "point_b.msg" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[53].dn";
connectAttr "plusMinusAverage1.msg" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[54].dn"
		;
connectAttr "point_a.msg" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[56].dn";
connectAttr "learning_vector_objectRN.msg" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[71].dn"
		;
connectAttr "plusMinusAverage1.msg" ":defaultRenderUtilityList1.u" -na;
connectAttr "plusMinusAverage3.msg" ":defaultRenderUtilityList1.u" -na;
connectAttr "multiplyDivide1.msg" ":defaultRenderUtilityList1.u" -na;
connectAttr "defaultRenderLayer.msg" ":defaultRenderingList1.r" -na;
// End of 01_vector_02_minus.ma
